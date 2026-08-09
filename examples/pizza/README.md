# Pizza: executable semantic knowledge, capability, and service slice

This example is the first executable vertical slice of **Executable Semantic Knowledge Architecture (ESKA)**.

It starts with one small semantic question:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that inference be verified, explained, traced, and exposed without duplicating the semantic logic?**

The example now separates three architectural concerns:

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
HTTP client
```

Knowledge Agent discovery and invocation remain deferred to a later increment.

## Why a derived slice?

The companion [pizza-ontology](https://github.com/GerhardBalz/pizza-ontology) repository preserves the historical Pizza ontology, including intentionally unsatisfiable teaching classes such as `IceCream` and `CheeseyVegetableTopping`.

That behavior is useful for ontology-engineering tests, but ROBOT performs logical validation before classification and therefore refuses to classify an incoherent ontology.

For this example, `spicy-pizza.ofn` is a **small coherent semantic slice** containing only the source axioms needed to demonstrate the `SpicyPizza` inference. The slice keeps the original Pizza entity IRIs and records its source and license.

This is an architectural boundary, not a new Pizza model:

```text
Pizza ontology
    │
    │ selected semantic knowledge
    ▼
coherent reasoning slice
    │
    │ executable with OWL semantics
    ▼
HermiT reasoner
    │
    ├── inferred classification
    ├── verification
    ├── explanation
    └── execution provenance
    │
    │ bounded and described as
    ▼
PizzaClassificationCapability
    │
    │ exposed by
    ▼
PizzaClassificationService
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

## Executable semantic knowledge

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

A Capability is useful only when its boundary is sufficiently explicit. The example therefore describes `PizzaClassificationCapability` in [`pizza-classification-capability.ttl`](pizza-classification-capability.ttl).

The contract states, in machine-readable form:

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

Example input
    AmericanHot

Example output
    SpicyPizza
```

The human-readable scope note narrows the initial capability further: it covers **class-level OWL classification for Pizza concepts** and excludes recommendation, ordering, preparation, pricing, and instance-data validation.

This is the practical meaning of a bounded Capability in ESKA:

> **Capability = ability + explicit boundary + defined outcome**

The current vocabulary for describing this contract is deliberately small and provisional. [`../../model/eska-capability.ttl`](../../model/eska-capability.ttl) contains only the ESKA terms needed for this example. It uses the provisional `urn:eska:core:` namespace rather than claiming a permanent public ESKA namespace prematurely.

## Knowledge Service

A **Knowledge Service** provides operational access to a Capability without redefining what that Capability means.

The example describes `PizzaClassificationService` in [`pizza-classification-service.ttl`](pizza-classification-service.ttl) and implements it in [`service.py`](service.py).

Its initial access contract is deliberately small:

```text
Service
    Pizza Classification Knowledge Service

Exposes Capability
    PizzaClassificationCapability

Operation
    ClassifyPizzaClassOperation

HTTP
    POST /classify

Input
    OWL Pizza class IRI

Output
    entailed OWL superclass IRIs

Semantic relation
    rdfs:subClassOf

Representation
    application/json
```

For example:

```json
{
  "class": "http://www.co-ode.org/ontologies/pizza/pizza.owl#AmericanHot"
}
```

returns classifications containing:

```text
http://www.co-ode.org/ontologies/pizza/pizza.owl#SpicyPizza
```

### The service is intentionally thin

`service.py` does **not** contain a rule saying that `AmericanHot` is spicy. It reads the superclass relationships from `results/reasoned.owl`, the semantic artifact produced by HermiT.

Therefore:

```text
Capability
    defines what ability exists

Knowledge Service
    defines how the ability is accessed

OWL reasoner
    remains the source of the classification behavior
```

This is another concrete application of the ESKA principle:

> **Execution must not sever semantics.**

The transport layer must not silently become a second, disconnected source of domain knowledge.

The provisional service vocabulary is in [`../../model/eska-service.ttl`](../../model/eska-service.ttl). As with the Capability model, it formalizes only the concepts required by the current executable example.

## Execute

Requirements:

- Java 17 or newer
- Python 3
- `curl`

### Semantic execution and contract verification

Run:

```bash
bash examples/pizza/run.sh
```

The script downloads the pinned ROBOT release on first execution and then performs six steps:

1. classify `spicy-pizza.ofn` with the HermiT OWL reasoner;
2. verify that `AmericanHot rdfs:subClassOf SpicyPizza` is present in the reasoned ontology;
3. generate a ROBOT explanation for that inferred axiom;
4. merge and verify the ESKA Capability model and `PizzaClassificationCapability` contract;
5. merge and verify the ESKA Service model and `PizzaClassificationService` contract;
6. write a PROV-O execution record connected to the Capability.

Generated files are written below `examples/pizza/results/` and are intentionally not committed.

### End-to-end Knowledge Service test

Run:

```bash
bash examples/pizza/test-service.sh
```

This runs the semantic execution, starts the HTTP service, retrieves the runtime service contract, calls `POST /classify`, and verifies that the response:

- identifies `PizzaClassificationService`;
- identifies `PizzaClassificationCapability`;
- preserves the `rdfs:subClassOf` semantic relation;
- accepts `AmericanHot` as the input class;
- contains `SpicyPizza` among the classifications.

GitHub Actions runs this same end-to-end path.

## Verification

There are now three model-level regression checks plus the runtime service test.

### Inference verification

`verify-spicy.sparql` fails if semantic execution no longer produces:

```text
AmericanHot SubClassOf SpicyPizza
```

### Capability verification

`verify-capability.sparql` fails if required facts such as the subject, input/output type, produced relation, semantic model, executable artifact, applicability condition, or example outcome disappear.

### Knowledge Service verification

`verify-service.sparql` fails if the service no longer:

- has type `KnowledgeService`;
- exposes `PizzaClassificationCapability`;
- provides `ClassifyPizzaClassOperation`;
- declares `POST /classify`;
- accepts and returns OWL classes;
- preserves `rdfs:subClassOf` as the result relation.

The end-to-end test then checks that the running service honors that contract.

The project therefore verifies increasingly different architectural invariants:

```text
Does semantic reasoning produce the correct result?

Is the bounded ability explicitly described?

Is the operational service contract explicitly described?

Does the running service expose the same Capability and semantic result?
```

## Explanation

ROBOT's explanation step asks the reasoner why this entailment holds:

```text
AmericanHot SubClassOf SpicyPizza
```

The generated `results/explanation.md` contains a minimal set of semantic axioms sufficient to justify the inference.

This is a concrete form of the ESKA principle that a result should remain traversable back toward the knowledge that gives it meaning.

## Provenance

`results/provenance.ttl` records the reasoning execution using PROV-O concepts and states that the reasoning activity conforms to `PizzaClassificationCapability`.

```text
Pizza semantic slice
        │ prov:used
        ▼
Reasoning activity
        │ dcterms:conformsTo
        ├──────────────────────► PizzaClassificationCapability
        │
        │ prov:generated
        ▼
Inferred statement
        │ prov:wasDerivedFrom
        ▼
Pizza source ontology
```

The service returns the Capability IRI and the reasoned semantic artifact used for its result. Service-invocation provenance is intentionally left for a later increment rather than being conflated with reasoning provenance.

## ESKA concepts demonstrated

| ESKA concept | Pizza realization |
| --- | --- |
| Semantic Model | Pizza OWL classes, properties, and class expressions |
| Semantic Knowledge | The selected Pizza axioms in `spicy-pizza.ofn` |
| Executable Semantic Knowledge | OWL classification performed by HermiT |
| Executable Semantic Knowledge Artifact | OWL classification with HermiT, identified in the Capability contract |
| Capability | Bounded Pizza Classification ability |
| Semantic Capability | Machine-readable `PizzaClassificationCapability` |
| Knowledge Service | Machine-readable and executable `PizzaClassificationService` |
| Verification | SPARQL verification of inference, Capability, and Service contracts plus HTTP integration test |
| Explanation | Reasoner explanation for the inferred subclass axiom |
| Provenance | PROV-O record connecting execution, Capability, source, and result |

Not yet demonstrated:

- Knowledge Agent discovery and invocation.

That is the next architectural layer after the service boundary has been tested.

## Source and license

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for provenance and licensing of the Pizza semantic material used by this example.
