# Pizza: executable semantic knowledge reference

This directory contains the executable Pizza reference examples for **Executable Semantic Knowledge Architecture (ESKA)**.

The Pizza domain demonstrates different formal execution semantics while testing a strict repository boundary:

```text
pizza-ontology
    owns Pizza domain semantics
        ↓ immutable commit + artifact manifest
ESKA
    operationalizes those semantics
```

ESKA does not maintain source copies of the Pizza OWL module, SHACL profile/data, SPARQL rule/vocabulary/data, or DMN decision artifacts used here. [`pizza-domain-source.json`](pizza-domain-source.json) pins `GerhardBalz/pizza-ontology` to an immutable Git commit, and [`fetch-domain-artifacts.py`](fetch-domain-artifacts.py) materializes the published artifacts under `.work/pizza-domain/` at execution time.

## Semantic source binding

```text
Repository
    GerhardBalz/pizza-ontology

Commit
    983b691d9d2102ffad97a3ec31aa9b1435b3e547

Manifest
    artifacts/manifest.ttl
```

The manifest publishes ten source-owned semantic distributions consumed by this reference:

- coherent Pizza OWL reasoning module;
- Pizza instance SHACL profile;
- conforming RDF validation example;
- non-conforming RDF validation example;
- vegetarian-warning SPARQL rule;
- rule-result vocabulary;
- rule-evaluation RDF data;
- DMN 1.5 dietary-suitability decision table;
- decision outcome vocabulary;
- canonical decision-input cases.

```text
artifact role/path
        +
pinned Git commit
        ↓
immutable semantic input
```

Runtime copies beneath `.work/` are disposable execution inputs, not a second semantic source of truth.

## Four execution modes

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
```

The OWL path is developed end-to-end through Capability, Service, and Agent. The SHACL, Rule, and Decision paths stay at the Semantic Capability / Execution / Result / Verification level so Service and Agent are not promoted by symmetry.

## 1. OWL classification path

The classification example asks:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that inference remain machine-traceable as it is exposed and invoked?**

The source-owned coherent module contains the relevant Pizza axioms but does **not** assert:

```text
AmericanHot SubClassOf SpicyPizza
```

HermiT derives that relation through OWL semantics.

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

[`pizza-classification-capability.ttl`](pizza-classification-capability.ttl) describes the bounded ability:

```text
Input / output
    owl:Class → owl:Class

Produced relation
    rdfs:subClassOf

Semantic model
    commit-pinned Pizza reasoning module

Executable artifact
    OWL classification with HermiT

Applicability
    coherent OWL model
```

### Knowledge Service

[`pizza-classification-service.ttl`](pizza-classification-service.ttl) describes `PizzaClassificationService`; [`service.py`](service.py) implements it.

The Service exposes the Capability without reimplementing Pizza classification semantics. It reads the reasoned output produced from the pinned semantic artifact.

### Knowledge Agent

[`pizza-knowledge-agent.ttl`](pizza-knowledge-agent.ttl) describes the deterministic `PizzaKnowledgeAgent`; [`agent.py`](agent.py) implements it.

The Agent knows the Capability it wants but does not hard-code the Service, path, HTTP method, result relation, representation fields, or expected `SpicyPizza` answer. [`discover-service.sparql`](discover-service.sparql) discovers the operation from the machine-readable architecture model.

This keeps semantic discovery separate from runtime deployment binding.

## 2. SHACL validation path

The validation mode is documented in [`validation/README.md`](validation/README.md).

> **Does concrete Pizza RDF data conform to the Pizza validation profile published by the domain repository?**

The source-owned non-conforming fixture deliberately:

- omits `pizza:hasBase`, producing a `sh:MinCountConstraintComponent` result;
- references a value not typed as `pizza:PizzaTopping`, producing a `sh:ClassConstraintComponent` result.

[`validation/pizza-validation-capability.ttl`](validation/pizza-validation-capability.ttl) describes:

```text
PizzaValidationCapability

Input
    Pizza RDF data graph

Output
    sh:ValidationReport

Produced relation
    sh:conforms

Semantic model
    commit-pinned Pizza SHACL profile

Executable artifact
    SHACL validation with pySHACL
```

## 3. SPARQL rule evaluation path

The Rule mode is documented in [`rules/README.md`](rules/README.md).

> **Can a source-owned semantic rule be evaluated deterministically and produce a machine-traceable derived result?**

The source-owned SPARQL 1.1 `CONSTRUCT` rule evaluates:

```text
Pizza
    hasTopping topping
    topping a MeatTopping
        ↓ evaluate
requiresVegetarianWarning true
```

[`rules/pizza-rule-evaluation-capability.ttl`](rules/pizza-rule-evaluation-capability.ttl) describes:

```text
PizzaRuleEvaluationCapability

Input
    explicit Pizza RDF data graph

Output
    derived RDF result graph

Produced relation
    urn:pizza-ontology:rule:requiresVegetarianWarning

Semantic model
    commit-pinned SPARQL CONSTRUCT rule

Executable artifact
    SPARQL evaluation with RDFLib

Applicability
    explicit RDF assertions; no implicit OWL entailment
```

The mode performs neither OWL inference nor SHACL validation.

## 4. DMN decision path

The Decision mode is documented in [`decisions/README.md`](decisions/README.md).

> **Can a source-owned formal decision model select semantic outcomes while remaining inside the same ESKA execution architecture?**

The source-owned OMG DMN 1.5 `UNIQUE` decision table consumes explicit boolean inputs:

```text
containsMeat  containsFish  → dietarySuitability
true          -             → NotVegetarian
false         true          → PescatarianOnly
false         false         → Vegetarian
```

[`decisions/pizza-dietary-suitability-capability.ttl`](decisions/pizza-dietary-suitability-capability.ttl) describes:

```text
PizzaDietarySuitabilityCapability

Input
    explicit decision context

Output
    decision:DietarySuitabilityOutcome

Produced relation
    decision:dietarySuitability

Semantic model
    commit-pinned DMN 1.5 decision table

Executable artifact
    canonical DMN decision evaluator

Applicability
    explicit containsMeat / containsFish booleans
```

The three canonical decision contexts produce:

```text
meatyPizza       → decision:NotVegetarian
fishPizza        → decision:PescatarianOnly
vegetarianPizza  → decision:Vegetarian
```

Each case produces a separate semantic `Result` and its own `Execution → Result → Verification` provenance chain.

## Execute

Requirements:

- Java 17 or newer for the OWL/ROBOT path;
- Python 3;
- network access to retrieve the commit-pinned public Pizza artifacts;
- `curl` for the pinned ROBOT download.

### OWL architecture

```bash
bash examples/pizza/run.sh
```

### Complete Knowledge Agent path

```bash
bash examples/pizza/test-agent.sh
```

### SHACL validation

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
python examples/pizza/validation/validate.py
```

### SPARQL rule evaluation

```bash
python -m pip install -r examples/pizza/rules/requirements.txt
python examples/pizza/rules/evaluate.py
```

### DMN decision evaluation

```bash
python -m pip install -r examples/pizza/decisions/requirements.txt
python examples/pizza/decisions/evaluate.py
```

The Decision runner materializes the pinned domain contract, verifies `PizzaDietarySuitabilityCapability`, evaluates all three canonical DMN contexts, validates the selected semantic outcomes, writes the RDF result graph, and records source-aware PROV-O provenance.

## Cross-mode core verification

The generic Capability verifier now checks the same contract across **four Capabilities**:

- `PizzaClassificationCapability`;
- `PizzaValidationCapability`;
- `PizzaRuleEvaluationCapability`;
- `PizzaDietarySuitabilityCapability`.

The generic runtime verifier checks the same pattern across **seven concrete executions**:

- one OWL reasoning execution;
- two SHACL validation executions;
- one SPARQL rule execution;
- three DMN decision executions.

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

`model/eska-core.ttl` required **no change** for either the Rule or Decision falsification modes.

No `Rule`, `RuleExecution`, `Decision`, `DecisionExecution`, `DecisionResult`, generic `ExecutionMode`, or new ESKA provenance hierarchy was introduced into core.

## Verification questions

The reference now checks:

```text
Is the domain artifact pinned to an immutable Pizza commit?

Does the pinned Pizza manifest still publish the expected role/path contract?

Does OWL reasoning produce the expected inference?

Does the classification Capability remain agent-accessible through the Service?

Does SHACL validation distinguish the positive and negative data?

Does SPARQL rule evaluation produce the expected derived statement and preserve its control case?

Does DMN select exactly one expected semantic outcome per decision context?

Do all four Capabilities satisfy the same generic core contract?

Do all seven executions satisfy the same Execution → Result → Verification pattern?

Do provenance records retain the source artifact identity?
```

## Ownership boundary

```text
GerhardBalz/pizza-ontology
│
├── Pizza Ontology 2.0 preservation source
├── coherent OWL reasoning module
├── SHACL validation profile + RDF cases
├── SPARQL rule + result vocabulary + RDF data
├── DMN decision + outcome vocabulary + decision cases
└── semantic artifact manifest
          │
          │ pinned commit
          ▼
GerhardBalz/executable-semantic-knowledge-architecture
│
├── Semantic Capability
├── Execution / Result / Verification
├── Knowledge Service         classification only
├── Knowledge Agent           classification only
└── execution provenance
```

Two principles are executable rather than merely documented:

> **Execution must not sever semantics.**

> **Execution architecture should not become the accidental owner of domain semantics.**

## Source and license

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for the cross-repository provenance and licensing boundary.
