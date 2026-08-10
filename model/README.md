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
        ├── eska-agent.ttl
        └── eska-deployment.ttl
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

The stable semantic structure is:

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

A `ServiceOperation` does not duplicate those assertions. This removes the hidden single-capability assumption from the earlier model and makes it possible for one Knowledge Service to expose multiple Capabilities unambiguously.

Concrete access details are separated through:

```text
ServiceOperation
    ↓ hasAccessBinding
AccessBinding
    ↓
HTTPAccessBinding
```

The HTTP Access Binding carries method, contract-relative path, media-type envelope, and representation-field mappings. It deliberately does not contain a runtime host or port.

The two working modes still differ in result representation:

```text
classification → list of owl:Class IRIs
validation     → JSON-LD sh:ValidationReport graph
```

`resultField` identifies where a semantic result is carried in an access representation; it does not prescribe one universal result shape. See [Knowledge Service Generalization](../docs/knowledge-service-generalization.md).

### `eska-agent.ttl`

Contains deterministic Knowledge Agent, discovery, and semantic invocation-adapter concepts.

The generalized reference Agent targets both Classification and Validation:

```text
PizzaGeneralizedKnowledgeAgent
    ├── targets PizzaClassificationCapability
    └── targets PizzaValidationCapability
```

Generic discovery/invocation is shared, while request/result representation is selected through a semantic adapter contract:

```text
KnowledgeAgent
    ↓ usesInvocationAdapter
SemanticInvocationAdapter
    ├── supportsInputType
    ├── supportsOutputType
    └── supportsRelation
```

The reference provides:

```text
IRIListInvocationAdapter
    owl:Class → rdfs:subClassOf → owl:Class

SHACLReportInvocationAdapter
    PizzaDataGraph → sh:conforms → sh:ValidationReport
```

The Agent combines the discovered semantic contract with a separately resolved runtime deployment. It remains deterministic and non-LLM; prompt or LLM semantics are not required for agent accessibility.

See [Knowledge Agent Generalization](../docs/knowledge-agent-generalization.md).

### `eska-deployment.ttl`

Contains the provisional runtime deployment-binding model. It exists because #13 and #14 made a stable distinction executable:

```text
Service contract
    what/how the operation means

Deployment binding
    where a concrete runtime Service instance is reachable
```

The deployment extension uses:

```text
ServiceDeployment
    ├── deploysService → KnowledgeService
    ├── inEnvironment  → DeploymentEnvironment
    └── hasDeploymentBinding
            ↓
       DeploymentBinding
            ↓
       HTTPDeploymentBinding
            └── baseURL
```

An Agent first discovers the stable Service/Operation/AccessBinding contract, then resolves one `ServiceDeployment` for the discovered Service and selected environment. Only at invocation time are the two access components combined:

```text
HTTPDeploymentBinding.baseURL
        +
HTTPAccessBinding.path
        ↓
concrete runtime endpoint
```

The Pizza regression provides blue and green deployments for both Classification and Validation and verifies that semantic discovery remains identical while base URLs and endpoints change.

`ServiceDeployment` specializes `prov:Entity`, so invocation provenance can identify the exact runtime deployment, environment, and deployment binding without redefining the semantic Result model.

See [Deployment Binding](../docs/deployment-binding.md).

Service, Agent, and Deployment remain outside core because operational exposure and runtime location are optional architectural layers rather than prerequisites for executable semantic knowledge.

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

The extension ontologies use `dcterms:requires` while the project still uses provisional `urn:eska:*` identifiers that are intentionally not presented as resolvable public ontology IRIs.

```text
eska-capability.ttl → requires eska-core.ttl
eska-service.ttl    → requires eska-core.ttl
eska-agent.ttl      → requires eska-core.ttl
eska-deployment.ttl → requires eska-service.ttl
```

The executable examples explicitly merge required model artifacts during verification rather than relying on `owl:imports`.

## Provisional namespace

All ESKA core terms currently use:

```text
urn:eska:core:
```

This is deliberate. The project should stabilize the concepts before choosing a permanent public namespace and publication policy.

See [Execution Mode Comparison](../docs/execution-mode-comparison.md) for the executable evidence used to decide which concepts currently belong in core.
