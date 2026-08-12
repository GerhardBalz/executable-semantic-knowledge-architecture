#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import RDF

ROOT = Path(__file__).resolve().parent
UB = "http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#"
RESEARCH_GROUP = URIRef(UB + "ResearchGroup")
SUB_ORGANIZATION_OF = URIRef(UB + "subOrganizationOf")
UNIVERSITY_0 = URIRef("http://www.University0.edu")
EXPECTED_QUERY_SHA256 = "8c1e6567896f19fbf5a179994ebd09285cd74aacaa3829e60b7d0193be3ff54c"
EXPECTED_GENERATOR_COMMIT = "48686cd616f564c8fc360dc5abbcc294678655c4"
EXPECTED_ANSWERS = 224


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_graph(directory: Path, rdf_format: str) -> tuple[Graph, list[str]]:
    require(directory.is_dir(), f"generated-data directory missing: {directory}")
    files = sorted(path for path in directory.rglob("*") if path.is_file())
    require(files, f"no generated RDF files found under {directory}")

    graph = Graph()
    parsed: list[str] = []
    for path in files:
        graph.parse(path, format=rdf_format)
        parsed.append(str(path.relative_to(directory)))

    require(len(graph) > 0, f"generated graph is empty: {directory}")
    require(any(graph.triples((None, RDF.type, RESEARCH_GROUP))), "LUBM ResearchGroup instances missing")
    require(any(graph.triples((None, SUB_ORGANIZATION_OF, None))), "LUBM subOrganizationOf assertions missing")
    return graph, parsed


def query_answers(graph: Graph, query_text: str) -> set[str]:
    return {str(row[0]) for row in graph.query(query_text)}


def materialize_transitive_suborganization(graph: Graph) -> int:
    parents: dict[URIRef, set[URIRef]] = {}
    for subject, obj in graph.subject_objects(SUB_ORGANIZATION_OF):
        if isinstance(subject, URIRef) and isinstance(obj, URIRef):
            parents.setdefault(subject, set()).add(obj)

    additions: set[tuple[URIRef, URIRef, URIRef]] = set()
    for subject in parents:
        seen: set[URIRef] = set()
        stack = list(parents.get(subject, ()))
        while stack:
            obj = stack.pop()
            if obj in seen:
                continue
            seen.add(obj)
            stack.extend(parents.get(obj, ()))
        for obj in seen:
            triple = (subject, SUB_ORGANIZATION_OF, obj)
            if triple not in graph:
                additions.add(triple)

    for triple in additions:
        graph.add(triple)
    return len(additions)


def verify_backend(label: str, directory: Path, rdf_format: str, query_text: str) -> dict[str, object]:
    graph, parsed_files = load_graph(directory, rdf_format)
    original_triples = len(graph)

    direct_answers = query_answers(graph, query_text)
    require(
        len(direct_answers) != EXPECTED_ANSWERS,
        f"{label}: negative control unexpectedly satisfies the 224-answer oracle without transitive materialization",
    )

    added = materialize_transitive_suborganization(graph)
    answers = query_answers(graph, query_text)
    require(len(answers) == EXPECTED_ANSWERS, f"{label}: expected 224 Query 11 answers, found {len(answers)}")

    return {
        "label": label,
        "format": rdf_format,
        "files": parsed_files,
        "originalTripleCount": original_triples,
        "transitiveTriplesAdded": added,
        "directAnswerCount": len(direct_answers),
        "materializedAnswerCount": len(answers),
        "answers": sorted(answers),
    }


def verify_contract() -> tuple[dict[str, object], str]:
    contract = json.loads((ROOT / "benchmark-contract.json").read_text(encoding="utf-8"))
    expected = json.loads((ROOT / "expected-result.json").read_text(encoding="utf-8"))
    query_bytes = (ROOT / contract["query"]["file"]).read_bytes()
    query_text = query_bytes.decode("utf-8")

    require(contract["benchmark"] == "LUBM(1,0)", "benchmark identity changed")
    require(contract["query"]["id"] == 11, "query id changed")
    require(contract["query"]["expectedAnswerCount"] == EXPECTED_ANSWERS, "external answer oracle changed")
    require(expected["expectedAnswerCount"] == EXPECTED_ANSWERS, "expected-result oracle changed")
    require(contract["implementationBackend"]["commit"] == EXPECTED_GENERATOR_COMMIT, "generator commit is not pinned")
    require(contract["implementationBackend"]["authority"] is False, "implementation backend must not be semantic authority")
    require(contract["datasetGeneration"] == {
        "universities": 1,
        "startingIndex": 0,
        "seed": 0,
        "threads": 1,
        "ontology": "http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl",
    }, "LUBM(1,0) generation contract changed")
    require(contract["serializations"] == ["NTRIPLES", "TURTLE"], "serialization contract changed")

    actual_hash = hashlib.sha256(query_bytes).hexdigest()
    require(actual_hash == EXPECTED_QUERY_SHA256, f"Query 11 text changed: {actual_hash}")
    require(contract["query"]["sha256"] == EXPECTED_QUERY_SHA256, "query hash contract changed")
    return contract, query_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ntriples", type=Path, required=True)
    parser.add_argument("--turtle", type=Path, required=True)
    args = parser.parse_args()

    contract, query_text = verify_contract()
    ntriples = verify_backend("NTRIPLES", args.ntriples, "nt", query_text)
    turtle = verify_backend("TURTLE", args.turtle, "turtle", query_text)

    nt_answers = set(ntriples.pop("answers"))
    ttl_answers = set(turtle.pop("answers"))
    require(nt_answers == ttl_answers, "normalized Query 11 answer sets differ across serializations")
    require(len(nt_answers) == EXPECTED_ANSWERS, "normalized answer set no longer matches Lehigh oracle")

    evidence = {
        "benchmark": contract["benchmark"],
        "query": contract["query"]["id"],
        "externalOracle": EXPECTED_ANSWERS,
        "generatorBackend": contract["implementationBackend"],
        "ntriples": ntriples,
        "turtle": turtle,
        "serializationInvariant": True,
        "normalizedAnswerCount": len(nt_answers),
    }
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("PASS: LUBM Query 11 matches Lehigh's 224-answer oracle across N-Triples and Turtle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
