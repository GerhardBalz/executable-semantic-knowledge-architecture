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

The core contains only concepts that have now been demonstrated across at least two different executable-semantic modes in the Pizza reference project:

- OWL reasoning;
- SHACL validation.

Both modes use a `SemanticModel`, an `ExecutableSemanticKnowledgeArtifact`, a bounded `SemanticCapability`, an `Execution`, a machine-interpretable `Result`, and an explicit `Verification` activity.

`Execution` and `Verification` specialize `prov:Activity`; `Result` specializes `prov:Entity`. ESKA therefore reuses PROV-O rather than inventing a parallel provenance model.

## Extensions

The other model files remain provisional extensions.

### `eska-capability.ttl`

Contains capability-specific helper terms that are useful in examples but are not yet justified as ESKA core semantics, currently `exampleInput` and `exampleOutput`.

### `eska-service.ttl`

Contains Knowledge Service and transport/representation concepts. Service exposure is currently demonstrated on the Pizza classification path but not yet on the validation path, so these terms are deliberately not core.

### `eska-agent.ttl`

Contains Knowledge Agent and discovery concepts. Agent discovery/invocation is currently demonstrated on the Pizza classification path only.

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

See [Execution Mode Comparison](../docs/execution-mode-comparison.md) for the evidence used to decide which concepts currently belong in the core.
