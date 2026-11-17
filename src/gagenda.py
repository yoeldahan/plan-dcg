# Prépare les événements à écrire dans Google Agenda (rappels de travail + lives + dates à faire).
# Les rappels identiques d'une semaine à l'autre deviennent un seul événement récurrent (RRULE + EXDATE).
# Usage : python3 src/gagenda.py [date de début, par défaut demain] > gagenda.json
import json, os, re, sys, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = dt.date
start = D.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today() + dt.timedelta(days=1)

def parse_ics(path):
    t = open(path, encoding="utf-8", newline="").read().replace("\r\n ", "").split("\r\n")
    evs, cur = [], None
    for l in t:
        if l == "BEGIN:VEVENT": cur = {}
        elif l == "END:VEVENT": evs.append(cur); cur = None
        elif cur is not None and ":" in l:
            k, v = l.split(":", 1); k = k.split(";")[0]
            v = v.replace("\\,", ",").replace("\\;", ";").replace("\\n", "\n").replace("\\\\", "\\")
            if k in ("DTSTART", "DTEND", "SUMMARY", "DESCRIPTION", "UID", "TRIGGER") and k not in cur: cur[k] = v
    return evs

def when(v):
    return (v[:4] + "-" + v[4:6] + "-" + v[6:8], (v[9:11] + ":" + v[11:13]) if "T" in v else None)

out = []
# 1) rappels de travail : regroupés par (jour de la semaine, heure, texte)
groups = {}
for e in parse_ics(os.path.join(ROOT, "rappels.ics")):
    d, h = when(e["DTSTART"]); _, h2 = when(e["DTEND"])
    if D.fromisoformat(d) < start: continue
    key = (D.fromisoformat(d).weekday(), h, h2, e["SUMMARY"])
    groups.setdefault(key, []).append(d)
for (wd, h, h2, txt), dates in sorted(groups.items(), key=lambda kv: (kv[1][0], kv[0][1])):
    dates.sort()
    first, last = dates[0], dates[-1]
    ev = {"summary": "DCG · " + txt, "start": first + "T" + h + ":00", "end": first + "T" + h2 + ":00", "reminders": [0], "kind": "rappel"}
    if len(dates) > 1:
        allw, x = [], D.fromisoformat(first)
        while x <= D.fromisoformat(last): allw.append(x.isoformat()); x += dt.timedelta(days=7)
        ex = [w for w in allw if w not in dates]
        ev["recurrence"] = ["RRULE:FREQ=WEEKLY;UNTIL=" + last.replace("-", "") + "T235959Z"] + \
            (["EXDATE;TZID=Europe/Paris:" + ",".join(w.replace("-", "") + "T" + h.replace(":", "") + "00" for w in ex)] if ex else [])
        ev["dates"] = len(dates)
    out.append(ev)
# 2) lives, examens blancs, certificats et dates à faire (calendrier.ics)
for e in parse_ics(os.path.join(ROOT, "calendrier.ics")):
    d, h = when(e["DTSTART"]); _, h2 = when(e["DTEND"])
    if D.fromisoformat(d) < start: continue
    if e["UID"].startswith("s-"): continue          # examens blancs et certificats : déjà dans les rappels de travail
    tr = e.get("TRIGGER")
    if h:   # live : rappel 30 min avant (sauf pendant une séance)
        out.append({"summary": "DCG · " + e["SUMMARY"], "start": d + "T" + h + ":00", "end": d + "T" + h2 + ":00",
                    "reminders": [30] if tr else [], "desc": e.get("DESCRIPTION", ""), "kind": "live"})
    elif tr:   # chose à faire : le matin même à 8 h (jamais la veille, pour ne pas sonner pendant Shabbat)
        if "Replay à regarder" in e["SUMMARY"]:   # le replay existe le lendemain du live (jamais un samedi)
            x = D.fromisoformat(d) + dt.timedelta(days=1)
            while x.weekday() == 5: x += dt.timedelta(days=1)
            d = x.isoformat()
        assert D.fromisoformat(d).weekday() != 5
        out.append({"summary": "DCG · À faire : " + e["SUMMARY"], "start": d + "T08:00:00", "end": d + "T08:15:00",
                    "reminders": [0], "desc": e.get("DESCRIPTION", ""), "kind": "todo"})
json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
