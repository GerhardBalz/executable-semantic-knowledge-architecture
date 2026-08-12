#!/usr/bin/env python3
"""Verify that one semantic lookup operation survives an OAK backend change."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from oaklib import get_adapter

BASE = Path(__file__).resolve().parent
PREFIX = "ESKAOAK"
NAMESPACE = "https://w3id.org/eska/example/oak-backend-independence#"
TERM = f"{PREFIX}:Child"
EXPECTED = {
    "entity": f"{NAMESPACE}Child",
    "label": "Child concept",
    "parents": [f"{NAMESPACE}Root"],
}
SELECTORS = {
    # For local RDF, omit an explicit scheme. OAK v0.7.4 dispatches the
    # .ttl suffix to its local SPARQL/RDF implementation; `sparql:` itself
    # denotes a SPARQL endpoint and therefore must not prefix a local path.
    "rdf-local": str(BASE / "fixture.ttl"),
    "obo-pronto": f"pronto:{BASE / 'fixture.obo'}",
}


def as_uri(adapter: Any, identifier: str) -> str:
    """Normalize an OAK node identifier to an absolute IRI when possible."""
    if identifier.startswith(("http://", "https://", "urn:")):
        return identifier
    uri = adapter.curie_to_uri(identifier)
    return uri or identifier


def execute(selector: str) -> tuple[dict[str, Any], str]:
    """Execute only interface-level OAK operations for one configured adapter."""
    adapter = get_adapter(selector)
    adapter.prefix_map()[PREFIX] = NAMESPACE

    result = {
        "entity": as_uri(adapter, TERM),
        "label": adapter.label(TERM),
        "parents": sorted(
            as_uri(adapter, parent)
            for parent in adapter.hierarchical_parents(TERM)
        ),
    }
    return result, type(adapter).__name__


def main() -> None:
    evidence: dict[str, dict[str, Any]] = {}
    adapter_classes: set[str] = set()

    for name, selector in SELECTORS.items():
        result, adapter_class = execute(selector)
        evidence[name] = {
            "selector": selector,
            "adapter_class": adapter_class,
            "result": result,
        }
        adapter_classes.add(adapter_class)

        if result != EXPECTED:
            raise SystemExit(
                f"{name} produced a different semantic result:\n"
                f"expected={json.dumps(EXPECTED, sort_keys=True)}\n"
                f"actual={json.dumps(result, sort_keys=True)}"
            )

    normalized_results = {
        json.dumps(entry["result"], sort_keys=True)
        for entry in evidence.values()
    }
    if len(normalized_results) != 1:
        raise SystemExit("OAK adapters disagree after semantic-result normalization")

    if len(adapter_classes) != len(SELECTORS):
        raise SystemExit(
            "The proving ground did not exercise materially different OAK adapter classes"
        )

    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("PASS: semantic lookup result is invariant across OAK adapter backends")


if __name__ == "__main__":
    main()
