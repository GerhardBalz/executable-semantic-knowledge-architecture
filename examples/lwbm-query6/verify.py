#!/usr/bin/env python3
import argparse, hashlib, html, json, re
from html.parser import HTMLParser
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, URIRef
from rdflib.collection import Collection

BASE = Path(__file__).resolve().parent
CONTRACT_PATH = BASE / "benchmark-contract.json"
QUERY_PATH = BASE / "query6-executable.sparql"
ARCH_PATH = BASE / "architecture.ttl"

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.parts=[]
    def handle_data(self,data): self.parts.append(data)
    def text(self): return "\n".join(self.parts)

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def assert_hash(path,expected,label):
    actual=sha256(path)
    if actual!=expected: raise AssertionError(f"{label} SHA-256 mismatch: expected {expected}, got {actual}")

def historical_query6(query_page, contract):
    p=TextExtractor(); p.feed(Path(query_page).read_text(encoding='iso-8859-1'))
    text=html.unescape(p.text()); q=contract['sources']['queryPage']
    if q['queryStartMarker'] not in text or q['queryEndMarker'] not in text: raise AssertionError('Historical Query 6 markers missing')
    section=text.split(q['queryStartMarker'],1)[1].split(q['queryEndMarker'],1)[0]
    normalized=re.sub(r'\s+',' ',section).strip()
    for pat in contract['historicalQuery6']['requiredPatterns']:
        if pat not in normalized: raise AssertionError(f'Historical Query 6 pattern missing: {pat}')
    if 'SELECT ?X' not in normalized: raise AssertionError('Historical Query 6 SELECT variable missing')
    return normalized

def load_raw(ontology,data):
    g=Graph(); g.parse(ontology,format='xml'); g.parse(data,format='xml'); return g

def answer_set(graph,query): return sorted({str(row[0]) for row in graph.query(query)})

def named_class_parent_edges(graph):
    parents={}
    for c,_,p in graph.triples((None,RDFS.subClassOf,None)):
        if isinstance(c,URIRef) and isinstance(p,URIRef): parents.setdefault(c,set()).add(p)
    for a,_,b in graph.triples((None,OWL.equivalentClass,None)):
        if isinstance(a,URIRef) and isinstance(b,URIRef):
            parents.setdefault(a,set()).add(b); parents.setdefault(b,set()).add(a)
    for c,_,head in graph.triples((None,OWL.intersectionOf,None)):
        if not isinstance(c,URIRef): continue
        try:
            for item in Collection(graph,head):
                if isinstance(item,URIRef): parents.setdefault(c,set()).add(item)
        except Exception as exc:
            raise AssertionError(f'Cannot read owl:intersectionOf list for {c}: {exc}') from exc
    return parents

def transitive_ancestors(parents):
    memo={}
    def visit(c,stack=frozenset()):
        if c in memo: return memo[c]
        if c in stack: return set()
        out=set(parents.get(c,set()))
        for p in tuple(out): out |= visit(p,stack|{c})
        memo[c]=out; return out
    for c in list(parents): visit(c)
    return memo

def materialize_query6_surface(raw):
    out=Graph()
    for prefix,ns in raw.namespaces(): out.bind(prefix,ns)
    for triple in raw: out.add(triple)
    ancestors=transitive_ancestors(named_class_parent_edges(raw))
    class_added=0
    for individual,_,cls in list(raw.triples((None,RDF.type,None))):
        if not isinstance(cls,URIRef): continue
        for parent in ancestors.get(cls,set()):
            triple=(individual,RDF.type,parent)
            if triple not in out: out.add(triple); class_added+=1
    property_added=0
    for prop in set(raw.subjects(RDF.type,OWL.TransitiveProperty)):
        edges={}
        for s,_,o in raw.triples((None,prop,None)): edges.setdefault(s,set()).add(o)
        for s in list(edges):
            seen=set(); stack=list(edges.get(s,set()))
            while stack:
                o=stack.pop()
                if o in seen: continue
                seen.add(o); stack.extend(edges.get(o,set()))
            for o in seen:
                triple=(s,prop,o)
                if triple not in out: out.add(triple); property_added+=1
    return out, {'classAssertionsAdded':class_added,'transitivePropertyAssertionsAdded':property_added}

def main():
    p=argparse.ArgumentParser()
    for name in ('ontology','data','query-page','oracle','evidence'): p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); c=json.loads(CONTRACT_PATH.read_text())
    for key,path in [('ontology',a.ontology),('data',a.data),('queryPage',a.query_page),('oracle',a.oracle)]: assert_hash(path,c['sources'][key]['sha256'],key)
    assert_hash(QUERY_PATH,c['executableProjection']['sha256'],'executable Query 6 projection')
    historical=historical_query6(a.query_page,c); query=QUERY_PATH.read_text()
    raw=load_raw(a.ontology,a.data); raw_answers=answer_set(raw,query)
    if len(raw_answers)!=c['verification']['rawExpectedDistinctCount']: raise AssertionError(f"Raw control expected 0, got {len(raw_answers)}")
    reasoned,added=materialize_query6_surface(raw); answers=answer_set(reasoned,query); expected=c['sources']['oracle']['expectedDistinctResultCount']
    if len(answers)!=expected: raise AssertionError(f'Reasoned Query 6 expected Lehigh oracle {expected}, got {len(answers)}')
    architecture=Graph(); architecture.parse(ARCH_PATH,format='turtle')
    digest=hashlib.sha256(('\n'.join(answers)+'\n').encode()).hexdigest()
    evidence={
      'benchmark':'LWBM','case':'4k-query6','authority':'Lehigh SWAT',
      'sources':{k:{'sha256':c['sources'][k]['sha256'],'verified':True} for k in ('ontology','data','queryPage','oracle')},
      'queryBoundary':{'historicalSyntax':c['historicalQuery6']['syntax'],'historicalPatternsVerified':True,'historicalSection':historical,'executableProjectionSha256':c['executableProjection']['sha256'],'transformation':c['executableProjection']['transformation']},
      'raw':{'triples':len(raw),'distinctAnswers':len(raw_answers)},
      'semanticSurface':c['semanticSurface']|added,
      'reasoned':{'triples':len(reasoned),'distinctAnswers':len(answers),'answerSetSha256':digest},
      'externalOracle':{'expectedDistinctAnswers':expected,'publishedObservations':c['sources']['oracle']['publishedObservations'],'matched':True},
      'architectureTriples':len(architecture)
    }
    a.evidence.parent.mkdir(parents=True,exist_ok=True); a.evidence.write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print(json.dumps(evidence,indent=2,sort_keys=True)); print("PASS: LWBM Query 6 matches Lehigh's 23-result oracle")
    return 0
if __name__=='__main__': raise SystemExit(main())
