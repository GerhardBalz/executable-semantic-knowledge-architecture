#!/usr/bin/env python3
"""Verify the machine-readable ESKA namespace/publication/versioning contract."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
CONTRACT = MODEL / "publication-contract.json"

ONTOLOGY_RE = re.compile(r"<([^>]+)>\s*\n\s*a owl:Ontology\s*;", re.MULTILINE)
VERSION_RE = re.compile(r'owl:versionInfo\s+"([^"]+)"')
TERM_DECL_RE = re.compile(
    r"^eska:([A-Za-z][A-Za-z0-9_-]*)\s*\n\s+a owl:(?:Class|ObjectProperty|DatatypeProperty)\s*;",
    re.MULTILINE,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    require(contract["contractVersion"] == "1.0", "unexpected publication contract version")
    require(
        contract["status"] == "provisional-publication-strategy",
        "publication strategy remains provisional until the source namespace migration is complete",
    )

    term = contract["termNamespace"]
    require(term["current"] == "urn:eska:core:", "unexpected current ESKA term namespace")
    require(term["target"] == "https://w3id.org/eska#", "unexpected target ESKA term namespace")
    require(
        term["activationStatus"] == "resolver-active-source-provisional",
        "resolver must be recorded active while the semantic source remains provisional",
    )
    require(len(term["activationPrerequisites"]) >= 4, "activation prerequisites are incomplete")

    routes = contract["publicationRoutes"]
    require(routes["vocabulary"] == "https://w3id.org/eska", "unexpected vocabulary publication route")
    require(routes["combinedRdf"].startswith("https://w3id.org/eska/"), "combined RDF route must use the persistent namespace")
    require(routes["combinedDocumentation"].startswith("https://w3id.org/eska/"), "documentation route must use the persistent namespace")

    release = contract["releaseVersioning"]
    require(release["repositoryTagPattern"] == "eska-v{version}", "unexpected ESKA release tag pattern")
    require(
        bool(re.match(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$", release["initialRepositoryVersion"])),
        "initial repository version is not SemVer",
    )
    require(release["semanticModuleVersionsIndependent"] is True, "module versions must remain independent from repository release versions")

    modules = contract["modules"]
    require(
        [module["name"] for module in modules] == ["core", "capability", "service", "agent", "deployment"],
        "module publication order/identity changed unexpectedly",
    )

    current_iris: set[str] = set()
    target_iris: set[str] = set()
    declared_terms: dict[str, str] = {}

    for module in modules:
        path = ROOT / module["path"]
        require(path.is_file(), f"missing module: {path}")
        text = path.read_text(encoding="utf-8")

        ontology_match = ONTOLOGY_RE.search(text)
        require(ontology_match is not None, f"{path}: ontology IRI not found")
        require(ontology_match.group(1) == module["currentOntologyIri"], f"{path}: current ontology IRI differs from publication contract")

        version_match = VERSION_RE.search(text)
        require(version_match is not None, f"{path}: owl:versionInfo not found")
        require(version_match.group(1) == module["currentVersion"], f"{path}: current module version differs from publication contract")

        # The resolver is live, but semantic source identity has deliberately not migrated yet.
        require(module["currentOntologyIri"].startswith("urn:eska:model:"), f"{path}: ontology IRI migrated before the atomic migration increment")
        require(module["targetOntologyIri"] == f"https://w3id.org/eska/model/{module['name']}", f"{path}: unexpected target ontology IRI")
        require(
            bool(re.match(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$", module["firstPublishedVersion"])),
            f"{path}: first published version is not SemVer",
        )
        require("https://w3id.org/eska" not in text, f"{path}: permanent semantic IRIs introduced before the atomic migration")

        current_iris.add(module["currentOntologyIri"])
        target_iris.add(module["targetOntologyIri"])

        for local_name in TERM_DECL_RE.findall(text):
            require(local_name not in declared_terms, f"ESKA term {local_name} is declared in both {declared_terms.get(local_name)} and {module['name']}")
            declared_terms[local_name] = module["name"]

    require(len(current_iris) == len(modules), "current ontology IRIs are not unique")
    require(len(target_iris) == len(modules), "target ontology IRIs are not unique")
    require(len(declared_terms) >= 20, f"unexpectedly few ESKA vocabulary terms discovered: {len(declared_terms)}")

    migration_pairs = {
        f"{term['current']}{local}": f"{term['target']}{local}"
        for local in declared_terms
    }
    require(len(migration_pairs) == len(declared_terms), "term namespace migration is not one-to-one")
    require(len(set(migration_pairs.values())) == len(migration_pairs), "target term IRIs collide")

    print("SUCCESS: ESKA governance records a live persistent resolver while preserving the provisional semantic source until atomic migration.")
    print(f"Current term namespace: {term['current']}")
    print(f"Target term namespace:  {term['target']} ({term['activationStatus']})")
    print(f"Ontology modules:       {len(modules)}")
    print(f"Declared ESKA terms:    {len(declared_terms)}")
    print(f"Initial repo release:   eska-v{release['initialRepositoryVersion']}")


if __name__ == "__main__":
    main()
