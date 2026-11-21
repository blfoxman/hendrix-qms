#!/usr/bin/env bash
# Builds hendrixqms.com: the intro page at the root, and each company's Hendrix at /<code>/.
# Usage: tools/build_site.sh [out-dir]   (default _site)
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=${1:-_site}
ASSETS="favicon.svg favicon-32.png favicon-48.png apple-touch-icon.png icon-192.png icon-512.png site.webmanifest og-image.png"
rm -rf "$OUT"; mkdir -p "$OUT"
cp site/index.html site/404.html site/sw.js "$OUT"/
for f in $ASSETS; do cp "$f" "$OUT"/; done
if [ -f CNAME ]; then cp CNAME "$OUT"/; fi
touch "$OUT/.nojekyll"
if [ -d site/media ]; then cp -r site/media "$OUT"/; fi
n=0
while read -r code; do
  code=$(echo "$code" | tr -d '[:space:]'); [ -z "$code" ] && continue; case "$code" in \#*) continue;; esac
  echo "$code" | grep -Eq '^[a-z0-9-]{2,40}$' || { echo "bad company code: $code" >&2; exit 1; }
  mkdir -p "$OUT/$code"; cp index.html sw.js $ASSETS "$OUT/$code"/; n=$((n+1))
done < site/companies.txt
echo "built $OUT: intro page + $n company platform(s)"
