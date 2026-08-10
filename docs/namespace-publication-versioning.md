# ESKA namespace, publication, and versioning strategy

## Decision

ESKA now has enough executable evidence to define its publication contract, but the permanent namespace must **not** be activated until a persistent resolver and actual publication targets exist.

The adopted target term namespace is:

```text
https://w3id.org/eska#
```

The current namespace remains authoritative until activation:

```text
urn:eska:core:
```

This is intentional. A resolvable-looking identifier must not be introduced before it resolves.

The machine-readable contract is [`model/publication-contract.json`](../model/publication-contract.json).

## Why a hash namespace

ESKA currently defines a relatively small vocabulary whose terms form one conceptual architecture and evolve together. The permanent term namespace therefore uses a hash namespace:

```text
https://w3id.org/eska#Execution
https://w3id.org/eska#SemanticCapability
https://w3id.org/eska#KnowledgeService
https://w3id.org/eska#KnowledgeAgent
https://w3id.org/eska#ServiceDeployment
```

Dereferencing an ESKA term removes the fragment and resolves the shared vocabulary resource at:

```text
https://w3id.org/eska
```

The persistent resolver is deliberately separate from the eventual HTML/RDF hosting implementation. The redirect target can move without changing semantic identifiers.

## Identity layers

ESKA distinguishes five identity/version layers.

### 1. Term IRI

Terms use one stable, unversioned namespace:

```text
https://w3id.org/eska#Execution
```

Compatible vocabulary evolution does not create a new term IRI merely because a module or repository release changes.

### 2. Stable module ontology IRI

The vocabulary remains split into independently governed ontology documents:

```text
https://w3id.org/eska/model/core
https://w3id.org/eska/model/capability
https://w3id.org/eska/model/service
https://w3id.org/eska/model/agent
https://w3id.org/eska/model/deployment
```

The modules remain separate because the executable architecture has demonstrated different stability boundaries:

- core is cross-mode and deliberately small;
- capability contains helper terms not justified as core;
- service captures operational exposure;
- agent captures deterministic discovery/invocation adaptation;
- deployment captures runtime location independently from service semantics.

A combined RDF distribution is a publication convenience, not a replacement for module identity.

### 3. Versioned module ontology IRI

Each module has an independently versioned immutable description:

```text
https://w3id.org/eska/model/core/0.1.0
https://w3id.org/eska/model/service/0.4.0
```

The current provisional module versions become the first published SemVer values without pretending that all modules evolved at the same rate:

| Module | Current | First published |
|---|---:|---:|
| core | `0.1-provisional` | `0.1.0` |
| capability | `0.2-provisional` | `0.2.0` |
| service | `0.4-provisional` | `0.4.0` |
| agent | `0.3-provisional` | `0.3.0` |
| deployment | `0.1-provisional` | `0.1.0` |

### 4. Distribution location

Logical publication routes are stable under the persistent namespace:

```text
https://w3id.org/eska/dist/eska.ttl
https://w3id.org/eska/dist/<version>/eska-core.ttl
https://w3id.org/eska/docs
```

The resolver may redirect these routes to GitHub Pages, immutable GitHub release assets, or another controlled hosting target. Consumers should depend on the persistent route, not the current backend host.

### 5. Repository release

Repository releases use:

```text
eska-v<major>.<minor>.<patch>
```

The first governed publication bundle is planned as:

```text
eska-v0.1.0
```

A repository release is a snapshot of the architecture, examples, documentation, tooling, and ontology modules. It is **not** a semantic version assertion for every module contained in that release.

## Semantic versioning policy

Ontology modules follow SemVer-style change classification.

### Patch

Use a patch increment for changes that preserve the intended machine-interpretable contract, for example:

- documentation and annotations;
- metadata improvements;
- typo corrections;
- publication/distribution fixes that do not change term meaning.

### Minor

Use a minor increment for backward-compatible additive semantic evolution, for example:

- new terms;
- new optional relationships;
- additional axioms that preserve established intended use.

### Major

Use a major increment for breaking semantic contract changes.

A materially incompatible change to the meaning of an existing term should normally deprecate and replace that term rather than silently reusing its IRI with a different meaning. A major module version does not by itself justify a new global term namespace.

## Publication and dereferencing

The intended public behavior is:

```text
term IRI
https://w3id.org/eska#Execution
        │ fragment removed by HTTP client
        ▼
https://w3id.org/eska
        │ persistent redirect / content negotiation
        ├── human-readable vocabulary documentation
        └── machine-readable RDF vocabulary distribution
```

Stable module and version routes provide module-specific RDF/documentation when consumers need a smaller or immutable artifact.

## Dependency representation

The first publication does not automatically replace the existing explicit module dependency pattern:

```turtle
dcterms:requires <...>
```

with `owl:imports` merely because the ontology IRIs become resolvable.

The executable reference currently merges required model artifacts explicitly. `owl:imports` should be introduced only if a future executable use case demonstrates that formal import closure is desirable and does not create unwanted network/runtime coupling.

## Migration from provisional URNs

The migration must be one deliberate, reviewable change rather than gradual mixed-namespace drift.

### Stage A — strategy established

Current state after this issue:

```text
terms:     urn:eska:core:*
modules:   urn:eska:model:*
strategy:  target https://w3id.org/eska#
status:    planned-not-active
```

CI verifies that permanent IRIs have **not** leaked into the ontology source before activation.

### Stage B — establish the resolver

Create and merge the W3ID redirect configuration for `https://w3id.org/eska` and deploy the actual HTML/RDF targets.

Verify at minimum:

- the vocabulary route resolves;
- human-readable documentation is available;
- RDF is available through the defined publication routes;
- module and version routes resolve;
- redirects can be changed without changing ESKA semantic identifiers.

### Stage C — namespace migration commit

Only after Stage B is live:

1. migrate every defined term one-to-one by local name:

   ```text
   urn:eska:core:Execution
       →
   https://w3id.org/eska#Execution
   ```

2. migrate ontology IRIs to the stable module IRIs;
3. add `owl:versionIRI` for the first published module versions;
4. retain explicit predecessor metadata for the provisional ontology identifiers;
5. generate and preserve a machine-readable predecessor map from every provisional term IRI to its permanent replacement;
6. run the complete seven-mode, Service/Agent/Deployment, and provenance-lineage reference suite.

Do not use `owl:sameAs` merely to bridge the old and new namespace. The migration record should describe predecessor/replacement history without asserting an unnecessarily strong identity relation.

### Stage D — first governed release

Create:

```text
eska-v0.1.0
```

and publish the combined and module-specific RDF distributions through the persistent routes.

The release tag must identify an immutable repository snapshot. The persistent namespace remains unversioned; versioned ontology/distribution routes identify immutable semantic descriptions.

## Compatibility and deprecation

Once the permanent namespace is active:

- published term IRIs are never silently repurposed;
- removed terms remain resolvable and are marked deprecated;
- replacement terms are linked explicitly;
- compatible additions do not require namespace changes;
- published versioned ontology IRIs remain immutable;
- persistent routes may change their backend redirect target without changing semantic identity.

## Authority boundary

The GitHub repository is the source-governance location for ESKA. `w3id.org` is the persistent public identifier/redirect layer. The eventual documentation/RDF host is a distribution target.

```text
GerhardBalz/executable-semantic-knowledge-architecture
    source governance
        ↓
w3id.org/eska
    persistent public identity
        ↓
HTML / RDF publication backend
    replaceable distribution location
```

Owning the repository does not make a not-yet-configured Web namespace resolvable. The permanent namespace becomes authoritative only when the resolver configuration and published artifacts actually exist.

## What this decision does not do

This strategy does **not**:

- migrate current source files to `https://w3id.org/eska#` yet;
- claim that the W3ID route is already configured;
- create a GitHub Release or tag;
- merge the ontology modules into one ontology identity;
- add `owl:imports` by symmetry;
- introduce a new ESKA publication/governance ontology;
- treat repository SemVer as identical to ontology-module SemVer.

Publication follows demonstrated semantic stability, and activation follows actual resolvability.
