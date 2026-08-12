#!/usr/bin/env python3
"""Verify the active ESKA namespace and core-0.2.0 compatibility contract."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "model/publication-contract.json"
MIGRATION = ROOT / "model/namespace-migration.json"
CORE = ROOT / "model/eska-core.ttl"

ONTOLOGY_RE = re.compile(r"<([^>]+)>\s*\n\s*a owl:Ontology\s*;", re.MULTILINE)
VERSION_IRI_RE = re.compile(r"owl:versionIRI\s+<([^>]+)>")
VERSION_RE = re.compile(r"owl:versionInfo\s+\"([^\"]+)\"")
TERM_DECL_RE = re.compile(
    r"^eska:([A-Za-z][A-Za-z0-9_-]*)\s*\n\s+a owl:(?:Class|ObjectProperty|DatatypeProperty)\s*;",
    re.MULTILINE,
)
SEMVER_RE = re.compile(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")

SMO_CLASS = "https://w3id.org/smo#SemanticModel"
SMO_VERSION = "https://w3id.org/smo/0.1.0"
ESKA_CLASS = "https://w3id.org/eska#SemanticModel"
EQUIVALENT_CLASS = "http://www.w3.org/2002/07/owl#equivalentClass"
SEMANTIC_MODEL_DEFINITION = (
    "A formal representation that gives knowledge explicit machine-interpretable meaning "
    "through concepts, relationships, constraints, axioms, or equivalent semantic structures."
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    migration = json.loads(MIGRATION.read_text(encoding="utf-8"))

    require(contract["contractVersion"] == "1.2", "unexpected publication contract version")
    require(contract["status"] == "core-0.2.0-release-pending", "unexpected publication state")

    term = contract["termNamespace"]
    require(term["current"] == "https://w3id.org/eska#", "unexpected active ESKA term namespace")
    require(term["predecessor"] == "urn:eska:core:", "unexpected predecessor term namespace")
    require(term["activationStatus"] == "active", "permanent namespace must be active")

    release = contract["releaseVersioning"]
    require(release["currentPublishedRepositoryVersion"] == "0.1.0", "published repository release changed unexpectedly")
    require(release["nextRepositoryVersion"] == "0.2.0", "next repository release must be 0.2.0")
    require(release["nextRepositoryReleaseStatus"] == "pending", "0.2.0 release must remain pending in this stage")

    alignment = contract["compatibility"]["semanticModelAlignment"]
    require(alignment == {
        "canonicalClass": SMO_CLASS,
        "compatibilityClass": ESKA_CLASS,
        "relation": EQUIVALENT_CLASS,
        "dependency": SMO_VERSION,
        "compatibilityClassDeprecated": False,
    }, "SemanticModel alignment contract mismatch")

    modules = contract["modules"]
    require([m["name"] for m in modules] == ["core", "capability", "service", "agent", "deployment"], "module identity/order changed")
    expected_versions = {
        "core": "0.2.0",
        "capability": "0.2.0",
        "service": "0.4.0",
        "agent": "0.3.0",
        "deployment": "0.1.0",
    }

    declared: dict[str, str] = {}
    ontology_pairs: set[tuple[str, str]] = set()
    for module in modules:
        path = ROOT / module["path"]
        text = path.read_text(encoding="utf-8")
        require("@prefix eska: <https://w3id.org/eska#>" in text, f"{path}: active term namespace missing")
        require("urn:eska:core:" not in text, f"{path}: provisional term namespace remains")
        require(module["version"] == expected_versions[module["name"]], f"{path}: unexpected module version")
        require(bool(SEMVER_RE.match(module["version"])), f"{path}: module version is not SemVer")

        ontology_match = ONTOLOGY_RE.search(text)
        require(ontology_match and ontology_match.group(1) == module["ontologyIri"], f"{path}: ontology IRI mismatch")
        version_iri_match = VERSION_IRI_RE.search(text)
        require(version_iri_match and version_iri_match.group(1) == module["versionIri"], f"{path}: version IRI mismatch")
        version_match = VERSION_RE.search(text)
        require(version_match and version_match.group(1) == module["version"], f"{path}: versionInfo mismatch")

        ontology_pairs.add((module["predecessorOntologyIri"], module["ontologyIri"]))
        for local in TERM_DECL_RE.findall(text):
            require(local not in declared, f"term {local} declared twice")
            declared[local] = module["name"]

    require(len(declared) == 53, f"expected 53 ESKA terms, found {len(declared)}")
    require(set(migration["terms"]) == set(declared), "migration term inventory differs from modules")
    require(migration["predecessorTermNamespace"] == term["predecessor"], "migration predecessor mismatch")
    require(migration["successorTermNamespace"] == term["current"], "migration successor mismatch")
    require(migration["owlSameAsUsed"] is False, "namespace migration must not use owl:sameAs")
    mapped = {(x["predecessor"], x["successor"]) for x in migration["ontologyIris"]}
    require(mapped == ontology_pairs, "ontology predecessor mapping incomplete")

    core = CORE.read_text(encoding="utf-8")
    require("@prefix smo: <https://w3id.org/smo#>" in core, "core 0.2.0 must declare the SMO namespace")
    require(f"dcterms:requires <{SMO_VERSION}>" in core, "core must depend explicitly on immutable SMO v0.1.0")
    require("owl:imports" not in core, "SMO alignment must not introduce owl:imports by symmetry")
    require("eska:SemanticModel\n    a owl:Class ;\n    owl:equivalentClass smo:SemanticModel ;" in core, "SemanticModel equivalentClass bridge missing")
    require("owl:deprecated" not in core, "eska:SemanticModel must not be deprecated in the first SMO bridge")
    require(f'skos:definition "{SEMANTIC_MODEL_DEFINITION}"@en' in core, "ESKA SemanticModel definition changed")
    require("eska:usesSemanticModel\n    a owl:ObjectProperty ;\n    rdfs:label \"uses semantic model\"@en ;\n    rdfs:range eska:SemanticModel ." in core, "usesSemanticModel compatibility surface changed")

    print("SUCCESS: ESKA core 0.2.0 and SMO SemanticModel compatibility are machine-verifiable.")
    print(f"Active term namespace:       {term['current']}")
    print("Core module version:         0.2.0")
    print("SemanticModel bridge:        owl:equivalentClass smo:SemanticModel")
    print(f"Immutable SMO dependency:    {SMO_VERSION}")
    print("ESKA SemanticModel deprecated: no")
    print("Next repository release:     eska-v0.2.0 (pending)")


if __name__ == "__main__":
    main()
