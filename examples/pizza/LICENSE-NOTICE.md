# Pizza example provenance and license

ESKA does not store a second source-of-truth copy of the Pizza semantic artifacts used by this example.

The domain artifacts are owned and published by the companion repository:

- Source repository: <https://github.com/GerhardBalz/pizza-ontology>
- Pinned source commit: `fcefdc7acddf2ca9a9dc4dad9e410cea992011ff`
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

## Repository-authored semantic-engineering artifacts

The source repository publishes the following newly authored artifacts under the **MIT License**:

### Validation

```text
artifacts/validation/pizza-instance-shapes.ttl
artifacts/validation/data/conforming.ttl
artifacts/validation/data/non-conforming.ttl
```

### Rule evaluation

```text
artifacts/rules/vegetarian-warning.rq
artifacts/rules/rule-vocabulary.ttl
artifacts/rules/data/menu-pizzas.ttl
```

### Decision evaluation

```text
artifacts/decisions/pizza-dietary-suitability.dmn
artifacts/decisions/decision-vocabulary.ttl
artifacts/decisions/data/cases.json
```

The manifest identifies the decision model as conforming to DMN 1.5.

### Calculation

```text
artifacts/calculations/pizza-area.openmath.xml
artifacts/calculations/calculation-vocabulary.ttl
artifacts/calculations/data/cases.json
```

The manifest identifies the mathematical formula as conforming to OpenMath 2.0 Revision 2. ESKA does not copy the formula, vocabulary, or calculation cases into its source tree. It supplies the bounded Semantic Capability, OpenMath evaluator binding, Execution, Result, Verification, and PROV-O lineage around the pinned artifacts.

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

Pizza repository-authored DMN/vocabulary/cases
    MIT
        ↓ pinned source artifact
ESKA decision evaluation execution
    MIT

Pizza repository-authored OpenMath/vocabulary/cases
    MIT
        ↓ pinned source artifact
ESKA calculation execution
    MIT
```
