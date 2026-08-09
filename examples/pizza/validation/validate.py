#!/usr/bin/env python3
"""Execute and verify the ESKA Pizza SHACL validation slice."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pyshacl
from rdflib import Graph, Literal, Namespace, RDF

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULTS = HERE / "results"

ESKA = Namespace("urn:eska:core:")
SH = Namespace("http://www.w3.org/ns/shacl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
VAL = Namespace("urn:eska:example:pizza:validation:")
DATA = Namespace("urn:eska:example:pizza:data:")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_capability_contract() -> None:
    architecture = Graph()
    architecture.parse(ROOT / "model" / "eska-core.ttl", format="turtle")
    architecture.parse(ROOT / "model" / "eska-capability.ttl", format="turtle")
    architecture.parse(HERE / "pizza-validation-capability.ttl", format="turtle")

    query = (HERE / "verify-validation-capability.sparql").read_text(encoding="utf-8")
    violations = list(architecture.query(query))
    require(not violations, "PizzaValidationCapability contract is incomplete")


def validate_data(
    data_file: str,
    expected_conforms: bool,
    report_file: str,
) -> Graph:
    data_graph = Graph().parse(HERE / data_file, format="turtle")
    shapes_graph = Graph().parse(HERE / "pizza-shapes.ttl", format="turtle")

    conforms, report_graph, _ = pyshacl.validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=True,
        advanced=False,
        debug=False,
    )

    require(
        conforms is expected_conforms,
        f"{data_file}: expected conforms={expected_conforms}, got {conforms}",
    )

    reports = list(report_graph.subjects(RDF.type, SH.ValidationReport))
    require(len(reports) == 1, f"{data_file}: expected exactly one SHACL ValidationReport")
    report = reports[0]
    require(
        (report, SH.conforms, Literal(expected_conforms)) in report_graph,
        f"{data_file}: SHACL report does not preserve sh:conforms={expected_conforms}",
    )

    report_graph.serialize(destination=RESULTS / report_file, format="turtle")
    return report_graph


def verify_expected_violation(report_graph: Graph) -> None:
    matching_results = [
        result
        for result in report_graph.subjects(SH.focusNode, DATA.invalidPizza)
        if (result, SH.sourceConstraintComponent, SH.MaxCountConstraintComponent)
        in report_graph
        and (result, SH.resultPath, Namespace("http://www.co-ode.org/ontologies/pizza/pizza.owl#").hasBase)
        in report_graph
    ]
    require(
        bool(matching_results),
        "Invalid Pizza report must identify the hasBase max-count violation on invalidPizza",
    )


def write_provenance() -> None:
    executed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    version = getattr(pyshacl, "__version__", "unknown")

    provenance = Graph()
    provenance.bind("dcterms", DCTERMS)
    provenance.bind("eska", ESKA)
    provenance.bind("prov", PROV)
    provenance.bind("sh", SH)
    provenance.bind("val", VAL)

    provenance.add((VAL.pyshacl, RDF.type, PROV.SoftwareAgent))
    provenance.add((VAL.pyshacl, DCTERMS.title, Literal(f"pySHACL {version}")))

    for name, data_entity, report_entity, conforms in (
        ("valid-pizza-validation", VAL.ValidPizzaDataGraph, VAL.ValidPizzaValidationReport, True),
        ("invalid-pizza-validation", VAL.InvalidPizzaDataGraph, VAL.InvalidPizzaValidationReport, False),
    ):
        activity = VAL[name]
        verification = VAL[f"{name}-verification"]

        provenance.add((activity, RDF.type, ESKA.Execution))
        provenance.add((activity, RDF.type, PROV.Activity))
        provenance.add((activity, ESKA.executesCapability, VAL.PizzaValidationCapability))
        provenance.add((activity, ESKA.usesSemanticModel, VAL.PizzaShapesGraph))
        provenance.add((activity, ESKA.usesExecutableArtifact, VAL.SHACLValidationArtifact))
        provenance.add((activity, ESKA.generatesResult, report_entity))
        provenance.add((activity, PROV.used, VAL.PizzaShapesGraph))
        provenance.add((activity, PROV.used, data_entity))
        provenance.add((activity, PROV.wasAssociatedWith, VAL.pyshacl))
        provenance.add((activity, PROV.generated, report_entity))
        provenance.add((activity, PROV.endedAtTime, Literal(executed_at)))

        provenance.add((report_entity, RDF.type, ESKA.Result))
        provenance.add((report_entity, RDF.type, PROV.Entity))
        provenance.add((report_entity, RDF.type, SH.ValidationReport))
        provenance.add((report_entity, SH.conforms, Literal(conforms)))
        provenance.add((report_entity, PROV.wasGeneratedBy, activity))

        provenance.add((verification, RDF.type, ESKA.Verification))
        provenance.add((verification, RDF.type, PROV.Activity))
        provenance.add((verification, ESKA.verifiesExecution, activity))
        provenance.add((verification, ESKA.verifiesResult, report_entity))
        provenance.add((verification, PROV.endedAtTime, Literal(executed_at)))

    provenance.serialize(destination=RESULTS / "provenance.ttl", format="turtle")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    print("1/4 Verifying PizzaValidationCapability contract...")
    verify_capability_contract()

    print("2/4 Validating conforming Pizza data...")
    validate_data("valid-pizza.ttl", True, "valid-report.ttl")

    print("3/4 Validating non-conforming Pizza data...")
    invalid_report = validate_data("invalid-pizza.ttl", False, "invalid-report.ttl")
    verify_expected_violation(invalid_report)

    print("4/4 Recording validation provenance...")
    write_provenance()

    print("SUCCESS: SHACL validation distinguishes conforming and non-conforming Pizza data.")
    print(f"Valid report:   {RESULTS / 'valid-report.ttl'}")
    print(f"Invalid report: {RESULTS / 'invalid-report.ttl'}")
    print(f"Provenance:     {RESULTS / 'provenance.ttl'}")


if __name__ == "__main__":
    main()
