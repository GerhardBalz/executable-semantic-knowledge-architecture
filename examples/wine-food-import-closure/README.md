# Wine + Food import-closure proving ground

This example implements ESKA #78 as an independent proving ground derived from the **architectural structure** of the W3C OWL Guide's Wine + Food example.

It tests one narrow claim:

> A semantic import dependency can retain its historical ontology identity while a controlled loader maps that identity to replaceable physical artifacts, without changing the normalized semantic result.

## Authority boundary

The files in `fixtures/` and `backends/` are **clean-room minimal test slices** created for this experiment. They are not copies of, replacements for, or authoritative versions of the W3C Wine or Food ontologies.

The experiment preserves only the historical identifiers and relationships needed for the test. It does not claim authority over W3C identifiers and does not republish the W3C ontology content.

Primary evidence:

- W3C OWL Guide Recommendation, 10 February 2004: https://www.w3.org/TR/2004/REC-owl-guide-20040210/
- W3C OWL Guide current publication: https://www.w3.org/TR/owl-guide/
- W3C OWL Test Cases: https://www.w3.org/TR/owl-test/
- W3C WebOnt working-group discussion of Wine/Food validation and import-location fixes: https://lists.w3.org/Archives/Public/www-webont-wg/2003Jun/0052.html
- W3C WebOnt review discussing `xml:base`, import identifiers and `.rdf` document suffixes: https://lists.w3.org/Archives/Public/www-webont-wg/2003Jul/0347.html

The dated 2004 Guide identifies these namespaces:

```text
http://www.w3.org/TR/2004/REC-owl-guide-20040210/wine#
http://www.w3.org/TR/2004/REC-owl-guide-20040210/food#
```

and describes the Wine ontology importing the Food ontology identity:

```text
http://www.w3.org/TR/2004/REC-owl-guide-20040210/food
```

## Test slice

The controlled Wine slice contains only the facts needed to establish the cross-ontology dependency:

```text
Wine ontology
  owl:imports Food ontology

wine:Wine
  rdfs:subClassOf food:PotableLiquid
```

Each valid Food backend contains:

```text
food:PotableLiquid
  rdfs:subClassOf food:ConsumableThing
```

Therefore the expected transitive result is:

```text
wine:Wine
  rdfs:subClassOf food:ConsumableThing
```

The verifier intentionally implements only the small `rdfs:subClassOf` transitive-closure surface required for this test. It is **not** a complete OWL reasoner and the result must not be generalized beyond this tested semantic operation.

## Physical mappings

Two mapping files resolve the same Food semantic identity to materially different repository paths:

```text
mappings/backend-a.json
    → backends/a/food.ttl

mappings/backend-b.json
    → backends/b/nested/food-reference.ttl
```

The backend files declare the same Food ontology identity and encode the same tested semantic slice.

The physical file path is runtime evidence only. It is not promoted to ontology identity.

## Controls

`verify.py` requires all of the following:

1. **Wine alone** — the expected `Wine → ConsumableThing` result is absent because the Food dependency has not been loaded.
2. **Missing mapping** — a Wine import with no physical mapping fails deterministically.
3. **Wrong-identity backend** — a physical file that contains plausible Food terms but does not declare the imported Food ontology identity is rejected.
4. **Backend A** — Wine + mapped Food closure produces the expected result.
5. **Backend B** — the same semantic identities mapped to a different physical layout produce exactly the same normalized result.

The final invariant is therefore:

```text
historical semantic identities
        +
explicit Wine → Food dependency
        +
replaceable physical mapping
        ↓
same tested semantic result
```

## ESKA mapping

`architecture.ttl` uses existing ESKA and PROV-O vocabulary only.

| Experiment concept | Representation |
|---|---|
| Wine / Food semantic sources | `eska:SemanticModel` |
| Import-aware subclass lookup | `eska:SemanticCapability` |
| Mapping-aware loader configurations | `eska:ExecutableSemanticKnowledgeArtifact` |
| Backend A / B runs | `eska:Execution` |
| Normalized inferred relation | `eska:Result` |
| Backend invariance check | `eska:Verification` |
| Concrete runtime usage / derivation | PROV-O |

No ESKA ontology term is added or modified.

## Run

```bash
python -m pip install -r examples/wine-food-import-closure/requirements.txt
python examples/wine-food-import-closure/verify.py
```

A passing run prints JSON evidence and ends with:

```text
PASS: Wine/Food import identity is stable across replaceable physical backends
```

## Scope and limitations

This proving ground demonstrates only the following:

- an explicit import identity can be kept distinct from physical retrieval paths;
- a missing import closure changes the tested semantic result;
- two physical mappings can preserve the same tested result;
- a mapped file must declare the semantic ontology identity it is meant to satisfy.

It does **not** demonstrate:

- full equivalence to the complete W3C Wine/Food ontologies;
- all OWL import semantics;
- full OWL DL reasoning;
- current W3C artifact availability;
- a new persistent publication scheme for historical W3C identifiers.

The historical W3C artifacts remain the reference authority for the original example. This repository owns only the executable test contract defined here.
