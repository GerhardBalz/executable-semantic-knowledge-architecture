#!/usr/bin/env python3
"""Verify stable Travel ontology identity across replaceable physical backends."""
from __future__ import annotations

import json
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF

ROOT = Path(__file__).resolve().parent
TRAVEL_ID = "http://www.owl-ontologies.com/travel.owl"
EXPECTED_CLASSES = [
    "http://www.owl-ontologies.com/travel.owl#Activity",
    "http://www.owl-ontologies.com/travel.owl#Destination",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(identity: str, catalog_path: Path) -> dict:
    catalog = read_json(catalog_path)
    entry = catalog.get("mappings", {}).get(identity)
    require(entry is not None, f"no physical mapping for semantic identity: {identity}")
    require(isinstance(entry.get("path"), str), "catalog mapping path missing")
    require(entry.get("format") in {"turtle", "xml"}, "unsupported catalog format")
    return entry


def observe(identity: str, catalog_path: Path) -> dict:
    entry = resolve(identity, catalog_path)
    physical_path = ROOT / entry["path"]
    require(physical_path.is_file(), f"mapped physical artifact missing: {entry['path']}")

    graph = Graph()
    graph.parse(physical_path, format=entry["format"])

    requested = URIRef(identity)
    declared = sorted(str(subject) for subject in graph.subjects(RDF.type, OWL.Ontology))
    require(str(requested) in declared, f"declared ontology identity mismatch: requested {identity}, found {declared}")

    selected_classes = sorted(
        str(subject)
        for subject in graph.subjects(RDF.type, OWL.Class)
        if str(subject) in EXPECTED_CLASSES
    )
    require(selected_classes == EXPECTED_CLASSES, f"selected Travel class evidence mismatch: {selected_classes}")

    return {
        "physical": {
            "path": entry["path"],
            "format": entry["format"],
        },
        "result": {
            "semanticIdentity": identity,
            "selectedClasses": selected_classes,
        },
    }


def expect_failure(fn, expected_text: str) -> str:
    try:
        fn()
    except AssertionError as exc:
        require(expected_text in str(exc), f"unexpected failure: {exc}")
        return "failed-as-expected"
    raise AssertionError("negative control unexpectedly passed")


def main() -> None:
    expected = read_json(ROOT / "expected-result.json")

    backend_a = observe(TRAVEL_ID, ROOT / "catalog-a.json")
    backend_b = observe(TRAVEL_ID, ROOT / "catalog-b.json")

    require(backend_a["result"] == expected, "backend A normalized result differs from expected result")
    require(backend_b["result"] == expected, "backend B normalized result differs from expected result")
    require(backend_a["result"] == backend_b["result"], "semantic result changed across physical backends")
    require(backend_a["physical"] != backend_b["physical"], "test requires materially different physical backends")

    unmapped = expect_failure(
        lambda: observe("https://example.invalid/unmapped-travel", ROOT / "catalog-a.json"),
        "no physical mapping",
    )
    wrong_identity = expect_failure(
        lambda: observe(TRAVEL_ID, ROOT / "catalog-wrong.json"),
        "declared ontology identity mismatch",
    )

    evidence = {
        "backendA": backend_a,
        "backendB": backend_b,
        "backendInvariant": True,
        "unmappedIdentity": unmapped,
        "wrongIdentityBackend": wrong_identity,
    }
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("PASS: Travel semantic identity is invariant across replaceable physical backends")


if __name__ == "__main__":
    main()
