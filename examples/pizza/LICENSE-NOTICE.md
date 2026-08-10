# Pizza example provenance and license

ESKA does not store a second source-of-truth copy of the Pizza semantic artifacts used by this example.

The domain artifacts are owned and published by the companion repository:

- Source repository: <https://github.com/GerhardBalz/pizza-ontology>
- Pinned source commit: `bba9fa883f326ebeb395140abd523dc517caf071`
- Consumer manifest: `artifacts/manifest.ttl`
- ESKA binding: [`pizza-domain-source.json`](pizza-domain-source.json)

At runtime, [`fetch-domain-artifacts.py`](fetch-domain-artifacts.py) materializes the pinned files under `.work/pizza-domain/`. These runtime copies are disposable execution inputs, not ESKA-owned semantic sources.

## Reasoning module

The coherent reasoning module:

```text
artifacts/reasoning/spicy-pizza.ofn
```

contains selected semantic content derived from the historical Pizza Ontology 2.0. The Pizza source repository records its upstream provenance and identifies the reasoning module as **Creative Commons Attribution 3.0 (CC BY 3.0)** material.

The historical Pizza ontology credits:

- Alan Rector
- Chris Wroe
- Matthew Horridge
- Nick Drummond
- Robert Stevens

## Validation profile and data

The source repository also publishes:

```text
artifacts/validation/pizza-instance-shapes.ttl
artifacts/validation/data/conforming.ttl
artifacts/validation/data/non-conforming.ttl
```

These are newly authored semantic-engineering artifacts. The Pizza artifact manifest identifies them under the **MIT License**.

## Rule semantics and data

The third execution mode consumes:

```text
artifacts/rules/vegetarian-warning.rq
artifacts/rules/rule-vocabulary.ttl
artifacts/rules/data/menu-pizzas.ttl
```

These source-owned SPARQL rule, vocabulary, and RDF input artifacts are also repository-authored semantic-engineering material identified as **MIT License** in the Pizza manifest.

ESKA does not copy those rule semantics into its own source tree. It supplies the Semantic Capability, evaluator binding, execution, verification, result model, and provenance around the pinned external artifacts.

## ESKA material

The MIT license at the root of this repository applies to newly created ESKA material such as:

- `SemanticCapability`, Service, and Agent contracts;
- runtime fetch/binding code;
- execution and verification code;
- ESKA provenance records;
- ESKA documentation.

It does not replace the license of externally consumed semantic material.

The licensing/provenance chain is therefore explicit:

```text
Pizza Ontology-derived reasoning semantics
    CC BY 3.0
        ↓ pinned source artifact
ESKA reasoning execution architecture
    MIT

Pizza repository-authored SHACL/data
    MIT
        ↓ pinned source artifact
ESKA validation execution
    MIT

Pizza repository-authored rule/vocabulary/data
    MIT
        ↓ pinned source artifact
ESKA rule evaluation execution
    MIT
```
