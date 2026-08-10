# Execution Mode Comparison

Executable Semantic Knowledge Architecture (ESKA) does not define one universal execution mechanism. Semantic artifacts are executable according to the operational semantics appropriate to their type.

The Pizza reference now demonstrates six execution modes:

| Concern | Semantic model | Operation | Primary result | Capability |
| --- | --- | --- | --- | --- |
| OWL reasoning | OWL class axioms | reason | inferred axiom | `PizzaClassificationCapability` |
| SHACL validation | SHACL shapes graph | validate | validation report | `PizzaValidationCapability` |
| Rule evaluation | SPARQL `CONSTRUCT` rule | evaluate | derived RDF statement | `PizzaRuleEvaluationCapability` |
| Decision evaluation | DMN 1.5 decision table | decide | semantic outcome | `PizzaDietarySuitabilityCapability` |
| Calculation | OpenMath formula + calculation vocabulary | calculate | typed decimal value | `PizzaAreaCalculationCapability` |
| Semantic mapping | Pizza source model + SPARQL mapping + Menu target model | transform | target RDF graph | `PizzaMenuProjectionCapability` |

## Shared provisional core

All six modes fit the same unchanged cross-mode abstraction:

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

The generic Capability verifier checks six Capabilities. The generic runtime verifier checks eleven concrete executions:

```text
1 reasoning
2 validation
1 rule
3 decision
3 calculation
1 mapping
```

## Mapping as a stronger falsification case

Mapping differs from the earlier modes because one operation must distinguish three semantic-model roles:

```text
source semantic model
        ↓
mapping semantic model
        ↓
target semantic model
```

The canonical example transforms Pizza RDF into a distinct Menu projection vocabulary:

```text
Pizza RDF
    pizza:Pizza
    rdfs:label
    pizza:hasTopping
        ↓ SPARQL CONSTRUCT mapping
Menu RDF
    menu:MenuItem
    menu:displayName
    menu:ingredientName
```

The mapping reuses SPARQL `CONSTRUCT` operationally, but its semantic contract differs from the Rule mode:

```text
Rule
    source model
        ↓ derive
    additional source-domain statement

Mapping
    source model
        ↓ mapping model
    target model
        ↓
    transformed graph
```

This is evidence that an ESKA execution mode should not be inferred solely from implementation technology.

## Semantic-model role result

The Mapping Capability needs machine-readable source, target, and mapping roles. The example therefore defines mapping-local properties:

```text
map:sourceSemanticModel
map:targetSemanticModel
map:mappingSemanticModel
```

Each is declared as:

```text
rdfs:subPropertyOf eska:usesSemanticModel
```

The Capability also explicitly states all three models through the generic core relation `eska:usesSemanticModel`.

This gives two layers:

```text
ESKA core
    eska:usesSemanticModel
        generic cross-mode relationship

Mapping-specific layer
    sourceSemanticModel
    targetSemanticModel
    mappingSemanticModel
        role-specific refinement
```

At runtime the same roles are recorded through qualified PROV-O usage using `prov:hadRole`.

The result is significant: **Mapping exposed a real need for role specificity, but not a need to change the generic core.** Only one execution mode currently needs these three roles, so promoting them into `eska-core.ttl` would still be premature.

## Falsification result

The sixth mode did **not** require:

- `Mapping` or `Transformation` as core classes;
- `MappingExecution` or `MappingResult`;
- a generic `ExecutionMode` taxonomy;
- source/target semantic-model properties in core;
- SPARQL-specific core properties;
- a new provenance hierarchy;
- promotion of Service or Agent semantics.

It did establish an extension pattern:

> **Cross-mode core relationships may be refined by mode-specific subproperties where an executable semantic contract requires additional roles.**

That pattern preserves a small core without discarding semantic precision.

## What remains outside core?

- `KnowledgeService` and `ServiceOperation` — demonstrated only for classification;
- `KnowledgeAgent` and `DiscoveryArtifact` — demonstrated only for classification;
- HTTP and representation-specific properties;
- deployment binding — supplied separately at runtime;
- Mapping role properties — currently justified only by Mapping;
- a dedicated `ExecutionMode` taxonomy — the six modes remain distinguishable through native semantic artifacts, Capabilities, results, and execution contracts;
- a dedicated ESKA provenance class — PROV-O remains sufficient.

## Execution is polymorphic

```text
Ontology    → reason
Constraint  → validate
Rule        → evaluate
Decision    → decide
Calculation → calculate
Mapping     → transform
```

The next strong falsification candidate is **Workflow → execute**, because workflow semantics may introduce sequencing, intermediate states, and multiple linked executions rather than one bounded computation producing one result.
