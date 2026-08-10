#!/usr/bin/env python3
"""Execute and verify the ESKA Pizza Workflow → execute mode."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pyshacl
from pyshacl import validate
import rdflib
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.compare import isomorphic

HERE = Path(__file__).resolve().parent
PIZZA = HERE.parent
ROOT = HERE.parents[2]
DOMAIN = PIZZA / ".work" / "pizza-domain"
RESULTS = HERE / "results"

BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
WF_SOURCE_NS = "urn:pizza-ontology:workflow:"
BPMN = {"bpmn": BPMN_NS, "wf": WF_SOURCE_NS}

ESKA = Namespace("urn:eska:core:")
WF = Namespace("urn:eska:example:pizza:workflow:")
WF_SOURCE = Namespace(WF_SOURCE_NS)
VAL = Namespace("urn:eska:example:pizza:validation:")
MAP = Namespace("urn:eska:example:pizza:mapping:")
MENU = Namespace("urn:pizza-ontology:menu:")
ART = Namespace("urn:pizza-ontology:artifact:")
SH = Namespace("http://www.w3.org/ns/shacl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def materialize_domain_artifacts() -> dict[str, object]:
    subprocess.run([sys.executable, str(PIZZA / "fetch-domain-artifacts.py")], check=True)
    return json.loads((DOMAIN / "source.json").read_text(encoding="utf-8"))


def architecture_graph() -> Graph:
    graph = Graph()
    graph.parse(ROOT / "model" / "eska-core.ttl", format="turtle")
    graph.parse(ROOT / "model" / "eska-capability.ttl", format="turtle")
    graph.parse(PIZZA / "validation" / "pizza-validation-capability.ttl", format="turtle")
    graph.parse(PIZZA / "mappings" / "pizza-menu-projection-capability.ttl", format="turtle")
    graph.parse(HERE / "pizza-menu-publication-workflow-capability.ttl", format="turtle")
    return graph


def verify_capability_contract(architecture: Graph) -> None:
    query = (HERE / "verify-workflow-capability.sparql").read_text(encoding="utf-8")
    violations = list(architecture.query(query))
    require(not violations, "PizzaMenuPublicationWorkflowCapability contract is incomplete")


def parse_bpmn() -> dict[str, object]:
    root = ET.parse(DOMAIN / "workflow.bpmn").getroot()
    require(root.tag == f"{{{BPMN_NS}}}definitions", "source workflow must use the BPMN 2.0 MODEL namespace")
    process = root.find("bpmn:process", BPMN)
    require(process is not None and process.get("id") == "PizzaMenuPublicationProcess", "unexpected BPMN process")
    require(process.get("isExecutable") == "true", "BPMN process must be executable")

    tasks: dict[str, URIRef] = {}
    for task in process.findall("bpmn:serviceTask", BPMN):
        binding = task.find("bpmn:extensionElements/wf:semanticOperation", BPMN)
        require(binding is not None and binding.get("ref"), f"{task.get('id')}: missing semantic operation binding")
        require(task.get("implementation") == binding.get("ref"), f"{task.get('id')}: implementation and semantic binding differ")
        tasks[str(task.get("id"))] = URIRef(str(binding.get("ref")))

    gateway = process.find("bpmn:exclusiveGateway[@id='ValidationGateway']", BPMN)
    require(gateway is not None and gateway.get("default") == "FlowRejected", "workflow must default validation failure to Rejected")

    outgoing: dict[str, list[tuple[str, str | None, str]]] = {}
    for flow in process.findall("bpmn:sequenceFlow", BPMN):
        source = str(flow.get("sourceRef"))
        target = str(flow.get("targetRef"))
        condition = flow.find("bpmn:conditionExpression", BPMN)
        condition_text = (condition.text or "").strip() if condition is not None else None
        outgoing.setdefault(source, []).append((str(flow.get("id")), condition_text, target))

    outcomes: dict[str, URIRef] = {}
    for end in process.findall("bpmn:endEvent", BPMN):
        binding = end.find("bpmn:extensionElements/wf:workflowOutcome", BPMN)
        require(binding is not None and binding.get("ref"), f"{end.get('id')}: missing workflow outcome")
        outcomes[str(end.get("id"))] = URIRef(str(binding.get("ref")))

    require(set(tasks) == {"ValidatePizzaData", "TransformPizzaToMenu"}, f"unexpected BPMN tasks: {sorted(tasks)}")
    require(outcomes == {"Published": WF_SOURCE.Published, "Rejected": WF_SOURCE.Rejected}, f"unexpected BPMN outcomes: {outcomes}")
    return {"process": str(process.get("id")), "tasks": tasks, "outgoing": outgoing, "gatewayDefault": "FlowRejected", "outcomes": outcomes}


def resolve_operation_capabilities(architecture: Graph) -> dict[URIRef, URIRef]:
    bindings: dict[URIRef, URIRef] = {}
    for binding in architecture.subjects(RDF.type, WF.WorkflowOperationBinding):
        operation = architecture.value(binding, WF.sourceOperation)
        capability = architecture.value(binding, WF.boundCapability)
        require(isinstance(operation, URIRef) and isinstance(capability, URIRef), f"incomplete workflow operation binding: {binding}")
        bindings[operation] = capability
    require(bindings == {
        WF_SOURCE.ValidatePizzaData: VAL.PizzaValidationCapability,
        WF_SOURCE.TransformPizzaToMenu: MAP.PizzaMenuProjectionCapability,
    }, f"unexpected operation-capability bindings: {bindings}")
    return bindings


def verify_source_workflow_vocabulary() -> None:
    graph = Graph().parse(DOMAIN / "workflow-vocabulary.ttl", format="turtle")
    require((WF_SOURCE.ValidatePizzaData, DCTERMS.requires, ART.PizzaInstanceShapes) in graph, "source ValidatePizzaData operation must require PizzaInstanceShapes")
    require((WF_SOURCE.TransformPizzaToMenu, DCTERMS.requires, ART.PizzaMenuProjectionMapping) in graph, "source TransformPizzaToMenu operation must require PizzaMenuProjectionMapping")
    require((WF_SOURCE.TransformPizzaToMenu, DCTERMS.requires, ART.PizzaMenuVocabulary) in graph, "source TransformPizzaToMenu operation must require PizzaMenuVocabulary")
    require((WF_SOURCE.Published, RDF.type, WF_SOURCE.WorkflowOutcome) in graph, "Published workflow outcome missing")
    require((WF_SOURCE.Rejected, RDF.type, WF_SOURCE.WorkflowOutcome) in graph, "Rejected workflow outcome missing")


def local_path_for_source_path(source: dict[str, object], source_path: str) -> Path:
    artifact_paths = dict(source["artifactPaths"])
    materialized = dict(source["materialized"])
    for role, path in artifact_paths.items():
        if path == source_path:
            return DOMAIN / str(materialized[role])
    raise AssertionError(f"workflow case references unpublished source path: {source_path}")


def source_url(source: dict[str, object], role: str) -> URIRef:
    repository = str(source["repository"])
    commit = str(source["commit"])
    artifact_paths = dict(source["artifactPaths"])
    return URIRef(f"https://github.com/{repository}/blob/{commit}/{artifact_paths[role]}")


def source_path_url(source: dict[str, object], source_path: str) -> URIRef:
    return URIRef(f"https://github.com/{source['repository']}/blob/{source['commit']}/{source_path}")


def capability_models_and_artifact(architecture: Graph, capability: URIRef) -> tuple[list[URIRef], URIRef]:
    models = [m for m in architecture.objects(capability, ESKA.usesSemanticModel) if isinstance(m, URIRef)]
    artifacts = [a for a in architecture.objects(capability, ESKA.usesExecutableArtifact) if isinstance(a, URIRef)]
    require(models, f"{capability}: no semantic model")
    require(len(artifacts) == 1, f"{capability}: expected one executable artifact")
    return models, artifacts[0]


def add_execution_contract(graph: Graph, architecture: Graph, execution: URIRef, capability: URIRef, result: URIRef) -> None:
    models, artifact = capability_models_and_artifact(architecture, capability)
    graph.add((execution, RDF.type, ESKA.Execution))
    graph.add((execution, RDF.type, PROV.Activity))
    graph.add((execution, ESKA.executesCapability, capability))
    graph.add((execution, ESKA.usesExecutableArtifact, artifact))
    graph.add((execution, ESKA.generatesResult, result))
    graph.add((execution, PROV.generated, result))
    graph.add((execution, PROV.wasAssociatedWith, WF.workflowEvaluator))
    for model in models:
        graph.add((execution, ESKA.usesSemanticModel, model))


def add_verification(graph: Graph, verification: URIRef, execution: URIRef, result: URIRef, ended_at: Literal) -> None:
    graph.add((verification, RDF.type, ESKA.Verification))
    graph.add((verification, RDF.type, PROV.Activity))
    graph.add((verification, ESKA.verifiesExecution, execution))
    graph.add((verification, ESKA.verifiesResult, result))
    graph.add((verification, PROV.used, result))
    graph.add((verification, PROV.endedAtTime, ended_at))


def run_workflow_case(
    source: dict[str, object], architecture: Graph, model: dict[str, object], operation_capabilities: dict[URIRef, URIRef], case: dict[str, object], provenance: Graph
) -> dict[str, object]:
    identifier = str(case["id"])
    case_node = WF[f"{identifier}-case"]
    overall_execution = WF[f"{identifier}-workflow-execution"]
    overall_result = WF[f"{identifier}-workflow-result"]
    overall_verification = WF[f"{identifier}-workflow-verification"]
    ended_at = Literal(datetime.now(timezone.utc).replace(microsecond=0), datatype=XSD.dateTime)

    input_path = local_path_for_source_path(source, str(case["input"]))
    input_url = source_path_url(source, str(case["input"]))
    input_graph = Graph().parse(input_path, format="turtle")
    shapes = Graph().parse(DOMAIN / "shapes.ttl", format="turtle")
    mapping_query = (DOMAIN / "mapping.rq").read_text(encoding="utf-8")

    add_execution_contract(provenance, architecture, overall_execution, WF.PizzaMenuPublicationWorkflowCapability, overall_result)
    provenance.add((overall_execution, PROV.used, source_url(source, "workflowModel")))
    provenance.add((overall_execution, PROV.used, source_url(source, "workflowVocabulary")))
    provenance.add((overall_execution, PROV.used, source_url(source, "workflowCases")))
    provenance.add((overall_execution, PROV.used, input_url))

    current = "Start"
    state: dict[str, object] = {}
    executed_steps: list[str] = []
    step_results: list[URIRef] = []
    prior_step_execution: URIRef | None = None
    transformed: Graph | None = None

    while current not in model["outcomes"]:
        tasks = model["tasks"]
        if current in tasks:
            operation = tasks[current]
            capability = operation_capabilities[operation]
            step_execution = WF[f"{identifier}-{current}-execution"]
            step_result = WF[f"{identifier}-{current}-result"]
            step_verification = WF[f"{identifier}-{current}-verification"]
            add_execution_contract(provenance, architecture, step_execution, capability, step_result)
            provenance.add((overall_execution, DCTERMS.hasPart, step_execution))
            provenance.add((step_execution, DCTERMS.isPartOf, overall_execution))
            if prior_step_execution is not None:
                provenance.add((step_execution, PROV.wasInformedBy, prior_step_execution))

            if operation == WF_SOURCE.ValidatePizzaData:
                shapes_url = source_url(source, "shapes")
                conforms, _, _ = validate(data_graph=input_graph, shacl_graph=shapes, inference="none", abort_on_first=False)
                state["validationConforms"] = bool(conforms)
                provenance.add((step_result, RDF.type, ESKA.Result))
                provenance.add((step_result, RDF.type, PROV.Entity))
                provenance.add((step_result, RDF.type, RDF.Statement))
                provenance.add((step_result, RDF.subject, case_node))
                provenance.add((step_result, RDF.predicate, SH.conforms))
                provenance.add((step_result, RDF.object, Literal(bool(conforms))))
                provenance.add((step_result, PROV.wasGeneratedBy, step_execution))
                provenance.add((step_result, PROV.wasDerivedFrom, input_url))
                provenance.add((step_result, PROV.wasDerivedFrom, shapes_url))
                provenance.add((step_execution, PROV.used, input_url))
                provenance.add((step_execution, PROV.used, shapes_url))
            elif operation == WF_SOURCE.TransformPizzaToMenu:
                require(state.get("validationConforms") is True, f"{identifier}: mapping executed without conforming validation")
                mapping_url = source_url(source, "mappingQuery")
                target_model_url = source_url(source, "mappingTargetVocabulary")
                query_result = input_graph.query(mapping_query)
                transformed = query_result.graph
                require(transformed is not None, f"{identifier}: mapping did not produce a graph")
                expected_path = local_path_for_source_path(source, str(case["expectedTarget"]))
                expected_url = source_path_url(source, str(case["expectedTarget"]))
                expected = Graph().parse(expected_path, format="turtle")
                require(isomorphic(transformed, expected), f"{identifier}: workflow target graph differs from expected")
                provenance.add((step_result, RDF.type, ESKA.Result))
                provenance.add((step_result, RDF.type, PROV.Entity))
                provenance.add((step_result, RDF.type, MAP.MenuProjectionGraph))
                provenance.add((step_result, DCTERMS.conformsTo, MAP.MenuTargetSemanticModel))
                provenance.add((step_result, PROV.wasGeneratedBy, step_execution))
                provenance.add((step_result, PROV.wasDerivedFrom, input_url))
                provenance.add((step_result, PROV.wasDerivedFrom, mapping_url))
                provenance.add((step_execution, PROV.used, input_url))
                provenance.add((step_execution, PROV.used, mapping_url))
                provenance.add((step_execution, PROV.used, target_model_url))
                provenance.add((step_verification, PROV.used, expected_url))
            else:
                raise AssertionError(f"unsupported workflow operation: {operation}")

            add_verification(provenance, step_verification, step_execution, step_result, ended_at)
            provenance.add((step_execution, PROV.endedAtTime, ended_at))
            executed_steps.append(str(operation))
            step_results.append(step_result)
            prior_step_execution = step_execution

        outgoing = model["outgoing"].get(current, [])
        require(outgoing, f"{identifier}: no outgoing BPMN flow from {current}")
        if current == "ValidationGateway":
            if state.get("validationConforms") is True:
                matches = [flow for flow in outgoing if flow[1] == "validationConforms"]
                require(len(matches) == 1, f"{identifier}: expected one conforming gateway path")
                current = matches[0][2]
            else:
                defaults = [flow for flow in outgoing if flow[0] == model["gatewayDefault"]]
                require(len(defaults) == 1, f"{identifier}: expected one default gateway path")
                current = defaults[0][2]
        else:
            require(len(outgoing) == 1, f"{identifier}: expected one outgoing flow from {current}")
            current = outgoing[0][2]

    outcome = model["outcomes"][current]
    require(str(outcome) == case["expectedOutcome"], f"{identifier}: expected {case['expectedOutcome']}, got {outcome}")
    require(executed_steps == case["expectedSteps"], f"{identifier}: expected steps {case['expectedSteps']}, got {executed_steps}")
    if outcome == WF_SOURCE.Rejected:
        require(transformed is None, f"{identifier}: rejected workflow must not execute Mapping")

    provenance.add((overall_result, RDF.type, ESKA.Result))
    provenance.add((overall_result, RDF.type, PROV.Entity))
    provenance.add((overall_result, RDF.type, WF.PizzaWorkflowResult))
    provenance.add((overall_result, RDF.type, RDF.Statement))
    provenance.add((overall_result, RDF.subject, case_node))
    provenance.add((overall_result, RDF.predicate, WF_SOURCE.workflowOutcome))
    provenance.add((overall_result, RDF.object, outcome))
    provenance.add((overall_result, PROV.wasGeneratedBy, overall_execution))
    for step_result in step_results:
        provenance.add((overall_result, PROV.wasDerivedFrom, step_result))
    provenance.add((overall_execution, PROV.endedAtTime, ended_at))
    add_verification(provenance, overall_verification, overall_execution, overall_result, ended_at)

    if transformed is not None:
        transformed.serialize(destination=RESULTS / f"{identifier}-menu.ttl", format="turtle")

    return {
        "id": identifier,
        "outcome": str(outcome),
        "steps": executed_steps,
        "validationConforms": bool(state.get("validationConforms")),
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    print("1/6 Materializing source-owned Pizza workflow artifacts...")
    source = materialize_domain_artifacts()

    print("2/6 Loading and verifying workflow/child Capability contracts...")
    architecture = architecture_graph()
    verify_capability_contract(architecture)
    operation_capabilities = resolve_operation_capabilities(architecture)

    print("3/6 Verifying source-owned BPMN and workflow operation vocabulary...")
    model = parse_bpmn()
    verify_source_workflow_vocabulary()

    print("4/6 Executing valid and invalid BPMN workflow cases...")
    cases_doc = json.loads((DOMAIN / "workflow-cases.json").read_text(encoding="utf-8"))
    require(cases_doc.get("workflow") == model["process"], "workflow cases target a different BPMN process")
    cases = cases_doc.get("cases")
    require(isinstance(cases, list) and len(cases) == 2, "expected exactly two workflow cases")

    provenance = Graph()
    provenance.bind("dcterms", DCTERMS)
    provenance.bind("eska", ESKA)
    provenance.bind("map", MAP)
    provenance.bind("prov", PROV)
    provenance.bind("sh", SH)
    provenance.bind("val", VAL)
    provenance.bind("wf", WF)
    provenance.bind("pizzaWf", WF_SOURCE)

    provenance.add((WF.workflowEvaluator, RDF.type, PROV.SoftwareAgent))
    provenance.add((
        WF.workflowEvaluator,
        DCTERMS.title,
        Literal(
            f"ESKA BPMN workflow evaluator / pySHACL {getattr(pyshacl, '__version__', 'unknown')} / RDFLib {rdflib.__version__}"
        ),
    ))

    results = [run_workflow_case(source, architecture, model, operation_capabilities, case, provenance) for case in cases]

    print("5/6 Verifying composite execution structure...")
    valid_overall = WF["valid-publication-workflow-execution"]
    invalid_overall = WF["invalid-rejection-workflow-execution"]
    valid_steps = list(provenance.objects(valid_overall, DCTERMS.hasPart))
    invalid_steps = list(provenance.objects(invalid_overall, DCTERMS.hasPart))
    require(len(valid_steps) == 2, f"valid workflow must contain two step executions, got {valid_steps}")
    require(len(invalid_steps) == 1, f"invalid workflow must contain one step execution, got {invalid_steps}")
    require((WF["valid-publication-TransformPizzaToMenu-execution"], PROV.wasInformedBy, WF["valid-publication-ValidatePizzaData-execution"]) in provenance, "valid mapping step must be informed by validation step")

    print("6/6 Writing workflow Results and provenance...")
    result_graph = Graph()
    result_graph.bind("pizzaWf", WF_SOURCE)
    result_graph.bind("wf", WF)
    for item in results:
        case_node = WF[f"{item['id']}-case"]
        result_graph.add((case_node, WF_SOURCE.workflowOutcome, URIRef(item["outcome"])))
    result_graph.serialize(destination=RESULTS / "workflow-results.ttl", format="turtle")
    provenance.serialize(destination=RESULTS / "provenance.ttl", format="turtle")

    print("SUCCESS: Workflow → execute is executable as a seventh ESKA semantic mode.")
    for item in results:
        print(f"- {item['id']}: conforms={item['validationConforms']} steps={len(item['steps'])} outcome={item['outcome']}")
    print(f"Results:    {RESULTS / 'workflow-results.ttl'}")
    print(f"Provenance: {RESULTS / 'provenance.ttl'}")


if __name__ == "__main__":
    main()
