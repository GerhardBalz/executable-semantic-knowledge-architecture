# Pizza decision evaluation

This directory implements the fourth executable-semantic mode in the ESKA Pizza reference project:

```text
Decision → decide
```

It exists primarily to falsify or strengthen the provisional ESKA core, not to add another Pizza application feature.

## Question

> **Can a source-owned DMN decision model select a semantic outcome while its model, Capability, execution, Result, Verification, and provenance remain machine-traceable?**

The DMN model, decision outcome vocabulary, and canonical input cases are owned by `pizza-ontology`. ESKA does not copy or redefine them.

```text
pizza-ontology
    pizza-dietary-suitability.dmn
    decision-vocabulary.ttl
    cases.json
        ↓ immutable commit + manifest
ESKA
    PizzaDietarySuitabilityCapability
        ↓ decide
Execution
        ↓
Result
        ↓
Verification + PROV-O
```

## Capability

[`pizza-dietary-suitability-capability.ttl`](pizza-dietary-suitability-capability.ttl) defines:

```text
Capability
    Pizza Dietary Suitability Decision

Subject
    Pizza

Input
    explicit decision context

Output
    decision:DietarySuitabilityOutcome

Produced relation
    decision:dietarySuitability

Semantic model
    source-owned DMN 1.5 UNIQUE decision table

Executable artifact
    ESKA canonical DMN decision evaluator

Applicability
    explicit containsMeat / containsFish boolean inputs
```

## Execution semantics

The preceding three ESKA modes are intentionally different:

```text
OWL ontology     → reason   → inferred axiom
SHACL constraint → validate → conformance report
SPARQL rule      → evaluate → derived RDF statement
DMN decision     → decide   → selected semantic outcome
```

The decision inputs are explicit. ESKA does not infer `containsMeat` or `containsFish` from the Pizza ontology or from the preceding rule mode.

## Execute

```bash
python -m pip install -r examples/pizza/decisions/requirements.txt
python examples/pizza/decisions/evaluate.py
```

The runner:

1. materializes the commit-pinned Pizza semantic artifact contract;
2. verifies `PizzaDietarySuitabilityCapability`;
3. parses the supported subset of the source-owned DMN 1.5 decision table;
4. requires exactly one matching rule per decision case under `UNIQUE` hit policy;
5. verifies the semantic outcome against the source-owned decision vocabulary;
6. writes semantic RDF decision results;
7. records one `Execution → Result → Verification` chain per decision case using PROV-O.

Generated files are written below `examples/pizza/decisions/results/`.

## Architectural significance

The fourth mode is first implemented without adding a decision-specific ESKA core class:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
→ Execution
→ Result
→ Verification
```

If the generic core verifiers also accept this mode without special-casing, the decision example becomes further evidence that execution semantics can vary while the architectural core remains stable.

`Decision`, `DecisionExecution`, `DecisionResult`, and `ExecutionMode` should therefore remain outside the core unless executable evidence demonstrates a real need for them.
