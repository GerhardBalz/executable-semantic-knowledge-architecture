# OAK backend-independence proving ground

This example tests whether an ESKA semantic-access capability can remain stable while its ontology-access implementation changes.

It is an executable experiment for #74, motivated by the SKE standards/tooling assessment in `GerhardBalz/semantic-knowledge-engineering#11`.

## Hypothesis

One semantic capability can be implemented through different Ontology Access Kit (OAK) adapters without changing the capability's semantic identity or the meaning of its result.

The stable capability in this example is:

> Given the semantic identity of a class, return its primary label and direct hierarchical parent identities.

The experiment intentionally separates that capability from the OAK adapter selector used to implement it.

## Two implementation paths

The same Python function calls the same OAK interface-level operations for both paths:

- `label()`;
- `hierarchical_parents()`;
- `curie_to_uri()` for result normalization.

Only the selector changes:

1. `sparql:fixture.ttl` — RDF/Turtle accessed through OAK's SPARQL/RDFLib-oriented adapter path;
2. `pronto:fixture.obo` — OBO Format accessed through OAK's Pronto adapter path.

The fixture is represented in both formats with the same semantic identities and hierarchy.

The verifier also checks that OAK instantiated two different adapter classes, so a configuration-only alias of one implementation does not satisfy the experiment accidentally.

## ESKA mapping

`architecture.ttl` describes the experiment using existing ESKA terms:

- `oakdemo:LookupCapability` is one `eska:SemanticCapability`;
- the two adapter-backed artifacts are `eska:ExecutableSemanticKnowledgeArtifact` instances;
- each run is an `eska:Execution` of the same Capability;
- each normalized output is an `eska:Result`;
- `oakdemo:BackendEquivalenceVerification` is an `eska:Verification` over both results.

OAK adapter types are deliberately **not** modeled as ESKA vocabulary. They are replaceable implementation choices.

## What is verified

`verify.py` requires both implementations to produce exactly:

```json
{
  "entity": "https://w3id.org/eska/example/oak-backend-independence#Child",
  "label": "Child concept",
  "parents": [
    "https://w3id.org/eska/example/oak-backend-independence#Root"
  ]
}
```

The run fails if:

- either adapter produces a different semantic result;
- the normalized results disagree;
- OAK resolves both selectors to the same adapter class.

This makes backend independence a falsifiable property rather than a documentation claim.

## Run

From the repository root:

1. install the pinned implementation dependency:

   ```bash
   python -m pip install -r examples/oak-backend-independence/requirements.txt
   ```

2. run the executable verification:

   ```bash
   python examples/oak-backend-independence/verify.py
   ```

CI runs the same sequence.

## Dependency policy

The proving ground pins `oaklib==0.7.4`, the OAK release selected when this experiment was created.

OAK is an implementation dependency of this example only. ESKA does not require OAK, and a future implementation should be able to satisfy the same semantic capability contract using another technology.

## Architectural conclusion tested

If the test passes, it provides concrete evidence for this boundary:

```text
SemanticCapability
    stable semantic operation
              |
              v
     interface-level access
        /             \
       v               v
 OAK SPARQL         OAK Pronto
 adapter             adapter
       \               /
        v             v
   same normalized semantic Result
```

The semantic capability remains stable; adapter/backend selection is replaceable implementation configuration.
