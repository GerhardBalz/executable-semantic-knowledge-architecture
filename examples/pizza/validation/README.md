# Pizza SHACL validation

This slice demonstrates **Executable Semantic Knowledge** through SHACL validation and now exposes that bounded semantic capability through a Knowledge Service and deterministic Knowledge Agent.

The Pizza-domain SHACL profile and example RDF data are **not owned by this repository**. They are published by [`GerhardBalz/pizza-ontology`](https://github.com/GerhardBalz/pizza-ontology) and consumed from the immutable commit recorded in [`../pizza-domain-source.json`](../pizza-domain-source.json).

```text
pizza-ontology
    owns Pizza SHACL profile + RDF examples
        ↓ commit-pinned fetch
ESKA
    PizzaValidationCapability
        ↓ pySHACL
    Execution → ValidationReport → Verification
        ↓ optional operational exposure
    PizzaValidationService
        ↓ discovered / invoked by
    PizzaValidationAgent
```

Runtime materialization is written only beneath `examples/pizza/.work/pizza-domain/`; it is not a second semantic source of truth.

## Validation question

> **Does a concrete Pizza RDF data graph conform to the source-owned Pizza validation profile?**

The published profile requires, for each explicit `pizza:Pizza` node:

- exactly one `pizza:hasBase` value;
- the base value to be a `pizza:PizzaBase`;
- at least one `pizza:hasTopping` value;
- each topping value to be a `pizza:PizzaTopping`.

OWL reasoning and SHACL validation remain different semantic operations:

```text
OWL
    What follows logically from the semantic model?

SHACL
    Does this explicit RDF data satisfy a validation profile?
```

The constraints remain represented in SHACL rather than duplicated as Python conditionals.

## Semantic Capability

[`pizza-validation-capability.ttl`](pizza-validation-capability.ttl) defines `PizzaValidationCapability`:

```text
Subject
    Pizza

Input
    Pizza RDF data graph

Output
    sh:ValidationReport

Produced relation
    sh:conforms

Semantic model
    source-owned Pizza SHACL profile

Executable artifact
    SHACL validation with pySHACL
```

The Capability is ESKA-owned because it describes how semantic knowledge is operationalized. The SHACL graph remains Pizza-owned because it defines domain-specific validation knowledge.

## Knowledge Service

[`pizza-validation-service.ttl`](pizza-validation-service.ttl) exposes the Capability without moving Pizza constraints into HTTP code:

```text
PizzaValidationService
    exposes PizzaValidationCapability
        ↓
POST /validate
        ↓
sh:ValidationReport
```

[`service.py`](service.py) accepts an expanded JSON-LD RDF graph inside the JSON request envelope, executes the commit-pinned SHACL profile through pySHACL, and returns the **actual SHACL report graph serialized as JSON-LD** in the discovered `report` field.

The service does not invent a transport-level validation rule or replace the report with a boolean. `sh:conforms` remains inside the semantic result graph.

## Deterministic Knowledge Agent

[`pizza-validation-agent.ttl`](pizza-validation-agent.ttl) defines `PizzaValidationAgent`. The Agent knows the Capability it wants, but not the endpoint implementing it.

[`discover-service.sparql`](discover-service.sparql) discovers:

- the Knowledge Service;
- operation;
- HTTP method and path;
- semantic input/output types;
- semantic result relation;
- request/result envelope fields.

The runtime service base URL remains a deployment binding supplied separately.

[`agent.py`](agent.py):

1. discovers the validation operation from the machine-readable architecture;
2. converts the supplied RDF input graph to expanded JSON-LD;
3. invokes the discovered Service operation;
4. checks that the returned Capability and relation match the discovered contract;
5. parses the returned JSON-LD as RDF;
6. requires exactly one `sh:ValidationReport` and interprets `sh:conforms` and any `sh:ValidationResult` nodes;
7. records `Execution → Result → Verification` provenance for the service invocation.

## Cross-mode Service / Agent evidence

Classification and validation now use the same provisional extension vocabulary:

```text
Classification
    SemanticCapability
        → KnowledgeService / ServiceOperation
        → KnowledgeAgent / DiscoveryArtifact

Validation
    SemanticCapability
        → KnowledgeService / ServiceOperation
        → KnowledgeAgent / DiscoveryArtifact
```

[`verify-cross-mode-service-agent.sparql`](verify-cross-mode-service-agent.sparql) verifies that both paths satisfy that same structural pattern.

The important difference is **result interpretation**:

```text
Classification result
    list of owl:Class IRIs

Validation result
    sh:ValidationReport RDF graph
```

This is evidence that `resultField` can identify where a semantically typed result is carried without requiring one universal JSON result shape. It is also evidence that a generic Knowledge Agent should interpret results according to semantic output type/relation rather than assuming every Capability returns a list of IRIs.

Neither `model/eska-service.ttl` nor `model/eska-agent.ttl` needed to change for this second mode.

## Data cases

The source repository publishes both cases.

### Conforming

The conforming graph must produce:

```text
sh:conforms true
```

### Non-conforming

The non-conforming graph deliberately:

- omits `pizza:hasBase`;
- points `pizza:hasTopping` at a value typed as `pizza:PizzaBase` rather than `pizza:PizzaTopping`.

The standalone validation regression verifies the expected `sh:MinCountConstraintComponent` and `sh:ClassConstraintComponent` results.

The Service/Agent integration additionally verifies that the conforming graph returns zero `sh:ValidationResult` nodes and the non-conforming graph returns one or more violations through the discovered service contract.

## Execute

Install the validation dependency:

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
```

Standalone semantic validation:

```bash
python examples/pizza/validation/validate.py
```

Service + Agent integration:

```bash
bash examples/pizza/validation/test-agent.sh
```

The integration test:

1. materializes the commit-pinned Pizza artifacts;
2. builds one architecture model containing both classification and validation Service/Agent paths;
3. verifies the validation Service and Agent contracts;
4. verifies the cross-mode Service/Agent extension pattern;
5. starts the validation Knowledge Service;
6. lets the deterministic Agent discover and invoke it for conforming and non-conforming RDF;
7. verifies SHACL result semantics and ESKA/PROV-O invocation lineage.

Generated reports, architecture artifacts, Agent results, and provenance remain under `examples/pizza/validation/results/`.

## Architectural significance

The boundary remains:

```text
Domain semantics               Execution architecture
────────────────────────       ─────────────────────────
pizza-ontology                 ESKA

SHACL profile       ────────►   Validation Capability
example RDF data   ────────►   Execution / Verification
                               Knowledge Service
                               Knowledge Agent
```

**Execution must not sever semantics, and execution architecture should not become the accidental owner of domain semantics.**
