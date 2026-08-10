# Pizza: executable semantic knowledge reference

This directory contains the executable reference examples for **Executable Semantic Knowledge Architecture (ESKA)**.

The Pizza domain demonstrates different formal execution semantics while also testing an important repository boundary:

```text
pizza-ontology
    owns Pizza domain semantics
        ↓ immutable commit + artifact manifest
ESKA
    operationalizes those semantics
```

ESKA does not store copies of the Pizza reasoning module, SHACL profile, validation data, rule query, rule vocabulary, or rule data used by this example. [`pizza-domain-source.json`](pizza-domain-source.json) pins `GerhardBalz/pizza-ontology` to an immutable Git commit, and [`fetch-domain-artifacts.py`](fetch-domain-artifacts.py) materializes the published artifacts under `.work/pizza-domain/` at execution time.

Three execution modes are implemented:

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
```

The OWL path is developed end-to-end through Capability, Service, and Agent. The SHACL and rule paths are developed through semantic execution, bounded Semantic Capabilities, verification, and provenance without adding Service or Agent layers.

## Semantic source binding

The current binding records:

```text
Repository
    GerhardBalz/pizza-ontology

Commit
    bba9fa883f326ebeb395140abd523dc517caf071

Manifest
    artifacts/manifest.ttl
```

The manifest publishes seven domain artifacts used here:

- coherent Pizza reasoning module;
- Pizza instance SHACL profile;
- conforming RDF validation example;
- non-conforming RDF validation example;
- vegetarian-warning SPARQL rule;
- rule result vocabulary;
- rule evaluation RDF data.

The combination of a stable role/path contract and immutable Git commit creates the actual execution binding:

```text
artifact role/path
        +
pinned Git commit
        ↓
immutable semantic input
```

Runtime copies beneath `.work/` are disposable materializations, not a second semantic source of truth.

## 1. OWL classification path

The classification example asks:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that inference remain machine-traceable as it is exposed and invoked?**

The domain-owned coherent module contains the relevant Pizza axioms but does **not** assert:

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

### Semantic Capability

[`pizza-classification-capability.ttl`](pizza-classification-capability.ttl) defines the bounded ESKA ability:

```text
Capability
    Pizza Classification

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

The **Semantic Model is source-owned by `pizza-ontology`**. The Capability and executable classification mechanism are ESKA architecture.

### Knowledge Service

[`pizza-classification-service.ttl`](pizza-classification-service.ttl) describes `PizzaClassificationService`; [`service.py`](service.py) implements it.

The service exposes `PizzaClassificationCapability` without reimplementing Pizza classification semantics. It reads the reasoned output produced from the pinned OWL artifact.

```text
Capability
    defines what ability exists

Knowledge Service
    defines how the ability is accessed

OWL semantic artifact + reasoner
    remain the source of classification behavior
```

### Knowledge Agent

[`pizza-knowledge-agent.ttl`](pizza-knowledge-agent.ttl) describes the deterministic `PizzaKnowledgeAgent`; [`agent.py`](agent.py) implements it.

The agent knows the Capability it wants but does not hard-code the Service, path, HTTP method, result relation, representation fields, or expected `SpicyPizza` answer. [`discover-service.sparql`](discover-service.sparql) discovers the operation from the machine-readable architecture model.

This keeps semantic discovery separate from runtime deployment binding:

```text
machine-readable ESKA architecture
        ↓ discover
Knowledge Agent
        +
runtime service base URL
        ↓ bind
service invocation
```

## 2. SHACL validation path

The second execution mode is documented in [`validation/README.md`](validation/README.md).

It asks:

> **Does concrete Pizza RDF data conform to the Pizza validation profile published by the domain repository?**

The SHACL profile requires an explicit Pizza node to have exactly one Pizza base and at least one correctly typed Pizza topping.

The source-owned non-conforming fixture deliberately omits a base and references a non-topping value through `hasTopping`, so ESKA verifies:

```text
pizza:hasBase
    sh:MinCountConstraintComponent

pizza:hasTopping
    sh:ClassConstraintComponent
```

[`validation/pizza-validation-capability.ttl`](validation/pizza-validation-capability.ttl) describes the bounded execution ability:

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

This is intentionally different from OWL classification:

```text
OWL entailment              → inferred semantic relation
SHACL constraint evaluation → conformance report
```

## 3. SPARQL rule evaluation path

The third execution mode is documented in [`rules/README.md`](rules/README.md).

It asks:

> **Can a source-owned semantic rule be evaluated deterministically and produce a machine-traceable derived result?**

The Pizza repository publishes a SPARQL 1.1 `CONSTRUCT` rule, a result vocabulary, and explicit RDF data. The rule evaluates:

```text
Pizza
    hasTopping topping
    topping a MeatTopping
        ↓ evaluate
requiresVegetarianWarning true
```

The published data contains a matching meat-topping Pizza and a vegetable-only control. ESKA requires exactly one warning result and verifies that the vegetable control produces none.

[`rules/pizza-rule-evaluation-capability.ttl`](rules/pizza-rule-evaluation-capability.ttl) describes the bounded ability:

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

The mode deliberately performs neither OWL inference nor SHACL validation:

```text
OWL ontology     → reason   → inferred axiom
SHACL constraint → validate → validation report
SPARQL rule      → evaluate → derived RDF statement
```

## Execute

Requirements for the classification path:

- Java 17 or newer;
- Python 3;
- network access to retrieve the commit-pinned public Pizza artifacts;
- `curl` for the pinned ROBOT download.

### Build and verify the OWL architecture

```bash
bash examples/pizza/run.sh
```

The script:

1. fetches the pinned Pizza artifact contract and semantic inputs;
2. classifies the source-owned reasoning module with HermiT;
3. verifies `AmericanHot → SpicyPizza`;
4. generates a reasoner explanation;
5. verifies the Semantic Capability contract;
6. verifies the Knowledge Service contract;
7. builds and verifies the Knowledge Agent architecture;
8. records reasoning provenance including the pinned Pizza source artifact.

### Run the complete Knowledge Agent path

```bash
bash examples/pizza/test-agent.sh
```

This runs semantic reasoning, starts the service, discovers the service operation, invokes it, validates semantic continuity, checks the result, and records agent invocation provenance.

### Run SHACL validation

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
python examples/pizza/validation/validate.py
```

The validation script fetches the same pinned Pizza contract, verifies `PizzaValidationCapability`, evaluates the source-owned positive/negative data, and records source-aware validation provenance.

### Run SPARQL rule evaluation

```bash
python -m pip install -r examples/pizza/rules/requirements.txt
python examples/pizza/rules/evaluate.py
```

The rule runner materializes the same pinned domain contract, verifies `PizzaRuleEvaluationCapability`, evaluates the source-owned SPARQL rule, checks the positive/control outcomes, and records rule execution and verification provenance.

## Cross-mode core verification

The third mode was introduced as a falsification test for the provisional ESKA core.

[`verify-core.sparql`](verify-core.sparql) now verifies the same Capability contract across:

- `PizzaClassificationCapability`;
- `PizzaValidationCapability`;
- `PizzaRuleEvaluationCapability`.

[`verify-core-executions.sparql`](verify-core-executions.sparql) verifies the same runtime pattern across four concrete executions:

- OWL reasoning;
- conforming SHACL validation;
- non-conforming SHACL validation;
- SPARQL rule evaluation.

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

`model/eska-core.ttl` required **no change** for the third mode. No `Rule`, `RuleExecution`, `ExecutionMode`, rule-specific result superclass, or new ESKA provenance hierarchy was introduced.

## Verification

The reference verifies both **semantic execution** and **semantic source ownership**:

```text
Is the domain artifact pinned to an immutable Pizza commit?

Does the pinned Pizza manifest still publish the expected role/path contract?

Does OWL reasoning produce the expected result?

Does the classification Capability remain explicit and agent-accessible?

Does SHACL validation distinguish the published positive and negative data?

Does rule evaluation produce the published rule outcome while preserving the control case?

Do all three Capabilities satisfy the same generic core contract?

Do all concrete executions satisfy the same Execution → Result → Verification pattern?

Do execution provenance records retain the source artifact identity?
```

## Ownership boundary

The architecture after this integration is:

```text
GerhardBalz/pizza-ontology
│
├── Pizza Ontology 2.0 preservation source
├── coherent reasoning module
├── Pizza SHACL validation profile
├── Pizza validation example data
├── SPARQL rule + result vocabulary
├── Pizza rule evaluation data
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

This makes two central ESKA principles concrete:

> **Execution must not sever semantics.**

> **Execution architecture should not become the accidental owner of domain semantics.**

## Source and license

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for the cross-repository provenance and licensing boundary.
