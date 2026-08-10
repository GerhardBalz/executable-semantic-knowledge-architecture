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

The core contains only concepts demonstrated across different executable-semantic modes in the Pizza reference project. It has now survived three distinct operational semantics:

- OWL reasoning;
- SHACL validation;
- SPARQL rule evaluation.

All three modes use a `SemanticModel`, an `ExecutableSemanticKnowledgeArtifact`, a bounded `SemanticCapability`, an `ApplicabilityCondition`, an `Execution`, a machine-interpretable `Result`, and an explicit `Verification` activity.

The third mode was intentionally used as a falsification test. No changes to `eska-core.ttl` were required to model or verify the rule-evaluation path.

`Execution` and `Verification` specialize `prov:Activity`; `Result` specializes `prov:Entity`. ESKA therefore continues to reuse PROV-O rather than inventing a parallel provenance model.

## Extensions

The other model files remain provisional extensions.

### `eska-capability.ttl`

Contains capability-specific helper terms that are useful in examples but are not yet justified as ESKA core semantics, currently `exampleInput` and `exampleOutput`.

### `eska-service.ttl`

Contains Knowledge Service and transport/representation concepts. Service exposure is currently demonstrated on the Pizza classification path but not on the validation or rule-evaluation paths, so these terms remain deliberately outside the core.

### `eska-agent.ttl`

Contains Knowledge Agent and discovery concepts. Agent discovery/invocation is currently demonstrated on the Pizza classification path only.

## Why there is no rule-specific core model

The third execution mode does not introduce `Rule`, `RuleExecution`, or `ExecutionMode` into the core.

The source-owned SPARQL rule is represented as the `SemanticModel` for `PizzaRuleEvaluationCapability`; RDFLib supplies the execution mechanism; and the existing `Execution → Result → Verification` pattern captures the concrete run.

```text
SPARQL rule
    a SemanticModel
        ↓
SemanticCapability
        ↓
Execution
        ↓
Result
        ↓
Verification
```

This keeps technology-specific semantics in their native artifacts until repeated executable evidence justifies a broader ESKA abstraction.

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
