# Pizza SHACL validation

This slice adds a second form of **Executable Semantic Knowledge** to ESKA: semantic validation.

The existing Pizza example demonstrates OWL inference:

```text
formal semantics
    ↓ reason
new entailed knowledge
```

This example demonstrates SHACL validation:

```text
formal constraints
    ↓ validate
conformance report
```

These are intentionally different operational semantics.

## Question

The example asks:

> **Does a concrete Pizza RDF data graph conform to an explicit Pizza data contract?**

The initial contract is deliberately small:

- each `pizza:Pizza` data node must have exactly one `pizza:hasBase` value;
- the base value must be a `pizza:PizzaBase`;
- each Pizza data node must have at least one `pizza:hasTopping` value;
- each topping value must be a `pizza:PizzaTopping`.

The constraints are represented in [`pizza-shapes.ttl`](pizza-shapes.ttl).

## Why SHACL in addition to OWL?

OWL reasoning and SHACL validation answer different questions.

The earlier slice asks:

> **What follows from the semantic model?**

The SHACL slice asks:

> **Does this concrete RDF data graph satisfy an explicit validation contract?**

For example, [`invalid-pizza.ttl`](invalid-pizza.ttl) gives one Pizza node two `hasBase` values. The SHACL shape declares `sh:maxCount 1`, so validation must report non-conformance.

This is deliberately not encoded as a Python `if` statement. The executable constraint is the SHACL graph; pySHACL evaluates that formal semantic artifact.

## Semantic Capability

[`pizza-validation-capability.ttl`](pizza-validation-capability.ttl) describes the bounded ability as `PizzaValidationCapability`.

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
    Pizza SHACL shapes graph

Executable artifact
    SHACL validation with pySHACL

Applicability
    parseable RDF using the Pizza ontology terms
```

The scope note explicitly excludes OWL class classification. This gives the project two different Semantic Capabilities built around different executable semantics:

```text
PizzaClassificationCapability
    OWL entailment
    → rdfs:subClassOf

PizzaValidationCapability
    SHACL constraint evaluation
    → sh:ValidationReport / sh:conforms
```

## Data cases

### Conforming

[`valid-pizza.ttl`](valid-pizza.ttl) contains one Pizza with one base and two toppings. It must produce:

```text
sh:conforms true
```

### Non-conforming

[`invalid-pizza.ttl`](invalid-pizza.ttl) contains one Pizza with two base values. It must produce:

```text
sh:conforms false
```

and a validation result whose source constraint is `sh:MaxCountConstraintComponent` on `pizza:hasBase`.

## Execute

Install the pinned validation dependency:

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
```

Run:

```bash
python examples/pizza/validation/validate.py
```

The script performs four checks:

1. verifies the machine-readable `PizzaValidationCapability` contract with SPARQL;
2. validates the conforming Pizza data and requires `sh:conforms true`;
3. validates the non-conforming Pizza data and requires the expected `hasBase` max-count violation;
4. records validation execution provenance using PROV-O.

Generated reports are written to `examples/pizza/validation/results/`.

## Architectural significance

The second execution mode tests whether ESKA is broader than ontology reasoning.

Both examples satisfy the same architectural pattern:

```text
Semantic Model
    ↓
Executable Semantic Knowledge Artifact
    ↓
Semantic Capability
    ↓
Verified Result
```

but their operational semantics differ:

```text
OWL ontology       → reason   → inferred axioms
SHACL shapes graph → validate → validation report
```

That distinction is intentional. ESKA does not define one universal meaning of "execute"; execution depends on the semantic artifact type.
