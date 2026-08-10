#!/usr/bin/env python3
"""Execute and verify the ESKA Pizza Decision → decide mode."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import rdflib
from rdflib import Graph, Literal, Namespace, RDF, URIRef

HERE = Path(__file__).resolve().parent
PIZZA = HERE.parent
ROOT = HERE.parents[2]
DOMAIN = PIZZA / ".work" / "pizza-domain"
RESULTS = HERE / "results"

DMN_NS = "https://www.omg.org/spec/DMN/20230324/MODEL/"
DMN = {"dmn": DMN_NS}
EXPECTED_INPUTS = ["containsMeat", "containsFish"]

ESKA = Namespace("urn:eska:core:")
DEC = Namespace("urn:eska:example:pizza:decision:")
DECISION = Namespace("urn:pizza-ontology:decision:")
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
    architecture.parse(HERE / "pizza-dietary-suitability-capability.ttl", format="turtle")

    query = (HERE / "verify-decision-capability.sparql").read_text(encoding="utf-8")
    violations = list(architecture.query(query))
    require(not violations, "PizzaDietarySuitabilityCapability contract is incomplete")


def text_of(element: ET.Element | None) -> str:
    require(element is not None, "required DMN text element is missing")
    return (element.text or "").strip()


def parse_decision_model() -> tuple[str, list[str], list[tuple[list[str], URIRef]]]:
    root = ET.parse(DOMAIN / "decision.dmn").getroot()
    require(root.tag == f"{{{DMN_NS}}}definitions", "source decision model must use the DMN 1.5 MODEL namespace")

    decision = root.find("dmn:decision[@id='pizzaDietarySuitabilityDecision']", DMN)
    require(decision is not None, "source decision model does not contain PizzaDietarySuitabilityDecision")

    table = decision.find("dmn:decisionTable", DMN)
    require(table is not None, "source decision must contain a DMN decisionTable")
    require(table.get("hitPolicy") == "UNIQUE", "Pizza decision table must use UNIQUE hit policy")

    inputs = [
        text_of(clause.find("dmn:inputExpression/dmn:text", DMN))
        for clause in table.findall("dmn:input", DMN)
    ]
    require(inputs == EXPECTED_INPUTS, f"unexpected DMN decision inputs: {inputs}")

    outputs = table.findall("dmn:output", DMN)
    require(len(outputs) == 1, "Pizza decision table must define exactly one output")
    require(outputs[0].get("name") == "dietarySuitability", "unexpected DMN output name")

    rules: list[tuple[list[str], URIRef]] = []
    for rule in table.findall("dmn:rule", DMN):
        tests = [text_of(entry.find("dmn:text", DMN)) for entry in rule.findall("dmn:inputEntry", DMN)]
        require(len(tests) == len(inputs), f"DMN rule {rule.get('id')} has the wrong number of input entries")
        output_entries = rule.findall("dmn:outputEntry", DMN)
        require(len(output_entries) == 1, f"DMN rule {rule.get('id')} must have exactly one output entry")
        raw_output = text_of(output_entries[0].find("dmn:text", DMN))
        require(raw_output.startswith('"') and raw_output.endswith('"'), f"DMN rule {rule.get('id')} output must be a quoted semantic IRI")
        rules.append((tests, URIRef(raw_output[1:-1])))

    require(len(rules) == 3, f"expected three Pizza decision rules, got {len(rules)}")
    return str(decision.get("id")), inputs, rules


def unary_test_matches(test: str, value: bool) -> bool:
    if test == "-":
        return True
    if test == "true":
        return value is True
    if test == "false":
        return value is False
    raise AssertionError(f"unsupported unary test in canonical DMN decision: {test!r}")


def decide(inputs: list[str], rules: list[tuple[list[str], URIRef]], context: dict[str, object]) -> URIRef:
    require(set(context) == set(inputs), f"decision context differs from model inputs: {sorted(context)}")
    require(all(isinstance(context[name], bool) for name in inputs), "Pizza decision inputs must be booleans")

    matches: list[URIRef] = []
    for tests, outcome in rules:
        if all(unary_test_matches(test, bool(context[name])) for test, name in zip(tests, inputs)):
            matches.append(outcome)

    require(len(matches) == 1, f"UNIQUE decision expected exactly one matching rule, got {matches}")
    return matches[0]


def source_url(source: dict[str, object], role: str) -> URIRef:
    repository = str(source["repository"])
    commit = str(source["commit"])
    artifact_paths = dict(source["artifactPaths"])
    return URIRef(f"https://github.com/{repository}/blob/{commit}/{artifact_paths[role]}")


def evaluate_cases() -> tuple[list[tuple[URIRef, URIRef]], Graph]:
    decision_id, inputs, rules = parse_decision_model()
    cases_doc = json.loads((DOMAIN / "decision-cases.json").read_text(encoding="utf-8"))
    require(cases_doc.get("decision") == decision_id, "Pizza decision cases target a different DMN decision")

    vocabulary = Graph().parse(DOMAIN / "decision-vocabulary.ttl", format="turtle")
    require((DECISION.dietarySuitability, RDF.type, URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")) in vocabulary, "decision vocabulary does not define dietarySuitability")

    cases = cases_doc.get("cases")
    require(isinstance(cases, list) and len(cases) == 3, "expected exactly three Pizza decision cases")

    decisions: list[tuple[URIRef, URIRef]] = []
    result_graph = Graph()
    result_graph.bind("decision", DECISION)

    for case in cases:
        require(isinstance(case, dict), "decision case must be an object")
        identifier = case.get("id")
        context = case.get("inputs")
        expected = case.get("expected")
        require(isinstance(identifier, str), "decision case must have a semantic identifier")
        require(isinstance(context, dict), f"{identifier}: decision inputs must be an object")
        require(isinstance(expected, str), f"{identifier}: expected semantic outcome must be an IRI string")

        outcome = decide(inputs, rules, context)
        require(str(outcome) == expected, f"{identifier}: expected {expected}, got {outcome}")
        require((outcome, RDF.type, DECISION.DietarySuitabilityOutcome) in vocabulary, f"{identifier}: outcome is not typed in the source-owned decision vocabulary")

        subject = URIRef(identifier)
        result_graph.add((subject, DECISION.dietarySuitability, outcome))
        decisions.append((subject, outcome))

    require(len(decisions) == 3, "expected three Pizza decision results")
    require(len(set(outcome for _, outcome in decisions)) == 3, "canonical decision cases must exercise three distinct outcomes")

    RESULTS.mkdir(parents=True, exist_ok=True)
    result_graph.serialize(destination=RESULTS / "decision-results.ttl", format="turtle")
    return decisions, result_graph


def write_provenance(source: dict[str, object], decisions: list[tuple[URIRef, URIRef]]) -> None:
    executed_at = datetime.now(timezone.utc).replace(microsecond=0)
    model_url = source_url(source, "decisionModel")
    vocabulary_url = source_url(source, "decisionVocabulary")
    cases_url = source_url(source, "decisionCases")

    provenance = Graph()
    provenance.bind("dec", DEC)
    provenance.bind("decision", DECISION)
    provenance.bind("dcterms", DCTERMS)
    provenance.bind("eska", ESKA)
    provenance.bind("prov", PROV)
    provenance.bind("rdf", RDF)

    provenance.add((DEC.dmnEvaluator, RDF.type, PROV.SoftwareAgent))
    provenance.add((DEC.dmnEvaluator, DCTERMS.title, Literal(f"ESKA canonical DMN evaluator / RDFLib {rdflib.__version__}")))

    for subject, outcome in decisions:
        local = str(subject).rsplit(":", 1)[-1]
        execution = DEC[f"{local}-decision-execution"]
        result = DEC[f"{local}-decision-result"]
        verification = DEC[f"{local}-decision-verification"]

        provenance.add((execution, RDF.type, ESKA.Execution))
        provenance.add((execution, RDF.type, PROV.Activity))
        provenance.add((execution, DCTERMS.conformsTo, DEC.PizzaDietarySuitabilityCapability))
        provenance.add((execution, ESKA.executesCapability, DEC.PizzaDietarySuitabilityCapability))
        provenance.add((execution, ESKA.usesSemanticModel, DEC.PizzaDietarySuitabilityDecisionModel))
        provenance.add((execution, ESKA.usesExecutableArtifact, DEC.DMNDecisionEvaluationArtifact))
        provenance.add((execution, ESKA.generatesResult, result))
        provenance.add((execution, PROV.used, model_url))
        provenance.add((execution, PROV.used, vocabulary_url))
        provenance.add((execution, PROV.used, cases_url))
        provenance.add((execution, PROV.wasAssociatedWith, DEC.dmnEvaluator))
        provenance.add((execution, PROV.generated, result))
        provenance.add((execution, PROV.endedAtTime, Literal(executed_at, datatype=XSD.dateTime)))

        provenance.add((result, RDF.type, ESKA.Result))
        provenance.add((result, RDF.type, PROV.Entity))
        provenance.add((result, RDF.type, RDF.Statement))
        provenance.add((result, RDF.subject, subject))
        provenance.add((result, RDF.predicate, DECISION.dietarySuitability))
        provenance.add((result, RDF.object, outcome))
        provenance.add((result, PROV.wasGeneratedBy, execution))
        provenance.add((result, PROV.wasDerivedFrom, model_url))
        provenance.add((result, PROV.wasDerivedFrom, cases_url))

        provenance.add((verification, RDF.type, ESKA.Verification))
        provenance.add((verification, RDF.type, PROV.Activity))
        provenance.add((verification, ESKA.verifiesExecution, execution))
        provenance.add((verification, ESKA.verifiesResult, result))
        provenance.add((verification, PROV.used, result))
        provenance.add((verification, PROV.endedAtTime, Literal(executed_at, datatype=XSD.dateTime)))

    provenance.serialize(destination=RESULTS / "provenance.ttl", format="turtle")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    print("1/4 Materializing source-owned Pizza decision artifacts...")
    source = materialize_domain_artifacts()

    print("2/4 Verifying PizzaDietarySuitabilityCapability contract...")
    verify_capability_contract()

    print("3/4 Evaluating source-owned DMN decision cases...")
    decisions, _ = evaluate_cases()

    print("4/4 Recording decision executions, results, verifications, and provenance...")
    write_provenance(source, decisions)

    print("SUCCESS: Decision → decide is executable as a fourth ESKA semantic mode.")
    for subject, outcome in decisions:
        print(f"- {subject} -> {outcome}")
    print(f"Results:    {RESULTS / 'decision-results.ttl'}")
    print(f"Provenance: {RESULTS / 'provenance.ttl'}")


if __name__ == "__main__":
    main()
