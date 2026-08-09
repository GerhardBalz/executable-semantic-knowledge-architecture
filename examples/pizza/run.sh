#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${HERE}/../.." && pwd)"
WORK_DIR="${HERE}/.work"
RESULTS_DIR="${HERE}/results"
VERIFY_DIR="${RESULTS_DIR}/verification"

ROBOT_VERSION="${ROBOT_VERSION:-1.9.10}"
ROBOT_JAR="${ROBOT_JAR:-${WORK_DIR}/robot.jar}"
ROBOT_URL="https://github.com/ontodev/robot/releases/download/v${ROBOT_VERSION}/robot.jar"

PIZZA_SOURCE="https://github.com/GerhardBalz/pizza-ontology/blob/main/src/ontology/pizza-edit.owl"
PIZZA_SOURCE_BLOB="397492e484de5560f8a7e048ce8999b707d94388"

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

if [[ ! -f "${ROBOT_JAR}" ]]; then
  echo "Downloading ROBOT ${ROBOT_VERSION}..."
  curl --fail --location --silent --show-error "${ROBOT_URL}" --output "${ROBOT_JAR}"
fi

ROBOT=(java -jar "${ROBOT_JAR}")

printf '\n1/7 Reasoning with HermiT...\n'
"${ROBOT[@]}" reason \
  --input "${HERE}/spicy-pizza.ofn" \
  --reasoner hermit \
  --include-indirect true \
  --annotate-inferred-axioms true \
  --output "${RESULTS_DIR}/reasoned.owl"

printf '\n2/7 Verifying expected inference...\n'
"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/reasoned.owl" \
  --queries "${HERE}/verify-spicy.sparql" \
  --output-dir "${VERIFY_DIR}"

printf '\n3/7 Explaining the inferred classification...\n'
"${ROBOT[@]}" explain \
  --input "${HERE}/spicy-pizza.ofn" \
  --reasoner hermit \
  --axiom "'American Hot' SubClassOf 'Spicy Pizza'" \
  --explanation "${RESULTS_DIR}/explanation.md"

printf '\n4/7 Verifying the Semantic Capability contract...\n'
"${ROBOT[@]}" merge \
  --input "${ROOT_DIR}/model/eska-core.ttl" \
  --input "${ROOT_DIR}/model/eska-capability.ttl" \
  --input "${HERE}/pizza-classification-capability.ttl" \
  --output "${RESULTS_DIR}/capability-model.owl"

"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/capability-model.owl" \
  --queries "${HERE}/verify-capability.sparql" \
  --output-dir "${VERIFY_DIR}"

printf '\n5/7 Verifying the Knowledge Service contract...\n'
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

printf '\n6/7 Building and verifying the Knowledge Agent architecture...\n'
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

printf '\n7/7 Recording semantic reasoning provenance...\n'
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
    dcterms:description "OWL reasoning execution for the ESKA Pizza SpicyPizza example"@en ;
    dcterms:conformsTo cap:PizzaClassificationCapability ;
    eska:executesCapability cap:PizzaClassificationCapability ;
    eska:usesSemanticModel cap:SpicyPizzaSemanticModel ;
    eska:usesExecutableArtifact cap:OWLClassificationArtifact ;
    eska:generatesResult run:american-hot-spicy-inference ;
    prov:used run:spicy-pizza-slice ;
    prov:wasAssociatedWith run:robot-hermit ;
    prov:endedAtTime "${EXECUTED_AT}"^^xsd:dateTime ;
    prov:generated run:american-hot-spicy-inference .

run:spicy-pizza-verification a eska:Verification, prov:Activity ;
    dcterms:description "Verification that OWL reasoning produced the expected AmericanHot to SpicyPizza semantic result."@en ;
    eska:verifiesExecution run:spicy-pizza-reasoning ;
    eska:verifiesResult run:american-hot-spicy-inference ;
    prov:used run:spicy-pizza-verification-query ;
    prov:endedAtTime "${EXECUTED_AT}"^^xsd:dateTime .

run:spicy-pizza-verification-query a prov:Entity ;
    dcterms:identifier "examples/pizza/verify-spicy.sparql" .

run:robot-hermit a prov:SoftwareAgent ;
    rdfs:label "ROBOT ${ROBOT_VERSION} with HermiT"@en .

run:spicy-pizza-slice a prov:Entity ;
    dcterms:source <${PIZZA_SOURCE}> ;
    dcterms:identifier "git-blob:${PIZZA_SOURCE_BLOB}" ;
    prov:wasDerivedFrom <${PIZZA_SOURCE}> .

run:american-hot-spicy-inference a eska:Result, prov:Entity, rdf:Statement ;
    rdf:subject pizza:AmericanHot ;
    rdf:predicate rdfs:subClassOf ;
    rdf:object pizza:SpicyPizza ;
    dcterms:description "AmericanHot is inferred to be a subclass of SpicyPizza."@en ;
    prov:wasGeneratedBy run:spicy-pizza-reasoning ;
    prov:wasDerivedFrom run:spicy-pizza-slice .
EOF

printf '\nSUCCESS: semantic reasoning, Capability, Knowledge Service, and Knowledge Agent contracts are verified.\n'
printf 'Inference:    AmericanHot SubClassOf SpicyPizza\n'
printf 'Explanation:  %s\n' "${RESULTS_DIR}/explanation.md"
printf 'Capability:   %s\n' "${HERE}/pizza-classification-capability.ttl"
printf 'Service:      %s\n' "${HERE}/pizza-classification-service.ttl"
printf 'Agent:        %s\n' "${HERE}/pizza-knowledge-agent.ttl"
printf 'Architecture: %s\n' "${RESULTS_DIR}/architecture-model.owl"
printf 'Provenance:   %s\n' "${RESULTS_DIR}/provenance.ttl"
