# Executable Semantic Knowledge Architecture (ESKA)

**Reference architecture and executable examples for formally represented, machine-interpretable, provenance-aware, verifiable, and agent-accessible knowledge.**

## Definition

**Executable Semantic Knowledge Architecture (ESKA)** is an architectural approach in which knowledge is explicitly and formally represented with machine-interpretable semantics, connected to executable mechanisms where appropriate, traceable to its provenance, verifiable, and directly discoverable and accessible by software agents.

A central principle is:

> **Execution must not sever semantics.**

Executable behavior should remain machine-traceable to the semantic knowledge that gives it meaning.

For a deeper explanation of this invariant, including failure modes, provenance versus semantic continuity, and the Pizza example, see [Semantic Continuity — Why Execution Must Not Sever Semantics](docs/semantic-continuity.md).

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
- **Verifiability** — semantics, execution, lineage, and publication contracts are checked by executable mechanisms.
- **Agent accessibility** — agents can discover and invoke machine-described capabilities rather than reconstructing meaning from prompts alone.
- **Explicit semantic-source ownership** — execution architecture should not become the accidental owner of domain semantics.

## ESKA core

The cross-mode core lives in [`model/eska-core.ttl`](model/eska-core.ttl), currently published as module version **0.2.0** under the permanent ESKA namespace:

```text
https://w3id.org/eska#
```

Core 0.2.0 aligns the ESKA compatibility class `eska:SemanticModel` with the canonical [`smo:SemanticModel`](https://w3id.org/smo#SemanticModel) using `owl:equivalentClass` and declares a dependency on immutable SMO 0.1.0. The ESKA compatibility IRI remains available; semantic authority for the reusable modeling concept stays with SMO.

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

Seven materially different execution modes have been used as falsification tests, and none required a mode-driven change to `model/eska-core.ttl`.

## Architectural extensions

Operational exposure and runtime location are optional layers, so they remain outside core.

### Knowledge Service — `eska-service.ttl` 0.4.0

A **Knowledge Service** exposes one or more Semantic Capabilities operationally.

```text
KnowledgeService
    ├── exposesCapability → SemanticCapability
    └── hasOperation      → ServiceOperation
                                ↓ realizesCapability
                           SemanticCapability
```

Semantic meaning stays on the Capability. Concrete access details are separate:

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

### Knowledge Agent — `eska-agent.ttl` 0.3.0

The generalized deterministic reference Agent targets Classification and Validation and selects semantically compatible request/result adapters from the discovered Capability contract.

```text
KnowledgeAgent
    ↓ usesInvocationAdapter
SemanticInvocationAdapter
    ├── supportsInputType
    ├── supportsOutputType
    └── supportsRelation
```

The first two adapters demonstrate different semantic representations:

```text
IRIListInvocationAdapter
    owl:Class → rdfs:subClassOf → owl:Class IRIs

SHACLReportInvocationAdapter
    PizzaDataGraph → sh:conforms → sh:ValidationReport RDF
```

The baseline remains deterministic and non-LLM. Agent accessibility is therefore an architectural property of explicit contracts, not a dependency on prompt engineering.

See [Knowledge Agent Generalization](docs/knowledge-agent-generalization.md).

### Deployment — `eska-deployment.ttl` 0.1.0

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

Blue/green executable evidence proves that semantic discovery and adapter selection remain stable while the concrete deployment and endpoint change.

See [Deployment Binding](docs/deployment-binding.md).

## Seven executable-semantic modes

The Pizza reference exercises:

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

Mapping and Workflow exposed real semantic refinements without forcing them into core:

- Mapping refines source/mapping/target semantic-model roles below `eska:usesSemanticModel` and uses qualified PROV-O roles at runtime.
- Workflow composes ordinary `eska:Execution` instances through `dcterms:hasPart`, `prov:wasInformedBy`, and `prov:wasDerivedFrom`, while BPMN-operation→Capability binding remains workflow-local.

See [Execution Mode Comparison](docs/execution-mode-comparison.md).

## Layered operational architecture

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

## Trust and lineage

ESKA deliberately does **not** define a parallel provenance ontology. The executable trust plane combines existing ESKA execution concepts with PROV-O and Dublin Core Terms.

CI verifies two profiles:

```text
Semantic execution lineage
    16 Executions
        ↓
    Result
        ↓ recursive prov:wasDerivedFrom
    immutable pizza-ontology Git artifact

Operational invocation lineage
    5 Agent Executions
        ↓
    Capability + Service + Invocation Adapter
    + ServiceDeployment + Environment + Binding
    + invocation input + architecture/deployment models
        ↓
    Result → Verification
```

Every semantic Result recursively reaches an immutable `pizza-ontology/blob/<commit>/...` source. All five generalized Agent invocation Executions have distinct identities derived from semantic Capability + concrete Service Deployment + invocation input identity.

See [Provenance, Evidence, and Result Lineage](docs/provenance-evidence-lineage.md).

## Namespace, publication, and versioning

The authoritative ESKA term namespace is:

```text
https://w3id.org/eska#
```

The W3ID resolver is active. The provisional `urn:eska:core:` term namespace and `urn:eska:model:*` ontology IRIs are retained only as historical predecessors in the machine-readable migration record; the migration does **not** assert `owl:sameAs`.

The publication contract separates stable term identity, independently versioned ontology modules, and repository releases:

```text
Term
    https://w3id.org/eska#Execution

Module
    https://w3id.org/eska/model/core

Versioned module
    https://w3id.org/eska/model/core/0.2.0

Repository release
    eska-v0.2.0
```

Module versions remain independent of the repository release version. The current governed publication state is `core-0.2.0-w3id-active`: repository release [`eska-v0.2.0`](https://github.com/GerhardBalz/executable-semantic-knowledge-architecture/releases/tag/eska-v0.2.0) is published, the permanent W3ID namespace is active, and the immutable core 0.2.0 W3ID route is active and live-verified. The earlier `eska-v0.1.0` release remains an immutable historical baseline.

`model/publication-contract.json`, `model/namespace-migration.json`, and the publication verifiers govern five independently versioned modules and the stable ESKA term namespace.

See [Namespace, Publication, and Versioning](docs/namespace-publication-versioning.md) for the current publication contract and verification model.

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

- seven executable-semantic modes over one stable cross-mode core architecture;
- sixteen verified semantic Executions, including composite Workflow child steps;
- twenty-three source-owned Pizza semantic distributions consumed from an immutable commit;
- generalized multi-capability Knowledge Service semantics;
- one generalized deterministic Knowledge Agent with semantic invocation adapters;
- blue/green Service deployments resolved separately from semantic discovery;
- five distinct operational Agent invocation lineages;
- immutable source/result lineage through PROV-O without a parallel ESKA provenance ontology;
- an active permanent W3ID namespace and immutable core 0.2.0 version route;
- explicit alignment of ESKA `SemanticModel` compatibility semantics with governed SMO 0.1.0.

The architecture intentionally does **not** claim that Service, Agent, Deployment, mode-specific role refinements, or technology-specific execution concepts belong in core.

## Roadmap

Completed foundations:

- [x] ESKA terminology and cross-mode core.
- [x] Seven executable-semantic modes and sixteen core Executions.
- [x] Commit-pinned Pizza semantic-source ownership boundary.
- [x] Generalized Knowledge Service semantics across Classification + Validation.
- [x] Generalized deterministic Knowledge Agent with semantic invocation adapters.
- [x] Deployment binding separated from semantic Service contracts with blue/green evidence.
- [x] Cross-cutting provenance/evidence/Result lineage verification across 16 semantic + 5 operational Executions.
- [x] Namespace/publication/versioning strategy and machine-readable governance contract.
- [x] W3ID resolver established and permanent ESKA IRIs migrated.
- [x] Immutable `eska-v0.1.0` repository release published and verified.
- [x] Core aligned with governed `smo:SemanticModel` semantics as module version 0.2.0.
- [x] Immutable `eska-v0.2.0` repository release and core 0.2.0 W3ID route published and verified.

There are currently **no open ESKA issues**. New reusable terms or architectural expansion should begin only when independent evidence demonstrates a requirement and established standards are first shown insufficient.

The project intentionally does **not** begin as a general software framework, LLM-agent platform, or large meta-ontology.

## Documentation

- [Semantic models](model/README.md)
- [Semantic Continuity — Why Execution Must Not Sever Semantics](docs/semantic-continuity.md)
- [Related Work and ESKA Positioning](docs/related-work.md)
- [Knowledge Service Generalization](docs/knowledge-service-generalization.md)
- [Knowledge Agent Generalization](docs/knowledge-agent-generalization.md)
- [Deployment Binding](docs/deployment-binding.md)
- [Provenance, Evidence, and Result Lineage](docs/provenance-evidence-lineage.md)
- [Namespace, Publication, and Versioning](docs/namespace-publication-versioning.md)
- [Execution Mode Comparison](docs/execution-mode-comparison.md)
- [Pizza executable reference](examples/pizza/README.md)

## License

New material in this repository is licensed under the [MIT License](LICENSE).

External semantic models and reference artifacts retain their own provenance and licensing. See [`examples/pizza/LICENSE-NOTICE.md`](examples/pizza/LICENSE-NOTICE.md).
