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
        │ operationalized as
        ▼
Executable Semantic Knowledge
        │ organized and governed by
        ▼
Executable Semantic Knowledge Architecture
```

### Semantic Knowledge

**Semantic Knowledge** is knowledge whose concepts, relationships, constraints, and context are explicitly and formally represented so that their meaning is machine-interpretable.

> **What does this knowledge mean?**

### Executable Semantic Knowledge

**Executable Semantic Knowledge** is Semantic Knowledge that can directly participate in machine reasoning, validation, computation, decision-making, transformation, or action through formally associated executable mechanisms.

> **What can a machine do with this meaning?**

Executable does not mean that all knowledge becomes procedural code. Different semantic artifacts have different operational interpretations:

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

### Executable Semantic Knowledge Architecture

**ESKA** provides the architecture for creating, managing, connecting, executing, verifying, governing, and exposing Semantic Knowledge and Executable Semantic Knowledge as first-class computational assets.

> **How do we systematically make semantic knowledge operational, trustworthy, and accessible?**

In compact form:

> **SK gives knowledge explicit meaning. ESK makes that meaning operational. ESKA makes operational semantic knowledge a governed architectural capability.**

## Core Principles

### Explicit formal semantics

Meaning is represented explicitly rather than existing only in documents, prompts, source code, or human interpretation.

### Machine interpretability

Machines can identify concepts, relationships, constraints, and applicable context rather than merely parse syntax.

### Executable where appropriate

Knowledge participates directly in computation according to its semantic type.

### Semantic continuity

Execution remains connected to the semantic model. Inputs, outputs, applicability, effects, rules, decisions, and results should remain machine-traceable to the concepts that define their meaning.

### Provenance awareness

Knowledge and derived results can be traced to sources, versions, transformations, assertions, and execution history.

### Verifiability

Knowledge and execution can be checked through logical consistency, constraint validation, tests, reproducibility, evidence, and provenance.

### Agent accessibility

Software agents can discover, query, interpret, reason over, verify, and invoke knowledge through explicit computational interfaces instead of reconstructing its meaning from unstructured text alone.

### Explicit ownership of semantic sources

Execution architecture should not become the accidental owner of domain semantics. Domain repositories can own semantic artifacts while ESKA consumes them through immutable, machine-described bindings.

## Provisional Core Concepts

The current provisional cross-mode core is defined in [`model/eska-core.ttl`](model/eska-core.ttl).

### Semantic Model

A **Semantic Model** is a formal representation that gives knowledge explicit machine-interpretable meaning through concepts, relationships, constraints, axioms, rules, decisions, or equivalent semantic structures.

### Executable Semantic Knowledge Artifact

An **Executable Semantic Knowledge Artifact** is a machine-executable artifact whose computational behavior remains explicitly connected to machine-interpretable semantic knowledge.

### Capability and Semantic Capability

A **Capability** is a bounded ability to achieve a defined kind of outcome within a specified scope.

A **Semantic Capability** is a Capability whose scope, inputs, outputs, applicability, constraints, and semantics are explicitly represented in machine-interpretable form.

A useful mnemonic remains:

```text
Capability = Ability + Boundary + Outcome
```

### Applicability Condition

An **Applicability Condition** is a machine-identifiable condition that must hold for a Semantic Capability or executable artifact to be applied as intended.

### Execution, Result and Verification

An **Execution** is a computational activity that applies executable semantic knowledge under a defined Semantic Capability.

A **Result** is a machine-interpretable entity produced by an Execution, such as an inferred statement, validation report, rule-derived statement, decision outcome, calculation, transformation, or action description.

A **Verification** is an activity that checks semantic knowledge, an Execution, or a Result against explicit criteria.

The shared runtime pattern is:

```text
SemanticCapability
        ↓
Execution
        ↓
Result
        ↓
Verification
```

ESKA reuses PROV-O rather than defining a parallel provenance model:

- `Execution` specializes `prov:Activity`;
- `Verification` specializes `prov:Activity`;
- `Result` specializes `prov:Entity`.

## Architectural Extensions

### Knowledge Service

A **Knowledge Service** is an operational interface through which knowledge can be discovered, queried, reasoned over, validated, evaluated, transformed, explained, or acted upon.

A Capability defines **what ability exists**. A Knowledge Service defines **how that ability is operationally accessible**.

The provisional Service extension lives in [`model/eska-service.ttl`](model/eska-service.ttl).

### Knowledge Agent

A **Knowledge Agent** is a software agent that can use machine-interpretable ESKA contracts to discover, interpret, query, reason over, verify, and invoke semantic capabilities and services.

The provisional Agent extension lives in [`model/eska-agent.ttl`](model/eska-agent.ttl). The Pizza reference Agent is deliberately deterministic and non-LLM so discovery and invocation are demonstrated as architectural properties rather than prompt behavior.

Service and Agent remain outside the core because they are currently demonstrated only on the classification path.

## Current Provisional Core

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

The core now has executable evidence across **four distinct semantic execution modes**:

```text
Ontology   → reason
Constraint → validate
Rule       → evaluate
Decision   → decide
```

The Rule and Decision modes were introduced as explicit falsification tests. Neither required a change to `model/eska-core.ttl`.

The four-mode evidence also did **not** justify introducing technology-shaped concepts such as:

- `Rule` or `RuleExecution` in core,
- `Decision`, `DecisionExecution`, or `DecisionResult` in core,
- a generic `ExecutionMode` taxonomy,
- DMN-specific core properties,
- a second ESKA provenance hierarchy,
- Service or Agent promotion into core.

The project continues to use the provisional namespace:

```text
urn:eska:core:
```

The concepts should stabilize further before a permanent public namespace and publication policy are chosen.

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

## Pizza as the Reference Domain

The companion repository [GerhardBalz/pizza-ontology](https://github.com/GerhardBalz/pizza-ontology) is the **source owner** for the Pizza semantic artifacts used by ESKA.

ESKA currently pins the Pizza artifact contract to:

```text
GerhardBalz/pizza-ontology
@983b691d9d2102ffad97a3ec31aa9b1435b3e547
```

through [`examples/pizza/pizza-domain-source.json`](examples/pizza/pizza-domain-source.json).

The Pizza repository publishes **ten** semantic distributions:

```text
OWL reasoning module
SHACL profile
2 validation RDF cases
SPARQL rule
rule-result vocabulary
rule RDF data
DMN 1.5 decision table
decision outcome vocabulary
canonical decision cases
```

The files are materialized only at runtime beneath `examples/pizza/.work/pizza-domain/`. CI explicitly fails if ESKA reintroduces those source-owned semantic artifacts as local source copies.

```text
pizza-ontology
    owns domain semantics
        ↓ immutable commit + artifacts/manifest.ttl
ESKA
    owns execution architecture
        ↓
Capability / Execution / Result / Verification
        ↓ optional exposure
Service / Agent
```

> **Execution must not sever semantics — and execution architecture should not become the accidental owner of domain semantics.**

## Executable Pizza Modes

### 1. OWL Classification — reason

The classification example asks whether `AmericanHot` can be inferred to be a `SpicyPizza`.

```text
source-owned coherent OWL module
        ↓ HermiT / ROBOT
AmericanHot ⊑ SpicyPizza
        ↓
PizzaClassificationCapability
        ↓
PizzaClassificationService
        ↓
PizzaKnowledgeAgent
```

This is the only current path extended through Knowledge Service and Knowledge Agent.

### 2. SHACL Validation — validate

The validation example asks whether explicit Pizza RDF data conforms to the source-owned SHACL profile.

```text
source-owned SHACL profile + RDF data
        ↓ pySHACL
SHACL ValidationReport
        ↓
PizzaValidationCapability
        ↓
Execution → Result → Verification
```

The source-owned positive and negative cases exercise both conforming and non-conforming executions.

### 3. SPARQL Rule Evaluation — evaluate

The rule example evaluates a source-owned SPARQL 1.1 `CONSTRUCT` rule over explicit RDF assertions.

```text
Pizza with explicit MeatTopping assertion
        ↓ RDFLib / SPARQL
requiresVegetarianWarning true
        ↓
PizzaRuleEvaluationCapability
        ↓
Execution → Result → Verification
```

The mode performs neither OWL inference nor SHACL validation.

### 4. DMN Decision Evaluation — decide

The Decision example consumes a source-owned OMG DMN 1.5 `UNIQUE` decision table and explicit decision contexts.

```text
containsMeat  containsFish  → dietarySuitability
true          -             → NotVegetarian
false         true          → PescatarianOnly
false         false         → Vegetarian
```

ESKA represents the bounded ability as `PizzaDietarySuitabilityCapability` and produces semantic RDF decision outcomes using `urn:pizza-ontology:decision:dietarySuitability`.

The three canonical cases produce:

```text
meatyPizza       → NotVegetarian
fishPizza        → PescatarianOnly
vegetarianPizza  → Vegetarian
```

Each case has its own `Execution → Result → Verification` PROV-O chain.

## Cross-Mode Falsification Result

CI now verifies the same generic Capability contract across **four Capabilities**:

```text
PizzaClassificationCapability
PizzaValidationCapability
PizzaRuleEvaluationCapability
PizzaDietarySuitabilityCapability
```

and the same runtime pattern across **seven concrete executions**:

```text
1 OWL reasoning execution
2 SHACL validation executions
1 SPARQL rule execution
3 DMN decision executions
```

All currently fit the unchanged abstraction:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
→ Execution
→ Result
→ Verification
```

This is stronger evidence for the provisional core, but not a claim of universal completeness. Future modes should continue attempting to falsify it.

## Initial Scope

- [x] Establish ESKA terminology and conceptual model.
- [x] Distinguish Semantic Knowledge, Executable Semantic Knowledge, and ESKA.
- [x] Implement Pizza OWL reasoning and semantic verification.
- [x] Define the first bounded Semantic Capability.
- [x] Expose classification through a Knowledge Service.
- [x] Demonstrate deterministic Knowledge Agent discovery and invocation.
- [x] Add SHACL validation as a second mode.
- [x] Generalize the provisional cross-mode core.
- [x] Separate Pizza semantic-artifact ownership from ESKA execution architecture.
- [x] Add SPARQL Rule → evaluate as a third mode.
- [x] Re-test the core generically across three modes.
- [x] Add DMN Decision → decide as a fourth mode.
- [x] Re-test the core generically across four modes and seven executions without changing the core model.
- [ ] Continue falsifying the core with another genuinely different mode where useful.
- [ ] Add richer provenance/evidence concepts only where executable use cases require them.
- [ ] Formalize deployment binding separately from semantic service contracts.
- [ ] Decide whether Validation should be exposed through Service and Agent layers.
- [ ] Decide on a permanent ESKA namespace and publication strategy after further stabilization.

The project intentionally does **not** begin as a general software framework, agent platform, or large meta-ontology.

## Status

The executable reference currently demonstrates:

```text
Ontology   → reason
Constraint → validate
Rule       → evaluate
Decision   → decide
```

with one shared core Capability abstraction and one shared runtime `Execution → Result → Verification` pattern.

The source-ownership invariant is also executable: Pizza domain semantics are fetched from the pinned `pizza-ontology` contract and are not duplicated as ESKA source files.

Service and Agent remain deliberately narrower than the core. Their current evidence is classification-specific, so they stay as extensions rather than being promoted by symmetry.

## License

New material in this repository is licensed under the [MIT License](LICENSE).

External semantic models and reference artifacts retain their own provenance and licensing. See [`examples/pizza/LICENSE-NOTICE.md`](examples/pizza/LICENSE-NOTICE.md) for the Pizza source and licensing boundary.
