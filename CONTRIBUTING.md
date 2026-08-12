# Contributing to ESKA

Contributions should preserve the distinction between semantic meaning, executable behavior, publication identity, and repository-specific implementation concerns established by the ESKA architecture.

## Documentation conventions

ESKA adopts the shared [Semantic Markdown convention](https://github.com/GerhardBalz/semantic-knowledge-engineering/blob/main/conventions/semantic-markdown.md) maintained by the Semantic Knowledge Engineering (SKE) initiative.

Use Markdown structure according to the meaning of the content:

1. use ordered lists for procedures and sequences where order is meaningful;
2. use unordered lists for non-sequential collections;
3. reserve fenced blocks for code, syntax, literal/preformatted content, identifiers, diagrams, output, or other cases where formatting is semantically significant.

Do not convert semantic diagrams, alignment layouts, command blocks, RDF/SPARQL/Turtle snippets, execution traces, or other intentionally preformatted material merely to avoid fenced blocks.

The shared convention originated from review feedback by @TallTed on `perma-id/w3id.org#6530`, where a procedural sequence was more appropriately represented as a native Markdown ordered list. ESKA issue #72 records the local adoption of that convention.

Repository-specific documentation needs may specialize the shared convention, but exceptions should be intentional and should preserve the meaning carried by formatting.

## Evidence before abstraction

ESKA evolves from executable evidence. New generic concepts should be justified by implemented use cases and should not duplicate semantics already owned by established standards or by source repositories.

In particular:

- Pizza-domain semantics remain owned by `GerhardBalz/pizza-ontology`;
- reusable Semantic Modeling concepts belong in `GerhardBalz/semantic-modeling-ontology` where established;
- ESKA owns execution, capability, result, verification, service, agent, and deployment architecture;
- cross-repository conventions and initiative coordination belong in `GerhardBalz/semantic-knowledge-engineering`.
