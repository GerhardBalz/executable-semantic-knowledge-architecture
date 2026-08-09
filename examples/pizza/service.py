#!/usr/bin/env python3
"""Minimal HTTP Knowledge Service for the ESKA Pizza classification capability.

The service is deliberately thin. It does not implement Pizza classification logic.
It reads superclass relationships from the reasoned OWL artifact produced by run.sh
and exposes those semantic results through HTTP.
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

SERVICE_IRI = "urn:eska:example:pizza:service:PizzaClassificationService"
CAPABILITY_IRI = "urn:eska:example:pizza:capability:PizzaClassificationCapability"
OPERATION_IRI = "urn:eska:example:pizza:service:ClassifyPizzaClassOperation"
PIZZA_NAMESPACE = "http://www.co-ode.org/ontologies/pizza/pizza.owl#"
SUBCLASS_RELATION = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
OWL_CLASS = "http://www.w3.org/2002/07/owl#Class"

RDF_ABOUT = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
RDF_RESOURCE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
RDFS_SUBCLASS = "{http://www.w3.org/2000/01/rdf-schema#}subClassOf"


class ReasonedKnowledge:
    """Read class-level semantic results from a reasoned RDF/XML ontology."""

    def __init__(self, ontology_path: Path) -> None:
        self.ontology_path = ontology_path
        self._superclasses = self._load_superclasses(ontology_path)

    @staticmethod
    def _load_superclasses(ontology_path: Path) -> dict[str, set[str]]:
        if not ontology_path.exists():
            raise FileNotFoundError(
                f"Reasoned ontology not found: {ontology_path}. Run examples/pizza/run.sh first."
            )

        root = ET.parse(ontology_path).getroot()
        superclasses: dict[str, set[str]] = {}

        for element in root.iter():
            subject = element.attrib.get(RDF_ABOUT)
            if not subject:
                continue
            for child in element:
                if child.tag != RDFS_SUBCLASS:
                    continue
                superclass = child.attrib.get(RDF_RESOURCE)
                if superclass:
                    superclasses.setdefault(subject, set()).add(superclass)

        return superclasses

    def classifications(self, class_iri: str) -> list[str]:
        return sorted(self._superclasses.get(class_iri, set()))


class KnowledgeServiceHandler(BaseHTTPRequestHandler):
    knowledge: ReasonedKnowledge

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep the reference example quiet unless an error is returned.
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

        if path == "/capabilities/pizza-classification":
            self._send_json(
                200,
                {
                    "service": SERVICE_IRI,
                    "capability": CAPABILITY_IRI,
                    "operation": OPERATION_IRI,
                    "method": "POST",
                    "path": "/classify",
                    "mediaType": "application/json",
                    "inputType": OWL_CLASS,
                    "outputType": OWL_CLASS,
                    "relation": SUBCLASS_RELATION,
                },
            )
            return

        self._send_json(404, {"error": "not-found", "path": path})

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlparse(self.path).path
        if path != "/classify":
            self._send_json(404, {"error": "not-found", "path": path})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid-json"})
            return

        class_iri = payload.get("class")
        if not isinstance(class_iri, str) or not class_iri:
            self._send_json(400, {"error": "missing-class-iri"})
            return

        if not class_iri.startswith(PIZZA_NAMESPACE):
            self._send_json(
                422,
                {
                    "error": "outside-capability-scope",
                    "message": "This reference service is bounded to Pizza ontology classes.",
                    "class": class_iri,
                    "capability": CAPABILITY_IRI,
                },
            )
            return

        classifications = self.knowledge.classifications(class_iri)
        if not classifications:
            self._send_json(
                404,
                {
                    "error": "class-not-found-or-unclassified",
                    "class": class_iri,
                    "capability": CAPABILITY_IRI,
                },
            )
            return

        self._send_json(
            200,
            {
                "service": SERVICE_IRI,
                "capability": CAPABILITY_IRI,
                "operation": OPERATION_IRI,
                "input": class_iri,
                "relation": SUBCLASS_RELATION,
                "classifications": classifications,
                "semanticArtifact": str(self.knowledge.ontology_path),
            },
        )


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="ESKA Pizza Classification Knowledge Service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument(
        "--reasoned",
        type=Path,
        default=here / "results" / "reasoned.owl",
        help="Reasoned RDF/XML ontology produced by examples/pizza/run.sh",
    )
    args = parser.parse_args()

    KnowledgeServiceHandler.knowledge = ReasonedKnowledge(args.reasoned)
    server = ThreadingHTTPServer((args.host, args.port), KnowledgeServiceHandler)
    print(f"Pizza Classification Knowledge Service listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
