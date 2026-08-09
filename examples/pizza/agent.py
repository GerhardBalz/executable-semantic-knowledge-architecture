#!/usr/bin/env python3
"""Deterministic ESKA Knowledge Agent for the Pizza classification example.

The agent does not contain Pizza classification logic and does not know which
Knowledge Service endpoint implements the capability. It discovers the service
operation from the machine-readable ESKA architecture model, combines that
contract with a runtime service location, invokes the service, and validates
that the response preserves the discovered semantic contract.
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

AGENT_IRI = "urn:eska:example:pizza:agent:PizzaKnowledgeAgent"
TARGET_CAPABILITY = "urn:eska:example:pizza:capability:PizzaClassificationCapability"


def _clean(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    return value


def discover_operation(robot_jar: Path, architecture: Path, query: Path) -> dict[str, str]:
    """Discover exactly one service operation that exposes the target capability."""

    if not robot_jar.exists():
        raise FileNotFoundError(f"ROBOT jar not found: {robot_jar}")
    if not architecture.exists():
        raise FileNotFoundError(f"Architecture model not found: {architecture}")

    with tempfile.TemporaryDirectory(prefix="eska-agent-") as temp_dir:
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

    if not rows:
        raise RuntimeError(
            f"No Knowledge Service exposes target capability {TARGET_CAPABILITY}"
        )
    if len(rows) != 1:
        raise RuntimeError(
            f"Discovery is ambiguous: found {len(rows)} service operations for {TARGET_CAPABILITY}"
        )

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


def invoke_service(
    contract: dict[str, str], service_base_url: str, input_iri: str
) -> tuple[str, dict[str, object]]:
    """Invoke the discovered HTTP/JSON operation and validate semantic continuity."""

    if contract["mediaType"] != "application/json":
        raise RuntimeError(
            f"Reference agent only supports application/json, discovered {contract['mediaType']}"
        )

    method = contract["method"].upper()
    if method != "POST":
        raise RuntimeError(f"Reference agent only supports POST, discovered {method}")

    endpoint = f"{service_base_url.rstrip('/')}/{contract['path'].lstrip('/')}"
    payload = {contract["requestField"]: input_iri}
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        method=method,
        headers={"Content-Type": contract["mediaType"], "Accept": contract["mediaType"]},
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

    capability_value = body.get(contract["capabilityField"])
    if capability_value != TARGET_CAPABILITY:
        raise RuntimeError(
            "Semantic continuity violation: service response capability does not match "
            f"the agent target ({capability_value!r})"
        )

    relation_value = body.get(contract["relationField"])
    if relation_value != contract["relation"]:
        raise RuntimeError(
            "Semantic continuity violation: service response relation does not match "
            f"the discovered contract ({relation_value!r})"
        )

    results = body.get(contract["resultField"])
    if not isinstance(results, list) or not all(isinstance(item, str) for item in results):
        raise RuntimeError("Knowledge Service result field is not a list of semantic IRIs")

    return endpoint, body


def _iri(value: str) -> str:
    if not value.startswith(("http://", "https://", "urn:")) or any(
        char in value for char in (">", "\n", "\r", " ")
    ):
        raise ValueError(f"Cannot serialize unsafe IRI in provenance: {value!r}")
    return f"<{value}>"


def write_provenance(
    path: Path,
    contract: dict[str, str],
    input_iri: str,
    architecture: Path,
) -> None:
    executed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    content = f"""@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix run: <urn:eska:example:pizza:agent-run:> .

run:knowledge-agent-invocation a prov:Activity ;
    dcterms:description "Pizza Knowledge Agent discovery and service invocation"@en ;
    dcterms:conformsTo {_iri(TARGET_CAPABILITY)} ;
    prov:wasAssociatedWith {_iri(AGENT_IRI)} ;
    prov:used {_iri(contract['service'])} ;
    prov:used {_iri(input_iri)} ;
    prov:endedAtTime "{executed_at}"^^xsd:dateTime ;
    prov:generated run:semantic-result .

run:semantic-result a prov:Entity ;
    dcterms:description "Semantic classifications returned through the discovered Knowledge Service"@en ;
    dcterms:relation {_iri(contract['relation'])} .

run:architecture-model a prov:Entity ;
    dcterms:identifier {json.dumps(str(architecture))} .
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="ESKA deterministic Pizza Knowledge Agent")
    parser.add_argument(
        "--robot-jar",
        type=Path,
        default=here / ".work" / "robot.jar",
        help="ROBOT jar used to execute the SPARQL discovery query",
    )
    parser.add_argument(
        "--architecture",
        type=Path,
        default=here / "results" / "architecture-model.owl",
        help="Merged machine-readable ESKA architecture model",
    )
    parser.add_argument(
        "--query",
        type=Path,
        default=here / "discover-service.sparql",
        help="SPARQL service discovery query",
    )
    parser.add_argument(
        "--service-base-url",
        default="http://127.0.0.1:8080",
        help="Runtime deployment binding. The semantic service path is discovered from ESKA.",
    )
    parser.add_argument("--input", required=True, help="OWL class IRI to classify")
    parser.add_argument("--output", type=Path, help="Optional JSON result file")
    parser.add_argument("--provenance", type=Path, help="Optional PROV-O execution record")
    args = parser.parse_args()

    contract = discover_operation(args.robot_jar, args.architecture, args.query)
    endpoint, response = invoke_service(contract, args.service_base_url, args.input)

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
        "invocation": {"endpoint": endpoint, "input": args.input},
        "semanticResult": {
            "relation": contract["relation"],
            "classifications": response[contract["resultField"]],
        },
    }

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if args.provenance:
        write_provenance(args.provenance, contract, args.input, args.architecture)


if __name__ == "__main__":
    main()
