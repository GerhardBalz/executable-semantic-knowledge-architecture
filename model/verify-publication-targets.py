#!/usr/bin/env python3
"""Verify ESKA current publication, immutable history, and staged core-0.2.0 routing."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from rdflib import Graph, URIRef
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parents[1]
W3ID_PAYLOAD = ROOT / "publication/w3id/eska/.htaccess"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def contains(graph: Graph, namespace: str) -> bool:
    return any(isinstance(term, URIRef) and str(term).startswith(namespace) for triple in graph for term in triple)


def require_backend_url(url: str) -> None:
    parsed = urlparse(str(url))
    require(parsed.scheme == "https" and parsed.netloc in {"github.com", "raw.githubusercontent.com"}, f"unexpected backend URL: {url}")


def main() -> None:
    contract = json.loads((ROOT / "model/publication-contract.json").read_text(encoding="utf-8"))
    targets = json.loads((ROOT / "publication/backend-targets.json").read_text(encoding="utf-8"))
    term = contract["termNamespace"]

    require(term["activationStatus"] == "active", "namespace not active")
    require(contract["status"] == "core-0.2.0-release-pending", "unexpected contract publication stage")
    require(targets["status"] == "w3id-active-versioned-core-0.2.0-release-pending", "backend status mismatch")
    require(targets["releaseTag"] == "eska-v0.1.0", "current published release tag mismatch")
    require(targets["nextReleaseTag"] == "eska-v0.2.0", "next governed release tag mismatch")
    require(targets["persistentVocabulary"] == "https://w3id.org/eska", "persistent vocabulary route mismatch")
    require(targets["w3idActivationPullRequest"] == "https://github.com/perma-id/w3id.org/pull/6530", "W3ID activation PR mismatch")
    require(targets["w3idVersionRoutesPullRequest"] == "https://github.com/perma-id/w3id.org/pull/6535", "W3ID version-routes PR mismatch")
    require(targets["w3idVersionRoutesMergeCommit"] == "bf72939d8d6a15d78f2be16a87eaca494e72882b", "W3ID version-routes merge commit mismatch")

    authoritative = Graph()
    for module in contract["modules"]:
        authoritative.parse(ROOT / module["path"], format="turtle")
    distribution = Graph().parse(ROOT / "dist/eska.ttl", format="turtle")
    require(isomorphic(authoritative, distribution), "combined distribution differs from authoritative modules")
    require(contains(distribution, term["current"]), "combined distribution lacks active W3ID terms")
    require(not contains(distribution, term["predecessor"]), "combined distribution contains provisional term IRIs")
    require(contains(distribution, "https://w3id.org/smo#"), "combined distribution lacks SMO SemanticModel compatibility evidence")

    for url in [targets["humanDocumentation"], targets["namespaceDocumentation"], targets["combinedRdf"]]:
        require_backend_url(url)

    modules = {module["name"]: module for module in contract["modules"]}
    target_modules = targets["modules"]
    require(set(target_modules) == set(modules), "backend module inventory mismatch")

    core = target_modules["core"]
    core_contract = modules["core"]
    require(core["iri"] == core_contract["ontologyIri"], "core ontology IRI mismatch")
    require(core["version"] == core_contract["version"] == "0.2.0", "core current version mismatch")
    require(core["versionIri"] == core_contract["versionIri"] == "https://w3id.org/eska/model/core/0.2.0", "core version IRI mismatch")
    require(core["versionStatus"] == "release-pending", "core 0.2.0 must remain release-pending")
    require(core["plannedReleaseTag"] == "eska-v0.2.0", "core planned release tag mismatch")
    require(core["versionRouteActive"] is False, "core 0.2.0 immutable route must not be active before release")
    require_backend_url(core["rdf"])
    require_backend_url(core["human"])
    require_backend_url(core["plannedVersionRdf"])
    require_backend_url(core["plannedVersionHuman"])
    require("/eska-v0.2.0/" in core["plannedVersionRdf"], "planned core RDF backend must target eska-v0.2.0")
    require("/eska-v0.2.0/" in core["plannedVersionHuman"], "planned core HTML backend must target eska-v0.2.0")
    require(core["plannedVersionDistribution"] == "https://w3id.org/eska/dist/0.2.0/eska-core.ttl", "planned core distribution route mismatch")

    previous = core["previousPublishedVersion"]
    require(previous["version"] == "0.1.0", "previous core version mismatch")
    require(previous["versionIri"] == "https://w3id.org/eska/model/core/0.1.0", "previous core version IRI mismatch")
    require(previous["versionRouteActive"] is True, "existing core 0.1.0 route must remain active")
    require("/eska-v0.1.0/" in previous["versionRdf"], "core 0.1.0 RDF backend moved")
    require("/eska-v0.1.0/" in previous["versionHuman"], "core 0.1.0 HTML backend moved")
    require(previous["versionDistribution"] == "https://w3id.org/eska/dist/0.1.0/eska-core.ttl", "core 0.1.0 distribution route changed")

    for name in ("capability", "service", "agent", "deployment"):
        module = modules[name]
        target = target_modules[name]
        require(target["iri"] == module["ontologyIri"], f"{name}: module IRI mismatch")
        require(target["version"] == module["version"], f"{name}: module version mismatch")
        require(target["versionIri"] == module["versionIri"], f"{name}: module version IRI mismatch")
        require(target["versionRouteActive"] is True, f"{name}: existing immutable route must stay active")
        require(target["versionDistribution"] == f"https://w3id.org/eska/dist/{module['version']}/eska-{name}.ttl", f"{name}: immutable distribution route mismatch")
        for key in ("rdf", "human", "versionRdf", "versionHuman"):
            require_backend_url(target[key])
        require("/eska-v0.1.0/" in target["versionRdf"], f"{name}: version RDF no longer targets immutable first release")
        require("/eska-v0.1.0/" in target["versionHuman"], f"{name}: version HTML no longer targets immutable first release")

    payload = W3ID_PAYLOAD.read_text(encoding="utf-8")
    require("model/core/0\\.1\\.0" in payload, "governed W3ID payload lost core 0.1.0 immutable route")
    require("model/core/0\\.2\\.0" not in payload, "core 0.2.0 W3ID route activated before immutable release")
    require("dist/0\\.2\\.0/eska-core\\.ttl" not in payload, "core 0.2.0 distribution route activated before immutable release")
    require("eska-v0.2.0/model/eska-core.ttl" not in payload, "W3ID payload must not target a not-yet-published release")

    for line in payload.splitlines():
        if "RewriteRule ^model/" in line and "/0\\." in line:
            require("/main/" not in line, f"immutable module route targets mutable main: {line}")
        if "RewriteRule ^dist/" in line and "eska-" in line:
            require("/main/" not in line, f"immutable distribution route targets mutable main: {line}")

    print("SUCCESS: ESKA current publication and staged core 0.2.0 immutable boundary are consistent.")
    print(f"Combined distribution triples: {len(distribution)}")
    print("Current core module:            0.2.0")
    print("Published core immutable route: 0.1.0 → eska-v0.1.0")
    print("Core 0.2.0 immutable route:     pending eska-v0.2.0")


if __name__ == "__main__":
    main()
