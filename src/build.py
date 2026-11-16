import re, json, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = open(os.path.join(HERE,'app.html')).read()
OUT = ROOT
s = SRC

def rep(old, new, count=1):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, count)

# --- head : appli installable
rep('<meta name="theme-color" content="#14382f">\n',
    '<meta name="theme-color" content="#14382f">\n'
    '<link rel="manifest" href="manifest.webmanifest">\n'
    '<meta name="apple-mobile-web-app-capable" content="yes">\n'
    '<meta name="mobile-web-app-capable" content="yes">\n'
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
    '<meta name="apple-mobile-web-app-title" content="Plan DCG">\n')
rep('<title>Plan DCG 2027</title>', '<title>Plan DCG</title>')

# --- plein écran : la barre verte passe sous l'heure de l'iPhone
rep('.app{max-width:620px;margin:0 auto;min-height:100%;padding:calc(env(safe-area-inset-top) + 0px) 0 calc(160px + env(safe-area-inset-bottom))}',
    '.app{max-width:620px;margin:0 auto;min-height:100%;padding:0 0 calc(160px + env(safe-area-inset-bottom))}')
rep('.appbar{background:var(--accent-2);color:#eaf4ef;padding:18px 20px 64px;',
    '.appbar{background:var(--accent-2);color:#eaf4ef;padding:calc(18px + env(safe-area-inset-top)) 20px 64px;')
rep('.method p{margin:6px 0 0}',
    '.method p{margin:6px 0 0}\n.sheet ol.steps{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px}\n'
    '.method .gh{display:flex;align-items:center;gap:10px;margin-top:10px;flex-wrap:wrap}\n'
    '.method .gh .dot{width:10px;height:10px;border-radius:50%;background:var(--warn)}\n.method .gh .dot.on{background:var(--accent)}\n'
    'html,body{background:var(--bg)}\nbody{overscroll-behavior-y:none}')

# --- fiche « relier à GitHub »
rep('  if (sheetState.type === "confirm") return renderConfirm(sh);\n',
    '  if (sheetState.type === "confirm") return renderConfirm(sh);\n  if (sheetState.type === "github") return renderGitHub(sh);\n')

# --- carte de sauvegarde dans Méthode
rep('  return [\n    c("Comment ton planning s\'adapte",',
    '  const linked = !!ghToken();\n'
    '  return [\n'
    '    c("Ta sauvegarde",\n'
    '      h("p",null, linked ? "Tes coches sont sauvegardées sur GitHub : je les vois le dimanche et le mardi, et tu ne perds rien si tu changes de téléphone." : "Pour l\'instant, tes coches sont seulement sur ce téléphone. Relie l\'appli à GitHub pour que je voie ta progression le dimanche et le mardi (3 minutes, une seule fois)."),\n'
    '      h("div",{class:"gh"}, h("span",{class:"dot"+(linked?" on":"")}), h("b",null, linked ? "Reliée à ton coach" : "Pas encore reliée"),\n'
    '        h("button",{class:"btn "+(linked?"soft":"primary"),style:"margin-left:auto",onclick:openGitHub}, linked ? "Gérer" : "Relier à GitHub"))),\n'
    '    c("Comment ton planning s\'adapte",')

# --- remplace l'ancienne écriture (base Claude) par la sauvegarde téléphone + GitHub
a = s.index('/* ================= écriture ================= */')
b = s.index('function toggleItem(')
s = s[:a] + '/* ================= écriture : voir « sauvegarde » plus bas ================= */\n' + s[b:]
a = s.index('/* ================= synchronisation ================= */')
b = s.index('/* anciennes coches (version précédente) : on les reprend */')
s = s[:a] + open(os.path.join(HERE,'pwa_store.js')).read() + '\n' + s[b:]

plan = open(os.path.join(ROOT,'plan.json')).read()
assert '</script' not in plan
s = s.replace('__PLAN__', plan)
open(os.path.join(OUT, 'index.html'), 'w').write(s)

# --- weeks (pour le coach), manifeste, service worker
# --- un fichier par semaine (lu par le coach le dimanche et le mardi)
P = json.loads(plan)
os.makedirs(os.path.join(OUT,'weeks'), exist_ok=True)
index = {"weeks": [], "milestones": P["milestones"]}
for w in P["weeks"]:
    ss = [dict(x, items=[{k:v for k,v in it.items() if k != "mod"} for it in x["items"]]) for x in P["sessions"] if x["week"] == w["id"]]
    json.dump({"week": w["id"], "n": w["n"], "phase": w["phase"], "sessions": ss, "milestones": P["milestones"]},
              open(os.path.join(OUT,'weeks',w["id"]+'.json'),'w'), ensure_ascii=False, indent=1)
    index["weeks"].append({"week": w["id"], "n": w["n"], "phase": w["phase"], "days": sorted({x["date"] for x in ss})})
json.dump(index, open(os.path.join(OUT,'weeks','index.json'),'w'), ensure_ascii=False, indent=1)
manifest = {
  "name": "Plan DCG 2027", "short_name": "Plan DCG", "id": "./", "start_url": "./", "scope": "./",
  "display": "standalone", "orientation": "portrait", "background_color": "#14382f", "theme_color": "#14382f", "lang": "fr",
  "description": "Ton planning DCG qui s'adapte. Pas à pas, jusqu'au sommet.",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
json.dump(manifest, open(os.path.join(OUT,'manifest.webmanifest'),'w'), ensure_ascii=False, indent=1)
open(os.path.join(OUT,'.nojekyll'),'w').write('')
print('index.html', len(s))
