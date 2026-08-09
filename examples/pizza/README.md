# Pizza: executable semantic knowledge reference

This directory contains the first executable reference examples for **Executable Semantic Knowledge Architecture (ESKA)**.

The Pizza domain is used to demonstrate that different formal semantic artifacts have different operational semantics while remaining connected through the same architectural ideas.

Two execution modes are currently implemented:

```text
OWL ontology
    ↓ reason
inferred semantic knowledge

SHACL shapes graph
    ↓ validate
semantic conformance report
```

The OWL path is developed end-to-end through Capability, Service, and Agent. The SHACL path is currently developed through semantic execution, a bounded Validation Capability, verification, and provenance.

## 1. OWL classification path

The classification example asks:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that inference remain machine-traceable as it is exposed and invoked?**

The path separates four architectural concerns:

```text
Executable Semantic Knowledge
        │ performs semantic reasoning
        ▼
Semantic Capability
        │ defines the bounded ability
        ▼
Knowledge Service
        │ exposes that ability operationally
        ▼
Knowledge Agent
        │ discovers and invokes the service
        ▼
Semantic Result
```

The agent is deliberately deterministic and non-LLM. The purpose is to show that **agent accessibility can follow from machine-readable architecture rather than prompt engineering**.

### Why a derived reasoning slice?

The companion [pizza-ontology](https://github.com/GerhardBalz/pizza-ontology) repository preserves the historical Pizza ontology, including intentionally unsatisfiable teaching classes such as `IceCream` and `CheeseyVegetableTopping`.

That behavior is useful for ontology-engineering tests, but ROBOT performs logical validation before classification and therefore refuses to classify an incoherent ontology.

For this example, `spicy-pizza.ofn` is a **small coherent semantic slice** containing only the source axioms needed to demonstrate the `SpicyPizza` inference. The slice keeps the original Pizza entity IRIs and records its source and license.

This is an architectural boundary, not a new Pizza model:

```text
Pizza ontology
    │ selected semantic knowledge
    ▼
coherent reasoning slice
    │ executable with OWL semantics
    ▼
HermiT reasoner
    │
    ├── inferred classification
    ├── verification
    ├── explanation
    └── provenance
    │ bounded and described as
    ▼
PizzaClassificationCapability
    │ exposed by
    ▼
PizzaClassificationService
    │ discovered and invoked by
    ▼
PizzaKnowledgeAgent
```

### Semantic knowledge

The relevant source knowledge can be summarized as follows:

```text
AmericanHot
    SubClassOf NamedPizza
    hasTopping some JalapenoPepperTopping

NamedPizza
    SubClassOf Pizza

JalapenoPepperTopping
    SubClassOf PepperTopping
    hasSpiciness some Hot

PepperTopping
    SubClassOf PizzaTopping

SpicyTopping ≡
    PizzaTopping
    and hasSpiciness some Hot

SpicyPizza ≡
    Pizza
    and hasTopping some SpicyTopping
```

The ontology does **not** assert:

```text
AmericanHot SubClassOf SpicyPizza
```

That relationship is the result we ask the reasoner to derive.

### Executable Semantic Knowledge

Running the example turns the formal semantic definitions into computational behavior:

```text
JalapenoPepperTopping
    ↓ HermiT reasoning
SpicyTopping

AmericanHot
    ↓ hasTopping some JalapenoPepperTopping
    ↓ JalapenoPepperTopping SubClassOf SpicyTopping
    ↓ AmericanHot SubClassOf Pizza
SpicyPizza
```

The expected inferred axiom is:

```text
AmericanHot SubClassOf SpicyPizza
```

This is **Executable Semantic Knowledge**: the classification follows from machine-interpretable semantics rather than from a hard-coded `if AmericanHot then SpicyPizza` rule.

### Semantic Capability

[`pizza-classification-capability.ttl`](pizza-classification-capability.ttl) describes the bounded ability in machine-readable form.

```text
Capability
    Pizza Classification

Subject
    Pizza

Input type
    owl:Class

Output type
    owl:Class

Produced relation
    rdfs:subClassOf

Semantic model
    Spicy Pizza semantic model slice

Executable artifact
    OWL classification with HermiT

Applicability
    coherent OWL model
```

The scope is intentionally narrow: **class-level OWL classification for Pizza concepts**. Recommendation, ordering, preparation, pricing, and instance-data validation are outside this capability.

> **Capability = ability + explicit boundary + defined outcome**

The provisional capability vocabulary is in [`../../model/eska-capability.ttl`](../../model/eska-capability.ttl).

### Knowledge Service

A **Knowledge Service** provides operational access to a Capability without redefining what the Capability means.

[`pizza-classification-service.ttl`](pizza-classification-service.ttl) describes `PizzaClassificationService`; [`service.py`](service.py) implements it.

```text
Service
    Pizza Classification Knowledge Service

Exposes
    PizzaClassificationCapability

Operation
    ClassifyPizzaClassOperation

HTTP
    POST /classify

Input / output type
    owl:Class → owl:Class

Semantic relation
    rdfs:subClassOf

Representation
    application/json
```

The service contract also describes the JSON fields used to carry the semantic input, result, relation, and Capability IRI. This makes the representation discoverable by a client rather than being implicit in client code.

`service.py` does **not** contain a rule saying that `AmericanHot` is spicy. It reads superclass relationships from `results/reasoned.owl`, the artifact produced by HermiT.

```text
Capability
    defines what ability exists

Knowledge Service
    defines how the ability is accessed

OWL reasoner
    remains the source of classification behavior
```

The provisional service vocabulary is in [`../../model/eska-service.ttl`](../../model/eska-service.ttl).

### Knowledge Agent

[`pizza-knowledge-agent.ttl`](pizza-knowledge-agent.ttl) describes the first `PizzaKnowledgeAgent`; [`agent.py`](agent.py) implements it.

The agent knows the **Semantic Capability it wants**:

```text
PizzaClassificationCapability
```

It does **not** hard-code:

- `PizzaClassificationService` as the service to call;
- `/classify` as the path;
- `POST` as the HTTP method;
- `rdfs:subClassOf` as the returned semantic relation;
- the JSON request/result field names;
- `SpicyPizza` as the expected semantic answer.

Instead, [`discover-service.sparql`](discover-service.sparql) queries `results/architecture-model.owl` for a Knowledge Service operation that exposes the target Capability.

```text
PizzaKnowledgeAgent
        │ targets
        ▼
PizzaClassificationCapability
        │ machine-readable architecture query
        ▼
PizzaClassificationService
        │ has operation
        ▼
ClassifyPizzaClassOperation
        │ describes
        ├── HTTP method
        ├── path
        ├── media type
        ├── payload fields
        ├── input/output semantic types
        └── semantic result relation
```

The agent then invokes the discovered operation and checks that the service response still identifies the target Capability and the discovered semantic relation.

#### Semantic discovery vs deployment binding

The architecture describes **what the service is and how its operation behaves**. It does not claim that a service always runs at a particular host or port.

The agent receives a runtime deployment binding separately and combines it with the discovered semantic path:

```text
runtime base URL + discovered /classify
```

This keeps **architectural meaning** separate from **deployment location**.

The provisional agent vocabulary is in [`../../model/eska-agent.ttl`](../../model/eska-agent.ttl).

## 2. SHACL validation path

The second execution mode is documented in [`validation/README.md`](validation/README.md).

It asks:

> **Does a concrete Pizza RDF data graph conform to an explicit Pizza data contract?**

The executable semantic artifact is [`validation/pizza-shapes.ttl`](validation/pizza-shapes.ttl), not a procedural validation function.

The initial shape requires each concrete `pizza:Pizza` node to have:

- exactly one `pizza:hasBase` value of type `pizza:PizzaBase`;
- at least one `pizza:hasTopping` value of type `pizza:PizzaTopping`.

Two data cases make the semantics visible:

```text
valid-pizza.ttl
    ↓ SHACL validation
sh:conforms true

invalid-pizza.ttl
    has two hasBase values
    ↓ SHACL validation
sh:conforms false
    + sh:MaxCountConstraintComponent
```

[`validation/pizza-validation-capability.ttl`](validation/pizza-validation-capability.ttl) describes this as a separate bounded Semantic Capability:

```text
PizzaValidationCapability

Input
    Pizza RDF data graph

Output
    sh:ValidationReport

Produced relation
    sh:conforms

Semantic model
    Pizza SHACL shapes graph

Executable artifact
    SHACL validation with pySHACL
```

This is intentionally different from `PizzaClassificationCapability`:

```text
PizzaClassificationCapability
    OWL entailment
    → rdfs:subClassOf

PizzaValidationCapability
    SHACL constraint evaluation
    → sh:ValidationReport / sh:conforms
```

The comparison tests an important ESKA principle: **executable** does not mean one universal execution technology. Execution depends on the semantic artifact type.

## Execute

Requirements for the classification path:

- Java 17 or newer
- Python 3
- `curl`

### Build and verify the OWL architecture

```bash
bash examples/pizza/run.sh
```

The script performs seven steps:

1. classify `spicy-pizza.ofn` with HermiT;
2. verify the expected `AmericanHot → SpicyPizza` inference;
3. generate a reasoner explanation;
4. verify the Semantic Capability contract;
5. verify the Knowledge Service contract;
6. build and verify the merged Knowledge Agent architecture model;
7. write PROV-O reasoning provenance.

Generated artifacts are written below `examples/pizza/results/` and are intentionally not committed.

### Run the complete Knowledge Agent path

```bash
bash examples/pizza/test-agent.sh
```

This builds the semantic architecture, starts the service, discovers the operation through SPARQL, invokes it, validates semantic continuity, checks the result, and writes agent invocation provenance.

### Run SHACL validation

Install the pinned validation dependency:

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
```

Then run:

```bash
python examples/pizza/validation/validate.py
```

This verifies the `PizzaValidationCapability` contract, validates both the conforming and non-conforming data graphs, checks the expected violation, and writes validation provenance.

GitHub Actions runs both the full OWL/Agent path and the SHACL validation path.

## Verification

The project now asks two groups of regression questions.

### Classification architecture

```text
Does semantic reasoning produce the correct result?

Is the bounded ability explicitly described?

Is the service contract explicit and semantically connected?

Can an agent discover how to access that Capability?

Does runtime invocation preserve the semantic contract and result?
```

### Validation architecture

```text
Is PizzaValidationCapability explicitly described?

Does conforming Pizza data produce sh:conforms true?

Does non-conforming Pizza data produce sh:conforms false?

Does the report identify the expected semantic constraint violation?

Is validation execution provenance recorded separately?
```

## Explanation and provenance

The classification path keeps knowledge derivation and agent invocation separate:

- `results/explanation.md` explains the OWL entailment;
- `results/provenance.ttl` records reasoning provenance;
- `results/agent-provenance.ttl` records Knowledge Agent discovery/invocation.

The validation path independently writes:

- `validation/results/valid-report.ttl`;
- `validation/results/invalid-report.ttl`;
- `validation/results/provenance.ttl`.

This avoids conflating different execution activities merely because they operate in the same Pizza domain.

## ESKA concepts demonstrated

| ESKA concept | Pizza realization |
| --- | --- |
| Semantic Model | Pizza OWL model and Pizza SHACL shapes graph |
| Semantic Knowledge | Selected Pizza axioms and concrete Pizza RDF data |
| Executable Semantic Knowledge | OWL reasoning and SHACL validation |
| Executable Semantic Knowledge Artifact | HermiT classification and pySHACL validation artifacts |
| Capability | Bounded Pizza Classification and Pizza Validation abilities |
| Semantic Capability | `PizzaClassificationCapability` and `PizzaValidationCapability` |
| Knowledge Service | Machine-readable and executable `PizzaClassificationService` |
| Knowledge Agent | Deterministic `PizzaKnowledgeAgent` with semantic service discovery |
| Verification | SPARQL contract checks, runtime integration, SHACL positive/negative tests |
| Explanation | Reasoner explanation for the inferred subclass axiom |
| Provenance | Separate PROV-O records for reasoning, agent invocation, and validation |

The repository now demonstrates that the ESKA concepts can span more than one execution mode. The next architectural work should generalize only those concepts that remain stable across reasoning and validation, rather than assuming the OWL classification path is universal.

## Source and license

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for provenance and licensing of the Pizza semantic material used by this example.
