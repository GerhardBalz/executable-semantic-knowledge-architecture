# LUBM Query 11 — external-oracle verification

This example is an executable semantic-correctness proving ground based on the **Lehigh University Benchmark (LUBM)**.

Unlike earlier ESKA examples whose expected results are local test contracts, this example verifies against an answer count published by the benchmark authors.

## Benchmark contract

The governed inputs are recorded in `benchmark-contract.json`.

The benchmark instance is:

```text
LUBM(1,0)
universities    1
starting index  0
seed            0
threads         1
```

The semantic model identity remains:

```text
http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl
```

The exact Query 11 text is stored in `query11.sparql` and pinned by SHA-256 in the machine contract.

## Why Query 11

Lehigh's SPARQL workload identifies Query 11 as a reasoning test. The query asks for `ub:ResearchGroup` instances whose `ub:subOrganizationOf` relationship reaches `http://www.University0.edu`.

The required semantic step is transitivity:

```text
ResearchGroup
    subOrganizationOf Department

Department
    subOrganizationOf University

therefore

ResearchGroup
    subOrganizationOf University
```

Lehigh's published LUBM(1,0) evaluation/reference contract gives Query 11 **224 answers** when the required reasoning is provided.

This example therefore treats `224` as an external oracle, not a value inferred from ESKA's own fixture design.

## Replaceable implementation backend

CI checks out:

```text
rvesse/lubm-uba
48686cd616f564c8fc360dc5abbcc294678655c4
```

That repository describes itself as a refactoring/scaling of the original Lehigh UBA generator while preserving generated data identically and includes a comparison mechanism against the original implementation.

The pinned GitHub repository is **not LUBM semantic authority**. It is a replaceable implementation backend for generating the Lehigh-defined benchmark data.

See `THIRD-PARTY-NOTICE.md` for provenance and licensing boundaries.

## Executable test

CI builds the pinned UBA implementation and generates the same LUBM(1,0) dataset twice:

1. N-Triples;
2. Turtle.

The verifier then:

1. loads the complete generated dataset for each serialization;
2. executes exact Query 11 before transitive materialization as a negative control;
3. materializes only the transitive closure of `ub:subOrganizationOf` required by this experiment;
4. executes exact Query 11 again;
5. requires exactly 224 answers in each serialization;
6. requires the normalized answer sets to be identical.

The verifier deliberately does **not** claim to be a complete OWL reasoner. It implements only the semantic operation required to test Query 11's published transitivity requirement.

## What this proves

The experiment establishes the following ESKA pattern using an independently defined oracle:

```text
Lehigh semantic model + benchmark definition
                ↓
pinned replaceable UBA implementation
                ↓
LUBM(1,0) generated artifact
                ↓
Query 11 reasoning Execution
                ↓
normalized Result
                ↓
Verification against Lehigh oracle = 224
```

It also tests physical-representation independence:

```text
same benchmark parameters
    ↓
N-Triples → 224 answers
Turtle    → 224 answers
    ↓
same normalized answer set
```

## ESKA boundary

`architecture.ttl` uses only existing ESKA and PROV-O terms:

- `eska:SemanticModel`;
- `eska:SemanticCapability`;
- `eska:ExecutableSemanticKnowledgeArtifact`;
- `eska:Execution`;
- `eska:Result`;
- `eska:Verification`;
- PROV-O runtime usage and lineage.

No ESKA vocabulary is added or modified.

## Authority boundary

- LUBM benchmark semantics and reference expectations remain Lehigh-authored.
- The generated RDF is benchmark execution input, not a new semantic authority.
- The pinned UBA GitHub backend is implementation infrastructure, not ontology identity or benchmark governance.
- ESKA does not republish the UBA source.
- This example does not change LUBM IRIs.
- This is a semantic-correctness test, not a performance benchmark or leaderboard.

## Primary evidence

- LUBM benchmark: https://swat.cse.lehigh.edu/projects/lubm/
- Lehigh SPARQL workload: https://swat.cse.lehigh.edu/projects/lubm/queries-sparql.txt
- Lehigh reference-answer index: https://swat.cse.lehigh.edu/projects/lubm/answers.htm
- Published LUBM evaluation: https://swat.cse.lehigh.edu/pubs/guo05a.pdf

## Run

The full test is intentionally run by GitHub Actions because it builds a pinned external implementation backend.

For the local verifier after generation:

```text
python -m pip install -r examples/lubm-query11/requirements.txt
python examples/lubm-query11/verify.py --ntriples <ntriples-dir> --turtle <turtle-dir>
```
