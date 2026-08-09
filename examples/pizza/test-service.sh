#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="127.0.0.1"
PORT="${PIZZA_SERVICE_PORT:-18080}"
BASE_URL="http://${HOST}:${PORT}"
AMERICAN_HOT="http://www.co-ode.org/ontologies/pizza/pizza.owl#AmericanHot"
SPICY_PIZZA="http://www.co-ode.org/ontologies/pizza/pizza.owl#SpicyPizza"
CAPABILITY="urn:eska:example:pizza:capability:PizzaClassificationCapability"
SERVICE="urn:eska:example:pizza:service:PizzaClassificationService"

bash "${HERE}/run.sh"

python3 "${HERE}/service.py" --host "${HOST}" --port "${PORT}" >"${HERE}/.work/service.log" 2>&1 &
SERVICE_PID=$!
trap 'kill "${SERVICE_PID}" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  if curl --fail --silent "${BASE_URL}/health" >/dev/null; then
    break
  fi
  sleep 0.2
done

curl --fail --silent "${BASE_URL}/health" >/dev/null

CONTRACT_JSON="$(curl --fail --silent "${BASE_URL}/capabilities/pizza-classification")"
CLASSIFICATION_JSON="$(curl --fail --silent \
  -H 'Content-Type: application/json' \
  -d "{\"class\":\"${AMERICAN_HOT}\"}" \
  "${BASE_URL}/classify")"

CONTRACT_JSON="${CONTRACT_JSON}" \
CLASSIFICATION_JSON="${CLASSIFICATION_JSON}" \
EXPECTED_CAPABILITY="${CAPABILITY}" \
EXPECTED_SERVICE="${SERVICE}" \
EXPECTED_INPUT="${AMERICAN_HOT}" \
EXPECTED_OUTPUT="${SPICY_PIZZA}" \
python3 - <<'PY'
import json
import os

contract = json.loads(os.environ["CONTRACT_JSON"])
result = json.loads(os.environ["CLASSIFICATION_JSON"])
capability = os.environ["EXPECTED_CAPABILITY"]
service = os.environ["EXPECTED_SERVICE"]
input_iri = os.environ["EXPECTED_INPUT"]
output_iri = os.environ["EXPECTED_OUTPUT"]
relation = "http://www.w3.org/2000/01/rdf-schema#subClassOf"

assert contract["service"] == service
assert contract["capability"] == capability
assert contract["method"] == "POST"
assert contract["path"] == "/classify"
assert contract["relation"] == relation

assert result["service"] == service
assert result["capability"] == capability
assert result["input"] == input_iri
assert result["relation"] == relation
assert output_iri in result["classifications"], result
PY

printf '\nSUCCESS: Knowledge Service exposes PizzaClassificationCapability over HTTP.\n'
printf 'Service:    %s\n' "${SERVICE}"
printf 'Capability: %s\n' "${CAPABILITY}"
printf 'Request:    %s\n' "${AMERICAN_HOT}"
printf 'Contains:   %s\n' "${SPICY_PIZZA}"
