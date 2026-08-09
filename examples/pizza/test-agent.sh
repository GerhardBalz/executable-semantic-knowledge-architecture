#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-18081}"
BASE_URL="http://127.0.0.1:${PORT}"
INPUT_IRI="http://www.co-ode.org/ontologies/pizza/pizza.owl#AmericanHot"
EXPECTED_IRI="http://www.co-ode.org/ontologies/pizza/pizza.owl#SpicyPizza"
RESULT="${HERE}/results/agent-result.json"
PROVENANCE="${HERE}/results/agent-provenance.ttl"

bash "${HERE}/run.sh"

python3 "${HERE}/service.py" --host 127.0.0.1 --port "${PORT}" \
  >"${HERE}/.work/service.log" 2>&1 &
SERVICE_PID=$!
trap 'kill "${SERVICE_PID}" 2>/dev/null || true' EXIT

for _ in $(seq 1 50); do
  if curl --fail --silent "${BASE_URL}/health" >/dev/null; then
    break
  fi
  sleep 0.1
done

curl --fail --silent "${BASE_URL}/health" >/dev/null

python3 "${HERE}/agent.py" \
  --robot-jar "${HERE}/.work/robot.jar" \
  --architecture "${HERE}/results/architecture-model.owl" \
  --query "${HERE}/discover-service.sparql" \
  --service-base-url "${BASE_URL}" \
  --input "${INPUT_IRI}" \
  --output "${RESULT}" \
  --provenance "${PROVENANCE}"

python3 - "${RESULT}" "${EXPECTED_IRI}" <<'PY'
import json
from pathlib import Path
import sys

result_path = Path(sys.argv[1])
expected = sys.argv[2]
result = json.loads(result_path.read_text(encoding="utf-8"))

assert result["agent"] == "urn:eska:example:pizza:agent:PizzaKnowledgeAgent"
assert result["targetCapability"] == "urn:eska:example:pizza:capability:PizzaClassificationCapability"
assert result["discovery"]["service"] == "urn:eska:example:pizza:service:PizzaClassificationService"
assert result["discovery"]["operation"] == "urn:eska:example:pizza:service:ClassifyPizzaClassOperation"
assert result["discovery"]["method"] == "POST"
assert result["discovery"]["path"] == "/classify"
assert result["semanticResult"]["relation"] == "http://www.w3.org/2000/01/rdf-schema#subClassOf"
assert expected in result["semanticResult"]["classifications"], result
PY

printf '\nSUCCESS: Knowledge Agent discovered and invoked PizzaClassificationCapability.\n'
printf 'Agent result: %s\n' "${RESULT}"
printf 'Provenance:   %s\n' "${PROVENANCE}"
