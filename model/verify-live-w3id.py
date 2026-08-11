#!/usr/bin/env python3
"""Verify live current and immutable ESKA W3ID routes from external CI."""
from __future__ import annotations
import json
from pathlib import Path
import urllib.error
import urllib.request
ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "model" / "publication-contract.json"
TARGETS_PATH = ROOT / "publication" / "backend-targets.json"
W3ID_BASE = "https://w3id.org/eska"
USER_AGENT = "ESKA-W3ID-verifier/1.1"
class RecordingRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__(); self.chain: list[tuple[int,str]] = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append((int(code), str(newurl)))
        return super().redirect_request(req, fp, code, msg, headers, newurl)
def require(condition: bool, message: str) -> None:
    if not condition: raise AssertionError(message)
def normalize(url: str) -> str: return url.rstrip("/")
def fetch(route: str, accept: str, expected_final: str, *, expect_text: str | None = None) -> list[tuple[int,str]]:
    handler = RecordingRedirectHandler(); opener = urllib.request.build_opener(handler)
    request = urllib.request.Request(route, headers={"Accept":accept,"User-Agent":USER_AGENT})
    try:
        with opener.open(request, timeout=30) as response:
            final_url=str(response.geturl()); status=int(response.status)
            content=response.read(32768).decode("utf-8",errors="replace") if expect_text is not None else ""
    except urllib.error.HTTPError as exc: raise AssertionError(f"{route} returned HTTP {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc: raise AssertionError(f"{route} could not be resolved/fetched: {exc.reason}") from exc
    require(status==200,f"{route}: final response was HTTP {status}, expected 200")
    require(normalize(final_url)==normalize(expected_final),f"{route}: resolved to {final_url}, expected {expected_final}")
    require(handler.chain,f"{route}: W3ID route did not redirect")
    require(any(code==303 for code,_ in handler.chain),f"{route}: redirect chain contains no HTTP 303: {handler.chain}")
    if expect_text is not None: require(expect_text in content,f"{route}: resolved representation lacks expected marker {expect_text!r}")
    return handler.chain
def main() -> None:
    contract=json.loads(CONTRACT_PATH.read_text(encoding="utf-8")); targets=json.loads(TARGETS_PATH.read_text(encoding="utf-8")); term=contract["termNamespace"]
    require(term["current"]=="https://w3id.org/eska#","unexpected permanent ESKA namespace")
    require(term["activationStatus"]=="active","unexpected activation state")
    require(targets["releaseTag"]=="eska-v0.1.0","unexpected governed release tag")
    checks: list[tuple[str,str,str,str|None]]=[
      (W3ID_BASE,"text/html",targets["humanDocumentation"],None),
      (W3ID_BASE,"text/turtle",targets["combinedRdf"],term["current"]),
      (f"{W3ID_BASE}/docs","text/html",targets["namespaceDocumentation"],None),
      (f"{W3ID_BASE}/dist/eska.ttl","text/turtle",targets["combinedRdf"],term["current"])]
    for module in contract["modules"]:
        name=str(module["name"]); target=targets["modules"][name]
        require(target["version"]==str(module["version"]),f"{name}: backend version differs from publication contract")
        require(target["versionIri"]==str(module["versionIri"]),f"{name}: backend version IRI differs from publication contract")
        checks += [
          (f"{W3ID_BASE}/model/{name}","text/html",target["human"],None),
          (f"{W3ID_BASE}/model/{name}","text/turtle",target["rdf"],str(module["ontologyIri"])),
          (target["versionIri"],"text/html",target["versionHuman"],str(module["versionIri"])),
          (target["versionIri"],"text/turtle",target["versionRdf"],str(module["versionIri"])),
          (target["versionDistribution"],"text/turtle",target["versionRdf"],str(module["versionIri"]))]
    print("Verifying live current and immutable ESKA W3ID routes...")
    for route,accept,expected,marker in checks:
        chain=fetch(route,accept,expected,expect_text=marker)
        print(f"PASS {route} [{accept}] -> {expected}")
        print("     redirects: "+" -> ".join(f"{code} {url}" for code,url in chain))
    print("SUCCESS: current and immutable W3ID routes are live and publication-consistent.")
    print(f"Routes checked: {len(checks)}")
    print(f"Permanent namespace: {term['current']}")
    print(f"Immutable release: {targets['releaseTag']}")
if __name__=="__main__": main()
