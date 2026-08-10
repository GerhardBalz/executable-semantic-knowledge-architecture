#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${HERE}/../.." && pwd)"
WORK_DIR="${HERE}/.work"
DOMAIN_DIR="${WORK_DIR}/pizza-domain"
RESULTS_DIR="${HERE}/results"
VERIFY_DIR="${RESULTS_DIR}/verification"
SOURCE_CONFIG="${HERE}/pizza-domain-source.json"

ROBOT_VERSION="${ROBOT_VERSION:-1.9.10}"
ROBOT_JAR="${ROBOT_JAR:-${WORK_DIR}/robot.jar}"
ROBOT_URL="https://github.com/ontodev/robot/releases/download/v${ROBOT_VERSION}/robot.jar"

PIZZA_REPOSITORY="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["repository"])' "${SOURCE_CONFIG}")"
PIZZA_COMMIT="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["commit"])' "${SOURCE_CONFIG}")"
PIZZA_REASONING_PATH="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["artifacts"]["reasoning"])' "${SOURCE_CONFIG}")"
PIZZA_MANIFEST_PATH="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["manifest"])' "${SOURCE_CONFIG}")"
PIZZA_REASONING_URL="https://github.com/${PIZZA_REPOSITORY}/blob/${PIZZA_COMMIT}/${PIZZA_REASONING_PATH}"
PIZZA_MANIFEST_URL="https://github.com/${PIZZA_REPOSITORY}/blob/${PIZZA_COMMIT}/${PIZZA_MANIFEST_PATH}"
PIZZA_REASONING_MODULE="${DOMAIN_DIR}/reasoning.ofn"

mkdir -p "${WORK_DIR}" "${RESULTS_DIR}" "${VERIFY_DIR}"
rm -f \
  "${RESULTS_DIR}/reasoned.owl" \
  "${RESULTS_DIR}/explanation.md" \
  "${RESULTS_DIR}/capability-model.owl" \
  "${RESULTS_DIR}/service-model.owl" \
  "${RESULTS_DIR}/architecture-model.owl" \
  "${RESULTS_DIR}/provenance.ttl" \
  "${RESULTS_DIR}/agent-result.json" \
  "${RESULTS_DIR}/agent-provenance.ttl"
rm -f "${VERIFY_DIR}"/* 2>/dev/null || true

printf '\n1/8 Materializing source-owned Pizza semantic artifacts...\n'
python3 "${HERE}/fetch-domain-artifacts.py"
test -s "${PIZZA_REASONING_MODULE}"

if [[ ! -f "${ROBOT_JAR}" ]]; then
  echo "Downloading ROBOT ${ROBOT_VERSION}..."
  curl --fail --location --silent --show-error "${ROBOT_URL}" --output "${ROBOT_JAR}"
fi

ROBOT=(java -jar "${ROBOT_JAR}")

printf '\n2/8 Reasoning with HermiT...\n'
"${ROBOT[@]}" reason \
  --input "${PIZZA_REASONING_MODULE}" \
  --reasoner hermit \
  --include-indirect true \
  --annotate-inferred-axioms true \
  --output "${RESULTS_DIR}/reasoned.owl"

printf '\n3/8 Verifying expected inference...\n'
"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/reasoned.owl" \
  --queries "${HERE}/verify-spicy.sparql" \
  --output-dir "${VERIFY_DIR}"

printf '\n4/8 Explaining the inferred classification...\n'
"${ROBOT[@]}" explain \
  --input "${PIZZA_REASONING_MODULE}" \
  --reasoner hermit \
  --axiom "'American Hot' SubClassOf 'Spicy Pizza'" \
  --explanation "${RESULTS_DIR}/explanation.md"

printf '\n5/8 Verifying the Semantic Capability contract...\n'
"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${ROOT_DIR}/model/eska-capability.ttl" \
  --input "${HERE}/pizza-classification-capability.ttl" \
  --output "${RESULTS_DIR}/capability-model.owl"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/capability-model.owl" \
  --queries "${HERE}/verify-capability.sparql" \
  --output-dir "${VERIFY_DIR}"

printf '\n6/8 Verifying the Knowledge Service contract...\n'
"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${ROOT_DIR}/model/eska-capability.ttl" \
  --input "${ROOT_DIR}/model/eska-service.ttl" \
  --input "${HERE}/pizza-classification-capability.ttl" \
  --input "${HERE}/pizza-classification-service.ttl" \
  --output "${RESULTS_DIR}/service-model.owl"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/service-model.owl" \
  --queries "${HERE}/verify-service.sparql" \
  --output-dir "${VERIFY_DIR}"

printf '\n7/8 Building and verifying the Knowledge Agent architecture...\n'
"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${ROOT_DIR}/model/eska-capability.ttl" \
  --input "${ROOT_DIR}/model/eska-service.ttl" \
  --input "${ROOT_DIR}/model/eska-agent.ttl" \
  --input "${HERE}/pizza-classification-capability.ttl" \
  --input "${HERE}/pizza-classification-service.ttl" \
  --input "${HERE}/pizza-knowledge-agent.ttl" \
  --output "${RESULTS_DIR}/architecture-model.owl"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/architecture-model.owl" \
  --queries "${HERE}/verify-agent.sparql" \
  --output-dir "${VERIFY_DIR}"

printf '\n8/8 Recording semantic reasoning provenance...\n'
EXECUTED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "${RESULTS_DIR}/provenance.ttl" <<EOF
@prefix cap: <urn:eska:example:pizza:capability:> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix eska: <urn:eska:core:> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#> .
@prefix run: <urn:eska:example:pizza:> .

run:spicy-pizza-reasoning a eska:Execution, prov:Activity ;
    dcterms:description "OWL reasoning execution for the ESKA Pizza SpicyPizza example using a commit-pinned, source-owned Pizza semantic artifact."@en ;
    dcterms:conformsTo cap:PizzaClassificationCapability ;
    eska:executesCapability cap:PizzaClassificationCapability ;
    eska:usesSemanticModel cap:SpicyPizzaSemanticModel ;
    eska:usesExecutableArtifact cap:OWLClassificationArtifact ;
    eska:generatesResult run:american-hot-spicy-inference ;
    prov:used run:pizza-reasoning-module ;
    prov:wasAssociatedWith run:robot-hermit ;
    prov:endedAtTime "${EXECUTED_AT}"^^xsd:dateTime ;
    prov:generated run:american-hot-spicy-inference .

run:spicy-pizza-verification a eska:Verification, prov:Activity ;
    dcterms:description "Verification that OWL reasoning over the pinned Pizza semantic artifact produced the expected AmericanHot to SpicyPizza semantic result."@en ;
    eska:verifiesExecution run:spicy-pizza-reasoning ;
    eska:verifiesResult run:american-hot-spicy-inference ;
    prov:used run:american-hot-spicy-inference ;
    prov:used run:spicy-pizza-verification-query ;
    prov:endedAtTime "${EXECUTED_AT}"^^xsd:dateTime .

run:spicy-pizza-verification-query a prov:Entity ;
    dcterms:identifier "examples/pizza/verify-spicy.sparql" .

run:robot-hermit a prov:SoftwareAgent ;
    rdfs:label "ROBOT ${ROBOT_VERSION} with HermiT"@en .

run:pizza-reasoning-module a prov:Entity ;
    dcterms:title "Source-owned Pizza coherent reasoning module"@en ;
    dcterms:identifier "${PIZZA_REASONING_PATH}@${PIZZA_COMMIT}" ;
    dcterms:source <${PIZZA_REASONING_URL}> ;
    dcterms:relation <${PIZZA_MANIFEST_URL}> .

run:american-hot-spicy-inference a eska:Result, prov:Entity, rdf:Statement ;
    rdf:subject pizza:AmericanHot ;
    rdf:predicate rdfs:subClassOf ;
    rdf:object pizza:SpicyPizza ;
    dcterms:description "AmericanHot is inferred to be a subclass of SpicyPizza."@en ;
    prov:wasGeneratedBy run:spicy-pizza-reasoning ;
    prov:wasDerivedFrom run:pizza-reasoning-module .
EOF

printf '\nSUCCESS: semantic reasoning, Capability, Knowledge Service, and Knowledge Agent contracts are verified.\n'
printf 'Pizza source: %s@%s\n' "${PIZZA_REPOSITORY}" "${PIZZA_COMMIT}"
printf 'Inference:    AmericanHot SubClassOf SpicyPizza\n'
printf 'Explanation:  %s\n' "${RESULTS_DIR}/explanation.md"
printf 'Capability:   %s\n' "${HERE}/pizza-classification-capability.ttl"
printf 'Service:      %s\n' "${HERE}/pizza-classification-service.ttl"
printf 'Agent:        %s\n' "${HERE}/pizza-knowledge-agent.ttl"
printf 'Architecture: %s\n' "${RESULTS_DIR}/architecture-model.owl"
printf 'Provenance:   %s\n' "${RESULTS_DIR}/provenance.ttl"
