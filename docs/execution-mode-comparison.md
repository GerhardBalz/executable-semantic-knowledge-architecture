# Execution Mode Comparison

Executable Semantic Knowledge Architecture (ESKA) does not define a single universal execution mechanism. Instead, semantic artifacts are executable according to the operational semantics appropriate to their type.

The Pizza reference project currently demonstrates two execution modes:

| Concern | OWL reasoning | SHACL validation |
| --- | --- | --- |
| Semantic model | OWL class axioms | SHACL shapes graph |
| Semantic input | Ontology / class knowledge | RDF data graph |
| Executable artifact | HermiT classification via ROBOT | SHACL validation via pySHACL |
| Operation | reason | validate |
| Primary result | inferred axiom | `sh:ValidationReport` |
| Result relation | `rdfs:subClassOf` | `sh:conforms` |
| Bounded capability | `PizzaClassificationCapability` | `PizzaValidationCapability` |
| Verification | expected inference query | expected conformance / violation checks |
| Provenance | PROV-O reasoning activity | PROV-O validation activity |

## What is stable across both modes?

The comparison supports a small set of concepts that appear independent of the execution technology:

```text
SemanticModel
        │
        │ gives meaning to
        ▼
Semantic Knowledge
        │
        │ operationalized through
        ▼
ExecutableSemanticKnowledgeArtifact
        │
        │ realizes
        ▼
SemanticCapability
        │
        │ executed as
        ▼
Execution
        │
        │ generates
        ▼
Result
        │
        ├── verified by → Verification
        └── traced with → PROV-O provenance
```

These concepts are therefore candidates for the provisional ESKA core model.

## What is not yet core?

Several concepts are important but have not yet been demonstrated across both execution modes:

- `KnowledgeService` — currently demonstrated only for classification;
- `ServiceOperation` — currently specific to operational service exposure;
- `KnowledgeAgent` and `DiscoveryArtifact` — currently demonstrated only on the classification path;
- HTTP-specific properties such as method, path and representation fields;
- deployment binding — currently supplied separately at runtime;
- a dedicated ESKA provenance class — PROV-O already provides the required vocabulary and should not be duplicated without evidence that an ESKA-specific abstraction is needed.

The core model should therefore remain smaller than the complete reference architecture.

## Execution is polymorphic

The two Pizza examples provide concrete evidence that **executable** in ESKA should not mean “converted to procedural code”.

Instead:

```text
Ontology   → reason
Constraint → validate
```

Both are executable because formal semantic artifacts participate directly in computation and produce machine-interpretable results.

Future examples can test whether the same core abstraction remains stable for additional execution modes such as:

```text
Rule        → evaluate
Decision    → decide
Calculation → calculate
Mapping     → transform
Workflow    → execute
```

The ESKA core should generalize only after those examples demonstrate stable semantics, not before.
