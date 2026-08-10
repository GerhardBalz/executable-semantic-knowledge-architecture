#!/usr/bin/env python3
"""Materialize source-owned Pizza semantic artifacts from an immutable Git commit."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "pizza-domain-source.json"
TARGET = HERE / ".work" / "pizza-domain"

EXPECTED_ARTIFACTS = {
    "reasoning": "artifacts/reasoning/spicy-pizza.ofn",
    "shapes": "artifacts/validation/pizza-instance-shapes.ttl",
    "validData": "artifacts/validation/data/conforming.ttl",
    "invalidData": "artifacts/validation/data/non-conforming.ttl",
}

LOCAL_NAMES = {
    "reasoning": "reasoning.ofn",
    "shapes": "shapes.ttl",
    "validData": "valid-data.ttl",
    "invalidData": "invalid-data.ttl",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_config() -> dict[str, object]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    repository = data.get("repository")
    commit = data.get("commit")
    manifest = data.get("manifest")
    artifacts = data.get("artifacts")

    require(repository == "GerhardBalz/pizza-ontology", f"unexpected Pizza source repository: {repository!r}")
    require(isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "Pizza source must be pinned to a 40-character Git commit SHA")
    require(manifest == "artifacts/manifest.ttl", f"unexpected manifest path: {manifest!r}")
    require(artifacts == EXPECTED_ARTIFACTS, "Pizza artifact role/path contract differs from the expected source-owned contract")
    return data


def raw_url(repository: str, commit: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repository}/{commit}/{path}"


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "ESKA-Pizza-domain-artifact-fetcher/1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            require(response.status == 200, f"unexpected HTTP status {response.status} for {url}")
            return response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to fetch pinned Pizza artifact {url}: {exc}") from exc


def main() -> None:
    config = read_config()
    repository = str(config["repository"])
    commit = str(config["commit"])
    manifest_path = str(config["manifest"])
    artifact_paths = dict(config["artifacts"])

    TARGET.mkdir(parents=True, exist_ok=True)

    manifest_bytes = download(raw_url(repository, commit, manifest_path))
    manifest_text = manifest_bytes.decode("utf-8")

    # The source repository verifies the RDF catalog semantically in its own CI.
    # Here we verify that our pinned operational binding still names exactly the
    # published repository-relative artifact paths before materializing them.
    for role, path in EXPECTED_ARTIFACTS.items():
        require(
            f'dcterms:identifier "{path}"' in manifest_text,
            f"Pizza source manifest at {commit} does not publish {role}: {path}",
        )

    (TARGET / "manifest.ttl").write_bytes(manifest_bytes)

    materialized: dict[str, str] = {}
    for role, path in artifact_paths.items():
        local_name = LOCAL_NAMES[role]
        data = download(raw_url(repository, commit, path))
        require(bool(data), f"downloaded empty Pizza artifact for {role}: {path}")
        (TARGET / local_name).write_bytes(data)
        materialized[role] = local_name

    source_metadata = {
        "repository": repository,
        "commit": commit,
        "manifest": manifest_path,
        "artifactPaths": artifact_paths,
        "materialized": materialized,
        "sourceTree": f"https://github.com/{repository}/tree/{commit}/artifacts",
    }
    (TARGET / "source.json").write_text(
        json.dumps(source_metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"SUCCESS: materialized Pizza semantic artifacts from immutable commit {commit}.")
    for role in sorted(materialized):
        print(f"- {role}: {artifact_paths[role]} -> {TARGET / materialized[role]}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
