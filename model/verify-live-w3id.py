#!/usr/bin/env python3
"""Verify the live W3ID resolver from an external-network CI runner."""

from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "model" / "publication-contract.json"
TARGETS_PATH = ROOT / "publication" / "backend-targets.json"

W3ID_BASE = "https://w3id.org/eska"
USER_AGENT = "ESKA-W3ID-verifier/1.0"


class RecordingRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.chain: list[tuple[int, str]] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        self.chain.append((int(code), str(newurl)))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def normalize(url: str) -> str:
    return url.rstrip("/")


def fetch(route: str, accept: str, expected_final: str, *, expect_text: str | None = None) -> list[tuple[int, str]]:
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
            content = response.read(16384).decode("utf-8", errors="replace") if expect_text is not None else ""
    except urllib.error.HTTPError as exc:
        raise AssertionError(f"{route} returned HTTP {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise AssertionError(f"{route} could not be resolved/fetched: {exc.reason}") from exc

    require(status == 200, f"{route}: final response was HTTP {status}, expected 200")
    require(normalize(final_url) == normalize(expected_final), f"{route}: resolved to {final_url}, expected {expected_final}")
    require(handler.chain, f"{route}: W3ID route did not redirect")
    require(any(code == 303 for code, _ in handler.chain), f"{route}: redirect chain contains no HTTP 303: {handler.chain}")
    if expect_text is not None:
        require(expect_text in content, f"{route}: resolved representation lacks expected marker {expect_text!r}")
    return handler.chain


def running_against_main() -> bool:
    """Return true only when Actions is validating the repository main branch.

    Feature-branch pushes are not pull_request events, so GITHUB_EVENT_NAME alone
    cannot distinguish them from post-merge main. GITHUB_HEAD_REF covers PR runs;
    GITHUB_REF_NAME covers ordinary branch pushes.
    """
    head_ref = os.environ.get("GITHUB_HEAD_REF", "").strip()
    ref_name = os.environ.get("GITHUB_REF_NAME", "").strip()
    if head_ref:
        return False
    if ref_name:
        return ref_name == "main"
    return os.environ.get("GITHUB_EVENT_NAME") == "push" and os.environ.get("GITHUB_REF") == "refs/heads/main"


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    targets = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))

    term = contract["termNamespace"]
    require(term["current"] == "https://w3id.org/eska#", "unexpected permanent ESKA namespace")
    require(term["predecessor"] == "urn:eska:core:", "unexpected predecessor ESKA namespace")
    require(term["activationStatus"] == "active", "live resolver verifier is running in an unexpected activation state")

    # W3ID intentionally redirects to the governed main branch. Any feature/PR
    # validation must therefore inspect the representation currently on main.
    # Only a run executing on main itself may require the permanent post-migration
    # representation.
    main_run = running_against_main()
    live_term_marker = term["current"] if main_run else term["predecessor"]

    checks: list[tuple[str, str, str, str | None]] = [
        (W3ID_BASE, "text/html", targets["humanDocumentation"], None),
        (W3ID_BASE, "text/turtle", targets["combinedRdf"], live_term_marker),
        (f"{W3ID_BASE}/docs", "text/html", targets["namespaceDocumentation"], None),
        (f"{W3ID_BASE}/dist/eska.ttl", "text/turtle", targets["combinedRdf"], live_term_marker),
    ]

    for module in contract["modules"]:
        name = str(module["name"])
        target = targets["modules"][name]
        live_module_marker = str(module["ontologyIri"] if main_run else module["predecessorOntologyIri"])
        checks.append((f"{W3ID_BASE}/model/{name}", "text/html", target["human"], None))
        checks.append((f"{W3ID_BASE}/model/{name}", "text/turtle", target["rdf"], live_module_marker))

    mode = "post-merge main" if main_run else "feature/PR validation against current main backend"
    print(f"Verifying live W3ID routes from the GitHub-hosted runner ({mode})...")
    for route, accept, expected_final, marker in checks:
        chain = fetch(route, accept, expected_final, expect_text=marker)
        rendered = " -> ".join(f"{code} {url}" for code, url in chain)
        print(f"PASS {route} [{accept}] -> {expected_final}")
        print(f"     redirects: {rendered}")

    print("SUCCESS: live W3ID resolver routes are externally reachable and match the expected publication phase.")
    print(f"Routes checked:       {len(checks)}")
    print(f"Permanent namespace:  {term['current']}")
    print(f"Predecessor namespace:{term['predecessor']}")
    print(f"Verification phase:   {mode}")


if __name__ == "__main__":
    main()
