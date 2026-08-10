#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIZZA_DIR="$(cd "${HERE}/.." && pwd)"
ROOT_DIR="$(cd "${PIZZA_DIR}/../.." && pwd)"
WORK_DIR="${PIZZA_DIR}/.work"
DOMAIN_DIR="${WORK_DIR}/pizza-domain"
RESULTS_DIR="${HERE}/results"
VERIFY_DIR="${RESULTS_DIR}/verification"
ROBOT_VERSION="${ROBOT_VERSION:-1.9.10}"
ROBOT_JAR="${ROBOT_JAR:-${WORK_DIR}/robot.jar}"
ROBOT_URL="https://github.com/ontodev/robot/releases/download/v${ROBOT_VERSION}/robot.jar"
PORT="${VALIDATION_PORT:-18082}"
BASE_URL="http://127.0.0.1:${PORT}"

mkdir -p "${WORK_DIR}" "${RESULTS_DIR}" "${VERIFY_DIR}"
python3 "${PIZZA_DIR}/fetch-domain-artifacts.py"

if [[ ! -f "${ROBOT_JAR}" ]]; then
  curl --fail --location --silent --show-error "${ROBOT_URL}" --output "${ROBOT_JAR}"
fi
ROBOT=(java -jar "${ROBOT_JAR}")

"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${ROOT_DIR}/model/eska-capability.ttl" \
  --input "${ROOT_DIR}/model/eska-service.ttl" \
  --input "${ROOT_DIR}/model/eska-agent.ttl" \
  --input "${HERE}/pizza-validation-capability.ttl" \
  --input "${HERE}/pizza-validation-service.ttl" \
  --input "${HERE}/pizza-validation-agent.ttl" \
  --output "${RESULTS_DIR}/architecture-model.owl"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/architecture-model.owl" \
  --queries "${HERE}/verify-validation-service.sparql" \
  --output-dir "${VERIFY_DIR}"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/architecture-model.owl" \
  --queries "${HERE}/verify-validation-agent.sparql" \
  --output-dir "${VERIFY_DIR}"

python3 "${HERE}/service.py" \
  --host 127.0.0.1 \
  --port "${PORT}" \
  --shapes "${DOMAIN_DIR}/shapes.ttl" \
  >"${WORK_DIR}/validation-service.log" 2>&1 &
SERVICE_PID=$!
trap 'kill "${SERVICE_PID}" 2>/dev/null || true' EXIT

for _ in $(seq 1 50); do
  if curl --fail --silent "${BASE_URL}/health" >/dev/null; then
    break
  fi
  sleep 0.1
done
curl --fail --silent "${BASE_URL}/health" >/dev/null

run_agent() {
  local name="$1"
  local input="$2"
  python3 "${HERE}/agent.py" \
    --robot-jar "${ROBOT_JAR}" \
    --architecture "${RESULTS_DIR}/architecture-model.owl" \
    --query "${HERE}/discover-service.sparql" \
    --service-base-url "${BASE_URL}" \
    --input "${input}" \
    --output "${RESULTS_DIR}/${name}-agent-result.json" \
    --provenance "${RESULTS_DIR}/${name}-agent-provenance.ttl"
}

run_agent valid "${DOMAIN_DIR}/valid-data.ttl"
run_agent invalid "${DOMAIN_DIR}/invalid-data.ttl"

python3 - "${RESULTS_DIR}" <<'PY'
import json
from pathlib import Path
import sys
from rdflib import Graph, Namespace, RDF

results = Path(sys.argv[1])
expected = {
    "valid": (True, 0),
    "invalid": (False, 1),
}
ESKA = Namespace("urn:eska:core:")
PROV = Namespace("http://www.w3.org/ns/prov#")
SH = Namespace("http://www.w3.org/ns/shacl#")
RUN = Namespace("urn:eska:example:pizza:validation-agent-run:")

for name, (expected_conforms, min_violations) in expected.items():
    result = json.loads((results / f"{name}-agent-result.json").read_text(encoding="utf-8"))
    assert result["agent"] == "urn:eska:example:pizza:validation-agent:PizzaValidationAgent"
    assert result["targetCapability"] == "urn:eska:example:pizza:validation:PizzaValidationCapability"
    assert result["discovery"]["service"] == "urn:eska:example:pizza:validation-service:PizzaValidationService"
    assert result["discovery"]["operation"] == "urn:eska:example:pizza:validation-service:ValidatePizzaDataOperation"
    assert result["discovery"]["method"] == "POST"
    assert result["discovery"]["path"] == "/validate"
    assert result["discovery"]["outputType"] == "http://www.w3.org/ns/shacl#ValidationReport"
    assert result["semanticResult"]["relation"] == "http://www.w3.org/ns/shacl#conforms"
    assert result["semanticResult"]["conforms"] is expected_conforms
    assert result["semanticResult"]["validationResultCount"] >= min_violations

    graph = Graph().parse(results / f"{name}-agent-provenance.ttl", format="turtle")
    execution = RUN.knowledge_agent_invocation
    report = RUN.validation_report
    verification = RUN.validation_report_verification
    assert (execution, RDF.type, ESKA.Execution) in graph
    assert (execution, ESKA.executesCapability, Namespace("urn:eska:example:pizza:validation:").PizzaValidationCapability) in graph
    assert (execution, ESKA.generatesResult, report) in graph
    assert (report, RDF.type, ESKA.Result) in graph
    assert (report, RDF.type, SH.ValidationReport) in graph
    assert (verification, RDF.type, ESKA.Verification) in graph
    assert (verification, ESKA.verifiesExecution, execution) in graph
    assert (verification, ESKA.verifiesResult, report) in graph
PY

printf '\nSUCCESS: Pizza Validation Agent discovered and invoked PizzaValidationCapability for conforming and non-conforming RDF.\n'
printf 'Architecture: %s\n' "${RESULTS_DIR}/architecture-model.owl"
printf 'Valid result: %s\n' "${RESULTS_DIR}/valid-agent-result.json"
printf 'Invalid result: %s\n' "${RESULTS_DIR}/invalid-agent-result.json"
