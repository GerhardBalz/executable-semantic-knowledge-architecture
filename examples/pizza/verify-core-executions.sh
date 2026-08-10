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

if [[ ! -f "${RESULTS_DIR}/provenance.ttl" ]]; then
  echo "Classification provenance not found. Run examples/pizza/run.sh first." >&2
  exit 1
fi

if [[ ! -f "${HERE}/validation/results/provenance.ttl" ]]; then
  echo "Validation provenance not found. Run examples/pizza/validation/validate.py first." >&2
  exit 1
fi

if [[ ! -f "${HERE}/rules/results/provenance.ttl" ]]; then
  echo "Rule-evaluation provenance not found. Run examples/pizza/rules/evaluate.py first." >&2
  exit 1
fi

if [[ ! -f "${HERE}/decisions/results/provenance.ttl" ]]; then
  echo "Decision provenance not found. Run examples/pizza/decisions/evaluate.py first." >&2
  exit 1
fi

if [[ ! -f "${HERE}/calculations/results/provenance.ttl" ]]; then
  echo "Calculation provenance not found. Run examples/pizza/calculations/evaluate.py first." >&2
  exit 1
fi

mkdir -p "${RESULTS_DIR}" "${VERIFY_DIR}"
ROBOT=(java -jar "${ROBOT_JAR}")

"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${RESULTS_DIR}/provenance.ttl" \
  --input "${HERE}/validation/results/provenance.ttl" \
  --input "${HERE}/rules/results/provenance.ttl" \
  --input "${HERE}/decisions/results/provenance.ttl" \
  --input "${HERE}/calculations/results/provenance.ttl" \
  --output "${RESULTS_DIR}/core-executions.owl"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/core-executions.owl" \
  --queries "${HERE}/verify-core-executions.sparql" \
  --output-dir "${VERIFY_DIR}"

echo "SUCCESS: reasoning, validation, rule evaluation, decision evaluation, and calculation share the ESKA Execution → Result → Verification core pattern."
