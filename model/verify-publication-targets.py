#!/usr/bin/env python3
"""Verify active/versioned ESKA W3ID publication metadata and RDF distribution."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse
from rdflib import Graph, URIRef
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parents[1]

def require(c: bool, m: str) -> None:
    if not c:
        raise AssertionError(m)

def contains(g: Graph, ns: str) -> bool:
    return any(isinstance(t, URIRef) and str(t).startswith(ns) for triple in g for t in triple)

def require_backend_url(url: str) -> None:
    p = urlparse(str(url))
    require(p.scheme == 'https' and p.netloc in {'github.com', 'raw.githubusercontent.com'}, f'unexpected backend URL: {url}')

def main() -> None:
    contract = json.loads((ROOT / 'model/publication-contract.json').read_text())
    targets = json.loads((ROOT / 'publication/backend-targets.json').read_text())
    term = contract['termNamespace']

    require(term['activationStatus'] == 'active', 'namespace not active')
    require(targets.get('status') == 'w3id-active-versioned', 'backend status does not reflect active versioned W3ID')
    require(targets.get('releaseTag') == 'eska-v0.1.0', 'governed release tag mismatch')
    require(targets.get('persistentVocabulary') == 'https://w3id.org/eska', 'persistent vocabulary route mismatch')
    require(targets.get('w3idActivationPullRequest') == 'https://github.com/perma-id/w3id.org/pull/6530', 'W3ID activation PR mismatch')
    require(targets.get('w3idVersionRoutesPullRequest') == 'https://github.com/perma-id/w3id.org/pull/6535', 'W3ID version-routes PR mismatch')
    require(targets.get('w3idVersionRoutesMergeCommit') == 'bf72939d8d6a15d78f2be16a87eaca494e72882b', 'W3ID version-routes merge commit mismatch')

    authoritative = Graph()
    for module in contract['modules']:
        authoritative.parse(ROOT / module['path'], format='turtle')
    distribution = Graph().parse(ROOT / 'dist/eska.ttl', format='turtle')
    require(isomorphic(authoritative, distribution), 'combined distribution differs from authoritative modules')
    require(contains(distribution, term['current']), 'combined distribution lacks active W3ID terms')
    require(not contains(distribution, term['predecessor']), 'combined distribution contains provisional term IRIs')

    for url in [targets['humanDocumentation'], targets['namespaceDocumentation'], targets['combinedRdf']]:
        require_backend_url(url)

    for module in contract['modules']:
        name = module['name']
        target = targets['modules'][name]
        require(target['iri'] == module['ontologyIri'], f'{name}: module IRI mismatch')
        require(target['version'] == module['version'], f'{name}: module version mismatch')
        require(target['versionIri'] == module['versionIri'], f'{name}: module version IRI mismatch')
        require(target['versionDistribution'] == f"https://w3id.org/eska/dist/{module['version']}/eska-{name}.ttl", f'{name}: immutable distribution route mismatch')
        for key in ('rdf', 'human', 'versionRdf', 'versionHuman'):
            require_backend_url(target[key])
        release_fragment = '/eska-v0.1.0/'
        require(release_fragment in target['versionRdf'], f'{name}: version RDF does not target immutable release')
        require(release_fragment in target['versionHuman'], f'{name}: version HTML does not target immutable release')

    print('SUCCESS: active/versioned ESKA W3ID publication metadata and distribution are consistent.')
    print(f'Combined distribution triples: {len(distribution)}')
    print(f"Active term namespace:          {term['current']}")
    print(f"Immutable repository release:   {targets['releaseTag']}")
    print(f"Versioned ontology modules:     {len(contract['modules'])}")

if __name__ == '__main__':
    main()
