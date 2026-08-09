#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${HERE}/.work"
RESULTS_DIR="${HERE}/results"
VERIFY_DIR="${RESULTS_DIR}/verification"

ROBOT_VERSION="${ROBOT_VERSION:-1.9.10}"
ROBOT_JAR="${ROBOT_JAR:-${WORK_DIR}/robot.jar}"
ROBOT_URL="https://github.com/ontodev/robot/releases/download/v${ROBOT_VERSION}/robot.jar"

PIZZA_SOURCE="https://github.com/GerhardBalz/pizza-ontology/blob/main/src/ontology/pizza-edit.owl"
PIZZA_SOURCE_BLOB="397492e484de5560f8a7e048ce8999b707d94388"

mkdir -p "${WORK_DIR}" "${RESULTS_DIR}" "${VERIFY_DIR}"
rm -f "${RESULTS_DIR}/reasoned.owl" "${RESULTS_DIR}/explanation.md" "${RESULTS_DIR}/provenance.ttl"
rm -f "${VERIFY_DIR}"/* 2>/dev/null || true

if [[ ! -f "${ROBOT_JAR}" ]]; then
  echo "Downloading ROBOT ${ROBOT_VERSION}..."
  curl --fail --location --silent --show-error "${ROBOT_URL}" --output "${ROBOT_JAR}"
fi

ROBOT=(java -jar "${ROBOT_JAR}")

printf '\n1/4 Reasoning with HermiT...\n'
"${ROBOT[@]}" reason \
  --input "${HERE}/spicy-pizza.ofn" \
  --reasoner hermit \
  --include-indirect true \
  --annotate-inferred-axioms true \
  --output "${RESULTS_DIR}/reasoned.owl"

printf '\n2/4 Verifying expected inference...\n'
"${ROBOT[@]}" verify \
  --input "${RESULTS_DIR}/reasoned.owl" \
  --queries "${HERE}/verify-spicy.sparql" \
  --output-dir "${VERIFY_DIR}"

printf '\n3/4 Explaining the inferred classification...\n'
"${ROBOT[@]}" explain \
  --input "${HERE}/spicy-pizza.ofn" \
  --reasoner hermit \
  --axiom "<http://www.co-ode.org/ontologies/pizza/pizza.owl#AmericanHot> SubClassOf <http://www.co-ode.org/ontologies/pizza/pizza.owl#SpicyPizza>" \
  --explanation "${RESULTS_DIR}/explanation.md"

printf '\n4/4 Recording execution provenance...\n'
EXECUTED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "${RESULTS_DIR}/provenance.ttl" <<EOF
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#> .
@prefix run: <urn:eska:example:pizza:> .

run:spicy-pizza-reasoning a prov:Activity ;
    dcterms:description "OWL reasoning execution for the ESKA Pizza SpicyPizza example"@en ;
    prov:used run:spicy-pizza-slice ;
    prov:wasAssociatedWith run:robot-hermit ;
    prov:endedAtTime "${EXECUTED_AT}"^^xsd:dateTime ;
    prov:generated run:american-hot-spicy-inference .

run:robot-hermit a prov:SoftwareAgent ;
    rdfs:label "ROBOT ${ROBOT_VERSION} with HermiT"@en .

run:spicy-pizza-slice a prov:Entity ;
    dcterms:source <${PIZZA_SOURCE}> ;
    dcterms:identifier "git-blob:${PIZZA_SOURCE_BLOB}" ;
    prov:wasDerivedFrom <${PIZZA_SOURCE}> .

run:american-hot-spicy-inference a prov:Entity, rdf:Statement ;
    rdf:subject pizza:AmericanHot ;
    rdf:predicate rdfs:subClassOf ;
    rdf:object pizza:SpicyPizza ;
    dcterms:description "AmericanHot is inferred to be a subclass of SpicyPizza."@en ;
    prov:wasGeneratedBy run:spicy-pizza-reasoning ;
    prov:wasDerivedFrom run:spicy-pizza-slice .
EOF

printf '\nSUCCESS: inferred and verified AmericanHot SubClassOf SpicyPizza\n'
printf 'Explanation: %s\n' "${RESULTS_DIR}/explanation.md"
printf 'Provenance:  %s\n' "${RESULTS_DIR}/provenance.ttl"
