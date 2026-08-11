#!/usr/bin/env python3
"""Deterministic Knowledge Agent for PizzaValidationCapability."""

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

AGENT_IRI = "urn:eska:example:pizza:validation-agent:PizzaValidationAgent"
TARGET_CAPABILITY = "urn:eska:example:pizza:validation:PizzaValidationCapability"
SHACL_REPORT = "http://www.w3.org/ns/shacl#ValidationReport"
SHACL_CONFORMS = "http://www.w3.org/ns/shacl#conforms"

ESKA = Namespace("https://w3id.org/eska#")
VAL = Namespace("urn:eska:example:pizza:validation:")
VALAGENT = Namespace("urn:eska:example:pizza:validation-agent:")
RUN = Namespace("urn:eska:example:pizza:validation-agent-run:")
SH = Namespace("http://www.w3.org/ns/shacl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")


def _clean(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    return value


def discover_operation(robot_jar: Path, architecture: Path, query: Path) -> dict[str, str]:
    if not robot_jar.exists():
        raise FileNotFoundError(f"ROBOT jar not found: {robot_jar}")
    if not architecture.exists():
        raise FileNotFoundError(f"Architecture model not found: {architecture}")

    with tempfile.TemporaryDirectory(prefix="eska-validation-agent-") as temp_dir:
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
            rows = [{key: _clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]

    if not rows:
        raise RuntimeError(f"No Knowledge Service exposes target capability {TARGET_CAPABILITY}")
    if len(rows) != 1:
        raise RuntimeError(f"Discovery is ambiguous: found {len(rows)} operations for {TARGET_CAPABILITY}")

    required = {
        "service",
        "operation",
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
    missing = sorted(key for key in required if not rows[0].get(key))
    if missing:
        raise RuntimeError(f"Discovered service contract is incomplete: {', '.join(missing)}")
    return rows[0]


def expanded_jsonld(path: Path, rdf_format: str) -> object:
    graph = Graph().parse(path, format=rdf_format)
    if len(graph) == 0:
        raise RuntimeError(f"Input RDF graph is empty: {path}")
    return json.loads(graph.serialize(format="json-ld"))


def invoke_service(
    contract: dict[str, str], service_base_url: str, document: object
) -> tuple[str, dict[str, object], Graph, bool, int]:
    if contract["mediaType"] != "application/json":
        raise RuntimeError(f"Reference validation agent only supports application/json, discovered {contract['mediaType']}")
    if contract["method"].upper() != "POST":
        raise RuntimeError(f"Reference validation agent only supports POST, discovered {contract['method']}")
    if contract["outputType"] != SHACL_REPORT:
        raise RuntimeError(f"Expected SHACL ValidationReport output, discovered {contract['outputType']}")
    if contract["relation"] != SHACL_CONFORMS:
        raise RuntimeError(f"Expected sh:conforms result relation, discovered {contract['relation']}")

    endpoint = f"{service_base_url.rstrip('/')}/{contract['path'].lstrip('/')}"
    payload = {contract["requestField"]: document}
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    try:
        with urlopen(request, timeout=10) as response:  # noqa: S310 - explicit local/reference HTTP client
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Knowledge Service returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Knowledge Service invocation failed: {exc}") from exc

    if not isinstance(body, dict):
        raise RuntimeError("Knowledge Service response is not a JSON object")
    if body.get(contract["capabilityField"]) != TARGET_CAPABILITY:
        raise RuntimeError("Semantic continuity violation: returned capability differs from target")
    if body.get(contract["relationField"]) != contract["relation"]:
        raise RuntimeError("Semantic continuity violation: returned relation differs from discovered contract")

    report_document = body.get(contract["resultField"])
    if not isinstance(report_document, (dict, list)):
        raise RuntimeError("Knowledge Service result field is not a JSON-LD SHACL report")

    report_graph = Graph().parse(data=json.dumps(report_document), format="json-ld")
    reports = list(report_graph.subjects(RDF.type, SH.ValidationReport))
    if len(reports) != 1:
        raise RuntimeError(f"Expected exactly one sh:ValidationReport, found {len(reports)}")
    conforms_literal = report_graph.value(reports[0], SH.conforms)
    if not isinstance(conforms_literal, Literal):
        raise RuntimeError("SHACL report is missing literal sh:conforms")
    conforms = bool(conforms_literal.toPython())
    violations = len(set(report_graph.subjects(RDF.type, SH.ValidationResult)))

    return endpoint, body, report_graph, conforms, violations


def write_provenance(
    path: Path,
    contract: dict[str, str],
    input_path: Path,
    architecture: Path,
    conforms: bool,
    violations: int,
) -> None:
    executed_at = datetime.now(timezone.utc).replace(microsecond=0)
    graph = Graph()
    graph.bind("dcterms", DCTERMS)
    graph.bind("eska", ESKA)
    graph.bind("prov", PROV)
    graph.bind("run", RUN)
    graph.bind("sh", SH)
    graph.bind("val", VAL)
    graph.bind("valagent", VALAGENT)

    execution = RUN.knowledge_agent_invocation
    result = RUN.validation_report
    verification = RUN.validation_report_verification
    input_entity = RUN.input_data_graph
    architecture_entity = RUN.architecture_model

    graph.add((VALAGENT.PizzaValidationAgent, RDF.type, PROV.SoftwareAgent))

    graph.add((execution, RDF.type, ESKA.Execution))
    graph.add((execution, RDF.type, PROV.Activity))
    graph.add((execution, DCTERMS.description, Literal("Pizza Validation Knowledge Agent discovery and service invocation", lang="en")))
    graph.add((execution, DCTERMS.conformsTo, URIRef(TARGET_CAPABILITY)))
    graph.add((execution, ESKA.executesCapability, URIRef(TARGET_CAPABILITY)))
    graph.add((execution, ESKA.usesSemanticModel, VAL.PizzaShapesGraph))
    graph.add((execution, ESKA.usesExecutableArtifact, VAL.SHACLValidationArtifact))
    graph.add((execution, ESKA.generatesResult, result))
    graph.add((execution, PROV.wasAssociatedWith, VALAGENT.PizzaValidationAgent))
    graph.add((execution, PROV.used, URIRef(contract["service"])))
    graph.add((execution, PROV.used, input_entity))
    graph.add((execution, PROV.used, architecture_entity))
    graph.add((execution, PROV.generated, result))
    graph.add((execution, PROV.endedAtTime, Literal(executed_at, datatype=XSD.dateTime)))

    graph.add((result, RDF.type, ESKA.Result))
    graph.add((result, RDF.type, PROV.Entity))
    graph.add((result, RDF.type, SH.ValidationReport))
    graph.add((result, SH.conforms, Literal(conforms)))
    graph.add((result, DCTERMS.description, Literal(f"SHACL ValidationReport returned through the discovered Knowledge Service; validation results={violations}.", lang="en")))
    graph.add((result, PROV.wasGeneratedBy, execution))

    graph.add((verification, RDF.type, ESKA.Verification))
    graph.add((verification, RDF.type, PROV.Activity))
    graph.add((verification, ESKA.verifiesExecution, execution))
    graph.add((verification, ESKA.verifiesResult, result))
    graph.add((verification, PROV.used, result))
    graph.add((verification, PROV.endedAtTime, Literal(executed_at, datatype=XSD.dateTime)))

    graph.add((input_entity, RDF.type, PROV.Entity))
    graph.add((input_entity, DCTERMS.identifier, Literal(str(input_path))))
    graph.add((architecture_entity, RDF.type, PROV.Entity))
    graph.add((architecture_entity, DCTERMS.identifier, Literal(str(architecture))))

    path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=path, format="turtle")


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="ESKA deterministic Pizza Validation Knowledge Agent")
    parser.add_argument("--robot-jar", type=Path, default=here.parent / ".work" / "robot.jar")
    parser.add_argument("--architecture", type=Path, default=here / "results" / "architecture-model.owl")
    parser.add_argument("--query", type=Path, default=here / "discover-service.sparql")
    parser.add_argument("--service-base-url", default="http://127.0.0.1:8081")
    parser.add_argument("--input", type=Path, required=True, help="RDF data graph to validate")
    parser.add_argument("--input-format", default="turtle")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--provenance", type=Path)
    args = parser.parse_args()

    contract = discover_operation(args.robot_jar, args.architecture, args.query)
    document = expanded_jsonld(args.input, args.input_format)
    endpoint, response, _, conforms, violations = invoke_service(contract, args.service_base_url, document)

    result = {
        "agent": AGENT_IRI,
        "targetCapability": TARGET_CAPABILITY,
        "discovery": {
            "service": contract["service"],
            "operation": contract["operation"],
            "method": contract["method"],
            "path": contract["path"],
            "mediaType": contract["mediaType"],
            "inputType": contract["inputType"],
            "outputType": contract["outputType"],
            "relation": contract["relation"],
        },
        "invocation": {"endpoint": endpoint, "input": str(args.input)},
        "semanticResult": {
            "relation": contract["relation"],
            "conforms": conforms,
            "validationResultCount": violations,
            "report": response[contract["resultField"]],
        },
    }

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if args.provenance:
        write_provenance(args.provenance, contract, args.input, args.architecture, conforms, violations)


if __name__ == "__main__":
    main()
