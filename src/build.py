import json, os, re, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = ROOT
s = open(os.path.join(HERE, 'app.html')).read()

def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

# icône de l'onglet : le logo, en data-URI
logo = open(os.path.join(ROOT, 'logo.svg')).read()
logo = re.sub(r'\s*\n\s*', ' ', logo).strip().replace('"', "'")
rep('__FAVICON__', 'data:image/svg+xml,' + urllib.parse.quote(logo, safe=" =:/'.,-()"))

# sauvegarde (ce téléphone + GitHub) et fiche « Relier à GitHub »
rep('/*@@PWA_STORE@@*/', open(os.path.join(HERE, 'pwa_store.js')).read())

plan = open(os.path.join(ROOT, 'plan.json')).read()
assert '</script' not in plan
rep('__PLAN__', plan)
open(os.path.join(OUT, 'index.html'), 'w').write(s)

# --- un fichier par semaine (lu par le coach le dimanche et le mardi)
P = json.loads(plan)
os.makedirs(os.path.join(OUT, 'weeks'), exist_ok=True)
index = {"weeks": [], "milestones": P["milestones"]}
for w in P["weeks"]:
    ss = [dict(x, items=[{k:v for k,v in it.items() if k != "mod"} for it in x["items"]]) for x in P["sessions"] if x["week"] == w["id"]]
    json.dump({"week": w["id"], "n": w["n"], "phase": w["phase"], "sessions": ss, "milestones": P["milestones"]},
              open(os.path.join(OUT, 'weeks', w["id"]+'.json'), 'w'), ensure_ascii=False, indent=1)
    index["weeks"].append({"week": w["id"], "n": w["n"], "phase": w["phase"], "days": sorted({x["date"] for x in ss})})
json.dump(index, open(os.path.join(OUT, 'weeks', 'index.json'), 'w'), ensure_ascii=False, indent=1)

# --- manifeste (couleur : la nuit du ciel)
manifest = {
  "name": "Plan DCG 2027", "short_name": "Plan DCG", "id": "./", "start_url": "./", "scope": "./",
  "display": "standalone", "orientation": "portrait", "background_color": "#141a3f", "theme_color": "#141a3f", "lang": "fr",
  "description": "Ton planning DCG qui s'adapte. Pas à pas, jusqu'au sommet.",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
json.dump(manifest, open(os.path.join(OUT, 'manifest.webmanifest'), 'w'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, '.nojekyll'), 'w').write('')
print('index.html', len(s))
