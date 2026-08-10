#!/usr/bin/env python3
"""Execute and verify the ESKA Pizza Mapping → transform mode."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import rdflib
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.compare import isomorphic

HERE = Path(__file__).resolve().parent
PIZZA = HERE.parent
ROOT = HERE.parents[2]
DOMAIN = PIZZA / ".work" / "pizza-domain"
RESULTS = HERE / "results"

ESKA = Namespace("urn:eska:core:")
MAP = Namespace("urn:eska:example:pizza:mapping:")
MENU = Namespace("urn:pizza-ontology:menu:")
PIZZA_NS = Namespace("http://www.co-ode.org/ontologies/pizza/pizza.owl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def materialize_domain_artifacts() -> dict[str, object]:
    subprocess.run([sys.executable, str(PIZZA / "fetch-domain-artifacts.py")], check=True)
    return json.loads((DOMAIN / "source.json").read_text(encoding="utf-8"))


def verify_capability_contract() -> None:
    architecture = Graph()
    architecture.parse(ROOT / "model" / "eska-core.ttl", format="turtle")
    architecture.parse(ROOT / "model" / "eska-capability.ttl", format="turtle")
    architecture.parse(HERE / "pizza-menu-projection-capability.ttl", format="turtle")

    query = (HERE / "verify-mapping-capability.sparql").read_text(encoding="utf-8")
    violations = list(architecture.query(query))
    require(not violations, "PizzaMenuProjectionCapability contract is incomplete")


def execute_mapping() -> Graph:
    source = Graph().parse(DOMAIN / "mapping-source-data.ttl", format="turtle")
    target_model = Graph().parse(DOMAIN / "mapping-target-vocabulary.ttl", format="turtle")
    expected = Graph().parse(DOMAIN / "mapping-expected-output.ttl", format="turtle")
    mapping_text = (DOMAIN / "mapping.rq").read_text(encoding="utf-8")

    require(
        (MENU.MenuItem, RDF.type, URIRef("http://www.w3.org/2002/07/owl#Class")) in target_model,
        "source-owned target semantic model does not define menu:MenuItem",
    )
    require(
        (MENU.displayName, RDF.type, URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty")) in target_model,
        "source-owned target semantic model does not define menu:displayName",
    )
    require(
        (MENU.ingredientName, RDF.type, URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty")) in target_model,
        "source-owned target semantic model does not define menu:ingredientName",
    )

    query_result = source.query(mapping_text)
    transformed = query_result.graph
    require(transformed is not None, "SPARQL CONSTRUCT mapping did not produce an RDF graph")
    require(isomorphic(transformed, expected), "transformed target graph differs from the source-owned canonical expected output")

    allowed_predicates = {RDF.type, MENU.displayName, MENU.ingredientName}
    for _, predicate, obj in transformed:
        require(predicate in allowed_predicates, f"unexpected predicate in target graph: {predicate}")
        require(not str(predicate).startswith(str(PIZZA_NS)), f"source Pizza predicate leaked into target graph: {predicate}")
        if predicate == RDF.type:
            require(obj == MENU.MenuItem, f"target rdf:type must be menu:MenuItem, got {obj}")
        require(not (isinstance(obj, URIRef) and str(obj).startswith(str(PIZZA_NS))), f"source Pizza entity leaked into target graph: {obj}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    transformed.serialize(destination=RESULTS / "menu-projection.ttl", format="turtle")
    return transformed


def source_url(source: dict[str, object], role: str) -> URIRef:
    repository = str(source["repository"])
    commit = str(source["commit"])
    artifact_paths = dict(source["artifactPaths"])
    return URIRef(f"https://github.com/{repository}/blob/{commit}/{artifact_paths[role]}")


def add_qualified_usage(graph: Graph, execution: URIRef, entity: URIRef, role: URIRef) -> None:
    usage = BNode()
    graph.add((usage, RDF.type, PROV.Usage))
    graph.add((usage, PROV.entity, entity))
    graph.add((usage, PROV.hadRole, role))
    graph.add((execution, PROV.qualifiedUsage, usage))


def write_provenance(source: dict[str, object]) -> None:
    executed_at = datetime.now(timezone.utc).replace(microsecond=0)

    mapping_url = source_url(source, "mappingQuery")
    target_model_url = source_url(source, "mappingTargetVocabulary")
    source_data_url = source_url(source, "mappingSourceData")
    expected_output_url = source_url(source, "mappingExpectedOutput")

    provenance = Graph()
    provenance.bind("dcterms", DCTERMS)
    provenance.bind("eska", ESKA)
    provenance.bind("map", MAP)
    provenance.bind("menu", MENU)
    provenance.bind("prov", PROV)

    execution = MAP.PizzaMenuProjectionExecution
    result = MAP.PizzaMenuProjectionResult
    verification = MAP.PizzaMenuProjectionVerification

    provenance.add((MAP.rdflibMapper, RDF.type, PROV.SoftwareAgent))
    provenance.add((MAP.rdflibMapper, DCTERMS.title, Literal(f"RDFLib {rdflib.__version__} SPARQL mapping evaluator")))

    for role in (MAP.SourceSemanticModelRole, MAP.TargetSemanticModelRole, MAP.MappingSemanticModelRole):
        provenance.add((role, RDF.type, PROV.Role))

    provenance.add((execution, RDF.type, ESKA.Execution))
    provenance.add((execution, RDF.type, PROV.Activity))
    provenance.add((execution, DCTERMS.conformsTo, MAP.PizzaMenuProjectionCapability))
    provenance.add((execution, ESKA.executesCapability, MAP.PizzaMenuProjectionCapability))
    provenance.add((execution, ESKA.usesSemanticModel, MAP.PizzaSourceSemanticModel))
    provenance.add((execution, ESKA.usesSemanticModel, MAP.MenuTargetSemanticModel))
    provenance.add((execution, ESKA.usesSemanticModel, MAP.PizzaToMenuMappingModel))
    provenance.add((execution, ESKA.usesExecutableArtifact, MAP.SPARQLMappingExecutionArtifact))
    provenance.add((execution, ESKA.generatesResult, result))
    provenance.add((execution, PROV.used, source_data_url))
    provenance.add((execution, PROV.used, mapping_url))
    provenance.add((execution, PROV.used, target_model_url))
    provenance.add((execution, PROV.wasAssociatedWith, MAP.rdflibMapper))
    provenance.add((execution, PROV.generated, result))
    provenance.add((execution, PROV.endedAtTime, Literal(executed_at, datatype=XSD.dateTime)))

    add_qualified_usage(provenance, execution, MAP.PizzaSourceSemanticModel, MAP.SourceSemanticModelRole)
    add_qualified_usage(provenance, execution, MAP.MenuTargetSemanticModel, MAP.TargetSemanticModelRole)
    add_qualified_usage(provenance, execution, MAP.PizzaToMenuMappingModel, MAP.MappingSemanticModelRole)

    provenance.add((result, RDF.type, ESKA.Result))
    provenance.add((result, RDF.type, PROV.Entity))
    provenance.add((result, RDF.type, MAP.MenuProjectionGraph))
    provenance.add((result, DCTERMS.conformsTo, MAP.MenuTargetSemanticModel))
    provenance.add((result, PROV.wasGeneratedBy, execution))
    provenance.add((result, PROV.wasDerivedFrom, source_data_url))
    provenance.add((result, PROV.wasDerivedFrom, mapping_url))

    provenance.add((verification, RDF.type, ESKA.Verification))
    provenance.add((verification, RDF.type, PROV.Activity))
    provenance.add((verification, ESKA.verifiesExecution, execution))
    provenance.add((verification, ESKA.verifiesResult, result))
    provenance.add((verification, PROV.used, result))
    provenance.add((verification, PROV.used, expected_output_url))
    provenance.add((verification, PROV.endedAtTime, Literal(executed_at, datatype=XSD.dateTime)))

    provenance.serialize(destination=RESULTS / "provenance.ttl", format="turtle")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    print("1/4 Materializing source-owned Pizza mapping artifacts...")
    source = materialize_domain_artifacts()

    print("2/4 Verifying PizzaMenuProjectionCapability contract...")
    verify_capability_contract()

    print("3/4 Transforming source Pizza RDF into the target Menu semantic model...")
    transformed = execute_mapping()

    print("4/4 Recording transformation result, verification, and semantic-model roles...")
    write_provenance(source)

    print("SUCCESS: Mapping → transform is executable as a sixth ESKA semantic mode.")
    print(f"Target triples: {len(transformed)}")
    print(f"Result:         {RESULTS / 'menu-projection.ttl'}")
    print(f"Provenance:     {RESULTS / 'provenance.ttl'}")


if __name__ == "__main__":
    main()
