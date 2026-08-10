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

### Explicit ownership of semantic sources

Execution architecture should not become the accidental owner of domain semantics. Semantic artifacts can be maintained by a domain repository and consumed through immutable, machine-described source bindings while ESKA retains ownership of execution, Capability, Service, Agent, verification, and provenance concerns.

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

`Capability`, `SemanticCapability`, their shared semantic contract properties, `SemanticModel`, `ExecutableSemanticKnowledgeArtifact`, and `ApplicabilityCondition` are part of the provisional cross-mode core in [`model/eska-core.ttl`](model/eska-core.ttl).

### Execution, Result and Verification

An **Execution** is a computational activity that applies executable semantic knowledge under a defined Semantic Capability.

A **Result** is a machine-interpretable entity produced by an Execution, such as an inferred statement, SHACL validation report, or rule-derived RDF statement.

A **Verification** is an activity that checks semantic knowledge, an Execution, or a Result against explicit criteria.

These concepts are part of the provisional ESKA core because OWL reasoning, SHACL validation, and SPARQL rule evaluation all instantiate the same pattern:

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

The repository separates a small cross-mode core from architectural extensions:

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

The core now has executable evidence across three distinct semantic execution modes: OWL reasoning, SHACL validation, and SPARQL rule evaluation. The third mode was used as an explicit falsification test and required no change to `model/eska-core.ttl`.

Service and Agent semantics remain extensions because they are currently exercised only on the classification path. The three-mode test also did not justify introducing `Rule`, `RuleExecution`, or an `ExecutionMode` taxonomy into the core.

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

The companion repository [GerhardBalz/pizza-ontology](https://github.com/GerhardBalz/pizza-ontology) is the **source owner** for the Pizza semantic artifacts used by the executable examples. It preserves Pizza Ontology 2.0, provides the canonical coherent reasoning module, publishes the Pizza SHACL validation profile and example data, publishes the Pizza rule-evaluation artifacts, and exposes those artifacts through a machine-readable manifest.

ESKA consumes that semantic artifact contract from an immutable commit recorded in [`examples/pizza/pizza-domain-source.json`](examples/pizza/pizza-domain-source.json):

```text
pizza-ontology
    │ owns
    ├── Pizza Ontology 2.0 preservation source
    ├── coherent OWL reasoning module
    ├── Pizza SHACL validation profile
    ├── validation example RDF
    ├── SPARQL rule + result vocabulary
    ├── rule evaluation RDF data
    └── artifacts/manifest.ttl
            │
            │ immutable Git commit
            ▼
ESKA
    │ operationalizes
    ├── Semantic Capability
    ├── Execution / Result / Verification
    ├── Knowledge Service
    ├── Knowledge Agent
    └── execution provenance
```

The current source binding pins:

```text
GerhardBalz/pizza-ontology
@bba9fa883f326ebeb395140abd523dc517caf071
```

The Pizza files are materialized only at runtime beneath `examples/pizza/.work/pizza-domain/`. They are not maintained as duplicate ESKA source files. CI explicitly fails if the former local semantic-copy paths—including the rule artifacts—are reintroduced.

This makes the ownership boundary executable:

> **Execution must not sever semantics — and execution architecture should not become the accidental owner of domain semantics.**

### First vertical slice: Pizza Classification

The executable example in [`examples/pizza`](examples/pizza) asks:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that result remain semantically connected as it is bounded, exposed, discovered, and invoked?**

The end-to-end slice spans two repositories while retaining one semantic source of truth:

```text
pizza-ontology
    source-owned coherent reasoning module
        ↓ pinned fetch
ESKA
    HermiT reasoning
        ↓
    Inferred Classification
        ↓ verify / explain / trace
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

> **Does concrete Pizza RDF data conform to the Pizza validation profile published by the domain repository?**

The source-owned SHACL profile defines explicit structural constraints. The source-owned conforming graph produces `sh:conforms true`.

The source-owned non-conforming graph deliberately:

- omits `pizza:hasBase`, producing a `sh:MinCountConstraintComponent` result;
- points `pizza:hasTopping` to a value not typed as `pizza:PizzaTopping`, producing a `sh:ClassConstraintComponent` result.

### Third execution mode: Pizza Rule Evaluation

The third executable example is implemented in [`examples/pizza/rules`](examples/pizza/rules) and asks:

> **Can a source-owned semantic rule be evaluated deterministically and produce a machine-traceable derived result?**

The source-owned SPARQL 1.1 `CONSTRUCT` rule operates on explicit RDF assertions. A Pizza with a topping explicitly typed `pizza:MeatTopping` produces:

```text
requiresVegetarianWarning true
```

while the vegetable-only control produces no warning result.

The three operational semantics are deliberately distinct:

```text
source-owned OWL module
    ↓ reason
inferred axiom

source-owned SHACL profile + RDF data
    ↓ validate
SHACL ValidationReport

source-owned SPARQL rule + RDF data
    ↓ evaluate
rule-derived RDF statement
```

The distinction is intentional. ESKA does not define one universal execution mechanism: a semantic artifact is executable according to the operational semantics appropriate to its type.

The third mode was then inserted into the same generic core verifiers as reasoning and validation. The result was a successful falsification pass: `model/eska-core.ttl` required no rule-specific change.

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
- [x] Separate Pizza domain-artifact ownership from ESKA execution architecture and consume the domain contract through an immutable source binding.
- [x] Add SPARQL rule evaluation as a third executable-semantic mode.
- [x] Re-test the provisional core generically across reasoning, validation, and rule evaluation without changing the core model.
- [ ] Continue falsifying the provisional core with another genuinely different execution mode before promoting further concepts.
- [ ] Add richer provenance and deployment-binding concepts where concrete use cases require them.
- [ ] Decide whether and how the validation Capability should be exposed through a Knowledge Service and Agent.
- [ ] Add additional semantic capabilities and alternative service or agent implementations.

The project intentionally does **not** begin as a general software framework, agent platform, or large meta-ontology.

## Status

The Pizza reference project now tests ESKA against three different executable-semantic modes, a deterministic Knowledge Agent path, and an explicit cross-repository semantic ownership boundary.

```text
Ontology   → reason
Constraint → validate
Rule       → evaluate
```

The classification path provides the first complete ESKA chain from externally owned formal semantic knowledge to agent-accessible operational knowledge:

```text
Source-owned Semantic Model
→ Executable Semantic Knowledge
→ Semantic Capability
→ Knowledge Service
→ Knowledge Agent
→ Semantic Result
```

The validation and rule-evaluation paths separately demonstrate that the core does not depend on classification semantics or service exposure:

```text
Source-owned SHACL Semantic Model
→ Executable Validation Artifact
→ PizzaValidationCapability
→ Execution
→ SHACL ValidationReport
→ Verification + Provenance

Source-owned SPARQL Rule Model
→ Executable Rule Evaluation Artifact
→ PizzaRuleEvaluationCapability
→ Execution
→ Derived RDF Result
→ Verification + Provenance
```

Across all three modes, CI verifies the shared core Capability abstraction:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
```

and verifies the shared runtime pattern across four concrete executions—reasoning, conforming validation, non-conforming validation, and rule evaluation:

```text
Execution
→ Result
→ Verification
```

CI also verifies the source-ownership invariant itself: Pizza domain artifacts are fetched from the pinned `pizza-ontology` contract and are not duplicated as ESKA source files.

The three-mode falsification pass strengthened the current provisional core without adding `Rule`, `RuleExecution`, `ExecutionMode`, a new result hierarchy, or ESKA-specific provenance classes. The project remains intentionally small and provisional; future modes should continue trying to falsify the current abstractions rather than expanding them by speculation.

## License

New material in this repository is licensed under the [MIT License](LICENSE).

External semantic models and reference artifacts used by examples retain their own provenance and licensing and should not be assumed to inherit this repository's license. See [`examples/pizza/LICENSE-NOTICE.md`](examples/pizza/LICENSE-NOTICE.md) for the current Pizza source and licensing boundary.