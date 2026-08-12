# ROBOT reason/verify proving ground

This example tests whether ROBOT can implement the existing ESKA `Execution → Result → Verification` pattern without introducing ROBOT-specific ESKA vocabulary.

It is an executable experiment for #76, following the standards/tooling assessment in `GerhardBalz/semantic-knowledge-engineering#11` and the OAK proving ground in #74.

## Hypothesis

A configured ROBOT reasoning operation can remain an implementation detail underneath one stable ESKA semantic capability.

The tested capability is ontology classification: given a semantic model, produce a reasoned ontology containing the expected inferred superclass relation.

## Fixture

`fixture.ttl` contains the asserted hierarchy:

```text
LeafClass
    ↓ rdfs:subClassOf
IntermediateClass
    ↓ rdfs:subClassOf
RootClass
```

The source does not assert:

```text
LeafClass rdfs:subClassOf RootClass
```

That relation is the semantic result this experiment expects ROBOT reasoning to materialize.

## Verification rule

`expected-inference.sparql` follows ROBOT `verify` semantics: a returned row is a violation.

The rule returns `LeafClass` only when the expected inferred superclass axiom is absent.

This gives the experiment a required negative control:

```text
source ontology + same verify rule
    → violation
    → ROBOT verify exits non-zero
```

and a positive path:

```text
source ontology
    ↓ ROBOT reason / ELK / include indirect / retain redundant subclass axioms
reasoned ontology
    ↓ same ROBOT verify rule
no violation
    → verification passes
```

The CI job succeeds only when both observations hold.

### Why redundant subclass retention is explicit

The first executable run established an important ROBOT behavior boundary. The negative control failed correctly, but the post-reasoning verification also failed because ROBOT removes redundant subclass axioms by default.

`LeafClass rdfs:subClassOf RootClass` is entailed by the two asserted subclass steps and is therefore logically redundant. The experiment needs that indirect inference to be observable in the serialized Result ontology, so `run.sh` explicitly combines:

```text
--include-indirect true
--remove-redundant-subclass-axioms false
```

This changes result serialization, not the semantic hypothesis or verification target.

## ESKA mapping

`architecture.ttl` uses existing ESKA terms only:

- `robotdemo:SourceSemanticModel` is an `eska:SemanticModel`;
- `robotdemo:ClassificationCapability` is one `eska:SemanticCapability`;
- `robotdemo:ReasonArtifact` and `robotdemo:VerifyArtifact` are replaceable `eska:ExecutableSemanticKnowledgeArtifact` implementations;
- `robotdemo:ReasonExecution` is an `eska:Execution`;
- `robotdemo:ReasonedOntology` is the generated `eska:Result`;
- `robotdemo:InferenceVerification` is an `eska:Verification` of the execution and result;
- `prov:wasDerivedFrom` records result lineage from the source semantic model.

No class or property is added to ESKA for ROBOT itself.

## Reproducibility

The example pins the official ROBOT v1.9.10 JAR published by Ontodev.

`run.sh` downloads the release asset and verifies this SHA-256 before execution:

```text
16a73c074f3df359a7338a84b4e0788785fe06117f931bb9796e9619ea776105
```

The large ROBOT JAR is not committed to this repository.

## Run

From the repository root:

```bash
bash examples/robot-reason-verify/run.sh
```

The script writes runtime artifacts beneath `examples/robot-reason-verify/build/`, including the reasoned ontology and an `evidence.json` summary. The build directory is ignored by Git.

## Observed evidence

GitHub Actions executed the experiment with ROBOT v1.9.10 and observed:

```json
{
  "negativeControl": "failed-as-expected",
  "reasoning": "completed",
  "reasonedVerification": "passed",
  "expectedInference": "LeafClass rdfs:subClassOf RootClass"
}
```

The positive verification reported zero violations. The hypothesis therefore survives this proving ground: the expected semantic relation was absent from the source serialization, produced by the configured reasoning Execution, and accepted by the same verification rule afterward.

## Architectural boundary

The observed result supports a deliberately narrow conclusion:

```text
ESKA SemanticCapability
        ↓
configured executable implementation
        ↓
ROBOT reason
        ↓
ESKA Result
        ↓
ROBOT verify
        ↓
ESKA Verification
```

ROBOT supplies executable reasoning and rule-checking behavior. OWL supplies the formal semantics. ESKA describes how the semantic source, executable implementation, execution, result, provenance, and verification remain explicitly connected.

The experiment does not make ROBOT an ESKA dependency and does not claim that all verification is ROBOT verification.
