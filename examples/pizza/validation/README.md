# Pizza SHACL validation

This slice demonstrates a second form of **Executable Semantic Knowledge** in ESKA: semantic validation.

The Pizza-domain SHACL profile and example RDF data are **not owned by this repository**. They are published by [`GerhardBalz/pizza-ontology`](https://github.com/GerhardBalz/pizza-ontology) and consumed here from the immutable commit recorded in [`../pizza-domain-source.json`](../pizza-domain-source.json).

```text
pizza-ontology
    owns Pizza SHACL profile + RDF examples
        ↓ commit-pinned fetch
ESKA
    defines PizzaValidationCapability
        ↓
    executes pySHACL
        ↓
    verifies + records provenance
```

The runtime materialization is written only beneath `examples/pizza/.work/pizza-domain/`; it is not a second semantic source of truth.

## Question

The example asks:

> **Does a concrete Pizza RDF data graph conform to the source-owned Pizza validation profile?**

The published profile requires, for each explicit `pizza:Pizza` node:

- exactly one `pizza:hasBase` value;
- the base value to be a `pizza:PizzaBase`;
- at least one `pizza:hasTopping` value;
- each topping value to be a `pizza:PizzaTopping`.

## Why SHACL in addition to OWL?

OWL reasoning and SHACL validation answer different questions.

```text
OWL
    What follows logically from the semantic model?

SHACL
    Does this explicit RDF data satisfy a validation profile?
```

The constraints remain represented in SHACL rather than duplicated as Python conditionals. ESKA's Python code invokes and verifies the executable semantic artifact; it does not own the Pizza validation semantics.

## Source binding

The source binding identifies:

- repository: `GerhardBalz/pizza-ontology`
- immutable Git commit
- machine-readable `artifacts/manifest.ttl`
- reasoning, SHACL, conforming-data, and non-conforming-data paths

`fetch-domain-artifacts.py` downloads the manifest and artifacts from the pinned commit and refuses an unexpected role/path contract.

## Semantic Capability

[`pizza-validation-capability.ttl`](pizza-validation-capability.ttl) describes the bounded ESKA ability as `PizzaValidationCapability`.

```text
Capability
    Pizza Validation

Subject
    Pizza

Input
    Pizza RDF data graph

Output
    sh:ValidationReport

Produced relation
    sh:conforms

Semantic model
    source-owned Pizza SHACL profile

Executable artifact
    SHACL validation with pySHACL
```

The Capability remains ESKA-owned because it describes how semantic knowledge is operationalized. The SHACL graph remains Pizza-owned because it defines domain-specific validation knowledge.

## Data cases

The source repository publishes both cases in its artifact manifest.

### Conforming

The conforming graph has a valid Pizza base and toppings and must produce:

```text
sh:conforms true
```

### Non-conforming

The non-conforming graph deliberately:

- omits `pizza:hasBase`;
- points `pizza:hasTopping` at a value typed as `pizza:PizzaBase` rather than `pizza:PizzaTopping`.

ESKA therefore verifies that the report contains:

```text
pizza:hasBase
    sh:MinCountConstraintComponent

pizza:hasTopping
    sh:ClassConstraintComponent
```

These expectations follow the published Pizza-domain fixture instead of preserving ESKA's former local test data.

## Execute

Install the validation dependency:

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
```

Run:

```bash
python examples/pizza/validation/validate.py
```

The script:

1. materializes the commit-pinned Pizza SHACL/data artifacts;
2. verifies the machine-readable `PizzaValidationCapability` contract;
3. validates the conforming graph;
4. validates the non-conforming graph and checks the expected source-owned violations;
5. records validation execution provenance including the pinned Pizza source URLs.

Generated validation reports remain in `examples/pizza/validation/results/`.

## Architectural significance

The repository boundary is itself part of the example:

```text
Domain semantics               Execution architecture
────────────────────────       ─────────────────────────
pizza-ontology                 ESKA

OWL module          ────────►   reasoning execution
SHACL profile       ────────►   validation capability
example RDF data   ────────►   verification / provenance
```

**Execution must not sever semantics, and execution architecture should not become the accidental owner of domain semantics.**
