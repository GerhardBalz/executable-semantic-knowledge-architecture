# ESKA publication distributions

This directory contains **generated publication distributions** for Executable Semantic Knowledge Architecture (ESKA).

They are publication targets, not an independent semantic source of truth.

```text
model/eska-*.ttl
    authoritative semantic modules
        ↓ verified graph union

dist/eska.ttl
    combined RDF publication distribution
```

`dist/eska.ttl` currently preserves the provisional namespace:

```text
https://w3id.org/eska#
```

The permanent target namespace defined by `model/publication-contract.json` is:

```text
https://w3id.org/eska#
```

That target is **not active yet**. The combined distribution must not contain permanent W3ID term IRIs before the W3ID resolver has been established and independently verified.

`model/verify-publication-targets.py` checks that the combined distribution is graph-equivalent to the union of all authoritative ontology modules and that publication activation boundaries are preserved.
