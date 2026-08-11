#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${HERE}/../.." && pwd)"
WORK_DIR="${HERE}/.work"
DOMAIN_DIR="${WORK_DIR}/pizza-domain"
RESULTS_DIR="${HERE}/results"
VERIFY_DIR="${RESULTS_DIR}/verification"
ROBOT_JAR="${ROBOT_JAR:-${WORK_DIR}/robot.jar}"
ARCHITECTURE="${RESULTS_DIR}/generalized-agent-architecture.owl"
DEPLOYMENT_MODEL="${HERE}/deployments/pizza-deployments.ttl"

CLASS_BLUE_PORT="${GENERAL_CLASS_BLUE_PORT:-18083}"
VALIDATION_BLUE_PORT="${GENERAL_VALIDATION_BLUE_PORT:-18084}"
CLASS_GREEN_PORT="${GENERAL_CLASS_GREEN_PORT:-18085}"
VALIDATION_GREEN_PORT="${GENERAL_VALIDATION_GREEN_PORT:-18086}"

CLASS_BLUE_BASE="http://127.0.0.1:${CLASS_BLUE_PORT}"
VALIDATION_BLUE_BASE="http://127.0.0.1:${VALIDATION_BLUE_PORT}"
CLASS_GREEN_BASE="http://127.0.0.1:${CLASS_GREEN_PORT}"
VALIDATION_GREEN_BASE="http://127.0.0.1:${VALIDATION_GREEN_PORT}"

CLASS_CAP="urn:eska:example:pizza:capability:PizzaClassificationCapability"
VALIDATION_CAP="urn:eska:example:pizza:validation:PizzaValidationCapability"
AMERICAN_HOT="http://www.co-ode.org/ontologies/pizza/pizza.owl#AmericanHot"
SPICY_PIZZA="http://www.co-ode.org/ontologies/pizza/pizza.owl#SpicyPizza"

mkdir -p "${RESULTS_DIR}" "${VERIFY_DIR}" "${WORK_DIR}"

# Make the regression runnable both inside CI and standalone.
if [[ ! -s "${ROBOT_JAR}" || ! -s "${RESULTS_DIR}/reasoned.owl" || ! -s "${DOMAIN_DIR}/shapes.ttl" ]]; then
  bash "${HERE}/run.sh"
fi

test -s "${ROBOT_JAR}"
test -s "${RESULTS_DIR}/reasoned.owl"
test -s "${DOMAIN_DIR}/shapes.ttl"
test -s "${DEPLOYMENT_MODEL}"
ROBOT=(java -jar "${ROBOT_JAR}")

"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${ROOT_DIR}/model/eska-capability.ttl" \
  --input "${ROOT_DIR}/model/eska-service.ttl" \
  --input "${ROOT_DIR}/model/eska-agent.ttl" \
  --input "${HERE}/pizza-classification-capability.ttl" \
  --input "${HERE}/pizza-classification-service.ttl" \
  --input "${HERE}/validation/pizza-validation-capability.ttl" \
  --input "${HERE}/validation/pizza-validation-service.ttl" \
  --input "${HERE}/pizza-generalized-agent.ttl" \
  --output "${ARCHITECTURE}"

"${ROBOT[@]}" verify \
  --input "${ARCHITECTURE}" \
  --queries "${HERE}/verify-generalized-agent.sparql" \
  --output-dir "${VERIFY_DIR}"

bash "${HERE}/deployments/verify.sh"

python3 "${HERE}/service.py" \
  --host 127.0.0.1 \
  --port "${CLASS_BLUE_PORT}" \
  --reasoned "${RESULTS_DIR}/reasoned.owl" \
  >"${WORK_DIR}/classification-blue.log" 2>&1 &
CLASS_BLUE_PID=$!

python3 "${HERE}/validation/service.py" \
  --host 127.0.0.1 \
  --port "${VALIDATION_BLUE_PORT}" \
  --shapes "${DOMAIN_DIR}/shapes.ttl" \
  >"${WORK_DIR}/validation-blue.log" 2>&1 &
VALIDATION_BLUE_PID=$!

python3 "${HERE}/service.py" \
  --host 127.0.0.1 \
  --port "${CLASS_GREEN_PORT}" \
  --reasoned "${RESULTS_DIR}/reasoned.owl" \
  >"${WORK_DIR}/classification-green.log" 2>&1 &
CLASS_GREEN_PID=$!

python3 "${HERE}/validation/service.py" \
  --host 127.0.0.1 \
  --port "${VALIDATION_GREEN_PORT}" \
  --shapes "${DOMAIN_DIR}/shapes.ttl" \
  >"${WORK_DIR}/validation-green.log" 2>&1 &
VALIDATION_GREEN_PID=$!

cleanup() {
  kill \
    "${CLASS_BLUE_PID}" \
    "${VALIDATION_BLUE_PID}" \
    "${CLASS_GREEN_PID}" \
    "${VALIDATION_GREEN_PID}" \
    2>/dev/null || true
}
trap cleanup EXIT

for _ in $(seq 1 50); do
  if curl --fail --silent "${CLASS_BLUE_BASE}/health" >/dev/null \
     && curl --fail --silent "${VALIDATION_BLUE_BASE}/health" >/dev/null \
     && curl --fail --silent "${CLASS_GREEN_BASE}/health" >/dev/null \
     && curl --fail --silent "${VALIDATION_GREEN_BASE}/health" >/dev/null; then
    break
  fi
  sleep 0.1
done

for base in \
  "${CLASS_BLUE_BASE}" \
  "${VALIDATION_BLUE_BASE}" \
  "${CLASS_GREEN_BASE}" \
  "${VALIDATION_GREEN_BASE}"
do
  curl --fail --silent "${base}/health" >/dev/null
done

run_agent() {
  local capability="$1"
  local environment="$2"
  local input="$3"
  local output="$4"
  local provenance="$5"
  python3 "${HERE}/knowledge_agent.py" \
    --robot-jar "${ROBOT_JAR}" \
    --architecture "${ARCHITECTURE}" \
    --query "${HERE}/discover-service-generic.sparql" \
    --capability "${capability}" \
    --deployment-model "${DEPLOYMENT_MODEL}" \
    --environment "${environment}" \
    --input "${input}" \
    --output "${output}" \
    --provenance "${provenance}"
}

run_agent \
  "${CLASS_CAP}" blue "${AMERICAN_HOT}" \
  "${RESULTS_DIR}/general-agent-classification-blue.json" \
  "${RESULTS_DIR}/general-agent-classification-blue-provenance.ttl"

run_agent \
  "${CLASS_CAP}" green "${AMERICAN_HOT}" \
  "${RESULTS_DIR}/general-agent-classification-green.json" \
  "${RESULTS_DIR}/general-agent-classification-green-provenance.ttl"

run_agent \
  "${VALIDATION_CAP}" blue "${DOMAIN_DIR}/valid-data.ttl" \
  "${RESULTS_DIR}/general-agent-validation-valid-blue.json" \
  "${RESULTS_DIR}/general-agent-validation-valid-blue-provenance.ttl"

run_agent \
  "${VALIDATION_CAP}" green "${DOMAIN_DIR}/valid-data.ttl" \
  "${RESULTS_DIR}/general-agent-validation-valid-green.json" \
  "${RESULTS_DIR}/general-agent-validation-valid-green-provenance.ttl"

run_agent \
  "${VALIDATION_CAP}" green "${DOMAIN_DIR}/invalid-data.ttl" \
  "${RESULTS_DIR}/general-agent-validation-invalid-green.json" \
  "${RESULTS_DIR}/general-agent-validation-invalid-green-provenance.ttl"

python3 - "${RESULTS_DIR}" "${SPICY_PIZZA}" <<'PY'
import json
from pathlib import Path
import sys
from rdflib import Graph, Namespace, RDF, URIRef

results = Path(sys.argv[1])
spicy = sys.argv[2]
AGENT = "urn:eska:example:pizza:general-agent:PizzaGeneralizedKnowledgeAgent"
ESKA = Namespace("https://w3id.org/eska#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SH = Namespace("http://www.w3.org/ns/shacl#")
DEP = "urn:eska:example:pizza:deployment:"


def load(name):
    return json.loads((results / name).read_text(encoding="utf-8"))


class_blue = load("general-agent-classification-blue.json")
class_green = load("general-agent-classification-green.json")
for document, environment, deployment, port in (
    (class_blue, "blue", DEP + "ClassificationBlueDeployment", "18083"),
    (class_green, "green", DEP + "ClassificationGreenDeployment", "18085"),
):
    assert document["agent"] == AGENT
    assert document["adapter"]["key"] == "iri-list"
    assert document["targetCapability"] == "urn:eska:example:pizza:capability:PizzaClassificationCapability"
    assert document["deployment"]["environmentIdentifier"] == environment
    assert document["deployment"]["deployment"] == deployment
    assert port in document["deployment"]["baseURL"]
    assert document["discovery"]["inputType"] == "http://www.w3.org/2002/07/owl#Class"
    assert document["discovery"]["outputType"] == "http://www.w3.org/2002/07/owl#Class"
    assert document["semanticResult"]["relation"] == "http://www.w3.org/2000/01/rdf-schema#subClassOf"
    assert spicy in document["semanticResult"]["values"], document

assert class_blue["discovery"] == class_green["discovery"]
assert class_blue["adapter"] == class_green["adapter"]
assert class_blue["deployment"] != class_green["deployment"]
assert class_blue["invocation"]["endpoint"] != class_green["invocation"]["endpoint"]
assert class_blue["semanticResult"] == class_green["semanticResult"]

valid_blue = load("general-agent-validation-valid-blue.json")
valid_green = load("general-agent-validation-valid-green.json")
invalid_green = load("general-agent-validation-invalid-green.json")

for document, environment, deployment, expected in (
    (valid_blue, "blue", DEP + "ValidationBlueDeployment", True),
    (valid_green, "green", DEP + "ValidationGreenDeployment", True),
    (invalid_green, "green", DEP + "ValidationGreenDeployment", False),
):
    assert document["agent"] == AGENT
    assert document["adapter"]["key"] == "rdf-jsonld-shacl-report"
    assert document["targetCapability"] == "urn:eska:example:pizza:validation:PizzaValidationCapability"
    assert document["deployment"]["environmentIdentifier"] == environment
    assert document["deployment"]["deployment"] == deployment
    assert document["discovery"]["outputType"] == "http://www.w3.org/ns/shacl#ValidationReport"
    assert document["semanticResult"]["relation"] == "http://www.w3.org/ns/shacl#conforms"
    assert document["semanticResult"]["conforms"] is expected
    if not expected:
        assert document["semanticResult"]["validationResultCount"] >= 1

assert valid_blue["discovery"] == valid_green["discovery"]
assert valid_blue["adapter"] == valid_green["adapter"]
assert valid_blue["deployment"] != valid_green["deployment"]
assert valid_blue["invocation"]["endpoint"] != valid_green["invocation"]["endpoint"]
assert valid_blue["semanticResult"]["conforms"] == valid_green["semanticResult"]["conforms"]

checks = [
    (
        "general-agent-classification-blue-provenance.ttl",
        DEP + "ClassificationBlueDeployment",
        DEP + "BlueEnvironment",
        "urn:eska:example:pizza:general-agent:IRIListInvocationAdapter",
        False,
    ),
    (
        "general-agent-classification-green-provenance.ttl",
        DEP + "ClassificationGreenDeployment",
        DEP + "GreenEnvironment",
        "urn:eska:example:pizza:general-agent:IRIListInvocationAdapter",
        False,
    ),
    (
        "general-agent-validation-valid-blue-provenance.ttl",
        DEP + "ValidationBlueDeployment",
        DEP + "BlueEnvironment",
        "urn:eska:example:pizza:general-agent:SHACLReportInvocationAdapter",
        True,
    ),
    (
        "general-agent-validation-valid-green-provenance.ttl",
        DEP + "ValidationGreenDeployment",
        DEP + "GreenEnvironment",
        "urn:eska:example:pizza:general-agent:SHACLReportInvocationAdapter",
        True,
    ),
    (
        "general-agent-validation-invalid-green-provenance.ttl",
        DEP + "ValidationGreenDeployment",
        DEP + "GreenEnvironment",
        "urn:eska:example:pizza:general-agent:SHACLReportInvocationAdapter",
        True,
    ),
]
execution_ids = set()
for filename, deployment, environment, adapter, is_shacl in checks:
    graph = Graph().parse(results / filename, format="turtle")
    executions = list(dict.fromkeys(graph.subjects(RDF.type, ESKA.Execution)))
    assert len(executions) == 1, (filename, executions)
    execution = executions[0]
    execution_ids.add(execution)
    generated = list(dict.fromkeys(graph.objects(execution, ESKA.generatesResult)))
    assert len(generated) == 1, (filename, generated)
    result = generated[0]
    verifications = [
        v
        for v in graph.subjects(ESKA.verifiesExecution, execution)
        if (v, ESKA.verifiesResult, result) in graph
    ]
    assert len(verifications) == 1, (filename, verifications)
    verification = verifications[0]
    assert (execution, PROV.used, URIRef(adapter)) in graph
    assert (execution, PROV.used, URIRef(deployment)) in graph
    assert (execution, PROV.used, URIRef(environment)) in graph
    assert (result, RDF.type, ESKA.Result) in graph
    assert (verification, RDF.type, ESKA.Verification) in graph
    assert (verification, PROV.used, result) in graph
    if is_shacl:
        assert (result, RDF.type, SH.ValidationReport) in graph

assert len(execution_ids) == len(checks), "Agent invocation provenance IRIs must remain unique across blue/green and input cases"
PY

printf '\nSUCCESS: semantic Service discovery is stable while blue/green deployment bindings change runtime endpoints.\n'
printf 'Architecture:      %s\n' "${ARCHITECTURE}"
printf 'Deployment model: %s\n' "${DEPLOYMENT_MODEL}"
printf 'Classification:   blue + green\n'
printf 'Validation:       blue + green, including non-conforming green case\n'
printf 'Provenance:       five distinct invocation identities\n'
