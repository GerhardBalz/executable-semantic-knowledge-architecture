#!/usr/bin/env python3
"""Verify cross-cutting ESKA provenance, evidence, and Result lineage profiles.

The verifier deliberately reuses ESKA core links, PROV-O, and dcterms. It does
not require a parallel ESKA provenance ontology.
"""

from __future__ import annotations

import re
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

ESKA = Namespace("urn:eska:core:")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

PIZZA_BLOB = re.compile(
    r"^https://github\.com/GerhardBalz/pizza-ontology/blob/[0-9a-f]{40}/.+"
)

SEMANTIC_PROVENANCE = [
    HERE / "results" / "provenance.ttl",
    HERE / "validation" / "results" / "provenance.ttl",
    HERE / "rules" / "results" / "provenance.ttl",
    HERE / "decisions" / "results" / "provenance.ttl",
    HERE / "calculations" / "results" / "provenance.ttl",
    HERE / "mappings" / "results" / "provenance.ttl",
    HERE / "workflows" / "results" / "provenance.ttl",
]

INVOCATION_PROVENANCE = [
    HERE / "results" / "general-agent-classification-blue-provenance.ttl",
    HERE / "results" / "general-agent-classification-green-provenance.ttl",
    HERE / "results" / "general-agent-validation-valid-blue-provenance.ttl",
    HERE / "results" / "general-agent-validation-valid-green-provenance.ttl",
    HERE / "results" / "general-agent-validation-invalid-green-provenance.ttl",
]

SUPPORT_MODELS = [
    ROOT / "model" / "eska-agent.ttl",
    ROOT / "model" / "eska-deployment.ttl",
    HERE / "pizza-generalized-agent.ttl",
    HERE / "pizza-classification-service.ttl",
    HERE / "validation" / "pizza-validation-service.ttl",
    HERE / "deployments" / "pizza-deployments.ttl",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_graphs(paths: list[Path]) -> Graph:
    graph = Graph()
    for path in paths:
        require(path.is_file() and path.stat().st_size > 0, f"missing provenance/model file: {path}")
        graph.parse(path, format="turtle")
    return graph


def one(values, message: str):
    unique = list(dict.fromkeys(values))
    require(len(unique) == 1, f"{message}: expected exactly one, got {unique}")
    return unique[0]


def typed_datetime(graph: Graph, subject: URIRef) -> Literal:
    value = one(graph.objects(subject, PROV.endedAtTime), f"{subject} prov:endedAtTime")
    require(isinstance(value, Literal), f"{subject}: endedAtTime is not a literal")
    require(value.datatype == XSD.dateTime, f"{subject}: endedAtTime must be xsd:dateTime, got {value.datatype}")
    return value


def execution_result_verification(graph: Graph, execution: URIRef) -> tuple[URIRef, URIRef]:
    require((execution, RDF.type, ESKA.Execution) in graph, f"{execution}: missing eska:Execution type")
    require((execution, RDF.type, PROV.Activity) in graph, f"{execution}: missing prov:Activity type")

    capability = one(graph.objects(execution, ESKA.executesCapability), f"{execution} executesCapability")
    require(isinstance(capability, URIRef), f"{execution}: Capability is not an IRI")

    result = one(graph.objects(execution, ESKA.generatesResult), f"{execution} generatesResult")
    require(isinstance(result, URIRef), f"{execution}: Result is not an IRI")
    require((execution, PROV.generated, result) in graph, f"{execution}: missing prov:generated Result")
    require((result, RDF.type, ESKA.Result) in graph, f"{result}: missing eska:Result type")
    require((result, RDF.type, PROV.Entity) in graph, f"{result}: missing prov:Entity type")
    require((result, PROV.wasGeneratedBy, execution) in graph, f"{result}: missing inverse generation lineage")

    agents = list(dict.fromkeys(graph.objects(execution, PROV.wasAssociatedWith)))
    require(agents, f"{execution}: no associated software/tool Agent")
    require(
        any((agent, RDF.type, PROV.SoftwareAgent) in graph for agent in agents),
        f"{execution}: associated Agent is not typed prov:SoftwareAgent: {agents}",
    )
    typed_datetime(graph, execution)

    verifications = [
        verification
        for verification in graph.subjects(ESKA.verifiesExecution, execution)
        if (verification, ESKA.verifiesResult, result) in graph
    ]
    verification = one(verifications, f"{execution} matching Verification")
    require(isinstance(verification, URIRef), f"{execution}: Verification is not an IRI")
    require((verification, RDF.type, ESKA.Verification) in graph, f"{verification}: missing eska:Verification type")
    require((verification, RDF.type, PROV.Activity) in graph, f"{verification}: missing prov:Activity type")
    require((verification, PROV.used, result) in graph, f"{verification}: Verification must prov:used the Result")
    typed_datetime(graph, verification)
    return result, verification


def is_immutable_pizza_source(node) -> bool:
    return isinstance(node, URIRef) and bool(PIZZA_BLOB.match(str(node)))


def traces_to_immutable_pizza_source(graph: Graph, node, visited: set) -> bool:
    if node in visited:
        return False
    visited.add(node)

    if is_immutable_pizza_source(node):
        return True

    for source in graph.objects(node, DCTERMS.source):
        if is_immutable_pizza_source(source):
            return True

    for parent in graph.objects(node, PROV.wasDerivedFrom):
        if traces_to_immutable_pizza_source(graph, parent, visited):
            return True
    return False


def verify_semantic_execution_profile() -> set[URIRef]:
    graph = parse_graphs(SEMANTIC_PROVENANCE)
    executions = set(graph.subjects(RDF.type, ESKA.Execution))
    require(len(executions) == 16, f"semantic execution profile expected 16 Executions, got {len(executions)}")

    for execution in executions:
        models = list(dict.fromkeys(graph.objects(execution, ESKA.usesSemanticModel)))
        artifacts = list(dict.fromkeys(graph.objects(execution, ESKA.usesExecutableArtifact)))
        require(models, f"{execution}: no Semantic Model lineage")
        require(artifacts, f"{execution}: no executable semantic artifact lineage")
        require(list(graph.objects(execution, PROV.used)), f"{execution}: no prov:used evidence")

        result, _ = execution_result_verification(graph, execution)
        derived = list(dict.fromkeys(graph.objects(result, PROV.wasDerivedFrom)))
        require(derived, f"{result}: no prov:wasDerivedFrom lineage")
        require(
            traces_to_immutable_pizza_source(graph, result, set()),
            f"{result}: cannot trace Result to an immutable pizza-ontology Git blob source",
        )

    return executions


def used_resource_of_type(graph: Graph, support: Graph, execution: URIRef, rdf_type: URIRef) -> URIRef:
    used = list(dict.fromkeys(graph.objects(execution, PROV.used)))
    matches = [resource for resource in used if (resource, RDF.type, rdf_type) in support]
    value = one(matches, f"{execution} prov:used resource typed {rdf_type}")
    require(isinstance(value, URIRef), f"{execution}: typed used resource is not an IRI")
    return value


def verify_operational_invocation_profile() -> set[URIRef]:
    support = parse_graphs(SUPPORT_MODELS)
    invocation_ids: set[URIRef] = set()

    for path in INVOCATION_PROVENANCE:
        graph = parse_graphs([path])
        executions = list(dict.fromkeys(graph.subjects(RDF.type, ESKA.Execution)))
        execution = one(executions, f"{path.name} invocation Execution")
        require(isinstance(execution, URIRef), f"{path.name}: invocation Execution must be an IRI")
        invocation_ids.add(execution)

        result, _ = execution_result_verification(graph, execution)

        used_resource_of_type(graph, support, execution, ESKA.KnowledgeService)
        used_resource_of_type(graph, support, execution, ESKA.SemanticInvocationAdapter)
        used_resource_of_type(graph, support, execution, ESKA.ServiceDeployment)
        used_resource_of_type(graph, support, execution, ESKA.DeploymentEnvironment)
        used_resource_of_type(graph, support, execution, ESKA.HTTPDeploymentBinding)

        derived = list(dict.fromkeys(graph.objects(result, PROV.wasDerivedFrom)))
        require(len(derived) == 1, f"{result}: invocation Result must derive directly from one invocation input")
        input_entity = derived[0]
        require((input_entity, RDF.type, PROV.Entity) in graph, f"{result}: derived invocation input is not a prov:Entity")
        require((execution, PROV.used, input_entity) in graph, f"{execution}: invocation input is not prov:used")
        require(list(graph.objects(input_entity, DCTERMS.identifier)), f"{input_entity}: invocation input lacks dcterms:identifier")

        local_used_entities = [
            resource
            for resource in graph.objects(execution, PROV.used)
            if (resource, RDF.type, PROV.Entity) in graph
        ]
        require(
            len(set(local_used_entities)) >= 3,
            f"{execution}: expected input + architecture model + deployment model provenance entities",
        )

    require(len(invocation_ids) == 5, "operational profile requires five unique Agent invocation Execution IRIs")
    return invocation_ids


def main() -> None:
    semantic = verify_semantic_execution_profile()
    operational = verify_operational_invocation_profile()
    require(semantic.isdisjoint(operational), "semantic and operational execution identities must not collide")

    print("SUCCESS: ESKA provenance/evidence lineage profiles are complete without a parallel provenance ontology.")
    print(f"Semantic execution lineage:    {len(semantic)} Executions")
    print(f"Operational invocation lineage: {len(operational)} Executions")
    print("Immutable source trace:         every semantic Result reaches pizza-ontology@commit")
    print("Operational context:            Service + adapter + deployment + environment + binding + input")


if __name__ == "__main__":
    main()
