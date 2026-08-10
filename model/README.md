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

The core has now survived seven distinct operational semantics:

- OWL reasoning;
- SHACL validation;
- SPARQL rule evaluation;
- DMN decision evaluation;
- OpenMath calculation;
- semantic mapping from a Pizza source model to a Menu target model;
- BPMN workflow execution composing validation and mapping.

All seven modes use a `SemanticModel`, an `ExecutableSemanticKnowledgeArtifact`, a bounded `SemanticCapability`, an `ApplicabilityCondition`, an `Execution`, a machine-interpretable `Result`, and an explicit `Verification` activity.

`model/eska-core.ttl` remains unchanged through this falsification sequence.

`Execution` and `Verification` specialize `prov:Activity`; `Result` specializes `prov:Entity`. ESKA continues to reuse PROV-O rather than inventing a parallel provenance model.

## Architectural extensions

### `eska-capability.ttl`

Contains capability-specific helper terms useful in examples but not yet justified as core semantics, currently `exampleInput` and `exampleOutput`.

### `eska-service.ttl`

Contains the provisional Knowledge Service model. Classification and validation provide the first cross-mode evidence for separating stable Service semantics from concrete access bindings.

The stable semantic structure is now:

```text
KnowledgeService
    ├── exposesCapability → SemanticCapability
    └── hasOperation      → ServiceOperation
                                ↓ realizesCapability
                           SemanticCapability
```

Semantic input/output/relation/applicability remain on the Capability:

```text
SemanticCapability
    inputType
    outputType
    producesRelation
    requiresCondition
```

A `ServiceOperation` no longer duplicates those assertions. This removes the hidden single-capability assumption from the earlier model and makes it possible for one Knowledge Service to expose multiple Capabilities unambiguously.

Concrete access details are separated through:

```text
ServiceOperation
    ↓ hasAccessBinding
AccessBinding
    ↓
HTTPAccessBinding
```

The current HTTP bindings carry method, contract-relative path, media-type envelope, and representation-field mappings. Runtime scheme/host/port remain separate deployment bindings.

The two working modes still differ in result representation:

```text
classification → list of owl:Class IRIs
validation     → JSON-LD sh:ValidationReport graph
```

`resultField` identifies where a semantic result is carried in an access representation; it does not prescribe one universal result shape. See [Knowledge Service Generalization](../docs/knowledge-service-generalization.md).

### `eska-agent.ttl`

Contains Knowledge Agent and discovery concepts. Deterministic Agent discovery/invocation is now demonstrated for both classification and validation:

```text
PizzaKnowledgeAgent
    targets PizzaClassificationCapability

PizzaValidationAgent
    targets PizzaValidationCapability
```

Both discover a Service operation from machine-readable ESKA contracts and combine that semantic contract with a runtime deployment binding.

The Agent vocabulary itself required no change, but the executable Agent implementations interpret results according to the discovered semantic output contract. Classification interprets `owl:Class` result IRIs; validation parses and checks a `sh:ValidationReport` RDF graph. This is evidence against embedding one result-shape assumption into the generic Agent model.

Service and Agent remain outside core because operational exposure is still an optional layer and only two of the seven execution modes currently demonstrate it.

## Mode-specific semantic refinements

### Mapping semantic-model roles

The generic core property remains:

```text
eska:usesSemanticModel
```

Mapping refines that relationship with example-local subproperties:

```text
map:sourceSemanticModel
map:mappingSemanticModel
map:targetSemanticModel
```

Only Mapping currently needs those roles, so they remain outside core. Qualified PROV-O usage provides the corresponding runtime role distinction.

### Workflow operation binding

Workflow creates a different adapter need. Source BPMN tasks identify source-domain semantic operation IRIs; ESKA must connect them to already established Semantic Capabilities.

The Workflow example therefore defines local binding terms:

```text
wf:WorkflowOperationBinding
wf:sourceOperation
wf:boundCapability
```

used to connect:

```text
pizzaWf:ValidatePizzaData
    → val:PizzaValidationCapability

pizzaWf:TransformPizzaToMenu
    → map:PizzaMenuProjectionCapability
```

Only Workflow currently requires this source-operation adapter, so these terms also remain outside core.

## Composite execution without composite core classes

Workflow is the first mode to compose multiple semantic executions conditionally.

The example still uses ordinary core `Execution` instances for both overall workflow runs and child steps:

```text
Workflow Execution
    │ dcterms:hasPart
    ├── Validation Execution
    │       ↓ Result
    └── Mapping Execution       conforming path only
            ↑ prov:wasInformedBy
       Validation Execution
```

The relationship between overall and child activities is represented using established vocabularies:

- `dcterms:hasPart` / `dcterms:isPartOf`;
- `prov:wasInformedBy`;
- `prov:wasDerivedFrom` for Result lineage.

This means the first composite execution case does not justify `WorkflowExecution`, `StepExecution`, or `CompositeExecution` in the ESKA core.

## Why there is no execution-type taxonomy in core

The executable modes do not require core classes such as `Rule`, `Decision`, `Calculation`, `Mapping`, `Workflow`, `Formula`, `Transformation`, or a generic `ExecutionMode`.

Their native semantic artifacts and bounded Capabilities carry the mode-specific meaning:

```text
SPARQL rule
    ↓ PizzaRuleEvaluationCapability

DMN decision
    ↓ PizzaDietarySuitabilityCapability

OpenMath formula
    ↓ PizzaAreaCalculationCapability

Pizza source model + SPARQL mapping + Menu target model
    ↓ PizzaMenuProjectionCapability

BPMN process + workflow vocabulary
    ↓ PizzaMenuPublicationWorkflowCapability
```

Each then participates in the same generic runtime pattern:

```text
Execution → Result → Verification
```

Workflow further demonstrates that one execution can contain other ordinary executions without requiring a second runtime ontology hierarchy.

## Dependency representation

The extension ontologies use:

```turtle
dcterms:requires <urn:eska:model:core>
```

rather than `owl:imports` while the project uses provisional `urn:eska:*` identifiers that are intentionally not presented as resolvable public ontology IRIs.

The executable examples explicitly merge required model artifacts during verification.

## Provisional namespace

All ESKA core terms currently use:

```text
urn:eska:core:
```

This is deliberate. The project should stabilize the concepts before choosing a permanent public namespace and publication policy.

See [Execution Mode Comparison](../docs/execution-mode-comparison.md) for the executable evidence used to decide which concepts currently belong in core.
