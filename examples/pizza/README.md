# Pizza: executable semantic knowledge to Knowledge Agent

This example is the first executable vertical slice of **Executable Semantic Knowledge Architecture (ESKA)**.

It starts with one small semantic question:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that inference remain machine-traceable as it is exposed and invoked?**

The example now separates four architectural concerns:

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

## Why a derived slice?

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

## Semantic knowledge

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

## Executable Semantic Knowledge

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

## Semantic Capability

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

## Knowledge Service

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

### The service is intentionally thin

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

## Knowledge Agent

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

The discovery path is:

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

### Semantic discovery vs deployment binding

The architecture describes **what the service is and how its operation behaves**. It does not claim that a service always runs at a particular host or port.

The agent therefore receives a runtime deployment binding separately, for example:

```text
http://127.0.0.1:18081
```

and combines it with the discovered semantic path:

```text
runtime base URL + discovered /classify
```

This keeps **architectural meaning** separate from **deployment location**.

The provisional agent vocabulary is in [`../../model/eska-agent.ttl`](../../model/eska-agent.ttl).

## Execute

Requirements:

- Java 17 or newer
- Python 3
- `curl`

### Build and verify the semantic architecture

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

This:

1. builds and verifies the semantic architecture;
2. starts `PizzaClassificationService`;
3. runs `PizzaKnowledgeAgent` with `AmericanHot` as input;
4. discovers the service operation through SPARQL;
5. invokes the discovered HTTP operation;
6. validates semantic continuity in the response;
7. verifies that the semantic result contains `SpicyPizza`;
8. writes agent invocation provenance.

GitHub Actions runs this same end-to-end path.

## Verification

The example now verifies four model-level contracts plus runtime behavior.

### Inference

`verify-spicy.sparql` fails if OWL reasoning no longer derives:

```text
AmericanHot SubClassOf SpicyPizza
```

### Semantic Capability

`verify-capability.sparql` fails if the bounded ability loses required semantic contract elements.

### Knowledge Service

`verify-service.sparql` fails if the service no longer exposes the intended Capability, semantic types, relation, HTTP operation, or representation fields.

### Knowledge Agent

`verify-agent.sparql` fails if the agent no longer targets the intended Capability or loses its machine-described discovery artifact.

### Runtime integration

`test-agent.sh` verifies that a running agent can discover and invoke the service while preserving the same Capability and semantic relation through the complete path.

So the regression questions now become:

```text
Does semantic reasoning produce the correct result?

Is the bounded ability explicitly described?

Is the service contract explicit and semantically connected?

Can an agent discover how to access that Capability?

Does runtime invocation preserve the semantic contract and result?
```

## Explanation and provenance

ROBOT generates `results/explanation.md` for the inferred subclass axiom.

`results/provenance.ttl` records the OWL reasoning activity and connects it to the Pizza semantic source and `PizzaClassificationCapability`.

`results/agent-provenance.ttl` separately records the Knowledge Agent discovery/invocation activity. Keeping these records separate avoids conflating **knowledge derivation** with **agent/service invocation**.

## ESKA concepts demonstrated

| ESKA concept | Pizza realization |
| --- | --- |
| Semantic Model | Pizza OWL classes, properties, and class expressions |
| Semantic Knowledge | Selected Pizza axioms in `spicy-pizza.ofn` |
| Executable Semantic Knowledge | OWL classification performed by HermiT |
| Executable Semantic Knowledge Artifact | OWL classification artifact identified by the Capability contract |
| Capability | Bounded Pizza Classification ability |
| Semantic Capability | Machine-readable `PizzaClassificationCapability` |
| Knowledge Service | Machine-readable and executable `PizzaClassificationService` |
| Knowledge Agent | Deterministic `PizzaKnowledgeAgent` with semantic service discovery |
| Verification | SPARQL contract checks plus end-to-end runtime integration |
| Explanation | Reasoner explanation for the inferred subclass axiom |
| Provenance | Separate PROV-O records for reasoning and agent invocation |

This completes the first end-to-end reference path from formal semantic knowledge to agent-accessible operational knowledge. It is still deliberately small: later increments can add semantic validation, richer provenance, generalized ESKA vocabulary, additional capabilities, and alternative service or agent implementations.

## Source and license

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for provenance and licensing of the Pizza semantic material used by this example.
