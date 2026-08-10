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
    HERE / "rules" / "vegetarian-warning.rq",
    HERE / "rules" / "rule-vocabulary.ttl",
    HERE / "rules" / "data" / "menu-pizzas.ttl",
    HERE / "decisions" / "pizza-dietary-suitability.dmn",
    HERE / "decisions" / "decision-vocabulary.ttl",
    HERE / "decisions" / "data" / "cases.json",
    HERE / "calculations" / "pizza-area.openmath.xml",
    HERE / "calculations" / "calculation-vocabulary.ttl",
    HERE / "calculations" / "data" / "cases.json",
)

EXPECTED_ARTIFACTS = {
    "reasoning": "artifacts/reasoning/spicy-pizza.ofn",
    "shapes": "artifacts/validation/pizza-instance-shapes.ttl",
    "validData": "artifacts/validation/data/conforming.ttl",
    "invalidData": "artifacts/validation/data/non-conforming.ttl",
    "ruleQuery": "artifacts/rules/vegetarian-warning.rq",
    "ruleVocabulary": "artifacts/rules/rule-vocabulary.ttl",
    "ruleData": "artifacts/rules/data/menu-pizzas.ttl",
    "decisionModel": "artifacts/decisions/pizza-dietary-suitability.dmn",
    "decisionVocabulary": "artifacts/decisions/decision-vocabulary.ttl",
    "decisionCases": "artifacts/decisions/data/cases.json",
    "calculationFormula": "artifacts/calculations/pizza-area.openmath.xml",
    "calculationVocabulary": "artifacts/calculations/calculation-vocabulary.ttl",
    "calculationCases": "artifacts/calculations/data/cases.json",
}

EXPECTED_MATERIALIZED = (
    "manifest.ttl",
    "reasoning.ofn",
    "shapes.ttl",
    "valid-data.ttl",
    "invalid-data.ttl",
    "rule.rq",
    "rule-vocabulary.ttl",
    "rule-data.ttl",
    "decision.dmn",
    "decision-vocabulary.ttl",
    "decision-cases.json",
    "calculation.openmath.xml",
    "calculation-vocabulary.ttl",
    "calculation-cases.json",
    "source.json",
)


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

    for name in EXPECTED_MATERIALIZED:
        require((DOMAIN_DIR / name).is_file(), f"Pinned Pizza artifact was not materialized during execution: {name}")

    source_metadata = json.loads((DOMAIN_DIR / "source.json").read_text(encoding="utf-8"))
    require(source_metadata.get("commit") == commit, "runtime Pizza materialization does not match the configured source commit")

    print("SUCCESS: Pizza domain semantics are commit-pinned, runtime-materialized, and not duplicated as ESKA source files.")
    print(f"Source: GerhardBalz/pizza-ontology@{commit}")


if __name__ == "__main__":
    main()
