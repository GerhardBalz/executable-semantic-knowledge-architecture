#!/usr/bin/env bash
set -euo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="$BASE/build"; rm -rf "$BUILD"; mkdir -p "$BUILD"
fetch_and_check() { local url="$1" expected="$2" out="$3"; curl --fail --location --silent --show-error --output "$out" "$url"; echo "$expected  $out" | sha256sum --check --status; printf 'verified %s  %s\n' "$expected" "$url"; }
fetch_and_check 'http://swat.cse.lehigh.edu/onto/wine.owl' '30da3cd5f8c3df59c83cbc309750292ed83e990157028f044be347b5240d1775' "$BUILD/ontology.owl"
fetch_and_check 'http://swat.cse.lehigh.edu/data/wine-data.owl' 'df22414d20d97937b84bce63665df791720025276350a64fa97e7b37db723b71' "$BUILD/data.owl"
fetch_and_check 'http://swat.cse.lehigh.edu/projects/benchmarks/lwbm/query-spq.html' 'f981639d0257a7a96c2e475902969322b0943ddf0a4b3d5405aeb6eacb9f1428' "$BUILD/query-spq.html"
fetch_and_check 'http://swat.cse.lehigh.edu/projects/benchmarks/lwbm/tkde-4t.gif' '7496ef4db76e91228dac73314227817f10345402a5f55305fa38ce303b520c11' "$BUILD/tkde-4t.gif"
python "$BASE/verify.py" --ontology "$BUILD/ontology.owl" --data "$BUILD/data.owl" --query-page "$BUILD/query-spq.html" --oracle "$BUILD/tkde-4t.gif" --evidence "$BUILD/evidence.json"
