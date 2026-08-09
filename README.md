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

The initial ESKA conceptual model distinguishes knowledge assets, bounded capabilities, operational services, and agents.

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

The first provisional machine-readable subset of this concept is captured in [`model/eska-capability.ttl`](model/eska-capability.ttl). It intentionally formalizes only the terms required by the Pizza Capability example rather than claiming to be a complete ESKA ontology.

### Knowledge Service

A **Knowledge Service** is an operational interface through which knowledge can be discovered, queried, reasoned over, validated, evaluated, transformed, explained, or acted upon.

A Capability defines **what ability exists**. A Knowledge Service defines **how that ability is operationally accessible**.

The first provisional machine-readable subset of this concept is captured in [`model/eska-service.ttl`](model/eska-service.ttl). The Pizza reference slice implements and verifies a concrete service without moving classification knowledge into the transport layer.

### Knowledge Agent

A **Knowledge Agent** is a software agent that can discover, interpret, query, reason over, invoke, and potentially extend Semantic Knowledge and Executable Semantic Knowledge through ESKA capabilities and services.

Agents are consumers and participants in ESKA, not the reason ESKA exists. The architecture remains useful without an LLM.

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
             ┌───────────────────┼───────┐  │ invoked by
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
Execution
  ↓
Result
```

and:

```text
Result
  ↓ why?
Execution
  ↓ used?
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

The first executable example is implemented in [`examples/pizza`](examples/pizza) and answers a deliberately small question:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that inference be verified, explained, traced, and exposed without duplicating the semantic logic?**

The slice now continues from semantic execution through a bounded Semantic Capability into an operational Knowledge Service:

```text
Pizza Semantic Model
        ↓ selected semantic knowledge
Coherent Reasoning Slice
        ↓ execute OWL semantics with HermiT
Inferred Classification
        ↓ verify expected semantic result
Verified Result
        ↓ trace through
Explanation + PROV-O Provenance
        ↓ bounded and machine-described as
PizzaClassificationCapability
        ↓ exposed through
PizzaClassificationService
        ↓ HTTP
POST /classify
```

This demonstrates **Executable Semantic Knowledge**, a machine-described **Semantic Capability**, and a machine-described and executable **Knowledge Service**. The service remains deliberately thin: it exposes classifications from the reasoned semantic artifact rather than implementing a second Pizza classification rule.

The next architectural layer is Knowledge Agent discovery and invocation.

The purpose is not to build a sophisticated pizza application. It is to demonstrate the semantic-to-execution chain with the smallest domain that makes the architecture visible.

## Initial Scope

The project evolves incrementally.

- [x] Establish the ESKA terminology and conceptual model.
- [x] Establish the distinction between Semantic Knowledge, Executable Semantic Knowledge, and ESKA.
- [x] Implement the first Pizza semantic reasoning slice.
- [x] Verify the inferred classification and add explanation and execution provenance.
- [x] Define and verify the first bounded Semantic Capability around executable semantic knowledge.
- [x] Expose the first Semantic Capability through a machine-described and executable Knowledge Service.
- [ ] Add explicit semantic validation examples in addition to inference verification.
- [ ] Generalize stable capability and service terms as the broader ESKA model is tested through additional examples.
- [ ] Demonstrate direct discovery and invocation by a Knowledge Agent.

The project intentionally does **not** begin as a general software framework, agent platform, or large meta-ontology.

## Status

This repository remains at an early reference-architecture stage, but the Pizza reference slice now spans formal semantic knowledge, executable OWL reasoning, verification, explanation, provenance, a bounded Semantic Capability, and an operational Knowledge Service.

The Knowledge Service is verified both as a machine-readable contract and through an end-to-end HTTP test. The next architectural layer is a Knowledge Agent that discovers and invokes the Capability through the Service rather than relying on hard-coded domain behavior.

## License

New material in this repository is licensed under the [MIT License](LICENSE).

External semantic models and reference artifacts used by examples retain their own provenance and licensing and should not be assumed to inherit this repository's license.
