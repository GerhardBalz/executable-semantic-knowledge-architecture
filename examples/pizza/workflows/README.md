# Pizza Workflow → execute

This example adds **Workflow → execute** as the seventh executable-semantic mode in ESKA.

The source-owned BPMN 2.0.2 process composes two already established semantic capabilities:

```text
Start
  ↓
PizzaValidationCapability
  ↓
sh:conforms?
  ├── false → Rejected
  └── true
        ↓
PizzaMenuProjectionCapability
        ↓
      Published
```

## Semantic source ownership

The BPMN process, workflow vocabulary, valid/invalid Pizza inputs, expected valid Menu graph, and workflow case contract are owned by `GerhardBalz/pizza-ontology` and fetched from the immutable source binding in `../pizza-domain-source.json`.

The BPMN model owns **control flow only**. It does not duplicate SHACL or SPARQL semantics.

## Operation binding

The source BPMN service tasks identify semantic operations:

```text
pizzaWf:ValidatePizzaData
pizzaWf:TransformPizzaToMenu
```

ESKA resolves those to existing Capabilities through workflow-local bindings:

```text
sourceOperation                    boundCapability
────────────────────────────────────────────────────────────
ValidatePizzaData           →     PizzaValidationCapability
TransformPizzaToMenu        →     PizzaMenuProjectionCapability
```

`sourceOperation` and `boundCapability` are deliberately not ESKA core properties. Only Workflow currently requires this adapter between source orchestration semantics and ESKA Capability identifiers.

## Composite execution

The workflow does not introduce a new execution hierarchy. Overall workflow runs and their steps are ordinary `eska:Execution` instances.

```text
Workflow Execution
    │ dcterms:hasPart
    ├── Validation Execution
    │       ↓ Result: sh:conforms
    │
    └── Mapping Execution             valid case only
            ↑ prov:wasInformedBy
       Validation Execution
```

Step executions retain the existing child Capability contracts. The overall workflow execution executes `PizzaMenuPublicationWorkflowCapability` and produces a semantic `Published` or `Rejected` workflow Result.

## Canonical cases

```text
valid-publication
    validation → conforms true
    mapping    → executed
    outcome    → Published

invalid-rejection
    validation → conforms false
    mapping    → not executed
    outcome    → Rejected
```

The invalid case is important: it proves that the workflow is conditional composition rather than a fixed sequence of calls.

## Execute

```bash
python -m pip install -r examples/pizza/workflows/requirements.txt
python examples/pizza/workflows/evaluate.py
```

The runner:

1. materializes the 23 source-owned Pizza artifacts;
2. verifies the Workflow and child Capability contracts;
3. parses BPMN ordering, task bindings, gateway condition/default flow, and outcomes;
4. resolves source operations to existing ESKA Capabilities;
5. executes SHACL validation on each workflow input;
6. conditionally executes the existing Pizza→Menu mapping;
7. verifies source-owned expected outcomes and target graph;
8. records overall and child `Execution → Result → Verification` chains;
9. records composition with Dublin Core Terms and ordering/dependency with PROV-O.

This is a deliberately small BPMN execution subset for architecture testing, not a general workflow engine.

## Falsification boundary

The experiment intentionally tests whether the existing ESKA core can survive composite execution without adding:

- `Workflow` as a core class;
- `WorkflowExecution`;
- `StepExecution`;
- `CompositeExecution`;
- `WorkflowResult` as a generic superclass;
- a generic `ExecutionMode` taxonomy.

If the generic seven-mode and sixteen-execution verifiers pass, the evidence supports keeping composition as a reusable pattern around the existing core rather than enlarging the core by symmetry.
