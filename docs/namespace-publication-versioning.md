# ESKA namespace, publication, and versioning

## Current state

ESKA uses the permanent term namespace:

```text
https://w3id.org/eska#
```

The W3ID resolver was established by `perma-id/w3id.org#6530` and externally verified before the semantic source was migrated. The five authoritative ontology modules now use stable W3ID ontology IRIs and explicit published `owl:versionIRI` values.

The machine-readable publication contract is [`model/publication-contract.json`](../model/publication-contract.json), and the explicit provisional→permanent predecessor inventory is [`model/namespace-migration.json`](../model/namespace-migration.json).

## Term namespace

ESKA terms share one stable, unversioned hash namespace:

```text
https://w3id.org/eska#Execution
https://w3id.org/eska#SemanticCapability
https://w3id.org/eska#KnowledgeService
https://w3id.org/eska#KnowledgeAgent
https://w3id.org/eska#ServiceDeployment
```

Dereferencing a term removes the fragment and resolves the shared vocabulary resource at `https://w3id.org/eska`. The resolver is deliberately independent of the current GitHub publication backend so that hosting can move without changing semantic identifiers.

## Ontology modules and versions

The vocabulary remains split into independently governed ontology documents:

| Module | Stable ontology IRI | First published version IRI |
|---|---|---|
| core | `https://w3id.org/eska/model/core` | `https://w3id.org/eska/model/core/0.1.0` |
| capability | `https://w3id.org/eska/model/capability` | `https://w3id.org/eska/model/capability/0.2.0` |
| service | `https://w3id.org/eska/model/service` | `https://w3id.org/eska/model/service/0.4.0` |
| agent | `https://w3id.org/eska/model/agent` | `https://w3id.org/eska/model/agent/0.3.0` |
| deployment | `https://w3id.org/eska/model/deployment` | `https://w3id.org/eska/model/deployment/0.1.0` |

The different version numbers intentionally preserve the demonstrated evolution of each module rather than flattening all modules to one semantic version.

A combined RDF distribution at `https://w3id.org/eska/dist/eska.ttl` is a publication convenience and does not replace the five module identities.

## Repository release versioning

Repository releases use:

```text
eska-v<major>.<minor>.<patch>
```

The first governed publication bundle is planned as `eska-v0.1.0`. Repository release versioning is independent from ontology-module semantic versions: a repository release snapshots the architecture, examples, documentation, tooling, and ontology modules together.

## Semantic versioning policy

Module versions follow a SemVer-style compatibility policy:

- **patch** — documentation, annotations, metadata, or corrections that preserve the intended machine-interpretable contract;
- **minor** — backward-compatible additive semantics such as new terms, optional relationships, or compatible axioms;
- **major** — breaking semantic contract changes.

Published term IRIs are not silently repurposed. Materially incompatible meanings should be deprecated and replaced explicitly rather than changing the meaning behind an existing IRI.

## Publication and dereferencing

The intended public behavior is:

```text
https://w3id.org/eska#Execution
        │ fragment removed by HTTP client
        ▼
https://w3id.org/eska
        │ W3ID 303 redirect / content negotiation
        ├── human-readable project/vocabulary documentation
        └── machine-readable RDF distribution
```

Stable module routes provide module-specific RDF/documentation. Versioned module/distribution routes are reserved for immutable governed publication artifacts.

## Module dependencies

Resolvable ontology IRIs do not by themselves require `owl:imports`. ESKA currently represents module dependencies explicitly with `dcterms:requires` and the executable reference merges the required model artifacts deliberately. `owl:imports` should be introduced only if a future executable use case demonstrates a useful formal import closure without unwanted network/runtime coupling.

## Namespace migration history

The permanent namespace was activated in explicit stages:

1. **Publication strategy** — the provisional source namespace and target W3ID namespace were machine-described.
2. **Resolver activation** — W3ID PR #6530 was merged and live HTML/RDF/module routes were externally verified while source IRIs remained provisional.
3. **Atomic semantic migration** — every declared ESKA term was migrated one-to-one by local name, the five ontology IRIs were migrated, first published module `owl:versionIRI` values were added, and all examples, queries, provenance fixtures, distributions, and verification logic were updated together.
4. **Governed repository release** — `eska-v0.1.0` is a separate publication step after the migration commit is verified.

The predecessor relation is recorded explicitly in `model/namespace-migration.json`. ESKA does **not** use `owl:sameAs` merely as a namespace-migration shortcut.

## Compatibility and deprecation

With the permanent namespace active:

- published term IRIs are never silently repurposed;
- removed terms remain resolvable and are marked deprecated;
- replacement terms are linked explicitly;
- compatible additions do not require namespace changes;
- published versioned ontology IRIs remain immutable;
- persistent W3ID routes may change their backend redirect target without changing semantic identity.

## Authority boundary

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

W3ID provides persistent public identity and redirects; the repository governs ESKA source. The backend location is deliberately replaceable.

## Boundaries

The namespace/publication model does not:

- collapse the five ontology modules into one ontology identity;
- make repository SemVer identical to module SemVer;
- add `owl:imports` by symmetry;
- introduce a separate ESKA publication/governance ontology;
- use `owl:sameAs` for predecessor migration;
- publish the `eska-v0.1.0` repository release as part of the Stage-3 migration itself.
