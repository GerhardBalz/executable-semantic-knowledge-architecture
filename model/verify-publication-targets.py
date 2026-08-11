#!/usr/bin/env python3
"""Verify active ESKA W3ID publication targets and combined RDF distribution."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse
from rdflib import Graph, URIRef
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parents[1]
def require(c: bool, m: str) -> None:
    if not c: raise AssertionError(m)
def contains(g: Graph, ns: str) -> bool:
    return any(isinstance(t, URIRef) and str(t).startswith(ns) for triple in g for t in triple)
def main() -> None:
    contract = json.loads((ROOT/'model/publication-contract.json').read_text())
    targets = json.loads((ROOT/'publication/backend-targets.json').read_text())
    term = contract['termNamespace']; require(term['activationStatus'] == 'active', 'namespace not active')
    authoritative = Graph()
    for module in contract['modules']: authoritative.parse(ROOT/module['path'], format='turtle')
    distribution = Graph().parse(ROOT/'dist/eska.ttl', format='turtle')
    require(isomorphic(authoritative, distribution), 'combined distribution differs from authoritative modules')
    require(contains(distribution, term['current']), 'combined distribution lacks active W3ID terms')
    require(not contains(distribution, term['predecessor']), 'combined distribution contains provisional term IRIs')
    require(targets.get('status') == 'w3id-active', 'backend status does not reflect active W3ID')
    require(targets.get('persistentVocabulary') == 'https://w3id.org/eska', 'persistent vocabulary route mismatch')
    allowed = {'github.com','raw.githubusercontent.com'}
    urls = [targets['humanDocumentation'], targets['namespaceDocumentation'], targets['combinedRdf']]
    for module in targets['modules'].values(): urls += [module['rdf'], module['human']]
    for url in urls:
        p=urlparse(str(url)); require(p.scheme=='https' and p.netloc in allowed, f'unexpected backend URL: {url}')
    for module in contract['modules']:
        require(targets['modules'][module['name']]['iri'] == module['ontologyIri'], f"{module['name']}: module IRI mismatch")
    print('SUCCESS: active ESKA W3ID publication targets and distribution are consistent.')
    print(f'Combined distribution triples: {len(distribution)}')
    print(f"Active term namespace:          {term['current']}")
if __name__ == '__main__': main()
