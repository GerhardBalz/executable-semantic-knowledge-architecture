# ESKA permanent identifier configuration

This directory mirrors the governed W3ID routing configuration for:

```text
https://w3id.org/eska
```

Project:

- **Executable Semantic Knowledge Architecture (ESKA)**
- Repository: `GerhardBalz/executable-semantic-knowledge-architecture`
- Point of contact: **Gerhard Balz** — GitHub `@GerhardBalz`

## Status

The permanent namespace is active.

Current routes were established through `perma-id/w3id.org#6530`. The first immutable module-version routes were added through `perma-id/w3id.org#6535` and target only the governed `eska-v0.1.0` release.

The stable term namespace is:

```text
https://w3id.org/eska#
```

## Current routing

Unversioned routes represent current governed `main`:

- vocabulary/documentation: `https://w3id.org/eska`;
- combined Turtle: `https://w3id.org/eska/dist/eska.ttl`;
- stable module routes under `https://w3id.org/eska/model/{module}`.

The active immutable routes for module versions first published in `eska-v0.1.0` remain bound to that tag, including core `0.1.0`, capability `0.2.0`, service `0.4.0`, agent `0.3.0`, and deployment `0.1.0`.

## Core 0.2.0 staging boundary

ESKA core `0.2.0` introduces the reviewed compatibility bridge to the published SMO `SemanticModel` class.

The planned immutable identities are:

```text
https://w3id.org/eska/model/core/0.2.0
https://w3id.org/eska/dist/0.2.0/eska-core.ttl
```

They are **not routed yet**.

The required order is:

1. merge and verify the core `0.2.0` semantic source on `main`;
2. publish governed repository release `eska-v0.2.0`;
3. verify the tagged core backend;
4. add the core `0.2.0` W3ID routes targeting only `eska-v0.2.0`;
5. verify the new immutable routes externally.

No immutable version route may target mutable `main`.

GitHub URLs are publication backends only; ESKA semantic identity remains in the W3ID namespace.
