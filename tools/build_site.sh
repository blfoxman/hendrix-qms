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
while read -r code name; do
  code=$(echo "$code" | tr -d '[:space:]'); [ -z "$code" ] && continue; case "$code" in \#*) continue;; esac
  echo "$code" | grep -Eq '^[a-z0-9-]{2,40}$' || { echo "bad company code: $code" >&2; exit 1; }
  mkdir -p "$OUT/$code"; cp index.html sw.js $ASSETS "$OUT/$code"/; n=$((n+1))
done < site/companies.txt
# Training Center: the page, its videos, and each company's public sign-in details (the same anon key the app ships with)
mkdir -p "$OUT/training"; cp -r site/training/. "$OUT/training/"
python3 - "$OUT/training/companies.js" <<'PY'
import json, re, sys
app = open('index.html', encoding='utf8').read()
url = re.search(r"^const HX_URL='([^']+)'", app, re.M).group(1); key = re.search(r"^const HX_KEY='([^']+)'", app, re.M).group(1)
out = {}
for line in open('site/companies.txt', encoding='utf8'):
    parts = line.strip().split(None, 1)
    if not parts or parts[0].startswith('#'): continue
    out[parts[0]] = {'name': parts[1].strip() if len(parts) > 1 else parts[0], 'url': url, 'key': key}
open(sys.argv[1], 'w').write('window.HX_COMPANIES=' + json.dumps(out, indent=1) + ';\n')
PY
echo "built $OUT: intro page + $n company platform(s)"
