# Pizza semantic mapping

This directory implements the sixth ESKA execution mode:

```text
Mapping → transform
```

It consumes the source-owned mapping artifacts from the companion `pizza-ontology` repository and tests whether a transformation with distinct source, mapping, and target semantic roles still fits the provisional ESKA core.

## Source-owned semantics

The pinned Pizza source provides:

- Pizza RDF source data;
- a SPARQL 1.1 `CONSTRUCT` mapping;
- a target Menu projection semantic model;
- a canonical expected target graph.

ESKA does not copy those semantic source artifacts.

## Semantic Capability

[`pizza-menu-projection-capability.ttl`](pizza-menu-projection-capability.ttl) defines `PizzaMenuProjectionCapability`.

```text
Input
    PizzaSourceGraph

Output
    MenuProjectionGraph

Produced relations
    rdf:type
    menu:displayName
    menu:ingredientName

Source semantic model
    Pizza vocabulary

Mapping semantic model
    source-owned SPARQL CONSTRUCT mapping

Target semantic model
    source-owned Menu projection vocabulary

Executable artifact
    SPARQL mapping evaluation with RDFLib
```

## Role-specific semantic models

Mapping is the first reference mode that needs to distinguish several semantic-model roles machine-readably.

The example therefore defines:

```text
map:sourceSemanticModel
map:targetSemanticModel
map:mappingSemanticModel
```

as mapping-local subproperties of:

```text
eska:usesSemanticModel
```

The Capability also states all three models through the generic `eska:usesSemanticModel` property.

This creates a useful layering rule:

```text
ESKA core
    usesSemanticModel
        ↑ generic cross-mode relation

Mapping example/extension
    sourceSemanticModel
    targetSemanticModel
    mappingSemanticModel
        ↑ role-specific refinement
```

The role properties are **not** promoted into `eska-core.ttl` because Mapping alone does not provide enough cross-mode evidence for them.

## Execute

```bash
python -m pip install -r examples/pizza/mappings/requirements.txt
python examples/pizza/mappings/evaluate.py
```

The runner:

1. materializes the commit-pinned Pizza mapping artifacts;
2. verifies the Mapping Semantic Capability and semantic-model roles;
3. evaluates the source-owned SPARQL transformation;
4. verifies exact target-graph equality with the source-owned expected output;
5. verifies that Pizza source classes/predicates do not leak into the target graph;
6. records one `Execution → Result → Verification` chain;
7. records source/mapping/target semantic roles using qualified PROV-O usage.

## Architectural significance

This mode differs from the earlier Rule mode even though both use SPARQL `CONSTRUCT` operationally:

```text
Rule
    source model
        ↓ derive
    source-domain statement

Mapping
    source model
        ↓ mapping model
    target model
        ↓
    transformed graph
```

The experiment therefore tests whether ESKA should classify execution modes by implementation technology or by semantic contract. The current design keeps the core technology-neutral and lets native/mapping-specific semantics provide the precision.
