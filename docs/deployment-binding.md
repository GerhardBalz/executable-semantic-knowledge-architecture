# Deployment Binding

This document records the executable evidence behind the provisional ESKA deployment-binding extension.

The purpose is to keep **stable semantic Service contracts** separate from **environment-specific runtime locations**.

## Architectural distinction

```text
Semantic Capability
        ↓ realized by
Service Operation
        ↓ has access contract
HTTP Access Binding
        │
        │ stable across deployments
        ▼
Knowledge Service
        ↑
        │ deploysService
Service Deployment
        ├── inEnvironment
        └── hasDeploymentBinding
                ↓
        HTTP Deployment Binding
                └── baseURL
```

The two bindings answer different questions.

```text
HTTP Access Binding
    How is this operation invoked?

    method
    contract-relative path
    media-type envelope
    representation field mappings

HTTP Deployment Binding
    Where is this Service deployment reachable?

    runtime base URL
```

The Agent combines them only at invocation time:

```text
baseURL + path → concrete endpoint
```

## Why deployment is not part of the Service contract

A stable Knowledge Service may have multiple deployments at the same time:

```text
PizzaClassificationService
    ├── blue  → http://127.0.0.1:18083
    └── green → http://127.0.0.1:18085

PizzaValidationService
    ├── blue  → http://127.0.0.1:18084
    └── green → http://127.0.0.1:18086
```

The semantic Service and Capability contracts do not change between those environments.

Embedding a host or port in `KnowledgeService`, `ServiceOperation`, or `HTTPAccessBinding` would therefore conflate stable architectural meaning with mutable deployment configuration.

## Provisional deployment model

[`../model/eska-deployment.ttl`](../model/eska-deployment.ttl) introduces a small optional extension:

```text
ServiceDeployment
DeploymentEnvironment
DeploymentBinding
HTTPDeploymentBinding

deploysService
inEnvironment
hasDeploymentBinding
baseURL
```

`ServiceDeployment` specializes `prov:Entity`, allowing a concrete runtime deployment to participate naturally in provenance without introducing a parallel lineage model.

The deployment ontology requires the provisional Service model:

```turtle
dcterms:requires <https://w3id.org/eska/model/service>
```

It remains outside `eska-core.ttl` because deployment is an optional operational concern rather than a prerequisite for executable semantic knowledge.

## Runtime resolution sequence

The generalized deterministic Pizza Agent now performs two independent lookups.

### 1. Semantic discovery

From the architecture model:

```text
requested SemanticCapability
        ↓
ServiceOperation
        ↓ realizesCapability
KnowledgeService
        ↓
HTTPAccessBinding
        ↓
SemanticInvocationAdapter
```

This produces the stable semantic/access contract:

- Service IRI;
- Operation IRI;
- Capability input/output/relation;
- HTTP method and contract-relative path;
- representation field mappings;
- compatible semantic invocation adapter.

### 2. Deployment resolution

From a separate deployment graph:

```text
KnowledgeService + environment
        ↓
ServiceDeployment
        ↓
HTTPDeploymentBinding
        ↓
baseURL
```

Only after both lookups does the Agent form the concrete endpoint.

## Executable evidence

[`../examples/pizza/deployments/pizza-deployments.ttl`](../examples/pizza/deployments/pizza-deployments.ttl) defines two local environments, `blue` and `green`, for both Classification and Validation.

[`../examples/pizza/deployments/verify-deployment.sparql`](../examples/pizza/deployments/verify-deployment.sparql) verifies that:

- each stable Service has two concrete deployments;
- each deployment identifies one environment and one HTTP Deployment Binding;
- runtime base URLs occur only on `HTTPDeploymentBinding` resources;
- Knowledge Services and Service Operations do not contain runtime base URLs.

The generalized Agent regression then starts all four runtime instances and invokes:

```text
Classification / blue
Classification / green
Validation / blue
Validation / green
```

plus a non-conforming Validation case in green.

The regression explicitly requires:

```text
blue.discovery == green.discovery
blue.adapter   == green.adapter
blue.deployment != green.deployment
blue.endpoint   != green.endpoint
```

For equivalent inputs, the semantic result must remain equivalent across the deployment change.

This demonstrates:

> **Semantic discovery is deployment-invariant; deployment resolution is a separate runtime concern.**

## Provenance

Agent invocation provenance records both semantic and deployment inputs.

A generalized Agent Execution `prov:used`:

- the stable Knowledge Service;
- the selected Semantic Invocation Adapter;
- the concrete Service Deployment;
- the Deployment Environment;
- the HTTP Deployment Binding;
- the architecture model;
- the deployment model;
- the invocation input.

This makes it possible to distinguish:

```text
What semantic ability was invoked?
    Capability / Service / Operation / Adapter

Where was it invoked?
    ServiceDeployment / Environment / DeploymentBinding
```

without changing the semantic Result model.

## Deliberate non-generalization

The first deployment example does **not** justify:

- Deployment concepts in `eska-core.ttl`;
- hosts or ports in `eska-service.ttl`;
- a cloud-provider or container-platform ontology;
- Kubernetes-, Docker-, serverless-, or process-specific deployment classes;
- load-balancer, retry, routing, or service-discovery infrastructure semantics;
- environment-specific semantic Capability variants;
- embedding production credentials or secrets in RDF deployment models.

The current model represents only the architectural seam needed by the executable evidence.

## Resulting layering

```text
Semantic Capability
    what the ability means

Knowledge Service / Service Operation
    stable operational exposure

Access Binding
    how an operation is invoked

Semantic Invocation Adapter
    how typed inputs/results are represented and interpreted

Service Deployment / Deployment Binding
    where a concrete runtime instance is reachable
```

This preserves the project principle:

> **Execution must not sever semantics.**

while adding a complementary operational principle:

> **Deployment must not redefine semantics.**
