#!/usr/bin/env python3
"""Generalized deterministic ESKA Knowledge Agent for the Pizza reference.

Discovery and HTTP invocation are generic. Semantically typed request/result
adaptation is selected from the machine-readable Agent + Capability contract.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from rdflib import Graph, Literal, Namespace, RDF, URIRef

AGENT_IRI = "urn:eska:example:pizza:general-agent:PizzaGeneralizedKnowledgeAgent"
IRI_LIST_ADAPTER = "iri-list"
SHACL_REPORT_ADAPTER = "rdf-jsonld-shacl-report"

ESKA = Namespace("urn:eska:core:")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
SH = Namespace("http://www.w3.org/ns/shacl#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")


def _clean(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    return value


def discover_contract(
    robot_jar: Path, architecture: Path, query: Path, target_capability: str
) -> dict[str, str]:
    if not robot_jar.exists():
        raise FileNotFoundError(f"ROBOT jar not found: {robot_jar}")
    if not architecture.exists():
        raise FileNotFoundError(f"Architecture model not found: {architecture}")

    with tempfile.TemporaryDirectory(prefix="eska-general-agent-") as temp_dir:
        output = Path(temp_dir) / "discovery.csv"
        subprocess.run(
            [
                "java",
                "-jar",
                str(robot_jar),
                "query",
                "--input",
                str(architecture),
                "--query",
                str(query),
                str(output),
            ],
            check=True,
        )
        with output.open(newline="", encoding="utf-8") as handle:
            rows = [
                {key: _clean(value) for key, value in row.items()}
                for row in csv.DictReader(handle)
            ]

    matches = [row for row in rows if row.get("capability") == target_capability]
    if not matches:
        raise RuntimeError(
            f"No compatible Service/adapter contract found for {target_capability}"
        )
    if len(matches) != 1:
        raise RuntimeError(
            f"Discovery is ambiguous: found {len(matches)} compatible contracts for {target_capability}"
        )

    required = {
        "agent",
        "capability",
        "adapter",
        "adapterKey",
        "service",
        "operation",
        "binding",
        "method",
        "path",
        "mediaType",
        "inputType",
        "outputType",
        "relation",
        "requestField",
        "resultField",
        "relationField",
        "capabilityField",
    }
    missing = sorted(key for key in required if not matches[0].get(key))
    if missing:
        raise RuntimeError(
            f"Discovered generalized Agent contract is incomplete: {', '.join(missing)}"
        )
    if matches[0]["agent"] != AGENT_IRI:
        raise RuntimeError("Discovery returned a different Knowledge Agent")
    return matches[0]


def prepare_input(contract: dict[str, str], raw_input: str, input_format: str) -> object:
    adapter_key = contract["adapterKey"]
    if adapter_key == IRI_LIST_ADAPTER:
        if not raw_input.startswith(("http://", "https://", "urn:")):
            raise RuntimeError("IRI-list adapter requires an IRI input")
        return raw_input

    if adapter_key == SHACL_REPORT_ADAPTER:
        path = Path(raw_input)
        graph = Graph().parse(path, format=input_format)
        if len(graph) == 0:
            raise RuntimeError(f"Input RDF graph is empty: {path}")
        return json.loads(graph.serialize(format="json-ld"))

    raise RuntimeError(f"Unsupported invocation adapter: {adapter_key}")


def invoke_service(
    contract: dict[str, str], service_base_url: str, prepared_input: object
) -> tuple[str, dict[str, object]]:
    if contract["mediaType"] != "application/json":
        raise RuntimeError(
            f"Reference Agent currently supports application/json access envelopes, discovered {contract['mediaType']}"
        )
    method = contract["method"].upper()
    if method != "POST":
        raise RuntimeError(f"Reference Agent currently supports POST, discovered {method}")

    endpoint = f"{service_base_url.rstrip('/')}/{contract['path'].lstrip('/')}"
    payload = {contract["requestField"]: prepared_input}
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        method=method,
        headers={"Content-Type": contract["mediaType"], "Accept": contract["mediaType"]},
    )

    try:
        with urlopen(request, timeout=10) as response:  # noqa: S310 - explicit reference HTTP client
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Knowledge Service returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Knowledge Service invocation failed: {exc}") from exc

    if not isinstance(body, dict):
        raise RuntimeError("Knowledge Service response is not a JSON object")
    if body.get(contract["capabilityField"]) != contract["capability"]:
        raise RuntimeError("Semantic continuity violation: returned capability differs from discovered contract")
    if body.get(contract["relationField"]) != contract["relation"]:
        raise RuntimeError("Semantic continuity violation: returned relation differs from discovered contract")
    return endpoint, body


def interpret_result(
    contract: dict[str, str], body: dict[str, object]
) -> dict[str, object]:
    result_value = body.get(contract["resultField"])
    adapter_key = contract["adapterKey"]

    if adapter_key == IRI_LIST_ADAPTER:
        if not isinstance(result_value, list) or not all(
            isinstance(item, str) for item in result_value
        ):
            raise RuntimeError("IRI-list adapter expected a list of semantic IRIs")
        if not all(item.startswith(("http://", "https://", "urn:")) for item in result_value):
            raise RuntimeError("IRI-list adapter received a non-IRI result")
        return {
            "adapterKey": adapter_key,
            "relation": contract["relation"],
            "values": result_value,
        }

    if adapter_key == SHACL_REPORT_ADAPTER:
        if not isinstance(result_value, (dict, list)):
            raise RuntimeError("SHACL adapter expected a JSON-LD RDF result")
        graph = Graph().parse(data=json.dumps(result_value), format="json-ld")
        reports = list(graph.subjects(RDF.type, SH.ValidationReport))
        if len(reports) != 1:
            raise RuntimeError(f"Expected exactly one sh:ValidationReport, found {len(reports)}")
        conforms_literal = graph.value(reports[0], SH.conforms)
        if not isinstance(conforms_literal, Literal):
            raise RuntimeError("SHACL ValidationReport is missing literal sh:conforms")
        return {
            "adapterKey": adapter_key,
            "relation": contract["relation"],
            "conforms": bool(conforms_literal.toPython()),
            "validationResultCount": len(set(graph.subjects(RDF.type, SH.ValidationResult))),
            "report": result_value,
        }

    raise RuntimeError(f"Unsupported invocation adapter: {adapter_key}")


def write_provenance(
    path: Path,
    contract: dict[str, str],
    raw_input: str,
    architecture: Path,
    semantic_result: dict[str, object],
) -> None:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    slug = "classification" if contract["adapterKey"] == IRI_LIST_ADAPTER else "validation"
    base = f"urn:eska:example:pizza:general-agent-run:{slug}:"
    execution = URIRef(base + "execution")
    result = URIRef(base + "result")
    verification = URIRef(base + "verification")
    input_entity = URIRef(base + "input")
    architecture_entity = URIRef(base + "architecture")

    graph = Graph()
    graph.bind("dcterms", DCTERMS)
    graph.bind("eska", ESKA)
    graph.bind("prov", PROV)
    graph.bind("sh", SH)

    graph.add((URIRef(AGENT_IRI), RDF.type, PROV.SoftwareAgent))
    graph.add((execution, RDF.type, ESKA.Execution))
    graph.add((execution, RDF.type, PROV.Activity))
    graph.add((execution, ESKA.executesCapability, URIRef(contract["capability"])))
    graph.add((execution, ESKA.generatesResult, result))
    graph.add((execution, PROV.wasAssociatedWith, URIRef(AGENT_IRI)))
    graph.add((execution, PROV.used, URIRef(contract["service"])))
    graph.add((execution, PROV.used, URIRef(contract["adapter"])))
    graph.add((execution, PROV.used, input_entity))
    graph.add((execution, PROV.used, architecture_entity))
    graph.add((execution, PROV.generated, result))
    graph.add((execution, PROV.endedAtTime, Literal(timestamp, datatype=XSD.dateTime)))

    graph.add((result, RDF.type, ESKA.Result))
    graph.add((result, RDF.type, PROV.Entity))
    graph.add((result, DCTERMS.relation, URIRef(contract["relation"])))
    graph.add((result, PROV.wasGeneratedBy, execution))
    if contract["adapterKey"] == SHACL_REPORT_ADAPTER:
        graph.add((result, RDF.type, SH.ValidationReport))
        graph.add((result, SH.conforms, Literal(bool(semantic_result["conforms"]))))
    else:
        for value in semantic_result.get("values", []):
            if isinstance(value, str):
                graph.add((result, DCTERMS.hasPart, URIRef(value)))

    graph.add((verification, RDF.type, ESKA.Verification))
    graph.add((verification, RDF.type, PROV.Activity))
    graph.add((verification, ESKA.verifiesExecution, execution))
    graph.add((verification, ESKA.verifiesResult, result))
    graph.add((verification, PROV.used, result))
    graph.add((verification, PROV.endedAtTime, Literal(timestamp, datatype=XSD.dateTime)))

    graph.add((input_entity, RDF.type, PROV.Entity))
    graph.add((input_entity, DCTERMS.identifier, Literal(raw_input)))
    graph.add((architecture_entity, RDF.type, PROV.Entity))
    graph.add((architecture_entity, DCTERMS.identifier, Literal(str(architecture))))

    path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=path, format="turtle")


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Generalized deterministic ESKA Pizza Knowledge Agent")
    parser.add_argument("--robot-jar", type=Path, default=here / ".work" / "robot.jar")
    parser.add_argument("--architecture", type=Path, required=True)
    parser.add_argument("--query", type=Path, default=here / "discover-service-generic.sparql")
    parser.add_argument("--capability", required=True)
    parser.add_argument("--service-base-url", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--input-format", default="turtle")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--provenance", type=Path)
    args = parser.parse_args()

    contract = discover_contract(args.robot_jar, args.architecture, args.query, args.capability)
    prepared = prepare_input(contract, args.input, args.input_format)
    endpoint, body = invoke_service(contract, args.service_base_url, prepared)
    semantic_result = interpret_result(contract, body)

    result = {
        "agent": AGENT_IRI,
        "targetCapability": contract["capability"],
        "adapter": {
            "iri": contract["adapter"],
            "key": contract["adapterKey"],
        },
        "discovery": {
            "service": contract["service"],
            "operation": contract["operation"],
            "accessBinding": contract["binding"],
            "method": contract["method"],
            "path": contract["path"],
            "mediaType": contract["mediaType"],
            "inputType": contract["inputType"],
            "outputType": contract["outputType"],
            "relation": contract["relation"],
        },
        "invocation": {"endpoint": endpoint, "input": args.input},
        "semanticResult": semantic_result,
    }

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if args.provenance:
        write_provenance(args.provenance, contract, args.input, args.architecture, semantic_result)


if __name__ == "__main__":
    main()
