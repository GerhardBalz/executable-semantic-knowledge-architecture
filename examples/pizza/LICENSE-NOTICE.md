# Pizza example provenance and license

ESKA does not store a second source-of-truth copy of the Pizza semantic artifacts used by this example.

The domain artifacts are owned and published by the companion repository:

- Source repository: <https://github.com/GerhardBalz/pizza-ontology>
- Pinned source commit: `ef05531c5a362d8d1454e94e59a44f750515dd1c`
- Consumer manifest: `artifacts/manifest.ttl`
- ESKA binding: [`pizza-domain-source.json`](pizza-domain-source.json)

At runtime, [`fetch-domain-artifacts.py`](fetch-domain-artifacts.py) materializes the pinned files under `.work/pizza-domain/`. These runtime copies are disposable execution inputs, not ESKA-owned semantic sources.

## Historical Pizza-derived reasoning material

`artifacts/reasoning/spicy-pizza.ofn` contains selected semantic content derived from Pizza Ontology 2.0 and retains the upstream **CC BY 3.0** boundary and historical contributor attribution.

## Repository-authored semantic-engineering artifacts

The Pizza repository identifies the following newly authored artifacts as **MIT License** material:

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

### Calculation

```text
artifacts/calculations/pizza-area.openmath.xml
artifacts/calculations/calculation-vocabulary.ttl
artifacts/calculations/data/cases.json
```

### Semantic mapping

```text
artifacts/mappings/pizza-to-menu.rq
artifacts/mappings/menu-vocabulary.ttl
artifacts/mappings/data/source-pizzas.ttl
artifacts/mappings/data/expected-menu.ttl
```

The mapping artifacts separately represent the transformation semantics, target Menu semantic model, canonical source graph, and expected target graph. ESKA does not copy them into its source tree; it supplies the Mapping Semantic Capability, role-specific semantic-model refinements, execution, verification, result, and PROV-O lineage around the pinned external artifacts.

## ESKA material

The MIT license at the root of this repository applies to newly created ESKA material such as:

- `SemanticCapability`, Service, and Agent contracts;
- runtime fetch/binding code;
- mode-specific role refinements defined by ESKA examples;
- execution and verification code;
- ESKA provenance records;
- ESKA documentation.

It does not replace the license of externally consumed semantic material.

The provenance/licensing chain is explicit:

```text
Pizza-derived reasoning semantics      CC BY 3.0 → ESKA reasoning architecture      MIT
Pizza SHACL/data                       MIT       → ESKA validation execution         MIT
Pizza rule/vocabulary/data             MIT       → ESKA rule execution               MIT
Pizza DMN/vocabulary/cases             MIT       → ESKA decision execution           MIT
Pizza OpenMath/vocabulary/cases        MIT       → ESKA calculation execution        MIT
Pizza mapping/target model/source data MIT       → ESKA transformation execution     MIT
```
