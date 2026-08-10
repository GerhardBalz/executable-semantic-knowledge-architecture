# Pizza example provenance and license

ESKA does not store a second source-of-truth copy of the Pizza semantic artifacts used by this example.

The domain artifacts are owned and published by the companion repository:

- Source repository: <https://github.com/GerhardBalz/pizza-ontology>
- Pinned source commit: `715f0460a43abacb5258eedd3d722da219a25a43`
- Consumer manifest: `artifacts/manifest.ttl`
- ESKA binding: [`pizza-domain-source.json`](pizza-domain-source.json)

At runtime, [`fetch-domain-artifacts.py`](fetch-domain-artifacts.py) materializes the pinned files under `.work/pizza-domain/`. These runtime copies are disposable execution inputs, not ESKA-owned semantic sources.

## Historical Pizza-derived reasoning material

`artifacts/reasoning/spicy-pizza.ofn` contains selected semantic content derived from Pizza Ontology 2.0 and retains the upstream **CC BY 3.0** boundary and historical contributor attribution.

## Repository-authored semantic-engineering artifacts

The Pizza repository identifies the following newly authored artifacts as **MIT License** material.

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

### Workflow execution

```text
artifacts/workflows/pizza-menu-publication.bpmn
artifacts/workflows/workflow-vocabulary.ttl
artifacts/workflows/data/valid-pizza.ttl
artifacts/workflows/data/invalid-pizza.ttl
artifacts/workflows/data/expected-valid-menu.ttl
artifacts/workflows/data/cases.json
```

The BPMN process is identified by the Pizza manifest as conforming to BPMN 2.0.2. It owns orchestration semantics while its semantic tasks remain bound to the separately published SHACL and Mapping artifacts.

ESKA does not copy the BPMN process, workflow vocabulary, cases, or workflow data into its source tree. ESKA supplies the Workflow Semantic Capability, source-operation→Capability bindings, composite execution structure, Result/Verification semantics, and provenance around the pinned external artifacts.

## ESKA material

The MIT license at the root of this repository applies to newly created ESKA material such as:

- `SemanticCapability`, Service, and Agent contracts;
- runtime fetch/binding code;
- mode-specific refinements and operation bindings defined by ESKA examples;
- execution and verification code;
- ESKA provenance records;
- ESKA documentation.

It does not replace the license of externally consumed semantic material.

The provenance/licensing chain is explicit:

```text
Pizza-derived reasoning semantics       CC BY 3.0 → ESKA reasoning architecture       MIT
Pizza SHACL/data                        MIT       → ESKA validation execution          MIT
Pizza rule/vocabulary/data              MIT       → ESKA rule execution                MIT
Pizza DMN/vocabulary/cases              MIT       → ESKA decision execution            MIT
Pizza OpenMath/vocabulary/cases         MIT       → ESKA calculation execution         MIT
Pizza mapping/target model/source data  MIT       → ESKA transformation execution      MIT
Pizza BPMN/workflow vocabulary/cases    MIT       → ESKA composite workflow execution  MIT
```
