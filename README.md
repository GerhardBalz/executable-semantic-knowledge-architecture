# Executable Semantic Knowledge Architecture (ESKA)

**Reference architecture and executable examples for formally represented, machine-interpretable, provenance-aware, verifiable, and agent-accessible knowledge.**

## Definition

**Executable Semantic Knowledge Architecture (ESKA)** is an architectural approach in which knowledge is explicitly and formally represented with machine-interpretable semantics, connected to executable mechanisms where appropriate, traceable to its provenance, verifiable, and directly discoverable and accessible by software agents.

A central principle is:

> **Execution must not sever semantics.**

Executable behavior should remain machine-traceable to the semantic knowledge that gives it meaning.

## From Semantic Knowledge to ESKA

```text
Semantic Knowledge
        │ operationalized as
        ▼
Executable Semantic Knowledge
        │ organized and governed by
        ▼
Executable Semantic Knowledge Architecture
```

**Semantic Knowledge** gives concepts, relationships, constraints, and context explicit machine-interpretable meaning.

> **What does this knowledge mean?**

**Executable Semantic Knowledge** lets that meaning participate directly in computation through formally associated mechanisms.

> **What can a machine do with this meaning?**

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

**ESKA** provides the architecture for creating, managing, connecting, executing, verifying, governing, and exposing those semantic assets.

> **How do we systematically make semantic knowledge operational, trustworthy, and accessible?**

## Core Principles

- **Explicit formal semantics** — meaning is represented explicitly rather than existing only in documents, prompts, or source code.
- **Machine interpretability** — machines can identify concepts, relationships, constraints, and context.
- **Executable where appropriate** — knowledge participates in computation according to its semantic type.
- **Semantic continuity** — execution remains connected to the semantic model and its inputs, outputs, applicability, and results.
- **Provenance awareness** — sources, versions, transformations, assertions, and executions remain traceable.
- **Verifiability** — semantics and executions are checked by mechanisms appropriate to their type.
- **Agent accessibility** — agents can discover and invoke machine-described capabilities rather than reconstructing meaning from prompts alone.
- **Explicit semantic-source ownership** — execution architecture should not become the accidental owner of domain semantics.

## Provisional ESKA Core

The current provisional cross-mode core lives in [`model/eska-core.ttl`](model/eska-core.ttl):

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

### Key concepts

A **Semantic Model** is a formal representation that gives knowledge explicit machine-interpretable meaning through concepts, relationships, constraints, axioms, rules, decisions, formulae, or equivalent semantic structures.

An **Executable Semantic Knowledge Artifact** is a machine-executable artifact whose behavior remains explicitly connected to semantic knowledge.

A **Capability** is a bounded ability to achieve a defined kind of outcome within a specified scope.

A **Semantic Capability** is a Capability whose scope, inputs, outputs, applicability, constraints, and semantics are explicitly machine-represented.

```text
Capability = Ability + Boundary + Outcome
```

An **Applicability Condition** identifies a condition that must hold for a Capability or executable artifact to be applied as intended.

An **Execution** is a computational activity that applies executable semantic knowledge under a defined Semantic Capability.

A **Result** is a machine-interpretable entity produced by an Execution.

A **Verification** checks semantic knowledge, an Execution, or a Result against explicit criteria.

### PROV-O reuse

ESKA reuses PROV-O rather than defining a parallel provenance model:

- `Execution` specializes `prov:Activity`;
- `Verification` specializes `prov:Activity`;
- `Result` specializes `prov:Entity`.

## Architectural Extensions

### Knowledge Service

A **Knowledge Service** is an operational interface through which knowledge can be accessed or a Semantic Capability invoked. A Capability defines **what ability exists**; a Service defines **how it is accessed**.

The provisional Service extension is in [`model/eska-service.ttl`](model/eska-service.ttl).

### Knowledge Agent

A **Knowledge Agent** can use machine-interpretable ESKA contracts to discover, interpret, verify, and invoke semantic capabilities and services.

The provisional Agent extension is in [`model/eska-agent.ttl`](model/eska-agent.ttl). The Pizza Agent is deliberately deterministic and non-LLM so agent accessibility is demonstrated as an architectural property.

Service and Agent remain outside the core because they are currently demonstrated only on the classification path.

## Five Executable-Semantic Modes

The provisional core now has executable evidence across five different operational semantics:

```text
Ontology    → reason
Constraint  → validate
Rule        → evaluate
Decision    → decide
Calculation → calculate
```

The generic Capability verifier covers **five Capabilities**. The generic runtime verifier covers **ten concrete Executions**:

```text
1 OWL reasoning execution
2 SHACL validation executions
1 SPARQL rule execution
3 DMN decision executions
3 OpenMath calculation executions
```

Rule, Decision, and Calculation were introduced as deliberate falsification tests. **None required a change to `model/eska-core.ttl`.**

The evidence has therefore not justified introducing technology-shaped core concepts such as:

- `Rule`, `Decision`, `Calculation`, or `Formula`;
- `RuleExecution`, `DecisionExecution`, or `CalculationExecution`;
- mode-specific Result superclasses;
- a generic `ExecutionMode` taxonomy;
- DMN- or OpenMath-specific core properties;
- a second ESKA provenance hierarchy;
- Service or Agent promotion into core.

The namespace remains deliberately provisional:

```text
urn:eska:core:
```

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

The companion repository [GerhardBalz/pizza-ontology](https://github.com/GerhardBalz/pizza-ontology) owns the Pizza semantic artifacts used by ESKA.

The current binding in [`examples/pizza/pizza-domain-source.json`](examples/pizza/pizza-domain-source.json) pins:

```text
GerhardBalz/pizza-ontology
@fcefdc7acddf2ca9a9dc4dad9e410cea992011ff
```

The Pizza repository publishes **thirteen source-owned semantic distributions**:

```text
OWL reasoning module
SHACL profile
2 validation RDF cases
SPARQL rule
rule-result vocabulary
rule RDF data
DMN 1.5 decision table
decision outcome vocabulary
decision cases
OpenMath area formula
calculation vocabulary
calculation cases
```

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
Service / Agent
```

> **Execution must not sever semantics — and execution architecture should not become the accidental owner of domain semantics.**

## Executable Pizza Modes

### 1. OWL Classification — reason

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

This is currently the only mode exposed through both Service and Agent.

### 2. SHACL Validation — validate

```text
source-owned SHACL profile + RDF data
        ↓ pySHACL
SHACL ValidationReport
        ↓
PizzaValidationCapability
        ↓
Execution → Result → Verification
```

### 3. SPARQL Rule Evaluation — evaluate

```text
explicit MeatTopping assertion
        ↓ RDFLib / SPARQL
requiresVegetarianWarning true
        ↓
PizzaRuleEvaluationCapability
        ↓
Execution → Result → Verification
```

### 4. DMN Decision Evaluation — decide

```text
containsMeat  containsFish  → dietarySuitability
true          -             → NotVegetarian
false         true          → PescatarianOnly
false         false         → Vegetarian
```

`PizzaDietarySuitabilityCapability` produces semantic decision outcomes through `decision:dietarySuitability`.

### 5. OpenMath Calculation — calculate

The source-owned mathematical expression represents:

```text
areaSquareCentimetres = π × (diameterCm / 2)²
```

`PizzaAreaCalculationCapability` consumes an explicit positive Pizza diameter and produces a `PizzaAreaResult`; the computed value is carried as an `xsd:decimal` through `calc:areaSquareCentimetres`.

Canonical results:

```text
20 cm → 314.159265 cm²
30 cm → 706.858347 cm²
40 cm → 1256.637061 cm²
```

The ESKA evaluator implements the supported OpenMath arithmetic semantics but does not encode the Pizza formula itself.

## Five-Mode Falsification Result

All five modes fit the unchanged abstraction:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
→ Execution
→ Result
→ Verification
```

The Calculation mode adds typed numeric outputs without requiring datatype-specific core classes: `PizzaAreaResult` is the Capability output type, while the semantic result relation carries the `xsd:decimal` value.

This is increasingly strong evidence for the provisional core, but it remains a falsifiable architecture rather than a claim of universal completeness.

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
- [x] Add SPARQL Rule → evaluate and re-test the core.
- [x] Add DMN Decision → decide and re-test the core.
- [x] Add OpenMath Calculation → calculate and re-test the core across five Capabilities / ten Executions.
- [ ] Continue falsifying the core with Mapping → transform or Workflow → execute where useful.
- [ ] Add richer provenance/evidence concepts only where executable use cases require them.
- [ ] Formalize deployment binding separately from semantic service contracts.
- [ ] Decide whether Validation should be exposed through Service and Agent layers.
- [ ] Decide on a permanent ESKA namespace and publication strategy after further stabilization.

The project intentionally does **not** begin as a general software framework, agent platform, or large meta-ontology.

## Status

The executable reference now demonstrates five distinct semantic operations with one shared Capability abstraction and one shared runtime pattern. Source ownership remains an executable invariant, while Service and Agent remain deliberately narrower classification extensions.

The next architectural test should continue trying to falsify the core rather than expanding it by symmetry.

## License

New material in this repository is licensed under the [MIT License](LICENSE).

External semantic models and reference artifacts retain their own provenance and licensing. See [`examples/pizza/LICENSE-NOTICE.md`](examples/pizza/LICENSE-NOTICE.md).
