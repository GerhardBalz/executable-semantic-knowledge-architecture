# ESKA namespace, publication, and versioning

## Current state

ESKA uses the permanent term namespace:

```text
https://w3id.org/eska#
```

The W3ID resolver was established through `perma-id/w3id.org#6530`. The first immutable module-version routes were established through `perma-id/w3id.org#6535` and remain bound to the governed `eska-v0.1.0` release.

Core `0.2.0` is now the current governed core and the second governed repository release exists as:

```text
eska-v0.2.0
a6ce0b9e795d271dce8a2b7be93d44932e8448d4
```

The tagged core backend has been verified. The core `0.2.0` immutable W3ID routes are intentionally still inactive until the dedicated upstream route contribution is merged and externally verified.

Machine-readable state is governed by [`model/publication-contract.json`](../model/publication-contract.json) and [`publication/backend-targets.json`](../publication/backend-targets.json).

## Term namespace

ESKA terms keep stable, unversioned IRIs such as:

```text
https://w3id.org/eska#SemanticModel
https://w3id.org/eska#Execution
https://w3id.org/eska#SemanticCapability
https://w3id.org/eska#KnowledgeService
https://w3id.org/eska#KnowledgeAgent
https://w3id.org/eska#ServiceDeployment
```

The move to SMO conceptual ownership does **not** create a second namespace migration. `eska:SemanticModel` remains a published compatibility class.

## SemanticModel compatibility in core 0.2.0

The reviewed SKE cross-repository decision established that the published SMO and ESKA definitions of `SemanticModel` are semantically identical and that ESKA's seven execution modes provide no evidence for an ESKA-specific narrowing.

Core `0.2.0` therefore contains:

```turtle
eska:SemanticModel owl:equivalentClass smo:SemanticModel .
```

and records an explicit dependency on the immutable SMO release identity:

```turtle
<https://w3id.org/eska/model/core>
    dcterms:requires <https://w3id.org/smo/0.1.0> .
```

This first bridge deliberately does not:

- deprecate `eska:SemanticModel`;
- change `eska:usesSemanticModel`;
- add `owl:imports` merely by symmetry;
- move ESKA-specific execution, capability, result, verification, service, agent, or deployment concepts into SMO;
- modify immutable `eska-v0.1.0` or `smo-v0.1.0`.

## Ontology modules and current versions

The vocabulary remains split into independently governed ontology documents:

| Module | Stable ontology IRI | Current version IRI | Publication state |
|---|---|---|---|
| core | `https://w3id.org/eska/model/core` | `https://w3id.org/eska/model/core/0.2.0` | tagged backend published via `eska-v0.2.0`; W3ID route pending |
| capability | `https://w3id.org/eska/model/capability` | `https://w3id.org/eska/model/capability/0.2.0` | immutable route active via `eska-v0.1.0` |
| service | `https://w3id.org/eska/model/service` | `https://w3id.org/eska/model/service/0.4.0` | immutable route active via `eska-v0.1.0` |
| agent | `https://w3id.org/eska/model/agent` | `https://w3id.org/eska/model/agent/0.3.0` | immutable route active via `eska-v0.1.0` |
| deployment | `https://w3id.org/eska/model/deployment` | `https://w3id.org/eska/model/deployment/0.1.0` | immutable route active via `eska-v0.1.0` |

The former core `0.1.0` version remains immutable and continues to resolve through its existing W3ID route to `eska-v0.1.0`.

A combined current RDF distribution is published at:

```text
https://w3id.org/eska/dist/eska.ttl
```

It represents the current governed module set and does not replace the individual module identities.

## Repository release versioning

Repository releases use:

```text
eska-v<major>.<minor>.<patch>
```

Governed repository releases now include:

```text
eska-v0.1.0    first permanent-namespace snapshot
eska-v0.2.0    core 0.2.0 + SMO SemanticModel compatibility
```

`eska-v0.2.0` was published by the guarded release workflow at commit:

```text
a6ce0b9e795d271dce8a2b7be93d44932e8448d4
```

Repository release versions remain independent from ontology-module versions. Unchanged modules keep their existing semantic versions even though they are present in the v0.2.0 repository snapshot.

## Core 0.2.0 immutable publication gate

The immutable core identities are intended to be:

```text
https://w3id.org/eska/model/core/0.2.0
https://w3id.org/eska/dist/0.2.0/eska-core.ttl
```

The immutable tagged backends now exist and have been verified:

```text
https://raw.githubusercontent.com/GerhardBalz/executable-semantic-knowledge-architecture/eska-v0.2.0/model/eska-core.ttl
https://github.com/GerhardBalz/executable-semantic-knowledge-architecture/blob/eska-v0.2.0/model/eska-core.ttl
```

The W3ID routes themselves remain **inactive**.

Governed order:

1. merge and verify core `0.2.0` on current `main` — **complete**;
2. publish `eska-v0.2.0` at one exact governed commit — **complete**;
3. verify the tagged `model/eska-core.ttl` backend — **complete**;
4. add a narrow W3ID increment for the core `0.2.0` ontology/version distribution routes — **next**;
5. require those routes to target only `eska-v0.2.0`, never mutable `main`;
6. externally verify current + immutable routes before declaring core `0.2.0` publication complete.

The repository-owned W3ID payload continues to mirror only currently active upstream routes until the dedicated core `0.2.0` route contribution is prepared.

## Semantic versioning policy

Module versions follow a SemVer-style compatibility policy:

- **patch** — documentation, annotations, metadata, or corrections that preserve the intended machine-interpretable contract;
- **minor** — backward-compatible additive semantics such as new terms, optional relationships, or compatible axioms;
- **major** — breaking semantic contract changes.

The SMO `owl:equivalentClass` bridge is treated as a backward-compatible additive semantic change, so core advanced from `0.1.0` to `0.2.0`.

Published term IRIs are never silently repurposed. Materially incompatible meanings should be deprecated and replaced explicitly rather than changing meaning behind an existing IRI.

## Module dependencies

Resolvable ontology IRIs do not by themselves require `owl:imports`.

ESKA represents architectural/module dependencies using `dcterms:requires`, and executable references merge required model artifacts deliberately. The core-to-SMO alignment follows the same rule by depending on immutable `https://w3id.org/smo/0.1.0` without introducing network import closure.

## Publication and dereferencing

Current public behavior remains:

```text
https://w3id.org/eska#Execution
        │ fragment removed by HTTP client
        ▼
https://w3id.org/eska
        │ W3ID redirect / content negotiation
        ├── human-readable project documentation
        └── current machine-readable RDF distribution
```

Stable unversioned module routes follow governed current source. Immutable version routes are activated only after their release-backed target exists and is verified.

## Namespace migration and publication history

The permanent namespace and governed publication were established in explicit stages:

1. publication strategy and machine-described predecessor/target identities;
2. current W3ID resolver activation through #6530;
3. atomic semantic migration to `https://w3id.org/eska#`;
4. governed `eska-v0.1.0` repository release;
5. immutable first-version routes through #6535;
6. core `0.2.0` SMO compatibility bridge;
7. governed `eska-v0.2.0` repository release;
8. core `0.2.0` immutable W3ID routing — pending.

The predecessor relation remains recorded in `model/namespace-migration.json`. ESKA does not use `owl:sameAs` as a namespace-migration shortcut.

## Compatibility and authority boundary

With the permanent namespace active:

- published term IRIs are never silently repurposed;
- `eska:SemanticModel` remains resolvable and non-deprecated in the first SMO alignment;
- compatible additions do not require namespace changes;
- published versioned ontology IRIs remain immutable;
- persistent W3ID routes may change backend locations without changing semantic identity.

```text
GerhardBalz/executable-semantic-knowledge-architecture
    source governance
        ↓
https://w3id.org/eska
    persistent public identity / resolver
        ↓
HTML / RDF publication backend
    replaceable distribution location
```

GitHub locations are publication backends, never ESKA semantic identities.
