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

A **Semantic Model** is a formal representation that gives knowledge explicit machine-interpretable meaning through concepts, relationships, constraints, axioms, rules, decisions, formulae, mappings, workflows, or equivalent semantic structures.

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

## Seven Executable-Semantic Modes

The provisional core now has executable evidence across seven different semantic operations:

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

Rule, Decision, Calculation, Mapping, and Workflow were introduced as deliberate falsification tests. **None required a change to `model/eska-core.ttl`.**

### Mapping: role refinement below core

Mapping needs several semantic models with distinct roles:

```text
source semantic model
        ↓
mapping semantic model
        ↓
target semantic model
```

The Mapping example therefore defines:

```text
map:sourceSemanticModel
map:mappingSemanticModel
map:targetSemanticModel
```

as mapping-local subproperties of the generic `eska:usesSemanticModel` relation. Runtime role semantics use qualified PROV-O usage and `prov:hadRole`.

This established one extension pattern:

> **Generic core relationships can be refined by mode-specific subproperties when an executable semantic contract requires additional role precision.**

### Workflow: composition below core

Workflow creates a different pressure: one semantic Capability orchestrates already established Capabilities and makes later execution conditional on an intermediate Result.

```text
PizzaMenuPublicationWorkflowCapability
        ↓
Workflow Execution
    │
    ├── Validation Execution
    │       ↓ sh:conforms
    │
    └── Mapping Execution       conforming path only
            ↑
       prov:wasInformedBy
       Validation Execution
```

Overall and child activities remain ordinary `eska:Execution` instances. Composition uses established vocabularies:

- `dcterms:hasPart` / `dcterms:isPartOf` for whole/step composition;
- `prov:wasInformedBy` for step dependency;
- `prov:wasDerivedFrom` for overall Result lineage from step Results.

The source BPMN model identifies source-domain semantic operation IRIs. ESKA connects them to established Capabilities with Workflow-local `sourceOperation` / `boundCapability` bindings. Those adapter terms remain outside core because only Workflow currently requires them.

This establishes a second extension pattern:

> **Composite semantic execution can be built from ordinary core Executions plus established part/dependency relations, while Workflow-specific operation binding remains local until broader evidence exists.**

### Cross-repository verification matters

The first Workflow integration run independently detected a source binding mismatch: the Pizza workflow vocabulary referenced an artifact name different from the mapping distribution actually published by the manifest. Pizza's first regression had repeated the same mistaken identifier and was therefore internally consistent.

Pizza PR #41 corrected the source before ESKA Workflow was merged. This is direct evidence that consumer-side verification of a semantic artifact contract adds value beyond source-side tests alone.

The seven-mode evidence still does **not** justify technology-shaped core concepts such as:

- `Rule`, `Decision`, `Calculation`, `Mapping`, `Workflow`, `Formula`, or `Transformation`;
- `WorkflowExecution`, `StepExecution`, `CompositeExecution`, or other mode-specific Execution subclasses;
- mode-specific Result superclasses;
- a generic `ExecutionMode` taxonomy;
- source/target or workflow-operation adapter properties in core;
- BPMN-, DMN-, OpenMath-, or SPARQL-specific core properties;
- a second ESKA provenance/composition hierarchy;
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

The current binding in [`examples/pizza/pizza-domain-source.json`](examples/pizza/pizza-domain-source.json) pins the corrected source commit:

```text
GerhardBalz/pizza-ontology
@715f0460a43abacb5258eedd3d722da219a25a43
```

The Pizza repository publishes **twenty-three source-owned semantic distributions**:

```text
OWL reasoning module
SHACL profile + 2 validation RDF cases
SPARQL rule + rule-result vocabulary + rule RDF data
DMN decision + decision vocabulary + decision cases
OpenMath formula + calculation vocabulary + calculation cases
SPARQL mapping + Menu target vocabulary + source RDF + expected target RDF
BPMN workflow + workflow vocabulary + valid/invalid inputs + expected target + cases
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

`PizzaDietarySuitabilityCapability` maps explicit decision contexts to semantic dietary-suitability outcomes through a source-owned DMN 1.5 model.

### 5. OpenMath Calculation — calculate

The source-owned formula represents:

```text
areaSquareCentimetres = π × (diameterCm / 2)²
```

`PizzaAreaCalculationCapability` produces typed decimal area Results without introducing numeric-specific core classes.

### 6. Semantic Mapping — transform

`PizzaMenuProjectionCapability` transforms explicit Pizza RDF into a separate target Menu semantic model. Its output is verified against a canonical target graph and source Pizza predicates/classes must not leak into the projection.

### 7. BPMN Workflow — execute

`PizzaMenuPublicationWorkflowCapability` composes Validation and Mapping:

```text
Start
  ↓
Validation
  ↓
conforms?
  ├── false → Rejected
  └── true
        ↓
Mapping
        ↓
      Published
```

Canonical behavior:

```text
valid-publication   → conforms=True  → 2 child steps → Published
invalid-rejection   → conforms=False → 1 child step  → Rejected
```

The invalid path proves conditional composition: the Mapping Capability is not executed when Validation fails.

## Seven-Mode Falsification Result

All seven modes fit the unchanged abstraction:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
→ Execution
→ Result
→ Verification
```

Mapping and Workflow also demonstrate how additional semantic precision can live below the core rather than forcing premature generalization into it.

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
- [x] Add Mapping → transform and demonstrate semantic-model role refinement.
- [x] Add BPMN Workflow → execute and demonstrate composite execution across seven Capabilities / sixteen Executions.
- [ ] Generalize Knowledge Service semantics beyond classification using cross-mode evidence.
- [ ] Generalize deterministic Knowledge Agent discovery/invocation beyond classification.
- [ ] Add richer provenance/evidence concepts only where executable use cases require them.
- [ ] Formalize deployment binding separately from semantic service contracts.
- [ ] Decide on a permanent ESKA namespace and publication strategy after further stabilization.

The project intentionally does **not** begin as a general software framework, agent platform, or large meta-ontology.

## Status

The executable reference now demonstrates seven distinct semantic operations with one shared provisional core Capability abstraction and one shared runtime `Execution → Result → Verification` pattern, including the first composite/conditional workflow.

After seven distinct execution modes, the next strongest test is no longer simply adding an eighth mode. The existing backlog now has enough execution evidence to test whether the **Knowledge Service and Knowledge Agent extensions generalize across modes**, starting with Validation.

## License

New material in this repository is licensed under the [MIT License](LICENSE).

External semantic models and reference artifacts retain their own provenance and licensing. See [`examples/pizza/LICENSE-NOTICE.md`](examples/pizza/LICENSE-NOTICE.md).
