# ESKA documentation conventions

ESKA adopts the shared [Semantic Markdown convention](https://github.com/GerhardBalz/semantic-knowledge-engineering/blob/main/conventions/semantic-markdown.md) from the Semantic Knowledge Engineering (SKE) initiative.

## Convention

Use Markdown structure according to content semantics:

1. use ordered lists when the reader must perform or understand steps in sequence;
2. use unordered lists for collections whose order is not meaningful;
3. use fenced blocks only when literal formatting, code, syntax, identifiers, diagrams, output, or alignment is part of the intended meaning.

## ESKA review

The adoption review covered the root overview, namespace/publication documentation, the W3ID migration note, the Pizza executable overview, and execution-mode documentation used by the reference examples.

The fenced `text` blocks retained in those documents are predominantly semantic diagrams, architecture mappings, namespace/identifier specimens, execution-mode mappings, formulas, aligned comparison output, or other deliberately preformatted content. Converting those blocks to Markdown lists would remove useful structure rather than improve semantics.

The procedural material reviewed already uses native Markdown ordered lists where sequence matters. For example, namespace migration history and evaluator/runtime steps are represented as ordered lists rather than fenced pseudo-lists.

The specific W3ID pre-activation procedural block that prompted ESKA #72 no longer exists because the ESKA namespace is active. No historical or immutable publication artifact is changed merely to restyle that removed material.

## Provenance

This convention was promoted into SKE after feedback from @TallTed on `perma-id/w3id.org#6530`, which recommended using a native Markdown ordered list for a procedural sequence instead of a fenced `text` block.

ESKA #72 is the first participating-repository adoption case for the shared SKE convention.

## Boundary

This is a documentation-structure convention only. It does not change ESKA ontology semantics, executable behavior, publication identifiers, provenance contracts, or immutable `eska-v0.1.0` content.
