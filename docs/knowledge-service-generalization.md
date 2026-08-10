# Knowledge Service Generalization

This document records the evidence-driven generalization of the provisional ESKA Knowledge Service extension after two executable exposure modes became available:

```text
Classification
    PizzaClassificationCapability
        → PizzaClassificationService
        → PizzaKnowledgeAgent

Validation
    PizzaValidationCapability
        → PizzaValidationService
        → PizzaValidationAgent
```

The purpose is to separate **stable Service semantics** from **access/representation details** without promoting Service concepts into the ESKA core.

## Evidence

Both executable paths already shared the same high-level structure:

```text
SemanticCapability
    → KnowledgeService
        → ServiceOperation
```

But the earlier model contained a hidden single-capability assumption:

```text
KnowledgeService
    exposesCapability Capability
    hasOperation Operation
```

There was no explicit statement that a particular Operation realizes a particular Capability. That is unambiguous only while a Service exposes exactly one Capability.

The generalized model adds:

```text
ServiceOperation
    eska:realizesCapability
        SemanticCapability
```

This allows one `KnowledgeService` to expose multiple Capabilities with independently discoverable Operations.

## Stable semantic contract

The semantic meaning of an invocation remains on the Capability:

```text
SemanticCapability
    inputType
    outputType
    producesRelation
    requiresCondition
```

A `ServiceOperation` no longer duplicates those assertions. It identifies which Capability it operationally realizes.

```text
KnowledgeService
    exposesCapability SemanticCapability
    hasOperation ServiceOperation

ServiceOperation
    realizesCapability SemanticCapability
```

This reduces semantic drift between Capability and Service contracts.

## Access binding

Concrete access details are separated from the semantic Service Operation:

```text
ServiceOperation
    hasAccessBinding
        AccessBinding
            ↓
        HTTPAccessBinding
```

The current HTTP examples use access-binding properties such as:

```text
httpMethod
path
mediaType
requestField
resultField
relationField
capabilityField
```

These properties describe how an operation is represented and invoked. They do not define the meaning of the Capability.

The contract-relative `path` is also distinct from runtime deployment location. Scheme, host, and port remain runtime deployment bindings and are deliberately not encoded in the semantic Service contract.

## Multi-capability evidence

`examples/pizza/pizza-multi-capability-service.ttl` provides a machine-readable contract specimen:

```text
PizzaKnowledgeService
    │
    ├── exposes PizzaClassificationCapability
    │       ↑
    │   ClassifyOperation
    │       ↓
    │   ClassifyHTTPBinding
    │
    └── exposes PizzaValidationCapability
            ↑
        ValidateOperation
            ↓
        ValidateHTTPBinding
```

Each `ServiceOperation` realizes exactly one Capability. The Service itself can expose both.

`verify-service-generalization.sparql` verifies that:

- the Service exposes both Capabilities;
- each Operation realizes the expected Capability;
- each Operation has a separate HTTP Access Binding;
- semantic input/output/relation/applicability remain on the Capability;
- semantic contract properties are not copied onto the Service Operations;
- no Operation realizes multiple Capabilities in this specimen.

## Classification vs Validation

The common Service structure generalizes, but result representations differ:

```text
Classification
    outputType owl:Class
    producesRelation rdfs:subClassOf
    access result field → list of IRI strings

Validation
    outputType sh:ValidationReport
    producesRelation sh:conforms
    access result field → JSON-LD RDF graph
```

This distinction is important.

`mediaType` describes the access representation envelope (`application/json` in both current examples). It does **not** replace the semantic `outputType`, and it does not imply that every result has one universal JSON shape.

The next Agent-generalization work should therefore interpret the discovered result according to semantic output/relation plus the concrete access representation, rather than assuming a list of IRIs.

## Applicability and errors

Semantic applicability remains on the Capability through `requiresCondition`.

The current examples also produce HTTP/runtime errors for malformed requests, out-of-scope inputs, unavailable data, and similar access failures. Two modes are not enough evidence for a stable ESKA error taxonomy, so HTTP status codes and implementation-specific errors remain access/runtime concerns rather than new semantic Service classes.

This is deliberate non-generalization.

## Architectural result

```text
ESKA core
    SemanticCapability
        input/output/relation/applicability

Service extension
    KnowledgeService
        ↓ hasOperation
    ServiceOperation
        ↓ realizesCapability
    SemanticCapability

Access extension within Service model
    ServiceOperation
        ↓ hasAccessBinding
    AccessBinding
        ↓
    HTTPAccessBinding
```

The result supports keeping `KnowledgeService` outside `eska-core.ttl` while making the Service extension itself less transport-shaped and safe for multi-capability services.

## What was not added

The generalization did **not** add:

- Knowledge Service concepts to the ESKA core;
- HTTP concepts to the ESKA core;
- a generic error/result hierarchy;
- a universal result representation;
- deployment URLs to semantic Service contracts;
- Service subclasses for reasoning vs validation;
- duplicated Capability semantics on Service Operations.

The current evidence supports one stable principle:

> **A Service Operation operationally realizes a Semantic Capability; the Capability defines semantic meaning, while an Access Binding defines how the operation is reached and represented.**
