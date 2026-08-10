#!/usr/bin/env python3
"""Execute and verify the ESKA Pizza rule-evaluation mode."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import rdflib
from rdflib import Graph, Literal, Namespace, RDF, URIRef

HERE = Path(__file__).resolve().parent
PIZZA = HERE.parent
ROOT = HERE.parents[2]
DOMAIN = PIZZA / ".work" / "pizza-domain"
RESULTS = HERE / "results"

ESKA = Namespace("urn:eska:core:")
RUL = Namespace("urn:eska:example:pizza:rule:")
RULE = Namespace("urn:pizza-ontology:rule:")
DATA = Namespace("urn:pizza-ontology:rule:example:")
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
    architecture.parse(HERE / "pizza-rule-evaluation-capability.ttl", format="turtle")

    query = (HERE / "verify-rule-capability.sparql").read_text(encoding="utf-8")
    violations = list(architecture.query(query))
    require(not violations, "PizzaRuleEvaluationCapability contract is incomplete")


def evaluate_rule() -> Graph:
    data = Graph().parse(DOMAIN / "rule-data.ttl", format="turtle")
    vocabulary = Graph().parse(DOMAIN / "rule-vocabulary.ttl", format="turtle")
    query_text = (DOMAIN / "rule.rq").read_text(encoding="utf-8")

    require(
        (RULE.requiresVegetarianWarning, RDF.type, RDF.Property) in vocabulary,
        "source-owned rule vocabulary does not define requiresVegetarianWarning",
    )

    query_result = data.query(query_text)
    result_graph = query_result.graph
    require(result_graph is not None, "SPARQL CONSTRUCT did not return an RDF graph")

    expected = (DATA.meatyPizza, RULE.requiresVegetarianWarning, Literal(True))
    control = (DATA.vegetablePizza, RULE.requiresVegetarianWarning, Literal(True))
    require(expected in result_graph, "rule evaluation must derive the vegetarian warning for meatyPizza")
    require(control not in result_graph, "rule evaluation must not derive a warning for vegetablePizza")

    warning_results = list(result_graph.triples((None, RULE.requiresVegetarianWarning, None)))
    require(len(warning_results) == 1, f"expected exactly one warning statement, got {len(warning_results)}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    result_graph.serialize(destination=RESULTS / "result.ttl", format="turtle")
    return result_graph


def source_url(source: dict[str, object], role: str) -> URIRef:
    repository = str(source["repository"])
    commit = str(source["commit"])
    artifact_paths = dict(source["artifactPaths"])
    path = artifact_paths[role]
    return URIRef(f"https://github.com/{repository}/blob/{commit}/{path}")


def write_provenance(source: dict[str, object]) -> None:
    executed_at = datetime.now(timezone.utc).replace(microsecond=0)

    rule_url = source_url(source, "ruleQuery")
    vocabulary_url = source_url(source, "ruleVocabulary")
    data_url = source_url(source, "ruleData")

    provenance = Graph()
    provenance.bind("dcterms", DCTERMS)
    provenance.bind("eska", ESKA)
    provenance.bind("prov", PROV)
    provenance.bind("rdf", RDF)
    provenance.bind("rul", RUL)
    provenance.bind("rule", RULE)

    execution = RUL.PizzaRuleEvaluationExecution
    result = RUL.MeatyPizzaWarningResult
    verification = RUL.PizzaRuleEvaluationVerification

    provenance.add((RUL.rdflib, RDF.type, PROV.SoftwareAgent))
    provenance.add((RUL.rdflib, DCTERMS.title, Literal(f"RDFLib {rdflib.__version__}")))

    provenance.add((execution, RDF.type, ESKA.Execution))
    provenance.add((execution, RDF.type, PROV.Activity))
    provenance.add((execution, DCTERMS.conformsTo, RUL.PizzaRuleEvaluationCapability))
    provenance.add((execution, ESKA.executesCapability, RUL.PizzaRuleEvaluationCapability))
    provenance.add((execution, ESKA.usesSemanticModel, RUL.VegetarianWarningRuleModel))
    provenance.add((execution, ESKA.usesExecutableArtifact, RUL.SPARQLRuleEvaluationArtifact))
    provenance.add((execution, ESKA.generatesResult, result))
    provenance.add((execution, PROV.used, rule_url))
    provenance.add((execution, PROV.used, vocabulary_url))
    provenance.add((execution, PROV.used, data_url))
    provenance.add((execution, PROV.wasAssociatedWith, RUL.rdflib))
    provenance.add((execution, PROV.generated, result))
    provenance.add((execution, PROV.endedAtTime, Literal(executed_at, datatype=XSD.dateTime)))

    provenance.add((result, RDF.type, ESKA.Result))
    provenance.add((result, RDF.type, PROV.Entity))
    provenance.add((result, RDF.type, RDF.Statement))
    provenance.add((result, RDF.subject, DATA.meatyPizza))
    provenance.add((result, RDF.predicate, RULE.requiresVegetarianWarning))
    provenance.add((result, RDF.object, Literal(True)))
    provenance.add((result, PROV.wasGeneratedBy, execution))
    provenance.add((result, PROV.wasDerivedFrom, rule_url))
    provenance.add((result, PROV.wasDerivedFrom, data_url))

    provenance.add((verification, RDF.type, ESKA.Verification))
    provenance.add((verification, RDF.type, PROV.Activity))
    provenance.add((verification, ESKA.verifiesExecution, execution))
    provenance.add((verification, ESKA.verifiesResult, result))
    provenance.add((verification, PROV.used, result))
    provenance.add((verification, PROV.endedAtTime, Literal(executed_at, datatype=XSD.dateTime)))

    provenance.serialize(destination=RESULTS / "provenance.ttl", format="turtle")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    print("1/4 Materializing source-owned Pizza rule artifacts...")
    source = materialize_domain_artifacts()

    print("2/4 Verifying PizzaRuleEvaluationCapability contract...")
    verify_capability_contract()

    print("3/4 Evaluating source-owned SPARQL rule...")
    evaluate_rule()

    print("4/4 Recording rule execution and verification provenance...")
    write_provenance(source)

    print("SUCCESS: Rule → evaluate is executable as a third ESKA semantic mode.")
    print("Derived:    meatyPizza requiresVegetarianWarning true")
    print("Control:    vegetablePizza has no warning result")
    print(f"Result:     {RESULTS / 'result.ttl'}")
    print(f"Provenance: {RESULTS / 'provenance.ttl'}")


if __name__ == "__main__":
    main()
