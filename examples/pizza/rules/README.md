# Pizza rule evaluation

This directory implements the third executable-semantic mode in the ESKA Pizza reference project:

```text
Rule → evaluate
```

It exists primarily to test the architecture, not to add another Pizza application feature.

## Question

> **Can a source-owned semantic rule be evaluated deterministically while its semantic model, bounded Capability, execution, result, verification, and provenance remain machine-traceable?**

The source-owned rule is a SPARQL 1.1 `CONSTRUCT` artifact published by the companion `pizza-ontology` repository. ESKA does not copy or redefine it.

```text
pizza-ontology
    vegetarian-warning.rq
    rule-vocabulary.ttl
    menu-pizzas.ttl
        ↓ immutable commit + manifest
ESKA
    PizzaRuleEvaluationCapability
        ↓ evaluate with RDFLib
Execution
        ↓
Result
        ↓
Verification + PROV-O
```

## Capability

[`pizza-rule-evaluation-capability.ttl`](pizza-rule-evaluation-capability.ttl) describes the bounded ability:

```text
Capability
    Pizza Rule Evaluation

Subject
    Pizza

Input
    explicit Pizza RDF data graph

Output
    derived RDF result graph

Produced relation
    urn:pizza-ontology:rule:requiresVegetarianWarning

Semantic model
    source-owned SPARQL CONSTRUCT rule

Executable artifact
    SPARQL rule evaluation with RDFLib

Applicability
    explicit RDF assertions; no implicit OWL entailment
```

The scope is intentionally distinct from the existing modes:

```text
OWL ontology
    ↓ HermiT
reason / entail

SHACL shapes
    ↓ pySHACL
validate / conform

SPARQL rule
    ↓ RDFLib
rule evaluate / derive
```

## Source ownership

The ESKA source binding in [`../pizza-domain-source.json`](../pizza-domain-source.json) pins `GerhardBalz/pizza-ontology` to an immutable commit and materializes the rule artifacts below `../.work/pizza-domain/` at runtime.

ESKA owns:

- the Semantic Capability;
- the executable evaluator binding;
- execution and result modeling;
- verification;
- execution provenance.

ESKA does **not** own:

- the Pizza rule query;
- the rule result vocabulary;
- the Pizza RDF input data.

## Execute

Install the pinned evaluator dependency:

```bash
python -m pip install -r examples/pizza/rules/requirements.txt
```

Run:

```bash
python examples/pizza/rules/evaluate.py
```

The runner:

1. materializes the commit-pinned source artifacts;
2. verifies `PizzaRuleEvaluationCapability` against the ESKA model;
3. evaluates the source-owned SPARQL `CONSTRUCT` rule;
4. requires the warning result for the matching Pizza and absence for the vegetable control;
5. writes the derived RDF result;
6. records `Execution → Result → Verification` provenance with PROV-O.

Generated artifacts are written to `examples/pizza/rules/results/`.

## Architectural significance

The third mode was deliberately implemented **without adding a rule-specific ESKA core class**. The subsequent cross-mode falsification pass now verifies the rule with the same generic queries used for OWL reasoning and SHACL validation:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
→ Execution
→ Result
→ Verification
```

Both generic core verifiers now include the rule path:

- [`../verify-core.sparql`](../verify-core.sparql) checks the shared Semantic Capability contract across all three modes;
- [`../verify-core-executions.sparql`](../verify-core-executions.sparql) checks the shared runtime `Execution → Result → Verification` pattern.

The result is intentionally conservative: **the third mode did not require a change to `model/eska-core.ttl`**. That strengthens the current core abstraction while leaving it provisional for future falsification by decisions, calculations, mappings, workflows, or other genuinely different execution semantics.
