#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${HERE}/../.." && pwd)"
ROBOT_JAR="${ROBOT_JAR:-${HERE}/.work/robot.jar}"
RESULTS_DIR="${HERE}/results"
VERIFY_DIR="${RESULTS_DIR}/verification"

if [[ ! -f "${ROBOT_JAR}" ]]; then
  echo "ROBOT jar not found at ${ROBOT_JAR}. Run examples/pizza/run.sh first." >&2
  exit 1
fi

for required in \
  "${RESULTS_DIR}/provenance.ttl" \
  "${HERE}/validation/results/provenance.ttl" \
  "${HERE}/rules/results/provenance.ttl" \
  "${HERE}/decisions/results/provenance.ttl" \
  "${HERE}/calculations/results/provenance.ttl" \
  "${HERE}/mappings/results/provenance.ttl" \
  "${HERE}/workflows/results/provenance.ttl" \
  "${RESULTS_DIR}/general-agent-classification-blue-provenance.ttl" \
  "${RESULTS_DIR}/general-agent-classification-green-provenance.ttl" \
  "${RESULTS_DIR}/general-agent-validation-valid-blue-provenance.ttl" \
  "${RESULTS_DIR}/general-agent-validation-valid-green-provenance.ttl" \
  "${RESULTS_DIR}/general-agent-validation-invalid-green-provenance.ttl"
do
  if [[ ! -f "${required}" ]]; then
    echo "Required execution/invocation provenance not found: ${required}" >&2
    exit 1
  fi
done

mkdir -p "${RESULTS_DIR}" "${VERIFY_DIR}"
ROBOT=(java -jar "${ROBOT_JAR}")

"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${RESULTS_DIR}/provenance.ttl" \
  --input "${HERE}/validation/results/provenance.ttl" \
  --input "${HERE}/rules/results/provenance.ttl" \
  --input "${HERE}/decisions/results/provenance.ttl" \
  --input "${HERE}/calculations/results/provenance.ttl" \
  --input "${HERE}/mappings/results/provenance.ttl" \
  --input "${HERE}/workflows/results/provenance.ttl" \
  --output "${RESULTS_DIR}/core-executions.owl"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/core-executions.owl" \
  --queries "${HERE}/verify-core-executions.sparql" \
  --output-dir "${VERIFY_DIR}"

echo "SUCCESS: reasoning, validation, rule evaluation, decision evaluation, calculation, mapping, and workflow share the ESKA Execution → Result → Verification core pattern across 16 concrete executions."

printf '\nVerifying provenance, evidence, and Result lineage profiles...\n'
python3 "${HERE}/verify-provenance-lineage.py"
