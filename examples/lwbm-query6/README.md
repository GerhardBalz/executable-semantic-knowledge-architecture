# LWBM Query 6 external-oracle proving ground

This example verifies a selected **Lehigh Wine Benchmark (LWBM) 4k / Query 6** result against evidence published by Lehigh rather than an expectation authored by ESKA.

## Authority boundary

Lehigh SWAT remains the authority for the benchmark ontology, 4k data, historical query workload, and published result evidence. The example does not vendor those payloads or replace their historical HTTP identities with GitHub or local file identities.

At runtime, CI fetches the exact Lehigh targets and requires the governed SHA-256 values before execution. Redirects and local files are retrieval mechanics only.

## Historical query versus executable projection

The recovered Lehigh query page uses historical tuple-style `WHERE` syntax. Query 6 asks for resources that are both `wine:Wine` and `wine:locatedIn wine:CaliforniaRegion`.

`query6-executable.sparql` is an explicitly declared mechanical SPARQL 1.1 syntax projection of exactly those two triple patterns. Its SHA-256 is pinned in `benchmark-contract.json`. It is not presented as the original Lehigh query text.

## External oracle

Lehigh's recovered 4k result table reports Query 6 as **23 results with completeness 100** for OWLim, Jena, and Pellet. The table bytes are hash-pinned, so `23` is an external benchmark-author target rather than a count derived from this execution.

## Scoped semantic materialization

An initial full HermiT assertion-materialization experiment was broader than this selected query requires. The accepted implementation therefore makes the semantic surface explicit and minimal rather than silently relying on a complete reasoner.

The verifier implements only sound OWL/RDFS consequences required by Query 6:

- transitive `rdfs:subClassOf` ancestry for named classes;
- named operands of `owl:intersectionOf` as superclasses of the described named class;
- named `owl:equivalentClass` pairs as bidirectional superclass edges;
- propagation of `rdf:type` to those named superclasses;
- transitive closure of properties declared `owl:TransitiveProperty`.

This surface is sufficient for the historical Wine ontology's class hierarchy and transitive `wine:locatedIn` relation. It is explicitly **not a complete OWL reasoner**. Correctness for the selected case is independently checked against Lehigh's 23-result oracle.

## Execution

The deterministic pipeline:

1. fetches the Lehigh ontology, 4k data, historical query page, and 4k result table;
2. verifies all source hashes;
3. verifies the historical Query 6 semantic patterns;
4. executes the SPARQL 1.1 projection over the unreasoned RDF union as a control;
5. materializes only the declared Query 6 semantic surface;
6. executes the same projection over the materialized graph;
7. requires exactly 23 distinct normalized answers and writes machine-readable evidence.

## ESKA mapping

`architecture.ttl` uses existing ESKA and PROV-O terms only: `SemanticModel`, `SemanticCapability`, `ExecutableSemanticKnowledgeArtifact`, `Execution`, `Result`, and `Verification`, with PROV-O for runtime usage and lineage.

No LWBM-specific ESKA vocabulary and no `model/` changes are required.

## Run

```bash
python -m pip install -r requirements.txt
bash run.sh
```

A successful run ends with:

```text
PASS: LWBM Query 6 matches Lehigh's 23-result oracle
```
