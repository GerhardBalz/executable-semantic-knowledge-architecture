# ESKA core 0.2.0 W3ID activation evidence

Upstream `perma-id/w3id.org#6543` was merged on 13 August 2026.

Merged upstream evidence:

```text
source head
0a213385a247adcf3293c1077e9c58e64fda9308

upstream merge commit
1230ac37c2100f752e2071606103b81f445d5d5c
```

The upstream configuration adds only the immutable ESKA core 0.2.0 routes and targets `eska-v0.2.0`, never mutable `main`.

The repository-owned mirror in `publication/w3id/eska/.htaccess` is synchronized with that active upstream configuration in the same change.

Live verification is intentionally performed from GitHub-hosted CI because the local execution environment used to prepare this evidence could not resolve `w3id.org` through DNS. The dedicated workflow requires all three public representations to resolve through an HTTP 303 chain to the immutable release backends:

```text
https://w3id.org/eska/model/core/0.2.0          Accept: text/html
https://w3id.org/eska/model/core/0.2.0          Accept: text/turtle
https://w3id.org/eska/dist/0.2.0/eska-core.ttl  Accept: text/turtle
```

Expected immutable backend:

```text
eska-v0.2.0/model/eska-core.ttl
```

Publication metadata must remain route-pending until this live CI gate passes. After successful verification, the follow-up state transition marks the core 0.2.0 route active and records the upstream PR and merge commit in governed publication metadata.
