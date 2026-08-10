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
  --input "${ROOT_DIR}/model/eska-service.ttl" \
  --input "${HERE}/pizza-classification-capability.ttl" \
  --input "${HERE}/validation/pizza-validation-capability.ttl" \
  --input "${HERE}/pizza-multi-capability-service.ttl" \
  --output "${RESULTS_DIR}/multi-capability-service-model.owl"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/multi-capability-service-model.owl" \
  --queries "${HERE}/verify-service-generalization.sparql" \
  --output-dir "${VERIFY_DIR}"

printf 'SUCCESS: one KnowledgeService exposes classification + validation through unambiguous ServiceOperation → SemanticCapability bindings.\n'
printf 'Semantic contract: Capability inputType / outputType / producesRelation / requiresCondition\n'
printf 'Access contract:   ServiceOperation → AccessBinding → HTTP/path/media/representation fields\n'
