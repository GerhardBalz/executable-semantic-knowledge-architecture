#!/usr/bin/env python3
"""Verify the cross-repository Pizza semantic-source ownership boundary."""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "pizza-domain-source.json"
DOMAIN_DIR = HERE / ".work" / "pizza-domain"

FORBIDDEN_LOCAL_COPIES = (
    HERE / "spicy-pizza.ofn",
    HERE / "validation" / "pizza-shapes.ttl",
    HERE / "validation" / "valid-pizza.ttl",
    HERE / "validation" / "invalid-pizza.ttl",
)

EXPECTED_ARTIFACTS = {
    "reasoning": "artifacts/reasoning/spicy-pizza.ofn",
    "shapes": "artifacts/validation/pizza-instance-shapes.ttl",
    "validData": "artifacts/validation/data/conforming.ttl",
    "invalidData": "artifacts/validation/data/non-conforming.ttl",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = json.loads(CONFIG.read_text(encoding="utf-8"))

    require(source.get("repository") == "GerhardBalz/pizza-ontology", "Pizza domain semantics must be sourced from the companion pizza-ontology repository")
    commit = source.get("commit")
    require(isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "Pizza domain source must be an immutable 40-character Git commit SHA")
    require(source.get("manifest") == "artifacts/manifest.ttl", "Pizza domain source must use the published semantic artifact manifest")
    require(source.get("artifacts") == EXPECTED_ARTIFACTS, "ESKA Pizza source binding no longer matches the published artifact role/path contract")

    for path in FORBIDDEN_LOCAL_COPIES:
        require(not path.exists(), f"ESKA must not regain ownership of Pizza domain semantic copy: {path.relative_to(HERE)}")

    require((DOMAIN_DIR / "manifest.ttl").is_file(), "Pinned Pizza manifest was not materialized during execution")
    require((DOMAIN_DIR / "reasoning.ofn").is_file(), "Pinned Pizza reasoning module was not materialized during execution")

    source_metadata = json.loads((DOMAIN_DIR / "source.json").read_text(encoding="utf-8"))
    require(source_metadata.get("commit") == commit, "runtime Pizza materialization does not match the configured source commit")

    print("SUCCESS: Pizza domain semantics are commit-pinned, runtime-materialized, and not duplicated as ESKA source files.")
    print(f"Source: GerhardBalz/pizza-ontology@{commit}")


if __name__ == "__main__":
    main()
