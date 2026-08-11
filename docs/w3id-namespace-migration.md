# ESKA permanent W3ID namespace migration

On 11 August 2026, upstream W3ID pull request `perma-id/w3id.org#6530` was merged and the live resolver was externally verified before semantic source migration.

ESKA then performs one deliberate migration from the provisional term namespace to the permanent W3ID namespace:

```text
urn:eska:core:<local-name>
    →
https://w3id.org/eska#<local-name>
```

The five ontology document identities migrate from `urn:eska:model:<module>` to `https://w3id.org/eska/model/<module>`. Their first published semantic versions use explicit `owl:versionIRI` values.

`model/namespace-migration.json` is the machine-readable predecessor inventory for all 53 declared terms and all five ontology IRIs. Namespace migration deliberately does not use `owl:sameAs`.

The repository release `eska-v0.1.0` remains the separate Stage-4 publication step after this migration commit and the complete executable reference suite are verified.
