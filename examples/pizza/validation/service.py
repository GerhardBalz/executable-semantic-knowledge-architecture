#!/usr/bin/env python3
"""Thin HTTP Knowledge Service for PizzaValidationCapability.

Pizza validation semantics remain in the source-owned SHACL profile. This service
parses an RDF graph supplied as expanded JSON-LD, executes pySHACL, and returns
the resulting SHACL ValidationReport as JSON-LD inside a small service envelope.
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from pyshacl import validate
from rdflib import Graph

SERVICE_IRI = "urn:eska:example:pizza:validation-service:PizzaValidationService"
CAPABILITY_IRI = "urn:eska:example:pizza:validation:PizzaValidationCapability"
OPERATION_IRI = "urn:eska:example:pizza:validation-service:ValidatePizzaDataOperation"
INPUT_TYPE = "urn:eska:example:pizza:validation:PizzaDataGraph"
OUTPUT_TYPE = "http://www.w3.org/ns/shacl#ValidationReport"
CONFORMS_RELATION = "http://www.w3.org/ns/shacl#conforms"


def contains_context(value: object) -> bool:
    if isinstance(value, dict):
        if "@context" in value:
            return True
        return any(contains_context(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_context(item) for item in value)
    return False


class ValidationKnowledge:
    """Execute the source-owned Pizza SHACL profile against supplied RDF data."""

    def __init__(self, shapes_path: Path) -> None:
        if not shapes_path.exists():
            raise FileNotFoundError(
                f"Pizza SHACL profile not found: {shapes_path}. Materialize Pizza artifacts first."
            )
        self.shapes_path = shapes_path
        self.shapes = Graph().parse(shapes_path, format="turtle")

    def validate_jsonld(self, document: object) -> object:
        if contains_context(document):
            raise ValueError("JSON-LD @context is not accepted by this reference service")

        data_graph = Graph()
        data_graph.parse(data=json.dumps(document), format="json-ld")
        if len(data_graph) == 0:
            raise ValueError("RDF input graph is empty")

        _, report_graph, _ = validate(
            data_graph=data_graph,
            shacl_graph=self.shapes,
            inference="none",
            abort_on_first=False,
        )
        if not isinstance(report_graph, Graph):
            raise RuntimeError(f"pySHACL did not produce an RDF ValidationReport graph: {report_graph}")

        return json.loads(report_graph.serialize(format="json-ld"))


class ValidationServiceHandler(BaseHTTPRequestHandler):
    knowledge: ValidationKnowledge

    def log_message(self, fmt: str, *args: object) -> None:
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(fmt, *args)

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlparse(self.path).path

        if path == "/health":
            self._send_json(200, {"status": "ok", "service": SERVICE_IRI})
            return

        if path == "/capabilities/pizza-validation":
            self._send_json(
                200,
                {
                    "service": SERVICE_IRI,
                    "capability": CAPABILITY_IRI,
                    "operation": OPERATION_IRI,
                    "method": "POST",
                    "path": "/validate",
                    "mediaType": "application/json",
                    "inputType": INPUT_TYPE,
                    "outputType": OUTPUT_TYPE,
                    "relation": CONFORMS_RELATION,
                },
            )
            return

        self._send_json(404, {"error": "not-found", "path": path})

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlparse(self.path).path
        if path != "/validate":
            self._send_json(404, {"error": "not-found", "path": path})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid-json"})
            return

        if not isinstance(payload, dict):
            self._send_json(400, {"error": "request-must-be-json-object"})
            return

        document = payload.get("data")
        if not isinstance(document, (dict, list)):
            self._send_json(400, {"error": "missing-jsonld-data"})
            return

        try:
            report = self.knowledge.validate_jsonld(document)
        except ValueError as exc:
            self._send_json(422, {"error": "invalid-rdf-input", "message": str(exc)})
            return
        except Exception as exc:
            self._send_json(500, {"error": "validation-failed", "message": str(exc)})
            return

        self._send_json(
            200,
            {
                "service": SERVICE_IRI,
                "capability": CAPABILITY_IRI,
                "operation": OPERATION_IRI,
                "relation": CONFORMS_RELATION,
                "report": report,
                "semanticArtifact": str(self.knowledge.shapes_path),
            },
        )


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="ESKA Pizza Validation Knowledge Service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8081, type=int)
    parser.add_argument(
        "--shapes",
        type=Path,
        default=here.parent / ".work" / "pizza-domain" / "shapes.ttl",
        help="Commit-pinned Pizza SHACL profile materialized from pizza-ontology",
    )
    args = parser.parse_args()

    ValidationServiceHandler.knowledge = ValidationKnowledge(args.shapes)
    server = ThreadingHTTPServer((args.host, args.port), ValidationServiceHandler)
    print(f"Pizza Validation Knowledge Service listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
