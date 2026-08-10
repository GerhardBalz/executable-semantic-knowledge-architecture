# Execution Mode Comparison

Executable Semantic Knowledge Architecture (ESKA) does not define a single universal execution mechanism. Instead, semantic artifacts are executable according to the operational semantics appropriate to their type.

The Pizza reference project now demonstrates three genuinely different execution modes:

| Concern | OWL reasoning | SHACL validation | Rule evaluation |
| --- | --- | --- | --- |
| Semantic model | OWL class axioms | SHACL shapes graph | SPARQL 1.1 `CONSTRUCT` rule |
| Semantic input | Ontology / class knowledge | RDF data graph | Explicit RDF rule-input graph |
| Executable artifact | HermiT classification via ROBOT | SHACL validation via pySHACL | SPARQL evaluation via RDFLib |
| Operation | reason | validate | evaluate |
| Primary result | inferred axiom | `sh:ValidationReport` | derived RDF statement |
| Result relation | `rdfs:subClassOf` | `sh:conforms` | `urn:pizza-ontology:rule:requiresVegetarianWarning` |
| Bounded capability | `PizzaClassificationCapability` | `PizzaValidationCapability` | `PizzaRuleEvaluationCapability` |
| Applicability boundary | coherent OWL model | parseable RDF using the SHACL vocabulary | explicit RDF assertions; no implicit OWL entailment |
| Verification | expected inference query | expected conformance / violation checks | expected derived statement + non-matching control |
| Provenance | PROV-O reasoning activity | PROV-O validation activity | PROV-O rule-evaluation activity |

## What is stable across all three modes?

The third mode was introduced as a falsification test for the provisional ESKA core. It fits the same abstraction without changing `model/eska-core.ttl`:

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

Across OWL reasoning, SHACL validation, and SPARQL rule evaluation, the same core concepts remain sufficient:

- `SemanticModel` identifies the formal semantic artifact that gives the operation meaning;
- `ExecutableSemanticKnowledgeArtifact` identifies the computational realization appropriate to that semantic type;
- `SemanticCapability` bounds subject, input, output, result relation, semantic model, executable artifact, and applicability;
- `ApplicabilityCondition` captures preconditions without embedding technology-specific rules in the core;
- `Execution` identifies a concrete computational activity;
- `Result` identifies the machine-interpretable output of that activity;
- `Verification` identifies an explicit check over execution and result;
- PROV-O provides the execution and derivation lineage without an ESKA-specific provenance hierarchy.

This is stronger evidence for the current core than the original two-mode comparison, but it is not a claim that the model is universally complete.

## Falsification result

The rule example did **not** require any of the following additions to the ESKA core:

- a `Rule` core class;
- a `RuleExecution` core class;
- a general `ExecutionMode` taxonomy;
- a rule-specific result superclass;
- a second ESKA provenance vocabulary;
- Service or Agent semantics.

That absence is architecturally useful. The rule semantics remain in the source-owned SPARQL artifact; ESKA describes how that semantic artifact participates in a bounded capability and concrete execution.

```text
Pizza SPARQL rule
        │ source-owned semantic model
        ▼
PizzaRuleEvaluationCapability
        │
        ▼
Execution
        │
        ▼
Derived RDF Result
        │
        ▼
Verification + PROV-O
```

## What is still not core?

Several concepts remain important but still lack cross-mode evidence:

- `KnowledgeService` — demonstrated only for classification;
- `ServiceOperation` — specific to operational service exposure;
- `KnowledgeAgent` and `DiscoveryArtifact` — demonstrated only on the classification path;
- HTTP-specific properties such as method, path and representation fields;
- deployment binding — currently supplied separately at runtime;
- a dedicated `ExecutionMode` concept — the three modes remain distinguishable through their semantic models, artifacts, capabilities, results, and implementations without requiring a core taxonomy;
- a dedicated ESKA provenance class — PROV-O continues to provide the required interoperable semantics.

The core model should therefore remain smaller than the complete reference architecture.

## Execution is polymorphic

The three Pizza examples now provide executable evidence for three different meanings of **execute**:

```text
Ontology   → reason
Constraint → validate
Rule       → evaluate
```

The mechanisms and result types differ, but formal semantic artifacts participate directly in computation and their results remain machine-traceable to the semantic knowledge that gives them meaning.

Future examples can continue trying to falsify the same core with modes such as:

```text
Decision    → decide
Calculation → calculate
Mapping     → transform
Workflow    → execute
```

A future mode should change the ESKA core only when an executable example demonstrates that a current concept is too broad, too narrow, or missing—not because a technology-specific taxonomy appears attractive in advance.
