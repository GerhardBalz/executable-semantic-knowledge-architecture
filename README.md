# Executable Semantic Knowledge Architecture (ESKA)

**Reference architecture and executable examples for formally represented, machine-interpretable, provenance-aware, verifiable, and agent-accessible knowledge.**

## Definition

**Executable Semantic Knowledge Architecture (ESKA)** is an architectural approach in which knowledge is explicitly and formally represented with machine-interpretable semantics, connected to executable mechanisms where appropriate, traceable to its provenance, verifiable, and directly discoverable and accessible by software agents.

A central principle is:

> **Execution must not sever semantics.**

Executable behavior should remain machine-traceable to the semantic knowledge that gives it meaning.

```text
Semantic Knowledge
        │ operationalized as
        ▼
Executable Semantic Knowledge
        │ organized and governed by
        ▼
Executable Semantic Knowledge Architecture
```

Different semantic artifacts have different operational interpretations:

```text
Ontology        → reason
Knowledge graph → query
Constraint      → validate
Rule            → evaluate
Decision        → decide
Calculation     → calculate
Mapping         → transform
Workflow        → execute
Capability      → invoke
```

## Core principles

- **Explicit formal semantics** — meaning is represented explicitly rather than existing only in prose, prompts, or source code.
- **Machine interpretability** — machines can identify concepts, relationships, constraints, inputs, outputs, and context.
- **Executable where appropriate** — knowledge participates in computation according to its semantic type.
- **Semantic continuity** — execution remains connected to the semantic model and artifacts that give it meaning.
- **Provenance awareness** — sources, versions, transformations, assertions, deployments, and executions remain traceable.
- **Verifiability** — semantics and executions are checked by mechanisms appropriate to their type.
- **Agent accessibility** — deterministic or intelligent consumers can discover and invoke machine-described capabilities rather than reconstructing meaning from prompts.
- **Explicit semantic-source ownership** — execution architecture should not become the accidental owner of domain semantics.

## Provisional ESKA core

The current cross-mode core lives in [`model/eska-core.ttl`](model/eska-core.ttl):

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
```

Supporting concepts include `Capability` and the semantic contract properties `subject`, `inputType`, `outputType`, `producesRelation`, `usesSemanticModel`, `usesExecutableArtifact`, and `requiresCondition`.

```text
Capability = Ability + Boundary + Outcome
```

ESKA reuses PROV-O rather than defining a parallel provenance model:

- `Execution` specializes `prov:Activity`;
- `Verification` specializes `prov:Activity`;
- `Result` specializes `prov:Entity`.

The core remains deliberately small. Seven materially different execution modes have been used as falsification tests, and none required a change to `model/eska-core.ttl`.

## Architectural extensions

Operational exposure and runtime location are optional layers, so they remain outside core.

### Knowledge Service — `eska-service.ttl` 0.4-provisional

A **Knowledge Service** exposes one or more Semantic Capabilities operationally.

The generalized structure is:

```text
KnowledgeService
    ├── exposesCapability → SemanticCapability
    └── hasOperation      → ServiceOperation
                                ↓ realizesCapability
                           SemanticCapability
```

Semantic meaning stays on the Capability:

```text
SemanticCapability
    ├── inputType
    ├── outputType
    ├── producesRelation
    └── requiresCondition
```

Concrete access details are separate:

```text
ServiceOperation
    ↓ hasAccessBinding
HTTPAccessBinding
    ├── httpMethod
    ├── path                  contract-relative
    ├── mediaType
    └── representation fields
```

One executable `PizzaKnowledgeService` specimen exposes both Classification and Validation without duplicating Capability semantics on its operations.

See [Knowledge Service Generalization](docs/knowledge-service-generalization.md).

### Knowledge Agent — `eska-agent.ttl` 0.3-provisional

A **Knowledge Agent** uses machine-interpretable contracts to discover, invoke, and interpret semantic capabilities.

The generalized deterministic reference Agent targets both Classification and Validation:

```text
PizzaGeneralizedKnowledgeAgent
    ├── targets PizzaClassificationCapability
    └── targets PizzaValidationCapability
```

Discovery and invocation are generic; semantically typed request/result handling is selected through an explicit adapter contract:

```text
KnowledgeAgent
    ↓ usesInvocationAdapter
SemanticInvocationAdapter
    ├── supportsInputType
    ├── supportsOutputType
    └── supportsRelation
```

The first two adapters demonstrate genuinely different representations:

```text
IRIListInvocationAdapter
    owl:Class → rdfs:subClassOf → owl:Class IRIs

SHACLReportInvocationAdapter
    PizzaDataGraph → sh:conforms → sh:ValidationReport RDF
```

The baseline remains deterministic and non-LLM. Agent accessibility is therefore an architectural property of explicit contracts, not a dependency on prompt engineering.

See [Knowledge Agent Generalization](docs/knowledge-agent-generalization.md).

### Deployment — `eska-deployment.ttl` 0.1-provisional

Runtime location is modeled separately from stable Service meaning:

```text
KnowledgeService
    ↑ deploysService
ServiceDeployment
    ├── inEnvironment → DeploymentEnvironment
    └── hasDeploymentBinding
            ↓
      HTTPDeploymentBinding
            └── baseURL
```

A concrete endpoint is formed only at invocation time:

```text
HTTPDeploymentBinding.baseURL
        +
HTTPAccessBinding.path
        ↓
concrete runtime endpoint
```

The generalized Agent performs semantic discovery first, then resolves a deployment for the discovered Service and selected environment.

Blue/green executable evidence proves:

```text
blue.discovery == green.discovery
blue.adapter   == green.adapter

blue.deployment != green.deployment
blue.endpoint   != green.endpoint

semantic result remains equivalent
```

Invocation provenance records both **what** was invoked and **where** it was invoked.

See [Deployment Binding](docs/deployment-binding.md).

## Seven executable-semantic modes

The Pizza reference currently exercises:

```text
Ontology    → reason
Constraint  → validate
Rule        → evaluate
Decision    → decide
Calculation → calculate
Mapping     → transform
Workflow    → execute
```

The generic Capability verifier covers **seven Capabilities**. The generic runtime verifier covers **sixteen concrete Executions**:

```text
1 OWL reasoning execution
2 SHACL validation executions
1 SPARQL rule execution
3 DMN decision executions
3 OpenMath calculation executions
1 semantic mapping execution
2 overall Workflow executions
3 actually executed Workflow child steps
```

### Mapping refinement below core

Mapping requires source, mapping, and target semantic-model roles. The example therefore defines mode-local subproperties of `eska:usesSemanticModel` and uses qualified PROV-O roles at runtime.

> **Generic core relationships can be refined by mode-specific terms when an executable semantic contract requires additional role precision.**

### Workflow composition below core

Workflow composes existing Capabilities conditionally while retaining ordinary core `Execution` instances:

```text
Workflow Execution
    │ dcterms:hasPart
    ├── Validation Execution
    │       ↓ sh:conforms
    └── Mapping Execution       conforming path only
            ↑ prov:wasInformedBy
       Validation Execution
```

Composition uses `dcterms:hasPart` / `isPartOf`, `prov:wasInformedBy`, and `prov:wasDerivedFrom`; Workflow-local operation bindings connect BPMN operation identifiers to established Semantic Capabilities.

No `WorkflowExecution`, `StepExecution`, or generic `ExecutionMode` taxonomy was needed in core.

See [Execution Mode Comparison](docs/execution-mode-comparison.md).

## Layered operational architecture

The executable evidence now supports a clear separation of concerns:

```text
SemanticCapability
    what the ability means
        ↓
KnowledgeService / ServiceOperation
    stable operational exposure
        ↓
HTTPAccessBinding
    method + relative path + representation mapping
        ↓
SemanticInvocationAdapter
    typed request/result representation and interpretation

separate runtime concern:

ServiceDeployment
    environment + concrete runtime binding
        ↓
HTTPDeploymentBinding.baseURL
```

At invocation time:

```text
Capability semantics
        +
Service / Access contract
        +
Invocation Adapter
        +
Deployment Binding
        ↓
Execution → Result → Verification
        ↓
PROV-O lineage
```

## Pizza as the reference domain

The companion repository [GerhardBalz/pizza-ontology](https://github.com/GerhardBalz/pizza-ontology) owns the Pizza semantic artifacts used by ESKA.

The current binding in [`examples/pizza/pizza-domain-source.json`](examples/pizza/pizza-domain-source.json) pins:

```text
GerhardBalz/pizza-ontology
@715f0460a43abacb5258eedd3d722da219a25a43
```

The Pizza repository publishes **twenty-three source-owned semantic distributions** covering OWL reasoning, SHACL validation, SPARQL rules, DMN decisions, OpenMath calculation, semantic mapping, and BPMN workflow execution.

ESKA materializes those artifacts only at runtime. CI fails if ESKA reintroduces source copies.

```text
pizza-ontology
    owns domain semantics
        ↓ immutable commit + artifacts/manifest.ttl
ESKA
    owns execution architecture
        ↓
Capability / Execution / Result / Verification
        ↓ optional exposure
Service / Agent / Deployment
```

> **Execution must not sever semantics — and execution architecture should not become the accidental owner of domain semantics.**

See [Pizza executable reference](examples/pizza/README.md).

## Current evidence

The repository now demonstrates:

- seven executable-semantic modes over one unchanged provisional core;
- sixteen verified core Executions, including composite Workflow child steps;
- cross-repository immutable semantic-source consumption;
- a generalized multi-capability Knowledge Service contract;
- one generalized deterministic Knowledge Agent across Classification and Validation;
- semantic invocation adapters selected from Capability input/output/relation contracts;
- blue/green Service deployments resolved separately from semantic discovery;
- execution, result, verification, source, adapter, and deployment provenance using ESKA + PROV-O.

The architecture intentionally does **not** claim that Service, Agent, Deployment, mode-specific role refinements, or technology-specific execution concepts belong in core.

## Roadmap

Completed foundations:

- [x] ESKA terminology and provisional core.
- [x] Pizza OWL reasoning and bounded Semantic Capability.
- [x] SHACL Validation as a second mode.
- [x] SPARQL Rule → evaluate.
- [x] DMN Decision → decide.
- [x] OpenMath Calculation → calculate.
- [x] Mapping → transform with source/mapping/target role refinement.
- [x] BPMN Workflow → execute with composite Execution evidence.
- [x] Commit-pinned Pizza semantic-source ownership boundary.
- [x] Validation Knowledge Service and deterministic Agent path.
- [x] Generalized Knowledge Service semantics across Classification + Validation.
- [x] Generalized deterministic Knowledge Agent with semantic invocation adapters.
- [x] Deployment binding separated from semantic Service contracts with blue/green evidence.

Next architectural work:

- [ ] Enrich execution provenance, evidence, and Result lineage only where the existing seven-mode / Service / Agent / Deployment evidence demonstrates a genuine gap.
- [ ] Decide on a permanent ESKA namespace and publication strategy after further stabilization.

The project intentionally does **not** begin as a general software framework, LLM-agent platform, or large meta-ontology.

## Documentation

- [Semantic models](model/README.md)
- [Knowledge Service Generalization](docs/knowledge-service-generalization.md)
- [Knowledge Agent Generalization](docs/knowledge-agent-generalization.md)
- [Deployment Binding](docs/deployment-binding.md)
- [Execution Mode Comparison](docs/execution-mode-comparison.md)
- [Pizza executable reference](examples/pizza/README.md)

## License

New material in this repository is licensed under the [MIT License](LICENSE).

External semantic models and reference artifacts retain their own provenance and licensing. See [`examples/pizza/LICENSE-NOTICE.md`](examples/pizza/LICENSE-NOTICE.md).
