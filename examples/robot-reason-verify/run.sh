#!/usr/bin/env bash
set -euo pipefail

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="$BASE/build"
ROBOT_VERSION="1.9.10"
ROBOT_URL="https://github.com/ontodev/robot/releases/download/v${ROBOT_VERSION}/robot.jar"
ROBOT_SHA256="16a73c074f3df359a7338a84b4e0788785fe06117f931bb9796e9619ea776105"
ROBOT_JAR="$BUILD/robot-${ROBOT_VERSION}.jar"
FIXTURE="$BASE/fixture.ttl"
RULE="$BASE/expected-inference.sparql"
REASONED="$BUILD/reasoned.ttl"
SOURCE_VERIFY="$BUILD/source-verification"
REASONED_VERIFY="$BUILD/reasoned-verification"

rm -rf "$BUILD"
mkdir -p "$SOURCE_VERIFY" "$REASONED_VERIFY"

curl --fail --location --silent --show-error \
  --output "$ROBOT_JAR" \
  "$ROBOT_URL"
echo "$ROBOT_SHA256  $ROBOT_JAR" | sha256sum --check --status

echo "ROBOT v${ROBOT_VERSION} checksum verified"

set +e
java -jar "$ROBOT_JAR" verify \
  --input "$FIXTURE" \
  --queries "$RULE" \
  --output-dir "$SOURCE_VERIFY" \
  >"$BUILD/source-verify.log" 2>&1
SOURCE_VERIFY_STATUS=$?
set -e

if [[ "$SOURCE_VERIFY_STATUS" -eq 0 ]]; then
  cat "$BUILD/source-verify.log"
  echo "ERROR: negative control unexpectedly passed on the unreasoned source ontology" >&2
  exit 1
fi

if [[ ! -f "$SOURCE_VERIFY/expected-inference.csv" ]]; then
  cat "$BUILD/source-verify.log"
  echo "ERROR: negative control failed without producing the expected violation CSV" >&2
  exit 1
fi

if ! grep -q "LeafClass" "$SOURCE_VERIFY/expected-inference.csv"; then
  cat "$SOURCE_VERIFY/expected-inference.csv"
  echo "ERROR: negative-control violation does not identify LeafClass" >&2
  exit 1
fi

echo "PASS: negative control fails before reasoning, as expected"

java -jar "$ROBOT_JAR" reason \
  --reasoner ELK \
  --include-indirect true \
  --remove-redundant-subclass-axioms false \
  --input "$FIXTURE" \
  --output "$REASONED"

java -jar "$ROBOT_JAR" verify \
  --input "$REASONED" \
  --queries "$RULE" \
  --output-dir "$REASONED_VERIFY"

cat > "$BUILD/evidence.json" <<EOF
{
  "robotVersion": "${ROBOT_VERSION}",
  "robotSha256": "${ROBOT_SHA256}",
  "negativeControl": "failed-as-expected",
  "reasoning": "completed",
  "reasonedVerification": "passed",
  "expectedInference": "LeafClass rdfs:subClassOf RootClass"
}
EOF

cat "$BUILD/evidence.json"
echo "PASS: ROBOT reason produced a result that satisfies the expected-inference verification"
