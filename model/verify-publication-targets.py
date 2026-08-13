#!/usr/bin/env python3
"""Verify ESKA current publication and active immutable core-0.2.0 routing."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from rdflib import Graph, URIRef
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parents[1]
W3ID_PAYLOAD = ROOT / "publication/w3id/eska/.htaccess"
RELEASE_TAG = "eska-v0.2.0"
RELEASE_COMMIT = "a6ce0b9e795d271dce8a2b7be93d44932e8448d4"
W3ID_PR = "https://github.com/perma-id/w3id.org/pull/6543"
W3ID_MERGE = "1230ac37c2100f752e2071606103b81f445d5d5c"
W3ID_VERIFY_RUN = "https://github.com/GerhardBalz/executable-semantic-knowledge-architecture/actions/runs/31694481671"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def contains(graph: Graph, namespace: str) -> bool:
    return any(
        isinstance(term, URIRef) and str(term).startswith(namespace)
        for triple in graph
        for term in triple
    )


def require_backend_url(url: str) -> None:
    parsed = urlparse(str(url))
    require(
        parsed.scheme == "https" and parsed.netloc in {"github.com", "raw.githubusercontent.com"},
        f"unexpected backend URL: {url}",
    )


def main() -> None:
    contract = json.loads((ROOT / "model/publication-contract.json").read_text(encoding="utf-8"))
    targets = json.loads((ROOT / "publication/backend-targets.json").read_text(encoding="utf-8"))
    term = contract["termNamespace"]

    require(term["activationStatus"] == "active", "namespace not active")
    require(contract["status"] == "core-0.2.0-w3id-active", "unexpected contract publication stage")
    require(targets["status"] == "w3id-active-versioned-core-0.2.0", "backend status mismatch")
    require(targets["releaseTag"] == RELEASE_TAG, "current published release tag mismatch")
    require(targets["releaseCommit"] == RELEASE_COMMIT, "release commit mismatch")
    require(targets["previousReleaseTag"] == "eska-v0.1.0", "previous release tag mismatch")

    evidence = contract["publicationEvidence"]
    require(evidence["core020RouteActive"] is True, "contract does not mark core 0.2.0 route active")
    require(evidence["core020RoutePullRequest"] == W3ID_PR, "contract W3ID PR mismatch")
    require(evidence["core020RouteMergeCommit"] == W3ID_MERGE, "contract W3ID merge mismatch")
    require(evidence["core020RouteVerificationRun"] == W3ID_VERIFY_RUN, "contract W3ID verification mismatch")
    require(targets["w3idCore020RoutesPullRequest"] == W3ID_PR, "backend W3ID PR mismatch")
    require(targets["w3idCore020RoutesMergeCommit"] == W3ID_MERGE, "backend W3ID merge mismatch")
    require(targets["w3idCore020VerificationRun"] == W3ID_VERIFY_RUN, "backend W3ID verification mismatch")

    authoritative = Graph()
    for module in contract["modules"]:
        authoritative.parse(ROOT / module["path"], format="turtle")
    distribution = Graph().parse(ROOT / "dist/eska.ttl", format="turtle")
    require(isomorphic(authoritative, distribution), "combined distribution differs from authoritative modules")
    require(contains(distribution, term["current"]), "combined distribution lacks active W3ID terms")
    require(not contains(distribution, term["predecessor"]), "combined distribution contains provisional term IRIs")
    require(contains(distribution, "https://w3id.org/smo#"), "combined distribution lacks SMO compatibility evidence")

    for url in [targets["humanDocumentation"], targets["namespaceDocumentation"], targets["combinedRdf"]]:
        require_backend_url(url)

    modules = {module["name"]: module for module in contract["modules"]}
    target_modules = targets["modules"]
    require(set(target_modules) == set(modules), "backend module inventory mismatch")

    core = target_modules["core"]
    core_contract = modules["core"]
    require(core["iri"] == core_contract["ontologyIri"], "core ontology IRI mismatch")
    require(core["version"] == core_contract["version"] == "0.2.0", "core current version mismatch")
    require(core["versionIri"] == "https://w3id.org/eska/model/core/0.2.0", "core version IRI mismatch")
    require(core["versionStatus"] == "active", "core route is not active")
    require(core["releaseTag"] == RELEASE_TAG, "core release tag mismatch")
    require(core["releaseCommit"] == RELEASE_COMMIT, "core release commit mismatch")
    require(core["versionBackendVerified"] is True, "core 0.2.0 tagged backend must be verified")
    require(core["versionRouteActive"] is True, "core 0.2.0 W3ID route must be active")
    require(core["versionRoutePullRequest"] == W3ID_PR, "core route PR evidence mismatch")
    require(core["versionRouteMergeCommit"] == W3ID_MERGE, "core route merge evidence mismatch")
    require(core["versionRouteVerificationRun"] == W3ID_VERIFY_RUN, "core route verification evidence mismatch")
    require("/eska-v0.2.0/" in core["versionRdf"], "core version RDF must target eska-v0.2.0")
    require("/eska-v0.2.0/" in core["versionHuman"], "core version HTML must target eska-v0.2.0")
    require(core["versionDistribution"] == "https://w3id.org/eska/dist/0.2.0/eska-core.ttl", "core distribution route mismatch")

    previous = core["previousPublishedVersion"]
    require(previous["version"] == "0.1.0", "previous core version mismatch")
    require(previous["versionRouteActive"] is True, "existing core 0.1.0 route must remain active")
    require("/eska-v0.1.0/" in previous["versionRdf"], "core 0.1.0 RDF backend moved")

    for name in ("capability", "service", "agent", "deployment"):
        module = modules[name]
        target = target_modules[name]
        require(target["iri"] == module["ontologyIri"], f"{name}: module IRI mismatch")
        require(target["version"] == module["version"], f"{name}: module version mismatch")
        require(target["versionIri"] == module["versionIri"], f"{name}: module version IRI mismatch")
        require(target["versionRouteActive"] is True, f"{name}: existing immutable route must stay active")
        require("/eska-v0.1.0/" in target["versionRdf"], f"{name}: version RDF no longer targets first release")

    payload = W3ID_PAYLOAD.read_text(encoding="utf-8")
    require("model/core/0\\.1\\.0" in payload, "governed W3ID payload lost core 0.1.0 immutable route")
    require("model/core/0\\.2\\.0" in payload, "governed W3ID payload lacks active core 0.2.0 route")
    require("dist/0\\.2\\.0/eska-core\\.ttl" in payload, "governed W3ID payload lacks active core 0.2.0 distribution route")
    require("eska-v0.2.0/model/eska-core.ttl" in payload, "core 0.2.0 routes do not target immutable release")

    for line in payload.splitlines():
        if "RewriteRule ^model/" in line and "/0\\." in line:
            require("/main/" not in line, f"immutable module route targets mutable main: {line}")
        if "RewriteRule ^dist/" in line and "eska-" in line:
            require("/main/" not in line, f"immutable distribution route targets mutable main: {line}")

    print("SUCCESS: ESKA v0.2.0 release and core 0.2.0 immutable W3ID routes are active and governed.")
    print(f"Combined distribution triples: {len(distribution)}")
    print(f"Published repository release:  {RELEASE_TAG} @ {RELEASE_COMMIT}")
    print("Published core 0.1.0 route:     active → eska-v0.1.0")
    print("Core 0.2.0 W3ID route:          active → eska-v0.2.0")


if __name__ == "__main__":
    main()
