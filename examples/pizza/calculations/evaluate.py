#!/usr/bin/env python3
"""Execute and verify the ESKA Pizza Calculation → calculate mode."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json
import math
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

OM_NS = "http://www.openmath.org/OpenMath"
OM = f"{{{OM_NS}}}"

ESKA = Namespace("urn:eska:core:")
CAL = Namespace("urn:eska:example:pizza:calculation:")
CALC = Namespace("urn:pizza-ontology:calculation:")
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
    architecture.parse(HERE / "pizza-area-calculation-capability.ttl", format="turtle")

    query = (HERE / "verify-calculation-capability.sparql").read_text(encoding="utf-8")
    violations = list(architecture.query(query))
    require(not violations, "PizzaAreaCalculationCapability contract is incomplete")


def local_name(element: ET.Element) -> str:
    return element.tag.removeprefix(OM)


def evaluate_openmath(element: ET.Element, variables: dict[str, float]) -> float:
    """Evaluate the small OpenMath arithmetic subset independently of any Pizza formula."""
    tag = local_name(element)

    if tag == "OMI":
        return float(int((element.text or "").strip()))

    if tag == "OMV":
        name = element.attrib["name"]
        require(name in variables, f"unbound OpenMath variable: {name}")
        return float(variables[name])

    if tag == "OMS":
        symbol = (element.attrib.get("cd"), element.attrib.get("name"))
        if symbol == ("nums1", "pi"):
            return math.pi
        raise AssertionError(f"unsupported standalone OpenMath symbol: {symbol}")

    if tag == "OMA":
        children = list(element)
        require(len(children) >= 2, "OpenMath application must contain an operator and arguments")
        operator = children[0]
        require(local_name(operator) == "OMS", "OpenMath application operator must be OMS")
        symbol = (operator.attrib.get("cd"), operator.attrib.get("name"))
        args = [evaluate_openmath(child, variables) for child in children[1:]]

        if symbol == ("arith1", "times"):
            return math.prod(args)
        if symbol == ("arith1", "divide"):
            require(len(args) == 2, "arith1:divide requires two arguments")
            return args[0] / args[1]
        if symbol == ("arith1", "power"):
            require(len(args) == 2, "arith1:power requires two arguments")
            return args[0] ** args[1]
        raise AssertionError(f"unsupported OpenMath operator: {symbol}")

    raise AssertionError(f"unsupported OpenMath element: {tag}")


def parse_formula() -> ET.Element:
    root = ET.parse(DOMAIN / "calculation.openmath.xml").getroot()
    require(local_name(root) == "OMOBJ", "source calculation formula must be an OpenMath OMOBJ")
    require(root.attrib.get("version") == "2.0", "source calculation formula must declare OpenMath version 2.0")
    require(root.attrib.get("cdbase") == "http://www.openmath.org/cd", "source calculation formula must use the OpenMath content-dictionary base")
    expressions = list(root)
    require(len(expressions) == 1, "source OpenMath OMOBJ must contain exactly one expression")
    return expressions[0]


def source_url(source: dict[str, object], role: str) -> URIRef:
    repository = str(source["repository"])
    commit = str(source["commit"])
    artifact_paths = dict(source["artifactPaths"])
    return URIRef(f"https://github.com/{repository}/blob/{commit}/{artifact_paths[role]}")


def calculate_cases() -> list[tuple[URIRef, Literal]]:
    expression = parse_formula()
    vocabulary = Graph().parse(DOMAIN / "calculation-vocabulary.ttl", format="turtle")
    require((CALC.diameterCentimetres, RDF.type, RDF.Property) in vocabulary, "calculation vocabulary does not define diameterCentimetres")
    require((CALC.areaSquareCentimetres, RDF.type, RDF.Property) in vocabulary, "calculation vocabulary does not define areaSquareCentimetres")

    cases_doc = json.loads((DOMAIN / "calculation-cases.json").read_text(encoding="utf-8"))
    require(cases_doc.get("calculation") == str(CALC.PizzaAreaCalculation), "calculation cases target a different semantic calculation")
    require(cases_doc.get("inputRelation") == str(CALC.diameterCentimetres), "unexpected calculation input relation")
    require(cases_doc.get("outputRelation") == str(CALC.areaSquareCentimetres), "unexpected calculation output relation")

    cases = cases_doc.get("cases")
    require(isinstance(cases, list) and len(cases) == 3, "expected exactly three Pizza calculation cases")

    calculated: list[tuple[URIRef, Literal]] = []
    result_graph = Graph()
    result_graph.bind("calc", CALC)

    for case in cases:
        identifier = case.get("id")
        diameter = case.get("diameterCm")
        expected = case.get("expectedAreaSquareCentimetres")
        require(isinstance(identifier, str), "calculation case must have a semantic identifier")
        require(isinstance(diameter, (int, float)) and not isinstance(diameter, bool), f"{identifier}: diameter must be numeric")
        require(isinstance(expected, (int, float)) and not isinstance(expected, bool), f"{identifier}: expected area must be numeric")
        require(math.isfinite(float(diameter)) and float(diameter) > 0, f"{identifier}: diameter must be positive and finite")

        actual = evaluate_openmath(expression, {"diameterCm": float(diameter)})
        rounded = round(actual, 6)
        require(math.isclose(rounded, float(expected), rel_tol=0.0, abs_tol=1e-6), f"{identifier}: expected {expected}, got {rounded}")

        subject = URIRef(identifier)
        value = Literal(Decimal(f"{rounded:.6f}"), datatype=XSD.decimal)
        result_graph.add((subject, CALC.areaSquareCentimetres, value))
        calculated.append((subject, value))

    RESULTS.mkdir(parents=True, exist_ok=True)
    result_graph.serialize(destination=RESULTS / "calculation-results.ttl", format="turtle")
    return calculated


def write_provenance(source: dict[str, object], calculated: list[tuple[URIRef, Literal]]) -> None:
    executed_at = datetime.now(timezone.utc).replace(microsecond=0)
    formula_url = source_url(source, "calculationFormula")
    vocabulary_url = source_url(source, "calculationVocabulary")
    cases_url = source_url(source, "calculationCases")

    provenance = Graph()
    provenance.bind("cal", CAL)
    provenance.bind("calc", CALC)
    provenance.bind("dcterms", DCTERMS)
    provenance.bind("eska", ESKA)
    provenance.bind("prov", PROV)
    provenance.bind("rdf", RDF)

    provenance.add((CAL.openMathEvaluator, RDF.type, PROV.SoftwareAgent))
    provenance.add((CAL.openMathEvaluator, DCTERMS.title, Literal(f"ESKA OpenMath subset evaluator / RDFLib {rdflib.__version__}")))

    for subject, value in calculated:
        local = str(subject).rsplit(":", 1)[-1]
        execution = CAL[f"{local}-calculation-execution"]
        result = CAL[f"{local}-calculation-result"]
        verification = CAL[f"{local}-calculation-verification"]

        provenance.add((execution, RDF.type, ESKA.Execution))
        provenance.add((execution, RDF.type, PROV.Activity))
        provenance.add((execution, DCTERMS.conformsTo, CAL.PizzaAreaCalculationCapability))
        provenance.add((execution, ESKA.executesCapability, CAL.PizzaAreaCalculationCapability))
        provenance.add((execution, ESKA.usesSemanticModel, CAL.PizzaAreaFormulaModel))
        provenance.add((execution, ESKA.usesExecutableArtifact, CAL.OpenMathCalculationArtifact))
        provenance.add((execution, ESKA.generatesResult, result))
        provenance.add((execution, PROV.used, formula_url))
        provenance.add((execution, PROV.used, vocabulary_url))
        provenance.add((execution, PROV.used, cases_url))
        provenance.add((execution, PROV.wasAssociatedWith, CAL.openMathEvaluator))
        provenance.add((execution, PROV.generated, result))
        provenance.add((execution, PROV.endedAtTime, Literal(executed_at, datatype=XSD.dateTime)))

        provenance.add((result, RDF.type, ESKA.Result))
        provenance.add((result, RDF.type, PROV.Entity))
        provenance.add((result, RDF.type, RDF.Statement))
        provenance.add((result, RDF.subject, subject))
        provenance.add((result, RDF.predicate, CALC.areaSquareCentimetres))
        provenance.add((result, RDF.object, value))
        provenance.add((result, PROV.wasGeneratedBy, execution))
        provenance.add((result, PROV.wasDerivedFrom, formula_url))
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

    print("1/4 Materializing source-owned Pizza calculation artifacts...")
    source = materialize_domain_artifacts()

    print("2/4 Verifying PizzaAreaCalculationCapability contract...")
    verify_capability_contract()

    print("3/4 Evaluating source-owned OpenMath calculation cases...")
    calculated = calculate_cases()

    print("4/4 Recording calculation executions, results, verifications, and provenance...")
    write_provenance(source, calculated)

    print("SUCCESS: Calculation → calculate is executable as a fifth ESKA semantic mode.")
    for subject, value in calculated:
        print(f"- {subject} -> {value} square centimetres")
    print(f"Results:    {RESULTS / 'calculation-results.ttl'}")
    print(f"Provenance: {RESULTS / 'provenance.ttl'}")


if __name__ == "__main__":
    main()
