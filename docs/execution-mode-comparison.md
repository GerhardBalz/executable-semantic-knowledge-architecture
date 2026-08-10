# Execution Mode Comparison

Executable Semantic Knowledge Architecture (ESKA) does not define one universal execution mechanism. Semantic artifacts are executable according to the operational semantics appropriate to their type.

The Pizza reference now demonstrates five genuinely different execution modes:

| Concern | OWL reasoning | SHACL validation | Rule evaluation | Decision evaluation | Calculation |
| --- | --- | --- | --- | --- | --- |
| Semantic model | OWL class axioms | SHACL shapes graph | SPARQL 1.1 `CONSTRUCT` rule | DMN 1.5 `UNIQUE` decision table | OpenMath formula + Pizza calculation vocabulary |
| Semantic input | ontology / class knowledge | RDF data graph | explicit RDF graph | explicit decision context | positive diameter in centimetres |
| Executable artifact | HermiT via ROBOT | pySHACL | RDFLib SPARQL | canonical DMN subset evaluator | OpenMath arithmetic evaluator |
| Operation | reason | validate | evaluate | decide | calculate |
| Primary result | inferred axiom | `sh:ValidationReport` | derived RDF statement | selected semantic outcome | typed decimal area value |
| Result relation | `rdfs:subClassOf` | `sh:conforms` | `rule:requiresVegetarianWarning` | `decision:dietarySuitability` | `calc:areaSquareCentimetres` |
| Bounded capability | `PizzaClassificationCapability` | `PizzaValidationCapability` | `PizzaRuleEvaluationCapability` | `PizzaDietarySuitabilityCapability` | `PizzaAreaCalculationCapability` |
| Applicability boundary | coherent OWL model | parseable RDF using SHACL vocabulary | explicit RDF assertions | explicit boolean decision inputs | positive finite diameter in centimetres |
| Verification | expected inference | expected conformance / violations | expected statement + control | expected UNIQUE outcome | expected numeric result at six decimals |
| Provenance | PROV-O reasoning activity | PROV-O validation activity | PROV-O rule activity | PROV-O decision activities | PROV-O calculation activities |

## What is stable across all five modes?

Rule, Decision, and Calculation were introduced as deliberate falsification tests. All five modes fit the same abstraction without changing `model/eska-core.ttl`:

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

Across all five modes:

- `SemanticModel` identifies the formal artifact that gives the operation meaning;
- `ExecutableSemanticKnowledgeArtifact` identifies the computational realization appropriate to that semantic type;
- `SemanticCapability` bounds subject, input, output, result relation, semantic model, executable artifact, and applicability;
- `ApplicabilityCondition` records explicit preconditions without embedding technology-specific semantics into core;
- `Execution` represents a concrete computational activity;
- `Result` represents its machine-interpretable output;
- `Verification` checks the execution and result;
- PROV-O provides execution and derivation lineage.

The generic Capability verifier now checks five Capabilities. The generic runtime verifier checks ten concrete executions: one reasoning execution, two validation executions, one rule execution, three decision executions, and three calculation executions.

## Calculation as a new falsification case

The calculation mode adds behavior not present in the first four modes:

```text
OpenMath mathematical expression
        +
Pizza calculation vocabulary
        ↓
PizzaAreaCalculationCapability
        ↓
OpenMath evaluator
        ↓
xsd:decimal area value
        ↓
Verification + PROV-O
```

The formula is source-owned by `pizza-ontology`. ESKA's evaluator implements OpenMath arithmetic semantics but does not contain the Pizza area formula itself.

The computed numeric value is represented as an `xsd:decimal` literal carried by the semantic relation `calc:areaSquareCentimetres`. The Capability output remains a semantically described `PizzaAreaResult`, so the generic `eska:outputType` relation does not need a special datatype-specific interpretation.

## Falsification result

The fifth mode did **not** require any of the following additions to the ESKA core:

- `Calculation` or `Formula` as core classes;
- `CalculationExecution`;
- `CalculationResult`;
- a generic `ExecutionMode` taxonomy;
- OpenMath-specific core properties;
- numeric-specific provenance concepts;
- promotion of Service or Agent semantics.

The mode-specific mathematical meaning stays in OpenMath and the source-owned calculation vocabulary. ESKA describes how those artifacts participate in a bounded Capability and concrete executions.

## What is still not core?

Several concepts remain important but lack sufficient cross-mode evidence:

- `KnowledgeService` and `ServiceOperation` — demonstrated only for classification;
- `KnowledgeAgent` and `DiscoveryArtifact` — demonstrated only for classification;
- HTTP and representation-specific properties;
- deployment binding — supplied separately at runtime;
- a dedicated `ExecutionMode` concept — the five modes remain distinguishable through native semantic models, artifacts, Capabilities, results, and implementations;
- a dedicated ESKA provenance class — PROV-O remains sufficient.

The core should remain smaller than the complete reference architecture.

## Execution is polymorphic

The executable evidence now covers:

```text
Ontology    → reason
Constraint  → validate
Rule        → evaluate
Decision    → decide
Calculation → calculate
```

The mechanisms and result types differ, but formal semantic artifacts participate directly in computation and their results remain machine-traceable to the semantics that give them meaning.

Future examples can continue trying to falsify the same core with modes such as:

```text
Mapping  → transform
Workflow → execute
```

A future mode should change the ESKA core only when an executable example demonstrates that a current concept is too broad, too narrow, or missing—not because a technology-specific taxonomy looks attractive in advance.
