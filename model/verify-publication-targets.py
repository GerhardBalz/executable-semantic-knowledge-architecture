#!/usr/bin/env python3
"""Verify ESKA publication targets while the W3ID resolver is live and source IRIs remain provisional."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from rdflib import Graph, URIRef
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
CONTRACT_PATH = MODEL / "publication-contract.json"
TARGETS_PATH = ROOT / "publication" / "backend-targets.json"
DIST_PATH = ROOT / "dist" / "eska.ttl"
W3ID_PATH = ROOT / "publication" / "w3id" / "eska" / ".htaccess"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def graph_contains_namespace(graph: Graph, namespace: str) -> bool:
    for triple in graph:
        for term in triple:
            if isinstance(term, URIRef) and str(term).startswith(namespace):
                return True
    return False


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    targets = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))

    require(
        contract["termNamespace"]["activationStatus"] == "resolver-active-source-provisional",
        "publication contract must record a live resolver while source IRIs remain provisional",
    )
    current_ns = str(contract["termNamespace"]["current"])
    target_ns = str(contract["termNamespace"]["target"])

    modules = contract["modules"]
    require(isinstance(modules, list) and len(modules) == 5, "expected five ESKA modules")

    authoritative = Graph()
    module_names: list[str] = []
    for module in modules:
        name = str(module["name"])
        module_names.append(name)
        path = ROOT / str(module["path"])
        require(path.is_file(), f"missing authoritative module: {path}")
        authoritative.parse(path, format="turtle")

    distribution = Graph().parse(DIST_PATH, format="turtle")
    require(
        isomorphic(authoritative, distribution),
        "dist/eska.ttl is not graph-equivalent to the union of authoritative model modules",
    )
    require(
        graph_contains_namespace(distribution, current_ns),
        "resolver-active distribution no longer contains the authoritative provisional namespace before migration",
    )
    require(
        not graph_contains_namespace(distribution, target_ns),
        "permanent W3ID semantic terms leaked into the distribution before atomic migration",
    )

    require(
        targets.get("status") == "w3id-resolver-active-source-provisional",
        "backend target status does not reflect the verified live resolver",
    )
    require(targets.get("repository") == contract.get("repository"), "backend repository differs from publication contract")
    require(targets.get("branch") == "main", "publication backend must track the governed main branch")

    target_modules = targets.get("modules")
    require(isinstance(target_modules, dict), "backend module targets must be an object")
    require(set(target_modules) == set(module_names), "backend module targets differ from publication modules")

    allowed_hosts = {"github.com", "raw.githubusercontent.com"}
    urls = [targets["humanDocumentation"], targets["namespaceDocumentation"], targets["combinedRdf"]]
    for module in target_modules.values():
        urls.extend([module["rdf"], module["human"]])
    for url in urls:
        parsed = urlparse(str(url))
        require(parsed.scheme == "https", f"publication backend must use HTTPS: {url}")
        require(parsed.netloc in allowed_hosts, f"unexpected publication backend host: {url}")

    require(
        targets["combinedRdf"].endswith("/main/dist/eska.ttl"),
        "combined RDF backend does not target the generated distribution",
    )
    for module in modules:
        name = str(module["name"])
        source_path = str(module["path"])
        require(
            target_modules[name]["rdf"].endswith(f"/main/{source_path}"),
            f"{name}: RDF backend does not target the authoritative module path",
        )

    htaccess = W3ID_PATH.read_text(encoding="utf-8")
    require("Point of contact: Gerhard Balz" in htaccess, "W3ID routing payload lacks contact information")
    require("RewriteEngine On" in htaccess or "RewriteEngine on" in htaccess, "W3ID routing payload lacks RewriteEngine")
    for expected in (
        "dist/eska\\.ttl",
        "model/core",
        "model/capability",
        "model/service",
        "model/agent",
        "model/deployment",
        "raw.githubusercontent.com/GerhardBalz/executable-semantic-knowledge-architecture/main/dist/eska.ttl",
    ):
        require(expected in htaccess, f"W3ID routing payload is missing contract: {expected}")

    # Versioned W3ID routes remain absent until immutable release targets exist.
    for module in modules:
        version = str(module["firstPublishedVersion"])
        forbidden = f"model/{module['name']}/{version}"
        require(forbidden not in htaccess, f"premature versioned W3ID route configured: {forbidden}")

    print("SUCCESS: W3ID publication routes are active while ESKA semantic source identity remains deliberately provisional.")
    print(f"Combined distribution triples: {len(distribution)}")
    print(f"Authoritative modules:          {len(modules)}")
    print(f"Current term namespace:         {current_ns}")
    print(f"Target term namespace:          {target_ns} (resolver active; source provisional)")
    print("W3ID routing source:            publication/w3id/eska/")


if __name__ == "__main__":
    main()
