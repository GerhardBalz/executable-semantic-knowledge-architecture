#!/usr/bin/env python3
"""Verify live current and immutable ESKA W3ID routes from external CI.

Current module routes must always be live. Immutable module-version routes are
verified only after publication metadata marks them active. A release-pending
version must remain unpublished while the previously published immutable route
continues to resolve from its governed release tag.
"""
from __future__ import annotations

import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "model" / "publication-contract.json"
TARGETS_PATH = ROOT / "publication" / "backend-targets.json"
W3ID_BASE = "https://w3id.org/eska"
USER_AGENT = "ESKA-W3ID-verifier/1.2"


class RecordingRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.chain: list[tuple[int, str]] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append((int(code), str(newurl)))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def normalize(url: str) -> str:
    return url.rstrip("/")


def fetch(
    route: str,
    accept: str,
    expected_final: str,
    *,
    expect_text: str | None = None,
) -> list[tuple[int, str]]:
    handler = RecordingRedirectHandler()
    opener = urllib.request.build_opener(handler)
    request = urllib.request.Request(
        route,
        headers={"Accept": accept, "User-Agent": USER_AGENT},
    )
    try:
        with opener.open(request, timeout=30) as response:
            final_url = str(response.geturl())
            status = int(response.status)
            content = (
                response.read(32768).decode("utf-8", errors="replace")
                if expect_text is not None
                else ""
            )
    except urllib.error.HTTPError as exc:
        raise AssertionError(
            f"{route} returned HTTP {exc.code}: {exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise AssertionError(
            f"{route} could not be resolved/fetched: {exc.reason}"
        ) from exc

    require(status == 200, f"{route}: final response was HTTP {status}, expected 200")
    require(
        normalize(final_url) == normalize(expected_final),
        f"{route}: resolved to {final_url}, expected {expected_final}",
    )
    require(handler.chain, f"{route}: W3ID route did not redirect")
    require(
        any(code == 303 for code, _ in handler.chain),
        f"{route}: redirect chain contains no HTTP 303: {handler.chain}",
    )
    if expect_text is not None:
        require(
            expect_text in content,
            f"{route}: resolved representation lacks expected marker {expect_text!r}",
        )
    return handler.chain


def require_unpublished(route: str, accept: str) -> list[tuple[int, str]]:
    """Require a staged immutable W3ID route to remain inactive.

    Internal W3ID canonicalization (for example a 301 adding a slash) is allowed,
    but an external 303 backend redirect is not. The terminal response must be a
    not-found/gone response rather than a successfully published representation.
    """
    handler = RecordingRedirectHandler()
    opener = urllib.request.build_opener(handler)
    request = urllib.request.Request(
        route,
        headers={"Accept": accept, "User-Agent": USER_AGENT},
    )
    try:
        with opener.open(request, timeout=30) as response:
            final_url = str(response.geturl())
            status = int(response.status)
    except urllib.error.HTTPError as exc:
        require(
            exc.code in {404, 410},
            f"{route}: unpublished route returned HTTP {exc.code}, expected 404/410",
        )
        require(
            not any(code == 303 for code, _ in handler.chain),
            f"{route}: release-pending route unexpectedly has a 303 backend redirect: {handler.chain}",
        )
        return handler.chain
    except urllib.error.URLError as exc:
        raise AssertionError(
            f"{route} could not be resolved while checking unpublished state: {exc.reason}"
        ) from exc

    raise AssertionError(
        f"{route}: release-pending immutable route unexpectedly resolved "
        f"with HTTP {status} to {final_url}; expected it to remain unpublished"
    )


def add_immutable_checks(
    checks: list[tuple[str, str, str, str | None]],
    *,
    version_iri: str,
    version_rdf: str,
    version_human: str,
    version_distribution: str,
) -> None:
    checks.extend(
        [
            (version_iri, "text/html", version_human, None),
            (version_iri, "text/turtle", version_rdf, version_iri),
            (version_distribution, "text/turtle", version_rdf, version_iri),
        ]
    )


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    targets = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
    term = contract["termNamespace"]

    require(term["current"] == "https://w3id.org/eska#", "unexpected permanent ESKA namespace")
    require(term["activationStatus"] == "active", "unexpected activation state")
    require(targets["releaseTag"] == "eska-v0.1.0", "unexpected published repository release tag")

    checks: list[tuple[str, str, str, str | None]] = [
        (W3ID_BASE, "text/html", targets["humanDocumentation"], None),
        (W3ID_BASE, "text/turtle", targets["combinedRdf"], term["current"]),
        (f"{W3ID_BASE}/docs", "text/html", targets["namespaceDocumentation"], None),
        (f"{W3ID_BASE}/dist/eska.ttl", "text/turtle", targets["combinedRdf"], term["current"]),
    ]
    unpublished_checks: list[tuple[str, str]] = []

    for module in contract["modules"]:
        name = str(module["name"])
        target = targets["modules"][name]

        require(
            target["version"] == str(module["version"]),
            f"{name}: backend current version differs from publication contract",
        )
        require(
            target["versionIri"] == str(module["versionIri"]),
            f"{name}: backend current version IRI differs from publication contract",
        )

        # Current module routes always represent governed main.
        checks.extend(
            [
                (f"{W3ID_BASE}/model/{name}", "text/html", target["human"], None),
                (
                    f"{W3ID_BASE}/model/{name}",
                    "text/turtle",
                    target["rdf"],
                    str(module["ontologyIri"]),
                ),
            ]
        )

        if target.get("versionRouteActive") is True:
            for key in ("versionRdf", "versionHuman", "versionDistribution"):
                require(key in target, f"{name}: active immutable route lacks {key}")
            add_immutable_checks(
                checks,
                version_iri=target["versionIri"],
                version_rdf=target["versionRdf"],
                version_human=target["versionHuman"],
                version_distribution=target["versionDistribution"],
            )
            continue

        # A current semantic version may exist on main before its immutable
        # repository release and W3ID route are published.
        require(
            target.get("versionStatus") == "release-pending",
            f"{name}: inactive immutable route is not explicitly release-pending",
        )
        require(
            target.get("plannedReleaseTag") == targets.get("nextReleaseTag"),
            f"{name}: planned release tag differs from repository nextReleaseTag",
        )
        require(
            target.get("plannedVersionDistribution")
            == f"https://w3id.org/eska/dist/{module['version']}/eska-{name}.ttl",
            f"{name}: planned immutable distribution route mismatch",
        )

        previous = target.get("previousPublishedVersion")
        require(previous is not None, f"{name}: release-pending version lacks previous published version evidence")
        require(
            previous.get("versionRouteActive") is True,
            f"{name}: previous published immutable version is not marked active",
        )
        add_immutable_checks(
            checks,
            version_iri=previous["versionIri"],
            version_rdf=previous["versionRdf"],
            version_human=previous["versionHuman"],
            version_distribution=previous["versionDistribution"],
        )

        unpublished_checks.extend(
            [
                (target["versionIri"], "text/html"),
                (target["versionIri"], "text/turtle"),
                (target["plannedVersionDistribution"], "text/turtle"),
            ]
        )

    print("Verifying live current and published immutable ESKA W3ID routes...")
    for route, accept, expected, marker in checks:
        chain = fetch(route, accept, expected, expect_text=marker)
        print(f"PASS {route} [{accept}] -> {expected}")
        print("     redirects: " + " -> ".join(f"{code} {url}" for code, url in chain))

    print("Verifying release-pending immutable routes remain unpublished...")
    for route, accept in unpublished_checks:
        chain = require_unpublished(route, accept)
        print(f"PASS unpublished {route} [{accept}]")
        if chain:
            print("     internal redirects: " + " -> ".join(f"{code} {url}" for code, url in chain))

    print("SUCCESS: current, published immutable, and release-pending W3ID states are publication-consistent.")
    print(f"Published route checks: {len(checks)}")
    print(f"Unpublished route checks: {len(unpublished_checks)}")
    print(f"Permanent namespace: {term['current']}")
    print(f"Published repository release: {targets['releaseTag']}")
    if targets.get("nextReleaseTag"):
        print(f"Next repository release: {targets['nextReleaseTag']} (pending)")


if __name__ == "__main__":
    main()
