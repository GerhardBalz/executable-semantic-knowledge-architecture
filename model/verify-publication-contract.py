#!/usr/bin/env python3
"""Verify the active ESKA namespace/publication/versioning contract."""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'model/publication-contract.json'
MIGRATION = ROOT / 'model/namespace-migration.json'
ONTOLOGY_RE = re.compile(r'<([^>]+)>\s*\n\s*a owl:Ontology\s*;', re.MULTILINE)
VERSION_IRI_RE = re.compile(r'owl:versionIRI\s+<([^>]+)>')
VERSION_RE = re.compile(r'owl:versionInfo\s+"([^"]+)"')
TERM_DECL_RE = re.compile(r'^eska:([A-Za-z][A-Za-z0-9_-]*)\s*\n\s+a owl:(?:Class|ObjectProperty|DatatypeProperty)\s*;', re.MULTILINE)
SEMVER_RE = re.compile(r'^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$')

def require(condition: bool, message: str) -> None:
    if not condition: raise AssertionError(message)

def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    migration = json.loads(MIGRATION.read_text(encoding='utf-8'))
    require(contract['contractVersion'] == '1.1', 'unexpected publication contract version')
    require(contract['status'] == 'permanent-namespace-active', 'permanent publication contract is not active')
    term = contract['termNamespace']
    require(term['current'] == 'https://w3id.org/eska#', 'unexpected active ESKA term namespace')
    require(term['predecessor'] == 'urn:eska:core:', 'unexpected predecessor term namespace')
    require(term['activationStatus'] == 'active', 'permanent namespace must be active')
    modules = contract['modules']
    require([m['name'] for m in modules] == ['core','capability','service','agent','deployment'], 'module identity/order changed')
    declared = {}
    ontology_pairs = set()
    for module in modules:
        path = ROOT / module['path']; text = path.read_text(encoding='utf-8')
        require('@prefix eska: <https://w3id.org/eska#>' in text, f'{path}: active term namespace missing')
        require('urn:eska:core:' not in text, f'{path}: provisional term namespace remains')
        om = ONTOLOGY_RE.search(text); require(om and om.group(1) == module['ontologyIri'], f'{path}: ontology IRI mismatch')
        vim = VERSION_IRI_RE.search(text); require(vim and vim.group(1) == module['versionIri'], f'{path}: version IRI mismatch')
        vm = VERSION_RE.search(text); require(vm and vm.group(1) == module['version'], f'{path}: versionInfo mismatch')
        require(bool(SEMVER_RE.match(module['version'])), f'{path}: module version is not SemVer')
        ontology_pairs.add((module['predecessorOntologyIri'], module['ontologyIri']))
        for local in TERM_DECL_RE.findall(text):
            require(local not in declared, f'term {local} declared twice'); declared[local] = module['name']
    require(len(declared) == 53, f'expected 53 ESKA terms, found {len(declared)}')
    require(set(migration['terms']) == set(declared), 'migration term inventory differs from modules')
    require(migration['predecessorTermNamespace'] == term['predecessor'], 'migration predecessor mismatch')
    require(migration['successorTermNamespace'] == term['current'], 'migration successor mismatch')
    require(migration['owlSameAsUsed'] is False, 'namespace migration must not use owl:sameAs')
    mapped = {(x['predecessor'], x['successor']) for x in migration['ontologyIris']}
    require(mapped == ontology_pairs, 'ontology predecessor mapping incomplete')
    print('SUCCESS: ESKA permanent namespace and predecessor mapping are machine-verifiable.')
    print(f"Active term namespace:      {term['current']}")
    print(f"Predecessor term namespace: {term['predecessor']}")
    print(f"Ontology modules:           {len(modules)}")
    print(f"Declared ESKA terms:        {len(declared)}")
    print(f"Next repository release:    eska-v{contract['releaseVersioning']['initialRepositoryVersion']}")
if __name__ == '__main__': main()
