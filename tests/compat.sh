#!/usr/bin/env bash
# Vérifie que l'appli écrit exactement les mêmes données pour le coach qu'une version de référence.
# Usage : tests/compat.sh [réf git, par défaut ddcb026 = avant la refonte]
# Les deux versions tournent avec le plan actuel (plan.json) : on compare le code, pas le programme.
# Navigateur : Google Chrome sur Mac, sinon Chromium via Playwright (node).
# Compare computed/schedule, history du jour et les coches, avec les mêmes coches de test.
# Affiche aussi les erreurs de la console.
set -e
cd "$(dirname "$0")/.."
REF=${1:-ddcb026}
PORT=8781
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
python3 src/build.py >/dev/null
git show "$REF:index.html" > tests/.old-index.html
python3 -I - tests/.old-index.html plan.json <<'PY'
import sys
p, plan = sys.argv[1], open(sys.argv[2]).read()
s = open(p).read()
a = s.index('<script type="application/json" id="plan">') + len('<script type="application/json" id="plan">')
b = s.index('</script>', a)
open(p, 'w').write(s[:a] + plan + s[b:])
PY
python3 -m http.server $PORT >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null; rm -f tests/.old-index.html' EXIT
sleep 1
run(){ # $1 = chemin de l'appli, $2 = fichier de sortie
  if [ ! -x "$CHROME" ]; then
    node tests/compat_run.js "http://localhost:$PORT/tests/compat.html?app=$1" "$2"
    return
  fi
  local prof; prof=$(mktemp -d)
  "$CHROME" --headless=new --disable-gpu --user-data-dir="$prof" --enable-logging=stderr --v=0 \
    --virtual-time-budget=20000 --dump-dom "http://localhost:$PORT/tests/compat.html?app=$1" \
    > "$2.dom" 2> "$2.log" || true
  rm -rf "$prof"
  python3 -I -c "import sys,re,html; s=open(sys.argv[1]).read(); m=re.search(r'RESULT (.*?)</pre>', s, re.S); print(html.unescape(m.group(1)) if m else 'NO RESULT')" "$2.dom" > "$2"
  grep -E "CONSOLE|Uncaught" "$2.log" | grep -v -i "service worker\|favicon\|fetching the script" > "$2.err" || true
}
set +e
T=$(mktemp -d)
run "/tests/.old-index.html" "$T/old.json"
run "/index.html" "$T/new.json"
python3 -I - "$T/old.json" "$T/new.json" <<'EOF'
import json, sys
a, b = [open(p).read().strip() for p in sys.argv[1:3]]
if a.startswith('NO') or b.startswith('NO'):
    print('ÉCHEC : pas de résultat', a[:80], b[:80]); sys.exit(1)
A, B = json.loads(a), json.loads(b)
ok = True
for k in ('computed', 'history', 'done'):
    if A.get(k) != B.get(k):
        ok = False; print('DIFFÉRENT :', k)
        sa, sb = json.dumps(A.get(k), ensure_ascii=False, sort_keys=True), json.dumps(B.get(k), ensure_ascii=False, sort_keys=True)
        i = next((i for i in range(min(len(sa), len(sb))) if sa[i] != sb[i]), min(len(sa), len(sb)))
        print('  ancien :', sa[max(0,i-120):i+200]); print('  nouveau:', sb[max(0,i-120):i+200])
newkeys = set(B['keys']) - set(A['keys'])
gone = set(A['keys']) - set(B['keys'])
print('clés ajoutées :', sorted(newkeys) or 'aucune'); print('clés disparues :', sorted(gone) or 'aucune')
if not A.get('computed'): ok = False; print('ÉCHEC : pas de computed/schedule')
else: print('jours calculés :', len(A['computed']['days']), '/', len(B['computed']['days'] if B.get('computed') else []))
print('COMPATIBLE' if ok else 'INCOMPATIBLE')
sys.exit(0 if ok else 1)
EOF
RC=$?
echo "--- console (nouvelle version)"; cat "$T/new.json.err"; echo "---"
exit $RC
