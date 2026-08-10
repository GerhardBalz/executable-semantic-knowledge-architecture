# Knowledge Agent Generalization

This document records the evidence-driven generalization of the provisional ESKA Knowledge Agent extension from the executable Pizza classification and validation paths.

## Evidence base

The project had two working deterministic Agent paths before this generalization:

```text
Classification
    PizzaClassificationCapability
        ↓
    PizzaClassificationService
        ↓ discovered by
    PizzaKnowledgeAgent

Validation
    PizzaValidationCapability
        ↓
    PizzaValidationService
        ↓ discovered by
    PizzaValidationAgent
```

Both already used machine-readable Service discovery and kept runtime deployment location separate from the semantic Service contract.

The generalized Service model from issue #13 added the stable Service structure:

```text
ServiceOperation
    ↓ realizesCapability
SemanticCapability

ServiceOperation
    ↓ hasAccessBinding
HTTPAccessBinding
```

The remaining Agent-side difference was representation handling.

## Cross-mode representation difference

Classification uses:

```text
semantic input
    owl:Class IRI

access representation
    JSON string field

semantic output
    owl:Class

access result
    JSON list of semantic IRIs
```

Validation uses:

```text
semantic input
    Pizza RDF graph

access representation
    expanded JSON-LD inside JSON envelope

semantic output
    sh:ValidationReport

access result
    JSON-LD RDF graph
```

This is evidence that Service discovery and HTTP invocation can be generalized, but an Agent cannot assume one universal request or result representation.

## Generalized Agent structure

The Agent extension now contains `SemanticInvocationAdapter`:

```text
KnowledgeAgent
    ↓ usesInvocationAdapter
SemanticInvocationAdapter
    ├── supportsInputType
    ├── supportsOutputType
    └── supportsRelation
```

An adapter does not redefine Capability semantics. Its support assertions describe which semantic contract it can encode and interpret.

The canonical Pizza reference defines:

```text
IRIListInvocationAdapter
    supportsInputType   owl:Class
    supportsOutputType  owl:Class
    supportsRelation    rdfs:subClassOf

SHACLReportInvocationAdapter
    supportsInputType   PizzaDataGraph
    supportsOutputType  sh:ValidationReport
    supportsRelation    sh:conforms
```

## One Agent, multiple semantic modes

`PizzaGeneralizedKnowledgeAgent` targets both:

- `PizzaClassificationCapability`
- `PizzaValidationCapability`

Its discovery query returns the Service operation, Access Binding, Capability semantic contract, and a compatible Agent invocation adapter.

At runtime the Agent selects exactly one contract for the requested Capability:

```text
target Capability
        ↓
ServiceOperation → realizesCapability
        ↓
Capability inputType / outputType / producesRelation
        ↓
matching SemanticInvocationAdapter
        ↓
HTTPAccessBinding
        ↓
runtime deployment base URL
        ↓
invoke
        ↓
semantic result interpretation
```

The deployment base URL is still supplied separately. The Agent model does not encode runtime host, port, or environment location.

## Semantic continuity

The generic runtime verifies that the Service response preserves the discovered semantic contract:

```text
returned capability == discovered Capability
returned relation   == Capability producesRelation
```

It then delegates representation-specific interpretation to the selected adapter.

For classification the adapter verifies a list of semantic IRIs and confirms the expected `SpicyPizza` classification.

For validation the adapter parses the JSON-LD result as RDF, requires exactly one `sh:ValidationReport`, reads `sh:conforms`, and counts `sh:ValidationResult` nodes.

Both conforming and non-conforming validation cases are exercised.

## Provenance

The generalized Agent records each invocation through the established ESKA runtime pattern:

```text
Execution
    executesCapability → target Capability
    prov:used          → discovered Service
    prov:used          → selected SemanticInvocationAdapter
    prov:generated     → Result

Result
    → semantic relation / adapter-specific semantic content

Verification
    verifiesExecution → Execution
    verifiesResult    → Result
```

This keeps adapter selection visible in runtime lineage rather than hiding it inside application code.

## Agent knowledge versus domain knowledge

The generalized Agent knows:

```text
- which Semantic Capabilities it is prepared to target;
- which semantic invocation adapters it supports;
- how to query the ESKA architecture;
- how to execute the supported access envelope.
```

The Agent does **not** contain:

```text
- Pizza OWL classification rules;
- Pizza SHACL constraints;
- the expected SpicyPizza answer;
- validation conformance outcomes;
- Service endpoint paths;
- runtime host/port locations.
```

Those concerns remain owned by the appropriate semantic model, Service contract, or deployment binding.

## Architectural result

The evidence supports the following layering:

```text
Capability semantics
    input / output / relation / applicability

Service contract
    Operation realizes Capability
    Operation has Access Binding

Agent contract
    targets Capability
    uses Discovery Artifact
    uses compatible Semantic Invocation Adapter

Deployment binding
    runtime location
```

The result does **not** justify:

- Agent concepts in `eska-core.ttl`;
- LLM-specific Agent semantics;
- prompt concepts in ESKA;
- a universal result JSON shape;
- a universal input serialization;
- HTTP-specific terms in the Agent model;
- classification-specific or validation-specific Agent subclasses;
- a generic ontology of every possible serializer/interpreter.

`SemanticInvocationAdapter` is justified because two working semantic modes already require materially different request/result handling while sharing the same discovery/invocation architecture.

## Baseline

The baseline remains deterministic and non-LLM.

This matters architecturally: Agent accessibility is demonstrated as a property of explicit machine-readable contracts, not as an emergent property of prompt interpretation.
