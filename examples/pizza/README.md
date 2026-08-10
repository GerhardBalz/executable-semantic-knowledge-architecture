# Pizza: executable semantic knowledge reference

This directory contains the executable Pizza reference examples for **Executable Semantic Knowledge Architecture (ESKA)**.

The reference tests different formal execution semantics while preserving a strict repository boundary:

```text
pizza-ontology
    owns Pizza domain semantics
        ↓ immutable commit + artifact manifest
ESKA
    operationalizes those semantics
```

ESKA does not maintain source copies of the Pizza OWL, SHACL, SPARQL, DMN, OpenMath, Mapping, or BPMN semantic artifacts used here. [`pizza-domain-source.json`](pizza-domain-source.json) pins `GerhardBalz/pizza-ontology` to an immutable Git commit, and [`fetch-domain-artifacts.py`](fetch-domain-artifacts.py) materializes the published artifacts under `.work/pizza-domain/` at execution time.

## Semantic source binding

```text
Repository
    GerhardBalz/pizza-ontology

Commit
    715f0460a43abacb5258eedd3d722da219a25a43

Manifest
    artifacts/manifest.ttl
```

The manifest publishes **twenty-three** source-owned semantic distributions consumed by this reference:

- coherent Pizza OWL reasoning module;
- Pizza instance SHACL profile plus conforming/non-conforming RDF examples;
- vegetarian-warning SPARQL rule, result vocabulary, and rule RDF data;
- DMN dietary-suitability decision, decision vocabulary, and canonical contexts;
- OpenMath Pizza-area formula, calculation vocabulary, and calculation cases;
- Pizza-to-Menu SPARQL mapping, Menu target vocabulary, source graph, and expected target graph;
- BPMN menu-publication workflow, workflow vocabulary, valid/invalid inputs, expected target graph, and workflow cases.

```text
artifact role/path
        +
pinned Git commit
        ↓
immutable semantic input
```

Runtime copies beneath `.work/` are disposable execution inputs, not a second semantic source of truth.

## Seven execution modes

```text
OWL         → reason
SHACL       → validate
SPARQL rule → evaluate
DMN         → decide
OpenMath    → calculate
Mapping     → transform
BPMN        → execute
```

All seven modes use the same provisional core Capability and runtime abstractions. Classification and Validation additionally provide the working cross-mode Service / Agent / Deployment evidence.

## 1. OWL Classification — reason

The source-owned coherent module does not assert:

```text
AmericanHot SubClassOf SpicyPizza
```

HermiT derives it through OWL semantics.

```text
Pizza reasoning module        pizza-ontology
        ↓ pinned fetch
HermiT reasoning              ESKA execution
        ↓
AmericanHot ⊑ SpicyPizza
        ↓
PizzaClassificationCapability
```

[`pizza-classification-capability.ttl`](pizza-classification-capability.ttl) describes the bounded `owl:Class → owl:Class` Capability producing `rdfs:subClassOf`.

## 2. SHACL Validation — validate

See [`validation/README.md`](validation/README.md).

`PizzaValidationCapability` consumes a Pizza RDF graph, uses the commit-pinned SHACL profile, and produces a `sh:ValidationReport` through `sh:conforms`.

The source-owned non-conforming fixture deliberately produces both a missing-base violation and a wrongly typed topping violation.

## 3. SPARQL Rule Evaluation — evaluate

See [`rules/README.md`](rules/README.md).

The source-owned SPARQL `CONSTRUCT` rule evaluates explicit Pizza RDF assertions and derives `requiresVegetarianWarning true` for the meat-topping case without performing OWL inference or SHACL validation.

## 4. DMN Decision Evaluation — decide

See [`decisions/README.md`](decisions/README.md).

The source-owned DMN decision table consumes explicit boolean context and produces one semantic dietary-suitability outcome per case through `PizzaDietarySuitabilityCapability`.

## 5. OpenMath Calculation — calculate

See [`calculations/README.md`](calculations/README.md).

The source-owned OpenMath expression represents:

```text
areaSquareCentimetres = π × (diameterCm / 2)²
```

`PizzaAreaCalculationCapability` produces a typed decimal Pizza-area Result.

## 6. Semantic Mapping — transform

See [`mappings/README.md`](mappings/README.md).

The source-owned Mapping artifacts distinguish:

```text
Pizza source semantic model
        ↓
SPARQL mapping semantic model
        ↓
Menu target semantic model
```

`PizzaMenuProjectionCapability` transforms explicit Pizza RDF into a target Menu graph and verifies the output against a canonical target graph.

Mapping uses mode-local source/mapping/target subproperties of `eska:usesSemanticModel` plus qualified PROV-O roles at runtime. These refinements remain outside core.

## 7. BPMN Workflow — execute

See [`workflows/README.md`](workflows/README.md).

The source-owned BPMN process composes the existing Validation and Mapping Capabilities:

```text
Start
  ↓
Validate Pizza RDF
  ↓
conforms?
  ├── false → Rejected
  └── true
        ↓
Transform Pizza → Menu
        ↓
      Published
```

BPMN owns control flow only. It does not duplicate SHACL constraints or Mapping semantics.

Overall Workflow runs and child steps remain ordinary `eska:Execution` instances, composed using `dcterms:hasPart` / `isPartOf`, `prov:wasInformedBy`, and `prov:wasDerivedFrom`.

Canonical behavior:

```text
valid-publication   → conforms=True  → Validation + Mapping → Published
invalid-rejection   → conforms=False → Validation only      → Rejected
```

## Cross-mode operational architecture

Classification and Validation are now the two executable specimens used to generalize the optional operational layers above core.

### Generalized Knowledge Service

The Service contract separates semantic meaning from access details:

```text
SemanticCapability
    inputType / outputType / producesRelation / applicability
        ↑ realizesCapability
ServiceOperation
        ↓ hasAccessBinding
HTTPAccessBinding
    method + relative path + media/representation fields
```

A machine-readable `PizzaKnowledgeService` specimen exposes both Classification and Validation through distinct operations without duplicating semantic Capability properties on those operations.

See [`../../docs/knowledge-service-generalization.md`](../../docs/knowledge-service-generalization.md).

### Generalized deterministic Knowledge Agent

One `PizzaGeneralizedKnowledgeAgent` targets both Classification and Validation.

```text
KnowledgeAgent
    ↓ usesInvocationAdapter
SemanticInvocationAdapter
    ├── supportsInputType
    ├── supportsOutputType
    └── supportsRelation
```

The canonical adapters are:

```text
IRIListInvocationAdapter
    owl:Class → rdfs:subClassOf → owl:Class IRIs

SHACLReportInvocationAdapter
    PizzaDataGraph → sh:conforms → sh:ValidationReport RDF
```

The Agent discovers a compatible Service/Operation/AccessBinding and selects exactly one adapter from the Capability `inputType` / `outputType` / `producesRelation` contract.

This keeps discovery/invocation generic while making request/result representation handling explicit. The baseline remains deterministic and non-LLM.

See [`../../docs/knowledge-agent-generalization.md`](../../docs/knowledge-agent-generalization.md).

### Separate deployment binding

Runtime location is resolved after semantic discovery from a separate deployment graph:

```text
KnowledgeService
    ↑ deploysService
ServiceDeployment
    ├── inEnvironment
    └── hasDeploymentBinding
            ↓
      HTTPDeploymentBinding
            └── baseURL
```

Invocation combines:

```text
HTTPDeploymentBinding.baseURL
        +
HTTPAccessBinding.path
        ↓
concrete endpoint
```

The reference defines blue and green Classification + Validation deployments and proves:

```text
blue.discovery == green.discovery
blue.adapter   == green.adapter

blue.deployment != green.deployment
blue.endpoint   != green.endpoint

semantic result remains equivalent
```

The Agent provenance records the selected Service Deployment, Deployment Environment, HTTP Deployment Binding, semantic adapter, architecture model, and deployment model.

See [`../../docs/deployment-binding.md`](../../docs/deployment-binding.md) and [`deployments/README.md`](deployments/README.md).

## Execute

Requirements:

- Java 17 or newer for ROBOT/HermiT;
- Python 3;
- network access to retrieve the commit-pinned public Pizza artifacts;
- `curl` for the pinned ROBOT download.

OWL classification Service + original deterministic Agent:

```bash
bash examples/pizza/test-agent.sh
```

SHACL validation and concrete Validation Service/Agent:

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
python examples/pizza/validation/validate.py
bash examples/pizza/validation/test-agent.sh
```

The validation integration also runs the generalized cross-mode Agent, including blue/green deployment verification.

Run the generalized Agent/deployment regression directly:

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
bash examples/pizza/test-generalized-agent.sh
```

Verify the deployment model only:

```bash
bash examples/pizza/deployments/verify.sh
```

SPARQL rule evaluation:

```bash
python -m pip install -r examples/pizza/rules/requirements.txt
python examples/pizza/rules/evaluate.py
```

DMN decision evaluation:

```bash
python -m pip install -r examples/pizza/decisions/requirements.txt
python examples/pizza/decisions/evaluate.py
```

OpenMath calculation:

```bash
python -m pip install -r examples/pizza/calculations/requirements.txt
python examples/pizza/calculations/evaluate.py
```

Semantic Mapping:

```bash
python -m pip install -r examples/pizza/mappings/requirements.txt
python examples/pizza/mappings/evaluate.py
```

BPMN Workflow:

```bash
python -m pip install -r examples/pizza/workflows/requirements.txt
python examples/pizza/workflows/evaluate.py
```

## Cross-mode core verification

The generic Capability verifier checks one common contract across **seven Capabilities**:

- `PizzaClassificationCapability`;
- `PizzaValidationCapability`;
- `PizzaRuleEvaluationCapability`;
- `PizzaDietarySuitabilityCapability`;
- `PizzaAreaCalculationCapability`;
- `PizzaMenuProjectionCapability`;
- `PizzaMenuPublicationWorkflowCapability`.

The generic runtime verifier checks the same core pattern across **sixteen concrete Executions**:

- one OWL reasoning execution;
- two SHACL validation executions;
- one SPARQL rule execution;
- three DMN decision executions;
- three OpenMath calculation executions;
- one semantic Mapping execution;
- two overall Workflow executions;
- three actually executed Workflow child steps.

The shared abstraction remains:

```text
SemanticModel
→ ExecutableSemanticKnowledgeArtifact
→ SemanticCapability
→ ApplicabilityCondition
→ Execution
→ Result
→ Verification
```

`model/eska-core.ttl` required **no change** for Rule, Decision, Calculation, Mapping, or Workflow falsification modes.

## Verification questions

The reference now asks, among other things:

```text
Is the Pizza domain source pinned to an immutable commit?

Does the manifest still publish the complete 23-artifact role/path contract?

Do all seven Capabilities satisfy the same generic core contract?

Do all sixteen Executions satisfy Execution → Result → Verification?

Can one Knowledge Service expose Classification + Validation unambiguously?

Can one deterministic Agent discover and invoke both modes?

Does the Agent select the correct semantic invocation adapter from the Capability contract?

Can the same semantic Service contract resolve to blue and green deployments?

Does semantic discovery remain stable while deployment base URLs/endpoints change?

Do equivalent inputs preserve equivalent semantic results across deployment changes?

Do provenance records retain source artifact identity, Mapping roles, Workflow composition, adapter identity, and concrete deployment identity?
```

## Ownership boundary

```text
GerhardBalz/pizza-ontology
│
├── Pizza Ontology 2.0 preservation source
├── OWL / SHACL / Rule / DMN / OpenMath semantic artifacts
├── Mapping + target semantic model
├── BPMN Workflow artifacts
└── semantic artifact manifest
          │
          │ immutable commit
          ▼
GerhardBalz/executable-semantic-knowledge-architecture
│
├── Semantic Capability
├── Execution / Result / Verification
├── mode-specific semantic refinements where required
├── Knowledge Service / Access Binding
├── deterministic Knowledge Agent / Invocation Adapter
├── Service Deployment / Deployment Binding
└── PROV-O execution and invocation lineage
```

Two principles are executable rather than merely documented:

> **Execution must not sever semantics.**

> **Execution architecture should not become the accidental owner of domain semantics.**

## Source and license

See [LICENSE-NOTICE.md](LICENSE-NOTICE.md) for the cross-repository provenance and licensing boundary.
