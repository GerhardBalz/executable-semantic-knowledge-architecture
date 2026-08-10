# Execution Mode Comparison

Executable Semantic Knowledge Architecture (ESKA) does not define a single universal execution mechanism. Semantic artifacts are executable according to the operational semantics appropriate to their type.

The Pizza reference now demonstrates four genuinely different execution modes:

| Concern | OWL reasoning | SHACL validation | Rule evaluation | Decision evaluation |
| --- | --- | --- | --- | --- |
| Semantic model | OWL class axioms | SHACL shapes graph | SPARQL 1.1 `CONSTRUCT` rule | DMN 1.5 `UNIQUE` decision table |
| Semantic input | Ontology / class knowledge | RDF data graph | Explicit RDF rule-input graph | Explicit decision-input context |
| Executable artifact | HermiT via ROBOT | pySHACL | RDFLib SPARQL evaluation | Canonical DMN subset evaluator |
| Operation | reason | validate | evaluate | decide |
| Primary result | inferred axiom | `sh:ValidationReport` | derived RDF statement | selected semantic outcome |
| Result relation | `rdfs:subClassOf` | `sh:conforms` | `rule:requiresVegetarianWarning` | `decision:dietarySuitability` |
| Bounded capability | `PizzaClassificationCapability` | `PizzaValidationCapability` | `PizzaRuleEvaluationCapability` | `PizzaDietarySuitabilityCapability` |
| Applicability boundary | coherent OWL model | parseable RDF using SHACL vocabulary | explicit RDF assertions; no implicit OWL entailment | explicit boolean decision inputs; no inferred input values |
| Verification | expected inference query | expected conformance / violations | expected derived statement + control | expected UNIQUE outcome for every decision context |
| Provenance | PROV-O reasoning activity | PROV-O validation activity | PROV-O rule-evaluation activity | PROV-O decision activities |

## What is stable across all four modes?

The rule and decision modes were introduced as falsification tests for the provisional ESKA core. Both fit the same abstraction without changing `model/eska-core.ttl`:

```text
SemanticModel
        ↓
ExecutableSemanticKnowledgeArtifact
        ↓
SemanticCapability
        ↓
ApplicabilityCondition
        ↓
Execution
        ↓
Result
        ↓
Verification
        ↓
PROV-O provenance
```

Across OWL reasoning, SHACL validation, SPARQL rule evaluation, and DMN decision evaluation:

- `SemanticModel` identifies the formal semantic artifact that gives the operation meaning;
- `ExecutableSemanticKnowledgeArtifact` identifies the computational realization appropriate to that semantic type;
- `SemanticCapability` bounds subject, input, output, result relation, semantic model, executable artifact, and applicability;
- `ApplicabilityCondition` records preconditions without embedding technology-specific semantics into the core;
- `Execution` represents a concrete computational activity;
- `Result` represents the machine-interpretable output of that activity;
- `Verification` explicitly checks execution and result;
- PROV-O provides execution and derivation lineage without an ESKA-specific provenance hierarchy.

The same generic Capability verifier now checks all four modes. The same generic runtime verifier checks seven concrete executions: one reasoning execution, two validation executions, one rule execution, and three decision executions.

## Falsification result

The fourth mode did **not** require any of the following additions to the ESKA core:

- `Decision` as a core class;
- `DecisionExecution`;
- `DecisionResult`;
- a generic `ExecutionMode` taxonomy;
- DMN-specific properties;
- a second provenance vocabulary;
- promotion of Service or Agent semantics.

The decision semantics remain in the source-owned DMN artifact and its outcome vocabulary. ESKA describes how that model participates in a bounded Capability and concrete executions.

```text
Pizza DMN decision model
        │ source-owned SemanticModel
        ▼
PizzaDietarySuitabilityCapability
        │
        ▼
Execution
        │
        ▼
Semantic outcome Result
        │
        ▼
Verification + PROV-O
```

## What is still not core?

Several concepts remain important but lack sufficient cross-mode evidence:

- `KnowledgeService` and `ServiceOperation` — demonstrated only for classification;
- `KnowledgeAgent` and `DiscoveryArtifact` — demonstrated only on classification;
- HTTP and representation-specific properties;
- deployment binding — supplied separately at runtime;
- a dedicated `ExecutionMode` concept — the four modes remain distinguishable through their native semantic models, artifacts, Capabilities, results, and implementations;
- a dedicated ESKA provenance class — PROV-O remains sufficient.

The core should remain smaller than the complete reference architecture.

## Execution is polymorphic

The executable evidence now covers:

```text
Ontology   → reason
Constraint → validate
Rule       → evaluate
Decision   → decide
```

The mechanisms and result types differ, but formal semantic artifacts participate directly in computation and their results remain machine-traceable to the semantics that give them meaning.

Future examples can continue trying to falsify the same core with modes such as:

```text
Calculation → calculate
Mapping     → transform
Workflow    → execute
```

A future mode should change the ESKA core only when an executable example demonstrates that a current concept is too broad, too narrow, or missing—not because a technology-specific taxonomy looks attractive in advance.
