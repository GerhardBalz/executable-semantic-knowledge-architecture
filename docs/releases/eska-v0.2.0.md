# ESKA v0.2.0

`eska-v0.2.0` is the second governed repository release of the Executable Semantic Knowledge Architecture.

## Main semantic change

The ESKA core module advances from `0.1.0` to `0.2.0` with the reviewed cross-repository Semantic Modeling alignment:

```turtle
eska:SemanticModel owl:equivalentClass smo:SemanticModel .
```

The reusable semantic-model concept is canonically owned by the published Semantic Modeling Ontology (SMO), while the already-published ESKA class remains a compatibility surface.

ESKA core records its dependency on immutable SMO v0.1.0 using:

```turtle
<https://w3id.org/eska/model/core>
    dcterms:requires <https://w3id.org/smo/0.1.0> .
```

This release deliberately does **not** deprecate `eska:SemanticModel`, change `eska:usesSemanticModel`, introduce `owl:imports`, or move ESKA-specific Capability, Execution, Result, Verification, Service, Agent, or Deployment semantics into SMO.

## Published ontology modules

| Module | Version | Ontology IRI |
|---|---:|---|
| core | 0.2.0 | `https://w3id.org/eska/model/core` |
| capability | 0.2.0 | `https://w3id.org/eska/model/capability` |
| service | 0.4.0 | `https://w3id.org/eska/model/service` |
| agent | 0.3.0 | `https://w3id.org/eska/model/agent` |
| deployment | 0.1.0 | `https://w3id.org/eska/model/deployment` |

Repository release versioning remains independent from the semantic versions of the contained ontology modules.

## Compatibility and executable evidence

The release preserves the stable ESKA term namespace:

```text
https://w3id.org/eska#
```

The core still exposes exactly the same ESKA term inventory; the new ontology axiom is backward-compatible and adds machine-readable equivalence to `https://w3id.org/smo#SemanticModel`.

The governed verification contract continues to cover seven executable-semantic modes, sixteen semantic Executions, generalized Knowledge Service and Knowledge Agent behavior, deployment binding, and provenance/evidence lineage. Publication verification additionally checks the SMO bridge, the immutable SMO dependency, non-deprecation of the ESKA compatibility class, and consistency between the five authoritative modules and the combined RDF distribution.

## Release bundle

The GitHub Release attaches:

- `dist/eska.ttl`;
- the five authoritative `model/eska-*.ttl` ontology modules;
- `model/publication-contract.json`;
- `model/namespace-migration.json`;
- `publication/backend-targets.json`.

The immutable Git tag provides the governed backend needed for the future core `0.2.0` W3ID version routes.

## Publication boundary

At release creation time the current ESKA routes remain live, the existing immutable routes remain bound to `eska-v0.1.0`, and these new routes remain intentionally inactive:

```text
https://w3id.org/eska/model/core/0.2.0
https://w3id.org/eska/dist/0.2.0/eska-core.ttl
```

After this release exists, the tagged core backend must be verified independently. Only then may a separate W3ID contribution activate those two routes against `eska-v0.2.0`. Immutable routes must never target mutable `main`.
