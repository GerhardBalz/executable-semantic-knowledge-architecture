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

mkdir -p "${RESULTS_DIR}" "${VERIFY_DIR}"

ROBOT=(java -jar "${ROBOT_JAR}")

"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${ROOT_DIR}/model/eska-capability.ttl" \
  --input "${HERE}/pizza-classification-capability.ttl" \
  --input "${HERE}/validation/pizza-validation-capability.ttl" \
  --output "${RESULTS_DIR}/core-examples.owl"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/core-examples.owl" \
  --queries "${HERE}/verify-core.sparql" \
  --output-dir "${VERIFY_DIR}"

echo "SUCCESS: reasoning and validation satisfy the same ESKA core Capability abstraction."
