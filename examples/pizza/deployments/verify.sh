#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIZZA_DIR="$(cd "${HERE}/.." && pwd)"
ROOT_DIR="$(cd "${PIZZA_DIR}/../.." && pwd)"
WORK_DIR="${PIZZA_DIR}/.work"
RESULTS_DIR="${HERE}/results"
VERIFY_DIR="${RESULTS_DIR}/verification"
ROBOT_JAR="${ROBOT_JAR:-${WORK_DIR}/robot.jar}"
MODEL="${RESULTS_DIR}/deployment-model.owl"

mkdir -p "${RESULTS_DIR}" "${VERIFY_DIR}"
test -s "${ROBOT_JAR}"
ROBOT=(java -jar "${ROBOT_JAR}")

"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${ROOT_DIR}/model/eska-service.ttl" \
  --input "${ROOT_DIR}/model/eska-deployment.ttl" \
  --input "${PIZZA_DIR}/pizza-classification-capability.ttl" \
  --input "${PIZZA_DIR}/pizza-classification-service.ttl" \
  --input "${PIZZA_DIR}/validation/pizza-validation-capability.ttl" \
  --input "${PIZZA_DIR}/validation/pizza-validation-service.ttl" \
  --input "${HERE}/pizza-deployments.ttl" \
  --output "${MODEL}"

"${ROBOT[@]}" verify \
  --input "${MODEL}" \
  --queries "${HERE}/verify-deployment.sparql" \
  --output-dir "${VERIFY_DIR}"

printf '\nSUCCESS: stable Service contracts remain separate from blue/green runtime deployment bindings.\n'
printf 'Deployment model: %s\n' "${MODEL}"
printf 'Environments:     blue, green\n'
printf 'Services:         PizzaClassificationService, PizzaValidationService\n'
