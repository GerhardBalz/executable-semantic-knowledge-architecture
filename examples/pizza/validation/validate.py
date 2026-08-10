#!/usr/bin/env python3
"""Execute and verify the ESKA Pizza SHACL validation slice."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pyshacl
from rdflib import Graph, Literal, Namespace, RDF, URIRef

HERE = Path(__file__).resolve().parent
PIZZA_EXAMPLE = HERE.parent
ROOT = HERE.parents[2]
RESULTS = HERE / "results"
DOMAIN_DIR = PIZZA_EXAMPLE / ".work" / "pizza-domain"
SOURCE_CONFIG = PIZZA_EXAMPLE / "pizza-domain-source.json"

ESKA = Namespace("urn:eska:core:")
SH = Namespace("http://www.w3.org/ns/shacl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
VAL = Namespace("urn:eska:example:pizza:validation:")
PIZZA = Namespace("http://www.co-ode.org/ontologies/pizza/pizza.owl#")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def source_binding() -> dict[str, object]:
    return json.loads(SOURCE_CONFIG.read_text(encoding="utf-8"))


def source_url(path: str) -> str:
    source = source_binding()
    return f"https://github.com/{source['repository']}/blob/{source['commit']}/{path}"


def materialize_domain_artifacts() -> None:
    subprocess.run(
        [sys.executable, str(PIZZA_EXAMPLE / "fetch-domain-artifacts.py")],
        check=True,
    )
    for path in (
        DOMAIN_DIR / "manifest.ttl",
        DOMAIN_DIR / "shapes.ttl",
        DOMAIN_DIR / "valid-data.ttl",
        DOMAIN_DIR / "invalid-data.ttl",
    ):
        require(path.is_file() and path.stat().st_size > 0, f"missing materialized Pizza domain artifact: {path}")


def verify_capability_contract() -> None:
    architecture = Graph()
    architecture.parse(ROOT / "model" / "eska-core.ttl", format="turtle")
    architecture.parse(ROOT / "model" / "eska-capability.ttl", format="turtle")
    architecture.parse(HERE / "pizza-validation-capability.ttl", format="turtle")

    query = (HERE / "verify-validation-capability.sparql").read_text(encoding="utf-8")
    violations = list(architecture.query(query))
    require(not violations, "PizzaValidationCapability contract is incomplete")


def validate_data(
    data_path: Path,
    expected_conforms: bool,
    report_file: str,
) -> Graph:
    data_graph = Graph().parse(data_path, format="turtle")
    shapes_graph = Graph().parse(DOMAIN_DIR / "shapes.ttl", format="turtle")

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
        f"{data_path.name}: expected conforms={expected_conforms}, got {conforms}",
    )

    reports = list(report_graph.subjects(RDF.type, SH.ValidationReport))
    require(len(reports) == 1, f"{data_path.name}: expected exactly one SHACL ValidationReport")
    report = reports[0]
    require(
        (report, SH.conforms, Literal(expected_conforms)) in report_graph,
        f"{data_path.name}: SHACL report does not preserve sh:conforms={expected_conforms}",
    )

    report_graph.serialize(destination=RESULTS / report_file, format="turtle")
    return report_graph


def verify_expected_violations(report_graph: Graph) -> None:
    expected = {
        (PIZZA.hasBase, SH.MinCountConstraintComponent),
        (PIZZA.hasTopping, SH.ClassConstraintComponent),
    }
    actual = {
        (path, component)
        for result in report_graph.subjects(RDF.type, SH.ValidationResult)
        for path in report_graph.objects(result, SH.resultPath)
        for component in report_graph.objects(result, SH.sourceConstraintComponent)
    }
    missing = expected - actual
    require(
        not missing,
        f"Invalid Pizza report is missing expected source-owned SHACL violations: {sorted(map(str, missing))}",
    )


def write_provenance() -> None:
    executed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    version = getattr(pyshacl, "__version__", "unknown")
    source = source_binding()
    commit = str(source["commit"])
    artifacts = dict(source["artifacts"])

    provenance = Graph()
    provenance.bind("dcterms", DCTERMS)
    provenance.bind("eska", ESKA)
    provenance.bind("prov", PROV)
    provenance.bind("sh", SH)
    provenance.bind("val", VAL)

    provenance.add((VAL.pyshacl, RDF.type, PROV.SoftwareAgent))
    provenance.add((VAL.pyshacl, DCTERMS.title, Literal(f"pySHACL {version}")))

    provenance.add((VAL.PizzaShapesGraph, RDF.type, PROV.Entity))
    provenance.add((VAL.PizzaShapesGraph, DCTERMS.identifier, Literal(f"{artifacts['shapes']}@{commit}")))
    provenance.add((VAL.PizzaShapesGraph, DCTERMS.source, URIRef(source_url(str(artifacts["shapes"])))))

    provenance.add((VAL.ValidPizzaDataGraph, RDF.type, PROV.Entity))
    provenance.add((VAL.ValidPizzaDataGraph, DCTERMS.identifier, Literal(f"{artifacts['validData']}@{commit}")))
    provenance.add((VAL.ValidPizzaDataGraph, DCTERMS.source, URIRef(source_url(str(artifacts["validData"])))))

    provenance.add((VAL.InvalidPizzaDataGraph, RDF.type, PROV.Entity))
    provenance.add((VAL.InvalidPizzaDataGraph, DCTERMS.identifier, Literal(f"{artifacts['invalidData']}@{commit}")))
    provenance.add((VAL.InvalidPizzaDataGraph, DCTERMS.source, URIRef(source_url(str(artifacts["invalidData"])))))

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

    print("1/5 Materializing source-owned Pizza validation artifacts...")
    materialize_domain_artifacts()

    print("2/5 Verifying PizzaValidationCapability contract...")
    verify_capability_contract()

    print("3/5 Validating conforming Pizza data...")
    validate_data(DOMAIN_DIR / "valid-data.ttl", True, "valid-report.ttl")

    print("4/5 Validating non-conforming Pizza data...")
    invalid_report = validate_data(DOMAIN_DIR / "invalid-data.ttl", False, "invalid-report.ttl")
    verify_expected_violations(invalid_report)

    print("5/5 Recording validation provenance...")
    write_provenance()

    print("SUCCESS: SHACL validation consumes the commit-pinned Pizza domain contract and distinguishes conforming from non-conforming data.")
    print(f"Pizza source:    {source_binding()['repository']}@{source_binding()['commit']}")
    print(f"Valid report:    {RESULTS / 'valid-report.ttl'}")
    print(f"Invalid report:  {RESULTS / 'invalid-report.ttl'}")
    print(f"Provenance:      {RESULTS / 'provenance.ttl'}")


if __name__ == "__main__":
    main()
