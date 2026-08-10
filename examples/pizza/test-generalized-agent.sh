#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${HERE}/../.." && pwd)"
WORK_DIR="${HERE}/.work"
DOMAIN_DIR="${WORK_DIR}/pizza-domain"
RESULTS_DIR="${HERE}/results"
VERIFY_DIR="${RESULTS_DIR}/verification"
ROBOT_JAR="${ROBOT_JAR:-${WORK_DIR}/robot.jar}"
CLASS_PORT="${GENERAL_CLASS_PORT:-18083}"
VALIDATION_PORT="${GENERAL_VALIDATION_PORT:-18084}"
CLASS_BASE="http://127.0.0.1:${CLASS_PORT}"
VALIDATION_BASE="http://127.0.0.1:${VALIDATION_PORT}"
ARCHITECTURE="${RESULTS_DIR}/generalized-agent-architecture.owl"

CLASS_CAP="urn:eska:example:pizza:capability:PizzaClassificationCapability"
VALIDATION_CAP="urn:eska:example:pizza:validation:PizzaValidationCapability"
AMERICAN_HOT="http://www.co-ode.org/ontologies/pizza/pizza.owl#AmericanHot"
SPICY_PIZZA="http://www.co-ode.org/ontologies/pizza/pizza.owl#SpicyPizza"

mkdir -p "${RESULTS_DIR}" "${VERIFY_DIR}" "${WORK_DIR}"

# Make the regression runnable both inside CI and standalone.
# run.sh materializes the pinned Pizza artifacts, downloads ROBOT when needed,
# and creates the classified ontology consumed by the Classification Service.
if [[ ! -s "${ROBOT_JAR}" || ! -s "${RESULTS_DIR}/reasoned.owl" || ! -s "${DOMAIN_DIR}/shapes.ttl" ]]; then
  bash "${HERE}/run.sh"
fi

test -s "${ROBOT_JAR}"
test -s "${RESULTS_DIR}/reasoned.owl"
test -s "${DOMAIN_DIR}/shapes.ttl"
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

python3 "${HERE}/service.py" \
  --host 127.0.0.1 \
  --port "${CLASS_PORT}" \
  --reasoned "${RESULTS_DIR}/reasoned.owl" \
  >"${WORK_DIR}/general-classification-service.log" 2>&1 &
CLASS_PID=$!

python3 "${HERE}/validation/service.py" \
  --host 127.0.0.1 \
  --port "${VALIDATION_PORT}" \
  --shapes "${DOMAIN_DIR}/shapes.ttl" \
  >"${WORK_DIR}/general-validation-service.log" 2>&1 &
VALIDATION_PID=$!

cleanup() {
  kill "${CLASS_PID}" "${VALIDATION_PID}" 2>/dev/null || true
}
trap cleanup EXIT

for _ in $(seq 1 50); do
  if curl --fail --silent "${CLASS_BASE}/health" >/dev/null \
     && curl --fail --silent "${VALIDATION_BASE}/health" >/dev/null; then
    break
  fi
  sleep 0.1
done
curl --fail --silent "${CLASS_BASE}/health" >/dev/null
curl --fail --silent "${VALIDATION_BASE}/health" >/dev/null

run_agent() {
  local capability="$1"
  local base_url="$2"
  local input="$3"
  local output="$4"
  local provenance="$5"
  python3 "${HERE}/knowledge_agent.py" \
    --robot-jar "${ROBOT_JAR}" \
    --architecture "${ARCHITECTURE}" \
    --query "${HERE}/discover-service-generic.sparql" \
    --capability "${capability}" \
    --service-base-url "${base_url}" \
    --input "${input}" \
    --output "${output}" \
    --provenance "${provenance}"
}

run_agent \
  "${CLASS_CAP}" \
  "${CLASS_BASE}" \
  "${AMERICAN_HOT}" \
  "${RESULTS_DIR}/general-agent-classification.json" \
  "${RESULTS_DIR}/general-agent-classification-provenance.ttl"

run_agent \
  "${VALIDATION_CAP}" \
  "${VALIDATION_BASE}" \
  "${DOMAIN_DIR}/valid-data.ttl" \
  "${RESULTS_DIR}/general-agent-validation-valid.json" \
  "${RESULTS_DIR}/general-agent-validation-valid-provenance.ttl"

run_agent \
  "${VALIDATION_CAP}" \
  "${VALIDATION_BASE}" \
  "${DOMAIN_DIR}/invalid-data.ttl" \
  "${RESULTS_DIR}/general-agent-validation-invalid.json" \
  "${RESULTS_DIR}/general-agent-validation-invalid-provenance.ttl"

python3 - "${RESULTS_DIR}" "${SPICY_PIZZA}" <<'PY'
import json
from pathlib import Path
import sys
from rdflib import Graph, Namespace, RDF, URIRef

results = Path(sys.argv[1])
spicy = sys.argv[2]
AGENT = "urn:eska:example:pizza:general-agent:PizzaGeneralizedKnowledgeAgent"
ESKA = Namespace("urn:eska:core:")
PROV = Namespace("http://www.w3.org/ns/prov#")
SH = Namespace("http://www.w3.org/ns/shacl#")

classification = json.loads((results / "general-agent-classification.json").read_text(encoding="utf-8"))
assert classification["agent"] == AGENT
assert classification["adapter"]["key"] == "iri-list"
assert classification["targetCapability"] == "urn:eska:example:pizza:capability:PizzaClassificationCapability"
assert classification["discovery"]["inputType"] == "http://www.w3.org/2002/07/owl#Class"
assert classification["discovery"]["outputType"] == "http://www.w3.org/2002/07/owl#Class"
assert classification["semanticResult"]["relation"] == "http://www.w3.org/2000/01/rdf-schema#subClassOf"
assert spicy in classification["semanticResult"]["values"], classification

for name, expected in (("valid", True), ("invalid", False)):
    document = json.loads((results / f"general-agent-validation-{name}.json").read_text(encoding="utf-8"))
    assert document["agent"] == AGENT
    assert document["adapter"]["key"] == "rdf-jsonld-shacl-report"
    assert document["targetCapability"] == "urn:eska:example:pizza:validation:PizzaValidationCapability"
    assert document["discovery"]["outputType"] == "http://www.w3.org/ns/shacl#ValidationReport"
    assert document["semanticResult"]["relation"] == "http://www.w3.org/ns/shacl#conforms"
    assert document["semanticResult"]["conforms"] is expected
    if not expected:
        assert document["semanticResult"]["validationResultCount"] >= 1

checks = [
    ("classification", "urn:eska:example:pizza:general-agent:IRIListInvocationAdapter", False),
    ("validation-valid", "urn:eska:example:pizza:general-agent:SHACLReportInvocationAdapter", True),
    ("validation-invalid", "urn:eska:example:pizza:general-agent:SHACLReportInvocationAdapter", True),
]
for name, adapter, is_shacl in checks:
    path = results / f"general-agent-{name}-provenance.ttl"
    graph = Graph().parse(path, format="turtle")
    slug = "classification" if name == "classification" else "validation"
    base = f"urn:eska:example:pizza:general-agent-run:{slug}:"
    execution = URIRef(base + "execution")
    result = URIRef(base + "result")
    verification = URIRef(base + "verification")
    assert (execution, RDF.type, ESKA.Execution) in graph
    assert (execution, ESKA.generatesResult, result) in graph
    assert (execution, PROV.used, URIRef(adapter)) in graph
    assert (result, RDF.type, ESKA.Result) in graph
    assert (verification, RDF.type, ESKA.Verification) in graph
    assert (verification, ESKA.verifiesExecution, execution) in graph
    assert (verification, ESKA.verifiesResult, result) in graph
    if is_shacl:
        assert (result, RDF.type, SH.ValidationReport) in graph
PY

printf '\nSUCCESS: one generalized deterministic Knowledge Agent discovered and invoked classification and validation using semantic invocation adapters.\n'
printf 'Architecture: %s\n' "${ARCHITECTURE}"
printf 'Classification: %s\n' "${RESULTS_DIR}/general-agent-classification.json"
printf 'Validation valid: %s\n' "${RESULTS_DIR}/general-agent-validation-valid.json"
printf 'Validation invalid: %s\n' "${RESULTS_DIR}/general-agent-validation-invalid.json"
