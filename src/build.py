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

# --- calendrier à ajouter dans l'iPhone : ce qui a une date fixe (lives, examens blancs, certificats, dates limites).
# Les séances de cours n'y sont pas : elles bougent avec ce que tu coches (elles restent dans l'appli).
def ics_text(t):
    return str(t).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
def ics_fold(line):
    out, b = [], line.encode("utf-8")
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80: cut -= 1   # ne coupe pas un caractère en deux
        out.append(b[:cut].decode("utf-8")); b = b[cut:]
    out.append(b.decode("utf-8"))
    return "\r\n ".join(out)
def ics_dt(date, hm=None):
    return date.replace("-", "") + ("T" + hm.replace(":", "") + "00" if hm else "")
def next_day(date):
    import datetime
    return (datetime.date.fromisoformat(date) + datetime.timedelta(days=1)).isoformat()
UEN = {"UE1": "Droit", "UE5": "Économie", "UE7": "Management", "UE8": "SI", "UE9": "Compta", "UE12": "Anglais", "UE13": "Communication"}
import datetime as _dt
REST = set(P.get("yomtov", []))
def after_rest(date):   # la veille est Shabbat ou Yom Tov : le rappel se fait le jour même, le matin
    d = _dt.date.fromisoformat(date) - _dt.timedelta(days=1)
    return d.weekday() == 5 or d.isoformat() in REST
ev = []
for m in P["milestones"]:
    who = (m["ue"] + " " + UEN.get(m["ue"], "") + " · ") if m.get("ue") else ""
    e = {"uid": m["id"], "sum": who + m["t"], "desc": m.get("note", ""), "date": m["date"]}
    if m.get("start"):
        e.update(start=m["start"], end=m.get("end") or m["start"], alarm=None if m.get("clash") else "-PT30M")
    else:
        e["alarm"] = ("PT8H" if after_rest(m["date"]) else "-PT6H") if m.get("todo") else None   # la veille à 18 h, ou le jour même à 8 h
    ev.append(e)
for x in P["sessions"]:
    if x["kind"] in ("examen", "certificat", "off"):
        lab = {"examen": x["title"], "certificat": "Certificat Studi (QCM)", "off": x.get("note") or "Journée off"}[x["kind"]]
        who = (x["ue"] + " " + UEN.get(x["ue"], "") + " · ") if x.get("ue") else ""
        e = {"uid": "s-" + x["id"], "sum": who + lab, "desc": " · ".join(i["t"] for i in x["items"]), "date": x["date"]}
        if x["kind"] != "off": e.update(start=x["start"], end=x["end"], alarm="-PT2H" if after_rest(x["date"]) else "-PT12H")
        ev.append(e)
lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Plan DCG//FR", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
         "X-WR-CALNAME:Plan DCG", "X-WR-TIMEZONE:Europe/Paris", "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H"]
stamp = P.get("generated", "2026-11-16").replace("-", "") + "T000000Z"
for e in sorted(ev, key=lambda e: (e["date"], e.get("start", ""))):
    lines += ["BEGIN:VEVENT", "UID:" + e["uid"] + "@plan-dcg", "DTSTAMP:" + stamp, "SUMMARY:" + ics_text(e["sum"])]
    if e.get("start"):
        lines += ["DTSTART:" + ics_dt(e["date"], e["start"]), "DTEND:" + ics_dt(e["date"], e["end"])]
    else:
        lines += ["DTSTART;VALUE=DATE:" + ics_dt(e["date"]), "DTEND;VALUE=DATE:" + ics_dt(next_day(e["date"])), "TRANSP:TRANSPARENT"]
    if e["desc"]: lines.append("DESCRIPTION:" + ics_text(e["desc"]))
    if e.get("alarm"):
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:" + ics_text(e["sum"]), "TRIGGER:" + e["alarm"], "END:VALARM"]
    lines.append("END:VEVENT")
lines.append("END:VCALENDAR")
open(os.path.join(OUT, "calendrier.ics"), "w", newline="").write("\r\n".join(ics_fold(l) for l in lines) + "\r\n")

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
