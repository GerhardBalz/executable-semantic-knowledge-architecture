# ESKA semantic models

The semantic model is intentionally split between a small **core** and provisional architectural extensions.

```text
eska-core.ttl
    │
    ├── SemanticModel
    ├── ExecutableSemanticKnowledgeArtifact
    ├── Capability / SemanticCapability
    ├── ApplicabilityCondition
    ├── Execution
    ├── Result
    └── Verification

        required by
        │
        ├── eska-capability.ttl
        ├── eska-service.ttl
        └── eska-agent.ttl
```

## `eska-core.ttl`

The core has now survived six distinct operational semantics:

- OWL reasoning;
- SHACL validation;
- SPARQL rule evaluation;
- DMN decision evaluation;
- OpenMath calculation;
- semantic mapping from a Pizza source model to a Menu target model.

All six modes use a `SemanticModel`, an `ExecutableSemanticKnowledgeArtifact`, a bounded `SemanticCapability`, an `ApplicabilityCondition`, an `Execution`, a machine-interpretable `Result`, and an explicit `Verification` activity.

`model/eska-core.ttl` remains unchanged through the six-mode falsification sequence.

`Execution` and `Verification` specialize `prov:Activity`; `Result` specializes `prov:Entity`. ESKA continues to reuse PROV-O rather than inventing a parallel provenance model.

## Architectural extensions

### `eska-capability.ttl`

Contains capability-specific helper terms that are useful in examples but are not yet justified as ESKA core semantics, currently `exampleInput` and `exampleOutput`.

### `eska-service.ttl`

Contains Knowledge Service and transport/representation concepts. Service exposure is currently demonstrated on the Pizza classification path only.

### `eska-agent.ttl`

Contains Knowledge Agent and discovery concepts. Agent discovery/invocation is currently demonstrated on the Pizza classification path only.

Service and Agent therefore remain deliberately outside core.

## Mode-specific semantic refinements

The Mapping example exposed a useful extension pattern without requiring a new shared ontology file.

The generic core property remains:

```text
eska:usesSemanticModel
```

The Mapping Capability needs three more precise roles, so its example model defines:

```text
map:sourceSemanticModel
map:targetSemanticModel
map:mappingSemanticModel
```

with each declared:

```text
rdfs:subPropertyOf eska:usesSemanticModel
```

The same Capability also states the three semantic models through the generic core relation.

This keeps the layering explicit:

```text
cross-mode core
    usesSemanticModel
        ↑
mode-specific refinement
    sourceSemanticModel
    targetSemanticModel
    mappingSemanticModel
```

Only Mapping currently needs that distinction, so promoting these roles into `eska-core.ttl` would violate the evidence-driven rule used by this project. At runtime, PROV-O `prov:hadRole` provides the corresponding role distinction for qualified semantic-model usage.

## Why there is no execution-type taxonomy in core

The executable modes do not require core classes such as `Rule`, `Decision`, `Calculation`, `Mapping`, `Formula`, `Transformation`, or a generic `ExecutionMode`.

Their native semantic artifacts and bounded Capabilities already carry the mode-specific meaning:

```text
SPARQL rule
    ↓ PizzaRuleEvaluationCapability

DMN decision
    ↓ PizzaDietarySuitabilityCapability

OpenMath formula
    ↓ PizzaAreaCalculationCapability

Pizza source model + SPARQL mapping + Menu target model
    ↓ PizzaMenuProjectionCapability
```

Each then participates in the same generic runtime pattern:

```text
Execution → Result → Verification
```

The mapping example also shows that sharing an implementation language does not make two semantic execution modes identical: both Rule and Mapping use SPARQL `CONSTRUCT`, but Rule derives a statement inside the source semantic domain while Mapping transforms into a distinct target semantic model.

## Dependency representation

The extension ontologies use:

```turtle
dcterms:requires <urn:eska:model:core>
```

rather than `owl:imports` while the project uses provisional `urn:eska:*` identifiers that are intentionally not presented as resolvable public ontology IRIs.

The executable examples explicitly merge the required model artifacts during verification.

## Provisional namespace

All ESKA core terms currently use:

```text
urn:eska:core:
```

This is deliberate. The project should stabilize the concepts before choosing a permanent public namespace and publication policy.

See [Execution Mode Comparison](../docs/execution-mode-comparison.md) for the executable evidence used to decide which concepts currently belong in core.
