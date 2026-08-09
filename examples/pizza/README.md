# Pizza: first executable semantic knowledge slice

This example is the first executable vertical slice of **Executable Semantic Knowledge Architecture (ESKA)**.

It deliberately answers one small question:

> **Can `AmericanHot` be inferred to be a `SpicyPizza`, and can that inference be verified, explained, and traced to its semantic source?**

The example stops at semantic execution. Capability exposure, Knowledge Services, and Knowledge Agents are intentionally deferred to later increments.

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

## Execute

Requirements:

- Java 17 or newer
- `curl`

Run:

```bash
bash examples/pizza/run.sh
```

The script downloads the pinned ROBOT release on first execution and then performs four steps:

1. classify `spicy-pizza.ofn` with the HermiT OWL reasoner;
2. verify that `AmericanHot rdfs:subClassOf SpicyPizza` is present in the reasoned ontology;
3. generate a ROBOT explanation for that inferred axiom;
4. write a PROV-O execution record for the inference.

Generated files are written below `examples/pizza/results/` and are intentionally not committed.

## Verification

`verify-spicy.sparql` is expressed as a negative test: it returns a violation only when the expected inferred subclass relationship is missing.

Therefore the example fails if semantic execution no longer produces:

```text
AmericanHot SubClassOf SpicyPizza
```

The test is about the **semantic result**, not about a particular serialization of the reasoned ontology.

## Explanation

ROBOT's explanation step asks the reasoner why this entailment holds:

```text
AmericanHot SubClassOf SpicyPizza
```

The generated `results/explanation.md` contains a minimal set of semantic axioms sufficient to justify the inference.

This is the first concrete form of the ESKA principle that a result should remain traversable back toward the knowledge that gives it meaning.

## Provenance

`results/provenance.ttl` records the execution using PROV-O concepts:

```text
Pizza semantic slice
        │ prov:used
        ▼
Reasoning activity
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
- the inferred RDF statement;
- the execution timestamp.

This is intentionally modest provenance. Later ESKA increments can formalize richer knowledge, verification, and execution lineage.

## ESKA concepts demonstrated

| ESKA concept | Pizza realization |
| --- | --- |
| Semantic Model | Pizza OWL classes, properties, and class expressions |
| Semantic Knowledge | The selected Pizza axioms in `spicy-pizza.ofn` |
| Executable Semantic Knowledge | OWL classification performed by HermiT |
| Verification | SPARQL-based assertion of the expected inference |
| Explanation | Reasoner explanation for the inferred subclass axiom |
| Provenance | PROV-O record connecting execution, source, and result |

Not yet demonstrated:

- Semantic Capability as a machine-described bounded ability;
- Knowledge Service exposure;
- agent discovery or invocation.

Those belong to later slices, after this semantic execution path is stable.

## Source and license

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for provenance and licensing of the Pizza semantic material used by this example.
