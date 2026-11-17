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
stamp = P.get("generated", "2026-11-16").replace("-", "") + "T000000Z"
def write_ics(fname, calname, events):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Plan DCG//FR", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             "X-WR-CALNAME:" + calname, "X-WR-TIMEZONE:Europe/Paris", "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H"]
    for e in sorted(events, key=lambda e: (e["date"], e.get("start", ""))):
        lines += ["BEGIN:VEVENT", "UID:" + e["uid"] + "@plan-dcg", "DTSTAMP:" + stamp, "SUMMARY:" + ics_text(e["sum"])]
        if e.get("start"):
            lines += ["DTSTART:" + ics_dt(e["date"], e["start"]), "DTEND:" + ics_dt(e["date"], e["end"])]
        else:
            lines += ["DTSTART;VALUE=DATE:" + ics_dt(e["date"]), "DTEND;VALUE=DATE:" + ics_dt(next_day(e["date"]))]
        if e.get("transp") or not e.get("start"): lines.append("TRANSP:TRANSPARENT")
        if e.get("desc"): lines.append("DESCRIPTION:" + ics_text(e["desc"]))
        if e.get("alarm"):
            lines += ["BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:" + ics_text(e["sum"]), "TRIGGER:" + e["alarm"], "END:VALARM"]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    open(os.path.join(OUT, fname), "w", newline="").write("\r\n".join(ics_fold(l) for l in lines) + "\r\n")
# Yoel ne veut plus de calendrier Apple : les abonnements restent en ligne mais vides, pour se vider tout seuls sur l'iPhone.
# Les événements servent encore à préparer Google Agenda (src/gagenda.py lit calendrier-source.ics et rappels-source.ics).
write_ics("calendrier-source.ics", "Plan DCG", ev)
write_ics("calendrier.ics", "Plan DCG", [])

# --- rappels de travail (un autre calendrier, « Plan DCG · Rappels ») : une alerte à chaque étape de la journée prévue.
# 2 h avant : Boker tov ; 30 min avant : prépare-toi ; puis chaque début de séance, la pause, la reprise et la fin.
def fh(t):
    hh, mm = map(int, t.split(":"))
    return f"{hh} h" + (f" {mm:02d}" if mm else "")
def add_min(t, m):
    hh, mm = map(int, t.split(":")); x = hh * 60 + mm + m
    return f"{x // 60:02d}:{x % 60:02d}"
def gap(a, b):
    h1, m1 = map(int, a.split(":")); h2, m2 = map(int, b.split(":"))
    return (h2 * 60 + m2) - (h1 * 60 + m1)
NOUN = {"UE1": "le droit", "UE5": "l'économie", "UE7": "le management", "UE8": "le SI", "UE9": "la compta", "UE12": "l'anglais", "UE13": "la communication"}
DE = {"UE1": "de droit", "UE5": "d'économie", "UE7": "de management", "UE8": "de SI", "UE9": "de compta", "UE12": "d'anglais", "UE13": "de communication"}
def what(x):   # ce que tu fais, avec son article : « la compta », « l'examen blanc de droit »…
    u = x.get("ue") or ""
    k = x["kind"]
    if k in ("cours", "exercices", "rapport"): return NOUN.get(u, "ta séance")
    if k == "examen": return "l'examen blanc " + DE.get(u, "")
    if k == "correction": return "la correction de ton examen blanc"
    if k == "reprise": return "la reprise des points faibles"
    if k == "certificat": return "le certificat Studi " + DE.get(u, "")
    if k == "bilan": return "ton bilan de la semaine"
    t = (x.get("title") or "").lower()
    return {"révision de la semaine": "la révision de la semaine", "cartes et fiches": "tes cartes et tes fiches",
            "révision des fiches": "la révision des fiches"}.get(t, "ta révision")
def the(x): return what(x)
def a_(w):     # « à » + article : au SI, à la compta, à l'anglais, à tes fiches
    return "au " + w[3:] if w.startswith("le ") else "aux " + w[4:] if w.startswith("les ") else "à " + w
cap1 = lambda w: w[:1].upper() + w[1:]
rp = []
days = {}
for x in P["sessions"]:
    if x["kind"] != "off": days.setdefault(x["date"], []).append(x)
for d, ss in sorted(days.items()):
    ss.sort(key=lambda x: x["start"])
    first, last = ss[0], ss[-1]
    R = lambda key, t, txt, end=None, desc="": rp.append({"uid": f"r-{d}-{key}", "date": d, "start": t, "end": end or add_min(t, 5),
                                                          "sum": txt, "desc": desc, "alarm": "PT0S", "transp": True})
    R("lever", add_min(first["start"], -120), f"Boker tov ! Debout : on commence à {fh(first['start'])} avec {the(first)}.")
    R("prep", add_min(first["start"], -30), f"Dans 30 min, on commence. Prépare ton bureau, ton café, et éloigne ton téléphone.")
    for i, x in enumerate(ss):
        prev = ss[i - 1] if i else None
        if prev and gap(prev["end"], x["start"]) >= 45:
            R("pause", prev["end"], f"Pause déjeuner, bien mérité. On reprend à {fh(x['start'])} avec {the(x)}.")
        if x["kind"] == "examen":
            txt = f"C'est l'heure : {what(x)}, en conditions réelles. Téléphone dans une autre pièce."
        elif x["kind"] == "bilan":
            txt = "Bilan de la semaine : 10 min pour cocher et écrire ce qui a coincé."
        elif i == 0:
            txt = f"On commence ! {cap1(what(x))} jusqu'à {fh(x['end'])}. Ouvre l'appli."
        elif prev and gap(prev["end"], x["start"]) >= 45:
            txt = f"On reprend ! {cap1(what(x))} jusqu'à {fh(x['end'])}."
        else:
            txt = f"Place {a_(what(x))}, jusqu'à {fh(x['end'])}."
        rp.append({"uid": f"r-{x['id']}", "date": d, "start": x["start"], "end": x["end"], "sum": txt,
                   "desc": " · ".join(i["t"] for i in x["items"] if i.get("k") != "B")[:400], "alarm": "PT0S"})
    R("fin", last["end"], "Journée finie, bravo ! Coche ce que tu as fait dans l'appli.")
for e in rp:   # jamais pendant Shabbat ou Yom Tov, jamais après 20 h
    wd = _dt.date.fromisoformat(e["date"]).weekday()
    assert wd != 5 and e["date"] not in REST and e["start"] >= "06:00" and e["start"] <= "20:00", e
write_ics("rappels-source.ics", "Plan DCG · Rappels", rp)
write_ics("rappels.ics", "Plan DCG · Rappels", [])

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
