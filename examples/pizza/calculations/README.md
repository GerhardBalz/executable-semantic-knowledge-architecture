# Pizza calculation

This directory implements the fifth executable-semantic mode in the ESKA Pizza reference project:

```text
Calculation → calculate
```

It exists primarily to test the architecture against typed numeric computation.

## Question

> **Can a source-owned mathematical formula be evaluated deterministically while its domain meaning, bounded Capability, typed result, verification, and provenance remain machine-traceable?**

The source-owned mathematical model is an OpenMath expression published by the companion `pizza-ontology` repository. ESKA does not copy or rewrite the formula.

```text
pizza-ontology
    pizza-area.openmath.xml
    calculation-vocabulary.ttl
    calculation cases
        ↓ immutable commit + manifest
ESKA
    PizzaAreaCalculationCapability
        ↓ evaluate OpenMath
Execution
        ↓
typed decimal Result
        ↓
Verification + PROV-O
```

## Capability

[`pizza-area-calculation-capability.ttl`](pizza-area-calculation-capability.ttl) describes the bounded ability:

```text
Capability
    Pizza Area Calculation

Input
    explicit Pizza diameter context

Output
    PizzaAreaResult

Produced relation
    urn:pizza-ontology:calculation:areaSquareCentimetres

Semantic model
    source-owned OpenMath formula

Executable artifact
    OpenMath calculation evaluation

Applicability
    positive finite diameter in centimetres
```

The numeric result is represented by a typed `xsd:decimal` value carried through the source-owned `calc:areaSquareCentimetres` relation.

## Execution semantics

The mode is intentionally distinct from the existing modes:

```text
OWL ontology      → reason    → inferred axiom
SHACL constraint  → validate  → validation report
SPARQL rule       → evaluate  → derived RDF statement
DMN decision      → decide    → selected semantic outcome
OpenMath formula  → calculate → typed numeric result
```

The OpenMath evaluator understands arithmetic operators independently of the Pizza formula. The actual Pizza area formula remains external and source-owned.

## Source ownership

The ESKA source binding in [`../pizza-domain-source.json`](../pizza-domain-source.json) pins `GerhardBalz/pizza-ontology` to an immutable commit and materializes the formula, vocabulary, and cases below `../.work/pizza-domain/` at runtime.

ESKA owns:

- the Semantic Capability;
- the OpenMath evaluator binding;
- execution/result modeling;
- verification;
- PROV-O lineage.

ESKA does **not** own:

- the Pizza OpenMath formula;
- the Pizza calculation vocabulary;
- the canonical diameter cases.

## Execute

Install the pinned dependency:

```bash
python -m pip install -r examples/pizza/calculations/requirements.txt
```

Run:

```bash
python examples/pizza/calculations/evaluate.py
```

The runner verifies all three source-owned cases:

```text
20 cm → 314.159265 cm²
30 cm → 706.858347 cm²
40 cm → 1256.637061 cm²
```

and emits one `Execution → Result → Verification` provenance chain per calculation case.

## Architectural significance

The calculation mode is implemented without adding `Calculation`, `Formula`, `CalculationExecution`, `CalculationResult`, or `ExecutionMode` to `model/eska-core.ttl`.

The first test remains the existing abstraction:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
→ Execution
→ Result
→ Verification
```

The generic cross-mode verification then determines whether that abstraction survives the fifth mode unchanged.
