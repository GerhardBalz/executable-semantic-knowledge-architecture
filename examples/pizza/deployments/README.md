# Pizza deployment binding example

This example demonstrates that a stable ESKA Knowledge Service contract can have multiple concrete runtime deployments without changing Capability meaning, Service discovery, Access Binding semantics, or Agent result interpretation.

## Deployment model

[`pizza-deployments.ttl`](pizza-deployments.ttl) defines two environments:

```text
blue
green
```

and two deployments of each working Pizza Service:

```text
PizzaClassificationService
    ├── blue  → http://127.0.0.1:18083
    └── green → http://127.0.0.1:18085

PizzaValidationService
    ├── blue  → http://127.0.0.1:18084
    └── green → http://127.0.0.1:18086
```

Those URLs are intentionally **not** present in the Service or Service Operation contracts.

## Binding layers

```text
Semantic Capability
        ↓
Knowledge Service / Service Operation
        ↓
HTTP Access Binding
    POST + contract-relative path + representation fields

separate runtime graph
        ↓
Service Deployment
        ↓
HTTP Deployment Binding
    base URL
```

At invocation time the generalized Agent combines:

```text
base URL + contract-relative path
```

## Verify the deployment model

The generalized Agent regression already invokes the deployment verifier, but it can also be run directly after the Pizza reasoning setup has materialized ROBOT:

```bash
bash examples/pizza/run.sh
bash examples/pizza/deployments/verify.sh
```

The SPARQL regression checks that:

- Classification and Validation each have exactly two deployments;
- each deployment identifies one environment and one HTTP Deployment Binding;
- runtime base URLs occur only on HTTP Deployment Bindings;
- stable Knowledge Service and Service Operation contracts do not contain runtime base URLs.

## Execute across deployments

Install the validation dependency, then run the generalized Agent integration:

```bash
python -m pip install -r examples/pizza/validation/requirements.txt
bash examples/pizza/test-generalized-agent.sh
```

The integration starts the blue and green Classification and Validation processes, then uses the same deterministic Agent and semantic discovery query against both environments.

The key regression is:

```text
blue.discovery == green.discovery
blue.adapter   == green.adapter

blue.deployment != green.deployment
blue.endpoint   != green.endpoint
```

Equivalent inputs must still produce equivalent semantic results across the deployment change.

## Provenance

Generalized Agent provenance records both sides of the invocation:

```text
semantic contract
    Capability
    Knowledge Service
    Semantic Invocation Adapter

runtime binding
    Service Deployment
    Deployment Environment
    HTTP Deployment Binding
```

This makes runtime location traceable without turning environment-specific deployment data into domain or Service semantics.
