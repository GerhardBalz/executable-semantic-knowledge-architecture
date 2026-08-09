# Executable Semantic Knowledge Architecture (ESKA)

**Reference architecture and executable examples for formally represented, machine-interpretable, provenance-aware, verifiable, and agent-accessible knowledge.**

## Definition

**Executable Semantic Knowledge Architecture (ESKA)** is an architectural approach in which knowledge is explicitly and formally represented with machine-interpretable semantics, connected to executable mechanisms where appropriate, traceable to its provenance, verifiable, and directly discoverable and accessible by software agents.

A central principle is:

> **Execution must not sever semantics.**

Executable behavior should remain machine-traceable to the semantic knowledge that gives it meaning.

## From Semantic Knowledge to ESKA

ESKA distinguishes three abstraction levels:

```text
Semantic Knowledge
        │
        │ operationalized as
        ▼
Executable Semantic Knowledge
        │
        │ organized and governed by
        ▼
Executable Semantic Knowledge Architecture
```

### Semantic Knowledge (SK)

**Semantic Knowledge** is knowledge whose concepts, relationships, constraints, and context are explicitly and formally represented so that their meaning is machine-interpretable.

The essential question is:

> **What does this knowledge mean?**

### Executable Semantic Knowledge (ESK)

**Executable Semantic Knowledge** is Semantic Knowledge that can directly participate in machine reasoning, validation, computation, decision-making, transformation, or action through formally associated executable mechanisms.

The essential question is:

> **What can a machine do with this meaning?**

Executable does not mean that all knowledge must become procedural code. Different semantic artifacts have different operational interpretations:

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

### Executable Semantic Knowledge Architecture (ESKA)

**ESKA** provides the architecture for creating, managing, connecting, executing, verifying, governing, and exposing Semantic Knowledge and Executable Semantic Knowledge as first-class computational assets.

The essential question is:

> **How do we systematically make semantic knowledge operational, trustworthy, and accessible?**

In compact form:

> **SK gives knowledge explicit meaning. ESK makes that meaning operational. ESKA makes operational semantic knowledge a governed architectural capability.**

## Core Principles

ESKA is based on the following principles.

### Explicit formal semantics

Meaning is represented explicitly rather than existing only in documents, prompts, source code, or human interpretation.

### Machine interpretability

Machines can identify the concepts involved, their relationships, constraints, and applicable context rather than merely parse their syntax.

### Executable where appropriate

Knowledge participates directly in computation according to its semantic type: reasoning, querying, validation, calculation, decision-making, transformation, workflow, or action.

### Semantic continuity

Execution remains connected to the semantic model. Inputs, outputs, applicability, effects, rules, and results should be machine-traceable to the concepts that define their meaning.

### Provenance awareness

Knowledge and derived results can be traced to their sources, versions, transformations, assertions, and execution history.

### Verifiability

Knowledge and execution can be checked through appropriate mechanisms such as logical consistency, constraint validation, tests, reproducibility, evidence, and provenance.

### Agent accessibility

Software agents can discover, query, interpret, reason over, verify, and invoke knowledge through explicit computational interfaces instead of reconstructing its meaning from unstructured text alone.

## Core Concepts

The ESKA conceptual model distinguishes knowledge assets, executable artifacts, bounded capabilities, executions and results, operational services, and agents.

### Semantic Model

A **Semantic Model** is a formal representation of the concepts, relationships, classifications, constraints, and axioms used to describe a domain and give its knowledge explicit machine-interpretable meaning.

Ontologies are one form of Semantic Model, but the concept is intentionally broader than any particular representation technology.

### Semantic Knowledge Graph

A **Semantic Knowledge Graph** is a graph of identifiable facts and relationships whose meaning is defined by one or more Semantic Models.

The Semantic Model primarily establishes meaning; the Semantic Knowledge Graph primarily contains assertions about actual or conceptual things.

### Executable Knowledge Artifact

An **Executable Knowledge Artifact** is a machine-executable artifact that embodies or applies knowledge to produce a computational result, decision, transformation, validation, or action.

An executable artifact does not necessarily have explicit formal semantics.

### Executable Semantic Knowledge Artifact

An **Executable Semantic Knowledge Artifact** is an Executable Knowledge Artifact whose inputs, outputs, applicability, effects, and knowledge dependencies are explicitly associated with Semantic Model elements in machine-interpretable form.

This is the artifact-level realization of Executable Semantic Knowledge.

### Capability

A **Capability** is a bounded ability to achieve a defined kind of outcome within a specified scope.

A useful capability is narrow enough to have a coherent outcome while remaining independent of a particular implementation.

A capability boundary may be characterized by its subject, intended outcome, inputs, outputs, applicability, constraints, and responsibility boundary.

### Semantic Capability

A **Semantic Capability** is a Capability whose scope, inputs, outputs, applicability, constraints, and semantics are explicitly represented in machine-interpretable form.

A Semantic Capability is not necessarily a capability *about semantics*. It is a capability that is itself semantically defined.

`Capability`, `SemanticCapability`, their shared semantic contract properties, `SemanticModel`, `ExecutableSemanticKnowledgeArtifact`, and `ApplicabilityCondition` are now part of the provisional cross-mode core in [`model/eska-core.ttl`](model/eska-core.ttl).

### Execution, Result and Verification

An **Execution** is a computational activity that applies executable semantic knowledge under a defined Semantic Capability.

A **Result** is a machine-interpretable entity produced by an Execution, such as an inferred statement or SHACL validation report.

A **Verification** is an activity that checks semantic knowledge, an Execution, or a Result against explicit criteria.

These concepts are also part of the provisional ESKA core because both OWL reasoning and SHACL validation now instantiate the same pattern:

```text
SemanticCapability
        ↓
Execution
        ↓
Result
        ↓
Verification
```

ESKA reuses PROV-O rather than defining a parallel provenance model: `Execution` and `Verification` specialize `prov:Activity`, while `Result` specializes `prov:Entity`.

### Knowledge Service

A **Knowledge Service** is an operational interface through which knowledge can be discovered, queried, reasoned over, validated, evaluated, transformed, explained, or acted upon.

A Capability defines **what ability exists**. A Knowledge Service defines **how that ability is operationally accessible**.

The provisional service extension is captured in [`model/eska-service.ttl`](model/eska-service.ttl). The Pizza classification slice implements and verifies a concrete service without moving classification knowledge into the transport layer.

### Knowledge Agent

A **Knowledge Agent** is a software agent that can use machine-interpretable ESKA contracts to discover, interpret, query, reason over, verify, and invoke semantic capabilities and services.

Agents are consumers and participants in ESKA, not the reason ESKA exists. The architecture remains useful without an LLM.

The provisional agent extension is captured in [`model/eska-agent.ttl`](model/eska-agent.ttl). The Pizza reference agent is deliberately deterministic and non-LLM so that discovery and invocation are demonstrated as architectural properties rather than prompt behavior.

## Provisional ESKA Core

The repository now separates a small cross-mode core from architectural extensions:

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

        extended by
        │
        ├── eska-capability.ttl
        ├── eska-service.ttl
        └── eska-agent.ttl
```

The core contains only concepts that have been demonstrated across more than one executable-semantic mode. Service and Agent semantics remain extensions because they are currently exercised only on the classification path.

The project deliberately continues to use the provisional namespace:

```text
urn:eska:core:
```

The concepts should stabilize before a permanent public namespace and publication policy are chosen.

See:

- [ESKA semantic models](model/README.md)
- [Execution Mode Comparison](docs/execution-mode-comparison.md)

## Conceptual Architecture

```text
                         ┌───────────────────────────────┐
                         │            ESKA               │
                         │ Executable Semantic Knowledge │
                         │          Architecture         │
                         └───────────────┬───────────────┘
                                         │ governs
                                         ▼
                         ┌───────────────────────────────┐
                         │      Semantic Capability      │
                         │  bounded meaning + ability    │
                         └───────┬──────────┬────────────┘
                                 │          │
                              uses          │ exposed through
                                 ▼          ▼
                        Knowledge Assets  Knowledge Service
                                 │          │
             ┌───────────────────┼───────┐  │ discovered / invoked by
             ▼                   ▼       ▼  ▼
       Semantic Model   Semantic Knowledge  Knowledge Agent
                           Graph       │          │
                                       ▼          ▼
                            Executable Semantic  Result / Action
                              Knowledge Artifact

        provenance · evidence · verification · versioning
        policy · authorization · lineage · execution records
        apply across the architecture
```

The architecture should support traversal in both directions:

```text
Concept
  ↓
Knowledge
  ↓
Executable Knowledge
  ↓
Capability
  ↓
Service
  ↓
Agent Invocation
  ↓
Result
```

and:

```text
Result
  ↓ why?
Agent Invocation
  ↓ used?
Service / Capability
  ↓ realized by?
Executable Knowledge
  ↓ defined by?
Semantic Knowledge
  ↓ defined in?
Semantic Model
  ↓ sourced from?
Provenance / Evidence
```

This enables explanation through explicit architecture and lineage rather than generated prose alone.

## Pizza as the Reference Example

ESKA uses the classic Pizza ontology as its initial reference domain because the domain is immediately understandable while still containing non-trivial formal semantics and reasoning behavior.

The companion repository [GerhardBalz/pizza-ontology](https://github.com/GerhardBalz/pizza-ontology) provides the semantic reference project based on the Manchester / Protégé Pizza ontology tradition.

The relationship is intentionally separated:

```text
pizza-ontology
     │
     │ provides the reference semantic domain
     ▼
Semantic Knowledge
     │
     │ operationalized through
     ▼
Executable Semantic Knowledge
     │
     │ organized and exposed through
     ▼
ESKA
```

ESKA should not require changing the Pizza ontology merely to make it executable. Instead, the reference implementation demonstrates how architecture can be built around and through an existing semantic model.

### First vertical slice: Pizza Classification

The executable example is implemented in [`examples/pizza`](examples/pizza) and answers a deliberately small question:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that result remain semantically connected as it is bounded, exposed, discovered, and invoked?**

The first end-to-end slice spans:

```text
Pizza Semantic Model
        ↓ selected semantic knowledge
Coherent Reasoning Slice
        ↓ execute OWL semantics with HermiT
Inferred Classification
        ↓ verify / explain / trace
Executable Semantic Knowledge
        ↓ bounded and machine-described as
PizzaClassificationCapability
        ↓ exposed through
PizzaClassificationService
        ↓ discovered from machine-readable contracts
PizzaKnowledgeAgent
        ↓ invokes service
Semantic Result
```

The Knowledge Agent knows the Capability it wants but does not hard-code the service, HTTP path, result relation, representation field names, or `SpicyPizza` as the answer. It discovers the service operation from the merged ESKA architecture model and combines that contract with a separate runtime deployment location.

This demonstrates a core ESKA claim:

> **Agent accessibility can be a property of the architecture rather than a property of a prompt.**

### Second execution mode: Pizza Validation

The second executable example is implemented in [`examples/pizza/validation`](examples/pizza/validation) and asks a different question:

> **Does a concrete Pizza RDF data graph conform to an explicit semantic validation contract?**

It introduces `PizzaValidationCapability` and a SHACL shapes graph with explicit structural constraints. A conforming Pizza graph produces `sh:conforms true`; a deliberately invalid Pizza with two `hasBase` values produces `sh:conforms false` and the expected `sh:MaxCountConstraintComponent` validation result.

This establishes two distinct forms of Executable Semantic Knowledge:

```text
OWL ontology
    ↓ reason
inferred axioms

SHACL shapes graph
    ↓ validate
SHACL ValidationReport
```

The distinction is intentional. ESKA does not define one universal execution mechanism: a semantic artifact is executable according to the operational semantics appropriate to its type.

The two modes also provide the evidence for the current ESKA core. CI verifies both the shared Semantic Capability contract and the shared runtime `Execution → Result → Verification` pattern.

The purpose of both examples is not to build a sophisticated pizza application. It is to make the semantic-to-execution architecture visible in a domain that is easy to understand.

## Initial Scope

The project evolves incrementally.

- [x] Establish the ESKA terminology and conceptual model.
- [x] Establish the distinction between Semantic Knowledge, Executable Semantic Knowledge, and ESKA.
- [x] Implement the first Pizza semantic reasoning slice.
- [x] Verify the inferred classification and add explanation and execution provenance.
- [x] Define and verify the first bounded Semantic Capability around executable semantic knowledge.
- [x] Expose the first Semantic Capability through a machine-described and executable Knowledge Service.
- [x] Demonstrate machine-described discovery and invocation by a deterministic Knowledge Agent.
- [x] Add semantic validation as a second executable-semantic mode using SHACL.
- [x] Generalize the first cross-mode ESKA core from concepts stable across reasoning and validation.
- [ ] Test the provisional core against additional execution modes before promoting further concepts.
- [ ] Add richer provenance and deployment-binding concepts where concrete use cases require them.
- [ ] Decide whether and how the validation Capability should be exposed through a Knowledge Service and Agent.
- [ ] Add additional semantic capabilities and alternative service or agent implementations.

The project intentionally does **not** begin as a general software framework, agent platform, or large meta-ontology.

## Status

The Pizza reference project now tests ESKA against two different executable-semantic modes and uses those modes to define and verify a small provisional ESKA core.

The classification path provides the first complete ESKA chain from formal semantic knowledge to agent-accessible operational knowledge:

```text
Semantic Model
→ Semantic Knowledge
→ Executable Semantic Knowledge
→ Semantic Capability
→ Knowledge Service
→ Knowledge Agent
→ Semantic Result
```

The validation path separately demonstrates that the same architectural ideas apply when execution means constraint evaluation rather than inference:

```text
SHACL Semantic Model
→ Executable Validation Artifact
→ PizzaValidationCapability
→ Execution
→ SHACL ValidationReport
→ Verification + Provenance
```

Across both paths, CI now verifies the shared core abstractions at two levels:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability

and

Execution
→ Result
→ Verification
```

The project remains intentionally small and provisional. The next architectural test should come from another genuinely different execution mode rather than expanding the ontology by speculation.

## License

New material in this repository is licensed under the [MIT License](LICENSE).

External semantic models and reference artifacts used by examples retain their own provenance and licensing and should not be assumed to inherit this repository's license.
