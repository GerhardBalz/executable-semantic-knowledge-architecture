# Pizza: executable semantic knowledge and capability slice

This example is the first executable vertical slice of **Executable Semantic Knowledge Architecture (ESKA)**.

It starts with one small semantic question:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that inference be verified, explained, and traced to its semantic source?**

It now also defines the bounded ability that performs this kind of work as a machine-readable **Semantic Capability**:

> **Pizza Classification — determine semantically entailed class-level classifications for Pizza classes using the Pizza semantic model.**

The example intentionally stops at Capability. Knowledge Service exposure and Knowledge Agent discovery or invocation are deferred to later increments.

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

## Execute

Requirements:

- Java 17 or newer
- `curl`

Run:

```bash
bash examples/pizza/run.sh
```

The script downloads the pinned ROBOT release on first execution and then performs five steps:

1. classify `spicy-pizza.ofn` with the HermiT OWL reasoner;
2. verify that `AmericanHot rdfs:subClassOf SpicyPizza` is present in the reasoned ontology;
3. generate a ROBOT explanation for that inferred axiom;
4. merge and verify the ESKA Capability model and `PizzaClassificationCapability` contract;
5. write a PROV-O execution record connected to the Capability.

Generated files are written below `examples/pizza/results/` and are intentionally not committed.

## Verification

There are now two semantic regression checks.

### Inference verification

`verify-spicy.sparql` is expressed as a negative test: it returns a violation only when the expected inferred subclass relationship is missing.

Therefore the example fails if semantic execution no longer produces:

```text
AmericanHot SubClassOf SpicyPizza
```

### Capability verification

`verify-capability.sparql` verifies the machine-readable Capability contract. It fails if required facts such as the subject, input/output type, produced relation, semantic model, executable artifact, applicability condition, or example outcome disappear.

The tests therefore verify both:

```text
Does the semantic execution still produce the expected result?

and

Is the bounded ability still explicitly described as the intended Semantic Capability?
```

## Explanation

ROBOT's explanation step asks the reasoner why this entailment holds:

```text
AmericanHot SubClassOf SpicyPizza
```

The generated `results/explanation.md` contains a minimal set of semantic axioms sufficient to justify the inference.

This is a concrete form of the ESKA principle that a result should remain traversable back toward the knowledge that gives it meaning.

## Provenance

`results/provenance.ttl` records the execution using PROV-O concepts and states that the reasoning activity conforms to `PizzaClassificationCapability`.

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

The record includes:

- the source Pizza ontology URL;
- the Git blob identifier of the source artifact used to construct the slice;
- ROBOT and HermiT as the software execution mechanism;
- the Semantic Capability to which the execution conforms;
- the inferred RDF statement;
- the execution timestamp.

This remains intentionally modest provenance. Later ESKA increments can formalize richer knowledge, verification, capability, and execution lineage.

## ESKA concepts demonstrated

| ESKA concept | Pizza realization |
| --- | --- |
| Semantic Model | Pizza OWL classes, properties, and class expressions |
| Semantic Knowledge | The selected Pizza axioms in `spicy-pizza.ofn` |
| Executable Semantic Knowledge | OWL classification performed by HermiT |
| Executable Semantic Knowledge Artifact | OWL classification with HermiT, identified in the Capability contract |
| Capability | Bounded Pizza Classification ability |
| Semantic Capability | Machine-readable `PizzaClassificationCapability` |
| Verification | SPARQL verification of inference and Capability contract |
| Explanation | Reasoner explanation for the inferred subclass axiom |
| Provenance | PROV-O record connecting execution, Capability, source, and result |

Not yet demonstrated:

- Knowledge Service exposure;
- Knowledge Agent discovery or invocation.

Those are the next architectural layers after the Capability boundary has been tested.

## Source and license

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for provenance and licensing of the Pizza semantic material used by this example.
