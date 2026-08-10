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

A **Semantic Model** is a formal representation that gives knowledge explicit machine-interpretable meaning through concepts, relationships, constraints, axioms, rules, decisions, formulae, mappings, or equivalent semantic structures.

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

## Six Executable-Semantic Modes

The provisional core now has executable evidence across six different semantic operations:

```text
Ontology    → reason
Constraint  → validate
Rule        → evaluate
Decision    → decide
Calculation → calculate
Mapping     → transform
```

The generic Capability verifier covers **six Capabilities**. The generic runtime verifier covers **eleven concrete Executions**:

```text
1 OWL reasoning execution
2 SHACL validation executions
1 SPARQL rule execution
3 DMN decision executions
3 OpenMath calculation executions
1 semantic mapping execution
```

Rule, Decision, Calculation, and Mapping were introduced as deliberate falsification tests. **None required a change to `model/eska-core.ttl`.**

### Mapping exposed a real refinement need

Mapping is the first mode that needs several semantic models with distinct roles:

```text
source semantic model
        ↓
mapping semantic model
        ↓
target semantic model
```

The Mapping example therefore defines role-specific properties:

```text
map:sourceSemanticModel
map:mappingSemanticModel
map:targetSemanticModel
```

as mapping-local subproperties of the generic core relation:

```text
eska:usesSemanticModel
```

At runtime the same distinctions are represented with qualified PROV-O usage and `prov:hadRole`.

This establishes an evidence-driven extension pattern:

> **Generic core relationships can be refined by mode-specific subproperties when an executable semantic contract requires additional role precision.**

Only Mapping currently requires these three role properties, so they remain outside `model/eska-core.ttl`.

The six-mode evidence has therefore not justified technology-shaped core concepts such as:

- `Rule`, `Decision`, `Calculation`, `Formula`, `Mapping`, or `Transformation`;
- mode-specific Execution or Result subclasses;
- a generic `ExecutionMode` taxonomy;
- source/target semantic-model properties in core;
- DMN-, OpenMath-, or SPARQL-specific core properties;
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
@ef05531c5a362d8d1454e94e59a44f750515dd1c
```

The Pizza repository publishes **seventeen source-owned semantic distributions**:

```text
OWL reasoning module
SHACL profile + 2 validation RDF cases
SPARQL rule + rule-result vocabulary + rule RDF data
DMN decision + decision vocabulary + decision cases
OpenMath formula + calculation vocabulary + calculation cases
SPARQL mapping + Menu target vocabulary + source RDF + expected target RDF
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

`PizzaAreaCalculationCapability` produces a `PizzaAreaResult`; the computed value is carried as an `xsd:decimal` through `calc:areaSquareCentimetres`.

### 6. Semantic Mapping — transform

`PizzaMenuProjectionCapability` transforms an explicit Pizza source graph into a target Menu graph:

```text
Pizza source semantic model
    pizza:Pizza
    rdfs:label
    pizza:hasTopping
        ↓ source-owned SPARQL mapping
Menu target semantic model
    menu:MenuItem
    menu:displayName
    menu:ingredientName
```

The output is verified against a source-owned canonical target graph and must not leak Pizza source predicates/classes.

The Mapping mode also demonstrates that execution semantics are not determined solely by implementation technology: Rule and Mapping both use SPARQL `CONSTRUCT`, but Rule derives a statement within the source semantic domain while Mapping transforms between distinct semantic models.

## Six-Mode Falsification Result

All six modes fit the unchanged abstraction:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
→ Execution
→ Result
→ Verification
```

Mapping adds role-specific semantic precision without forcing those roles into core. That is stronger evidence for the current architecture than simply adding another technology-specific class hierarchy.

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
- [x] Add OpenMath Calculation → calculate and re-test the core.
- [x] Add Mapping → transform and re-test the core across six Capabilities / eleven Executions.
- [x] Demonstrate mapping-specific semantic-model role refinements without changing the core.
- [ ] Continue falsifying the core with Workflow → execute where useful.
- [ ] Add richer provenance/evidence concepts only where executable use cases require them.
- [ ] Formalize deployment binding separately from semantic service contracts.
- [ ] Decide whether Validation should be exposed through Service and Agent layers.
- [ ] Decide on a permanent ESKA namespace and publication strategy after further stabilization.

The project intentionally does **not** begin as a general software framework, agent platform, or large meta-ontology.

## Status

The executable reference now demonstrates six distinct semantic operations with one shared core Capability abstraction and one shared runtime pattern. Mapping additionally demonstrates how a mode-specific semantic contract can refine a generic core relation without forcing premature vocabulary into the core itself.

Source ownership remains an executable invariant, while Service and Agent remain deliberately narrower classification extensions.

The next strong architectural falsification candidate is **Workflow → execute**, because workflow semantics may introduce sequencing, intermediate state, and multiple linked executions rather than one bounded computation producing one result.

## License

New material in this repository is licensed under the [MIT License](LICENSE).

External semantic models and reference artifacts retain their own provenance and licensing. See [`examples/pizza/LICENSE-NOTICE.md`](examples/pizza/LICENSE-NOTICE.md).
