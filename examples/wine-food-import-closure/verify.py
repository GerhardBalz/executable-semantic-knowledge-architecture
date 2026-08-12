#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS

ROOT = Path(__file__).resolve().parent
WINE_FILE = ROOT / "fixtures" / "wine.ttl"
WINE_ONTOLOGY = URIRef("http://www.w3.org/TR/2004/REC-owl-guide-20040210/wine")
FOOD_ONTOLOGY = URIRef("http://www.w3.org/TR/2004/REC-owl-guide-20040210/food")
WINE_CLASS = URIRef("http://www.w3.org/TR/2004/REC-owl-guide-20040210/wine#Wine")
POTABLE_LIQUID = URIRef("http://www.w3.org/TR/2004/REC-owl-guide-20040210/food#PotableLiquid")
CONSUMABLE_THING = URIRef("http://www.w3.org/TR/2004/REC-owl-guide-20040210/food#ConsumableThing")
EXPECTED = {
    "subject": str(WINE_CLASS),
    "predicate": str(RDFS.subClassOf),
    "object": str(CONSUMABLE_THING),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse(path: Path) -> Graph:
    graph = Graph()
    graph.parse(path, format="turtle")
    return graph


def subclass_reachable(graph: Graph, child: URIRef, parent: URIRef) -> bool:
    frontier = [child]
    visited: set[URIRef] = set()
    while frontier:
        current = frontier.pop()
        if current in visited:
            continue
        visited.add(current)
        for candidate in graph.objects(current, RDFS.subClassOf):
            if not isinstance(candidate, URIRef):
                continue
            if candidate == parent:
                return True
            frontier.append(candidate)
    return False


def load_import_closure(mapping_path: Path) -> tuple[Graph, list[dict[str, str]]]:
    graph = parse(WINE_FILE)
    require((WINE_ONTOLOGY, RDF.type, OWL.Ontology) in graph, "Wine test slice does not declare the expected ontology identity")
    imports = sorted({obj for obj in graph.objects(WINE_ONTOLOGY, OWL.imports) if isinstance(obj, URIRef)}, key=str)
    require(imports == [FOOD_ONTOLOGY], f"unexpected Wine import set: {[str(value) for value in imports]}")

    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    import_map = mapping.get("imports", {})
    evidence: list[dict[str, str]] = []

    for imported_iri in imports:
        target = import_map.get(str(imported_iri))
        if target is None:
            raise ValueError(f"no physical mapping for import {imported_iri}")
        physical_path = (mapping_path.parent / target).resolve()
        require(physical_path.is_file(), f"mapped import file missing: {physical_path}")
        imported_graph = parse(physical_path)
        require(
            (imported_iri, RDF.type, OWL.Ontology) in imported_graph,
            f"mapped backend {physical_path} does not declare imported ontology identity {imported_iri}",
        )
        for triple in imported_graph:
            graph.add(triple)
        evidence.append({"semanticIdentity": str(imported_iri), "physicalPath": str(physical_path.relative_to(ROOT))})

    return graph, evidence


def normalized_result(graph: Graph) -> dict[str, str]:
    require(
        subclass_reachable(graph, WINE_CLASS, CONSUMABLE_THING),
        "expected Wine→ConsumableThing entailment is absent",
    )
    return EXPECTED.copy()


def main() -> None:
    wine_only = parse(WINE_FILE)
    require((WINE_CLASS, RDFS.subClassOf, POTABLE_LIQUID) in wine_only, "Wine test slice lost the cross-ontology subclass edge")
    require(
        not subclass_reachable(wine_only, WINE_CLASS, CONSUMABLE_THING),
        "negative control unexpectedly entailed Wine→ConsumableThing without Food import closure",
    )

    try:
        load_import_closure(ROOT / "mappings" / "no-food.json")
    except ValueError as exc:
        require("no physical mapping" in str(exc), f"unexpected missing-mapping failure: {exc}")
        missing_mapping = "failed-as-expected"
    else:
        raise AssertionError("missing import mapping control unexpectedly succeeded")

    try:
        load_import_closure(ROOT / "mappings" / "wrong-identity.json")
    except AssertionError as exc:
        require("does not declare imported ontology identity" in str(exc), f"unexpected identity failure: {exc}")
        wrong_identity = "failed-as-expected"
    else:
        raise AssertionError("wrong-identity backend unexpectedly succeeded")

    results: dict[str, dict[str, str]] = {}
    physical: dict[str, list[dict[str, str]]] = {}
    for name in ("backend-a", "backend-b"):
        graph, evidence = load_import_closure(ROOT / "mappings" / f"{name}.json")
        results[name] = normalized_result(graph)
        physical[name] = evidence

    require(results["backend-a"] == results["backend-b"] == EXPECTED, "physical backend changed normalized semantic result")
    require(
        physical["backend-a"][0]["physicalPath"] != physical["backend-b"][0]["physicalPath"],
        "backend equivalence test did not use distinct physical paths",
    )

    print(json.dumps({
        "wineAlone": "expected-entailment-absent",
        "missingMapping": missing_mapping,
        "wrongIdentityBackend": wrong_identity,
        "backendA": {"result": results["backend-a"], "imports": physical["backend-a"]},
        "backendB": {"result": results["backend-b"], "imports": physical["backend-b"]},
        "backendInvariant": True,
    }, indent=2, sort_keys=True))
    print("PASS: Wine/Food import identity is stable across replaceable physical backends")


if __name__ == "__main__":
    main()
