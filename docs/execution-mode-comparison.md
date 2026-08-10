# Execution Mode Comparison

Executable Semantic Knowledge Architecture (ESKA) does not define one universal execution mechanism. Semantic artifacts are executable according to the operational semantics appropriate to their type.

The Pizza reference now demonstrates seven execution modes:

| Concern | Semantic model | Operation | Primary result | Capability |
| --- | --- | --- | --- | --- |
| OWL reasoning | OWL class axioms | reason | inferred axiom | `PizzaClassificationCapability` |
| SHACL validation | SHACL shapes graph | validate | validation report | `PizzaValidationCapability` |
| Rule evaluation | SPARQL `CONSTRUCT` rule | evaluate | derived RDF statement | `PizzaRuleEvaluationCapability` |
| Decision evaluation | DMN 1.5 decision table | decide | semantic outcome | `PizzaDietarySuitabilityCapability` |
| Calculation | OpenMath formula + calculation vocabulary | calculate | typed decimal value | `PizzaAreaCalculationCapability` |
| Semantic mapping | Pizza source model + SPARQL mapping + Menu target model | transform | target RDF graph | `PizzaMenuProjectionCapability` |
| Workflow execution | BPMN 2.0.2 process + workflow vocabulary | execute | Published / Rejected composite result | `PizzaMenuPublicationWorkflowCapability` |

## Shared provisional core

All seven modes use the same unchanged cross-mode abstraction:

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
        ↓
PROV-O provenance
```

The generic Capability verifier checks seven Capabilities. The generic runtime verifier now checks sixteen concrete executions:

```text
1 reasoning
2 validation
1 rule
3 decision
3 calculation
1 mapping
5 workflow-related executions
```

The five Workflow-related executions are two overall workflow runs plus the three child steps that actually execute across the valid and invalid paths.

## Mapping: role refinement without core expansion

Mapping needs explicit source, mapping, and target semantic-model roles. The example defines:

```text
map:sourceSemanticModel
map:mappingSemanticModel
map:targetSemanticModel
```

as subproperties of `eska:usesSemanticModel`, while runtime role semantics use qualified PROV-O `prov:Usage` / `prov:hadRole`.

This established a reusable extension pattern: mode-specific semantic precision can refine a generic core relation without immediately becoming core vocabulary.

## Workflow: composition without a new execution hierarchy

Workflow introduces a different pressure: one semantic Capability coordinates existing Capabilities and makes later execution conditional on an intermediate Result.

```text
PizzaMenuPublicationWorkflowCapability
        ↓
Workflow Execution
    │
    ├── dcterms:hasPart → Validation Execution
    │                         ↓ Result: sh:conforms
    │
    └── dcterms:hasPart → Mapping Execution        conforming case only
                              ↑
                      prov:wasInformedBy
                        Validation Execution
```

The BPMN process owns ordering, gateway semantics, and end outcomes. It does not contain the SHACL constraints or SPARQL mapping logic.

The source BPMN tasks identify Pizza workflow operation IRIs. ESKA needs to resolve those source identifiers to established Semantic Capabilities, so the Workflow example introduces a local binding layer:

```text
wf:sourceOperation
        ↓
wf:boundCapability
```

with:

```text
pizzaWf:ValidatePizzaData
    → val:PizzaValidationCapability

pizzaWf:TransformPizzaToMenu
    → map:PizzaMenuProjectionCapability
```

Only Workflow currently needs this adapter, so the binding properties remain outside `eska-core.ttl`.

## Composite Result and lineage

The valid case executes two child steps and produces `Published`. The invalid case executes Validation only and produces `Rejected`.

```text
valid-publication
    Validation Execution
        ↓ conforms true
    Mapping Execution
        ↓
    Workflow Result: Published

invalid-rejection
    Validation Execution
        ↓ conforms false
    Workflow Result: Rejected
```

Each overall run and each step remains an ordinary `eska:Execution`; every concrete activity still produces an `eska:Result` and has an `eska:Verification`.

Composition itself uses established vocabulary:

- `dcterms:hasPart` / `dcterms:isPartOf` for overall/step composition;
- `prov:wasInformedBy` for execution dependency/order;
- `prov:wasDerivedFrom` from overall workflow Result to step Results.

No ESKA-specific composite-execution hierarchy was required.

## Falsification result

If the seventh-mode CI remains green, Workflow does **not** require any of the following additions to the ESKA core:

- `Workflow` as a core class;
- `WorkflowExecution`;
- `StepExecution`;
- `CompositeExecution`;
- a generic Workflow Result superclass;
- a generic `ExecutionMode` taxonomy;
- BPMN-specific core properties;
- a new provenance or composition vocabulary;
- Service or Agent promotion.

It does establish a second evidence-backed extension pattern:

> **Composite semantic execution can be built from ordinary core Executions plus established part/dependency relations, while Workflow-specific operation binding remains local until broader evidence exists.**

## Execution is polymorphic

```text
Ontology    → reason
Constraint  → validate
Rule        → evaluate
Decision    → decide
Calculation → calculate
Mapping     → transform
Workflow    → execute
```

The core should change only when executable evidence demonstrates that its current concepts are too broad, too narrow, or missing—not because a technology-specific taxonomy looks attractive in advance.
