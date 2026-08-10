# Pizza: executable semantic knowledge reference

This directory contains the executable Pizza reference examples for **Executable Semantic Knowledge Architecture (ESKA)**.

The reference tests different formal execution semantics while preserving a strict repository boundary:

```text
pizza-ontology
    owns Pizza domain semantics
        ↓ immutable commit + artifact manifest
ESKA
    operationalizes those semantics
```

ESKA does not maintain source copies of the Pizza OWL, SHACL, SPARQL, DMN, OpenMath, Mapping, or BPMN semantic artifacts used here. [`pizza-domain-source.json`](pizza-domain-source.json) pins `GerhardBalz/pizza-ontology` to an immutable Git commit, and [`fetch-domain-artifacts.py`](fetch-domain-artifacts.py) materializes the published artifacts under `.work/pizza-domain/` at execution time.

## Semantic Source Binding

```text
Repository
    GerhardBalz/pizza-ontology

Commit
    715f0460a43abacb5258eedd3d722da219a25a43

Manifest
    artifacts/manifest.ttl
```

The manifest publishes **twenty-three** source-owned semantic distributions consumed by this reference:

- coherent Pizza OWL reasoning module;
- Pizza instance SHACL profile;
- conforming and non-conforming RDF validation examples;
- vegetarian-warning SPARQL rule, result vocabulary, and rule RDF data;
- DMN 1.5 dietary-suitability decision, decision vocabulary, and canonical contexts;
- OpenMath Pizza-area formula, calculation vocabulary, and canonical calculation cases;
- Pizza-to-Menu SPARQL mapping, Menu target vocabulary, canonical source graph, and expected target graph;
- BPMN 2.0.2 menu-publication workflow, workflow vocabulary, valid/invalid workflow inputs, expected valid target graph, and workflow cases.

```text
artifact role/path
        +
pinned Git commit
        ↓
immutable semantic input
```

Runtime copies beneath `.work/` are disposable execution inputs, not a second semantic source of truth.

## Seven Execution Modes

```text
source-owned OWL module
    ↓ reason
inferred semantic knowledge

source-owned SHACL profile + RDF data
    ↓ validate
semantic conformance report

source-owned SPARQL rule + RDF data
    ↓ evaluate
rule-derived RDF statement

source-owned DMN decision + explicit context
    ↓ decide
semantic decision outcome

source-owned OpenMath formula + numeric context
    ↓ calculate
typed decimal numeric result

source-owned Pizza graph + mapping + target model
    ↓ transform
target Menu RDF graph

source-owned BPMN process + workflow vocabulary
    ↓ execute
composite Published / Rejected result
```

The OWL path is developed end-to-end through Capability, Service, and Agent. Validation, Rule, Decision, Calculation, Mapping, and Workflow remain at the Semantic Capability / Execution / Result / Verification level so operational exposure concepts are not promoted by symmetry.

## 1. OWL Classification — reason

The classification example asks:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that inference remain machine-traceable as it is exposed and invoked?**

The source-owned coherent module does not assert:

```text
AmericanHot SubClassOf SpicyPizza
```

HermiT derives it through OWL semantics.

```text
Pizza reasoning module        pizza-ontology
        ↓ pinned fetch
HermiT reasoning              ESKA execution
        ↓
AmericanHot ⊑ SpicyPizza
        ↓
PizzaClassificationCapability
        ↓
PizzaClassificationService
        ↓ discovered by
PizzaKnowledgeAgent
```

[`pizza-classification-capability.ttl`](pizza-classification-capability.ttl) describes a bounded `owl:Class → owl:Class` Capability producing `rdfs:subClassOf` through the commit-pinned Pizza reasoning model and HermiT execution.

[`pizza-classification-service.ttl`](pizza-classification-service.ttl) and [`service.py`](service.py) expose the Capability without reimplementing Pizza reasoning semantics.

[`pizza-knowledge-agent.ttl`](pizza-knowledge-agent.ttl) and [`agent.py`](agent.py) demonstrate deterministic semantic discovery/invocation without hard-coding the Service operation or expected `SpicyPizza` answer.

## 2. SHACL Validation — validate

See [`validation/README.md`](validation/README.md).

`PizzaValidationCapability` consumes a Pizza RDF graph, uses the commit-pinned SHACL profile, and produces a `sh:ValidationReport` through `sh:conforms`.

The source-owned non-conforming fixture deliberately produces both a missing-base violation and a wrongly typed topping violation.

## 3. SPARQL Rule Evaluation — evaluate

See [`rules/README.md`](rules/README.md).

The source-owned SPARQL 1.1 `CONSTRUCT` rule evaluates explicit Pizza RDF assertions:

```text
Pizza
    hasTopping topping
    topping a MeatTopping
        ↓ evaluate
requiresVegetarianWarning true
```

`PizzaRuleEvaluationCapability` uses the commit-pinned SPARQL rule and RDFLib. It performs neither OWL inference nor SHACL validation.

## 4. DMN Decision Evaluation — decide

See [`decisions/README.md`](decisions/README.md).

The source-owned DMN 1.5 `UNIQUE` decision table consumes explicit boolean inputs and produces one semantic dietary-suitability outcome through `PizzaDietarySuitabilityCapability`.

Each canonical context has its own `Execution → Result → Verification` PROV-O chain.

## 5. OpenMath Calculation — calculate

See [`calculations/README.md`](calculations/README.md).

The source-owned OpenMath expression represents:

```text
areaSquareCentimetres = π × (diameterCm / 2)²
```

`PizzaAreaCalculationCapability` produces a `PizzaAreaResult`; the actual value is represented as an `xsd:decimal` literal through `calc:areaSquareCentimetres`.

## 6. Semantic Mapping — transform

See [`mappings/README.md`](mappings/README.md).

The source-owned mapping artifacts distinguish:

```text
Pizza source semantic model
        ↓
SPARQL mapping semantic model
        ↓
Menu target semantic model
```

`PizzaMenuProjectionCapability` transforms explicit Pizza RDF into a target Menu graph. The output is compared isomorphically with the source-owned canonical target graph, and Pizza source predicates/classes are rejected from the target graph.

### Mapping semantic-model roles

Mapping defines example-local:

```text
map:sourceSemanticModel
map:mappingSemanticModel
map:targetSemanticModel
```

as subproperties of `eska:usesSemanticModel`. Runtime provenance represents the same roles with qualified PROV-O usage and `prov:hadRole`.

These properties remain outside `model/eska-core.ttl` because only Mapping currently justifies them.

### Rule versus Mapping

Both use SPARQL `CONSTRUCT`, but their semantic contracts differ:

```text
Rule
    source semantic model
        ↓ derive
    source-domain statement

Mapping
    source semantic model
        ↓ mapping semantic model
    target semantic model
        ↓
    transformed target graph
```

Execution semantics therefore cannot be inferred solely from implementation technology.

## 7. BPMN Workflow — execute

See [`workflows/README.md`](workflows/README.md).

The source-owned BPMN 2.0.2 process composes the existing Validation and Mapping Capabilities:

```text
Start
  ↓
Validate Pizza RDF
  ↓
validationConforms?
  ├── false → Rejected
  └── true
        ↓
Transform Pizza → Menu
        ↓
      Published
```

BPMN owns control flow only. It does not duplicate the SHACL constraints or SPARQL Mapping semantics.

### Workflow operation binding

Source BPMN tasks identify semantic operation IRIs. ESKA maps those identifiers to existing Capabilities through workflow-local bindings:

```text
pizzaWf:ValidatePizzaData
    → val:PizzaValidationCapability

pizzaWf:TransformPizzaToMenu
    → map:PizzaMenuProjectionCapability
```

`sourceOperation` and `boundCapability` remain Workflow-local terms rather than core vocabulary.

### Composite execution

Overall Workflow runs and their child steps remain ordinary `eska:Execution` instances:

```text
Workflow Execution
    │ dcterms:hasPart
    ├── Validation Execution
    │       ↓ sh:conforms
    │
    └── Mapping Execution       conforming path only
            ↑
       prov:wasInformedBy
       Validation Execution
```

Overall Results are derived from step Results with PROV-O. No `WorkflowExecution`, `StepExecution`, or `CompositeExecution` core classes are introduced.

Canonical behavior:

```text
valid-publication   → conforms=True  → Validation + Mapping → Published
invalid-rejection   → conforms=False → Validation only      → Rejected
```

The rejected path proves that the Workflow is conditional composition rather than a fixed sequence of calls.

### Independent contract verification

The first ESKA Workflow integration detected a source artifact-name mismatch that Pizza's first internally consistent regression had not caught. Pizza PR #41 corrected the source before the Workflow increment was merged. This provides concrete evidence for independent consumer-side verification of semantic artifact contracts.

## Execute

Requirements:

- Java 17 or newer for OWL/ROBOT;
- Python 3;
- network access to retrieve the commit-pinned public Pizza artifacts;
- `curl` for the pinned ROBOT download.

OWL architecture:

```bash
bash examples/pizza/run.sh
```

Complete Knowledge Agent path:

```bash
bash examples/pizza/test-agent.sh
```

SHACL validation:

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
python examples/pizza/validation/validate.py
```

SPARQL rule evaluation:

```bash
python -m pip install -r examples/pizza/rules/requirements.txt
python examples/pizza/rules/evaluate.py
```

DMN decision evaluation:

```bash
python -m pip install -r examples/pizza/decisions/requirements.txt
python examples/pizza/decisions/evaluate.py
```

OpenMath calculation:

```bash
python -m pip install -r examples/pizza/calculations/requirements.txt
python examples/pizza/calculations/evaluate.py
```

Semantic mapping:

```bash
python -m pip install -r examples/pizza/mappings/requirements.txt
python examples/pizza/mappings/evaluate.py
```

BPMN workflow:

```bash
python -m pip install -r examples/pizza/workflows/requirements.txt
python examples/pizza/workflows/evaluate.py
```

## Cross-Mode Core Verification

The generic Capability verifier checks one common contract across **seven Capabilities**:

- `PizzaClassificationCapability`;
- `PizzaValidationCapability`;
- `PizzaRuleEvaluationCapability`;
- `PizzaDietarySuitabilityCapability`;
- `PizzaAreaCalculationCapability`;
- `PizzaMenuProjectionCapability`;
- `PizzaMenuPublicationWorkflowCapability`.

The generic runtime verifier checks the same core pattern across **sixteen concrete Executions**:

- one OWL reasoning execution;
- two SHACL validation executions;
- one SPARQL rule execution;
- three DMN decision executions;
- three OpenMath calculation executions;
- one semantic mapping execution;
- two overall Workflow executions;
- three actually executed Workflow child steps.

The shared abstraction remains:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
→ Execution
→ Result
→ Verification
```

`model/eska-core.ttl` required **no change** for the Rule, Decision, Calculation, Mapping, or Workflow falsification modes.

Mapping and Workflow exposed real refinements, but the executable evidence supports keeping those refinements below core:

- Mapping refines semantic-model roles;
- Workflow adds source-operation→Capability bindings and composite part/dependency relations.

## Verification Questions

The reference now checks:

```text
Is the Pizza domain source pinned to an immutable commit?

Does the manifest still publish the complete 23-artifact role/path contract?

Does OWL reasoning produce the expected inference?

Does the classification Capability remain Service- and Agent-accessible?

Does SHACL distinguish conforming and non-conforming data?

Does the SPARQL rule produce the expected derived statement and preserve its control case?

Does DMN select exactly one expected semantic outcome per context?

Does OpenMath calculate the expected typed numeric values?

Does Mapping produce exactly the target semantic graph without leaking source vocabulary?

Does Workflow execute Mapping only after a conforming Validation result?

Do all seven Capabilities satisfy the same generic core contract?

Do all sixteen Executions satisfy the same Execution → Result → Verification pattern?

Do provenance records retain source artifact identity, Mapping roles, Workflow composition, and step dependency?
```

## Ownership Boundary

```text
GerhardBalz/pizza-ontology
│
├── Pizza Ontology 2.0 preservation source
├── coherent OWL reasoning module
├── SHACL validation profile + RDF cases
├── SPARQL rule + vocabulary + RDF data
├── DMN decision + vocabulary + cases
├── OpenMath formula + calculation vocabulary + cases
├── SPARQL mapping + Menu target vocabulary + source/target RDF
├── BPMN workflow + workflow vocabulary + cases
└── semantic artifact manifest
          │
          │ pinned commit
          ▼
GerhardBalz/executable-semantic-knowledge-architecture
│
├── Semantic Capability
├── Execution / Result / Verification
├── mode-specific semantic refinements where required
├── composite execution using established part/dependency relations
├── Knowledge Service         classification only
├── Knowledge Agent           classification only
└── execution provenance
```

Two principles are executable rather than merely documented:

> **Execution must not sever semantics.**

> **Execution architecture should not become the accidental owner of domain semantics.**

## Source and License

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for the cross-repository provenance and licensing boundary.
