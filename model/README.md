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

The core contains only concepts demonstrated across different executable-semantic modes in the Pizza reference project. It has now survived four distinct operational semantics:

- OWL reasoning;
- SHACL validation;
- SPARQL rule evaluation;
- DMN decision evaluation.

All four modes use a `SemanticModel`, an `ExecutableSemanticKnowledgeArtifact`, a bounded `SemanticCapability`, an `ApplicabilityCondition`, an `Execution`, a machine-interpretable `Result`, and an explicit `Verification` activity.

Both the rule and decision modes were intentionally used as falsification tests. No changes to `eska-core.ttl` were required to model or generically verify either mode.

`Execution` and `Verification` specialize `prov:Activity`; `Result` specializes `prov:Entity`. ESKA therefore continues to reuse PROV-O rather than inventing a parallel provenance model.

## Extensions

The other model files remain provisional extensions.

### `eska-capability.ttl`

Contains capability-specific helper terms that are useful in examples but are not yet justified as ESKA core semantics, currently `exampleInput` and `exampleOutput`.

### `eska-service.ttl`

Contains Knowledge Service and transport/representation concepts. Service exposure is currently demonstrated on the Pizza classification path but not on validation, rule-evaluation, or decision paths, so these terms remain deliberately outside the core.

### `eska-agent.ttl`

Contains Knowledge Agent and discovery concepts. Agent discovery/invocation is currently demonstrated on the Pizza classification path only.

## Why there is no execution-type taxonomy in core

The third and fourth execution modes do not introduce `Rule`, `Decision`, `RuleExecution`, `DecisionExecution`, or `ExecutionMode` into the core.

Their native semantic artifacts already carry the mode-specific meaning:

```text
SPARQL rule
    a SemanticModel
        ↓
PizzaRuleEvaluationCapability
        ↓
Execution → Result → Verification

DMN decision table
    a SemanticModel
        ↓
PizzaDietarySuitabilityCapability
        ↓
Execution → Result → Verification
```

The execution mechanism is represented separately as an `ExecutableSemanticKnowledgeArtifact`. This keeps technology-specific semantics in their native artifacts until repeated executable evidence justifies a broader ESKA abstraction.

## Dependency representation

The extension ontologies use:

```turtle
dcterms:requires <urn:eska:model:core>
```

rather than `owl:imports` while the project uses provisional `urn:eska:*` identifiers that are intentionally not presented as resolvable public ontology IRIs.

The executable examples explicitly merge the required model artifacts during verification.

## Provisional namespace

All ESKA terms currently use:

```text
urn:eska:core:
```

This is deliberate. The project should stabilize the concepts before choosing a permanent public namespace and publication policy.

See [Execution Mode Comparison](../docs/execution-mode-comparison.md) for the executable evidence used to decide which concepts currently belong in the core.
