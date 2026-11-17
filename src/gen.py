import json, datetime as dt, sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from curriculum import CURRICULUM, UE_NAMES, EVENTS

D = dt.date
START = D(2026, 11, 16)
END = D(2027, 5, 23)
EXAM = D(2027, 5, 24)     # début visé des écrits (dates officielles 2027 pas encore publiées)
P1_END = D(2027, 3, 16)   # fin du premier passage (mardi)
P2_END = D(2027, 4, 20)
OFF = {
    D(2027, 3, 23): "Mariage de ton frère : pas de révision.",
    D(2027, 3, 29): "Lundi de Pâques (férié) : repos, ou rattrapage si tu es en retard.",
    D(2027, 5, 17): "Lundi de Pentecôte (férié) : repos, ou rattrapage si tu es en retard.",
}
# Yom Tov : jamais de séance (les mêmes dates que OFF_DATES dans src/app.html)
YOM_TOV = {D(2027, 4, 22): "Pessah", D(2027, 4, 23): "Pessah", D(2027, 4, 28): "Pessah", D(2027, 4, 29): "Pessah",
           D(2027, 6, 11): "Chavouot", D(2027, 6, 12): "Chavouot"}
# tes créneaux : lundi 9 h – 13 h et 14 h – 17 h, mardi 9 h – 13 h et 14 h – 18 h, dimanche 10 h 30 – 15 h 30
WINDOWS = {0: [("09:00", "13:00"), ("14:00", "17:00")], 1: [("09:00", "13:00"), ("14:00", "18:00")], 6: [("10:30", "15:30")]}

def mins(a, b):
    h1, m1 = map(int, a.split(":")); h2, m2 = map(int, b.split(":"))
    return (h2 * 60 + m2) - (h1 * 60 + m1)

P1_TEMPLATE = {
    0: [("09:00", "10:45", "UE9"), ("11:00", "13:00", "UE8"), ("14:00", "15:30", "UE5"), ("15:45", "17:00", "UE1")],
    1: [("09:00", "10:45", "UE9"), ("11:00", "12:15", "UE8"), ("12:15", "13:00", "UE12"), ("14:00", "15:45", "UE7"),
        ("16:00", "17:15", "UE5"), ("17:15", "17:50", "UE12"), ("17:50", "18:00", "BILAN")],
    6: [("10:30", "12:30", "UE13"), ("13:15", "14:15", "REV"), ("14:15", "15:30", "UE9")],
}

# --- dates d'étude
days = []
d = START
while d <= END:
    if d.weekday() in (0, 1, 6) and d not in YOM_TOV:
        days.append(d)
    d += dt.timedelta(days=1)

def week_start(day):
    # semaines dimanche -> mardi ; la semaine 0 commence lundi 16/11
    if day < D(2026, 11, 22):
        return D(2026, 11, 16)
    return day - dt.timedelta(days=(day.weekday() + 1) % 7)

# --- slots de la phase 1
p1_slots = []
for day in days:
    if day > P1_END or day in OFF:
        continue
    for (a, b, ue) in P1_TEMPLATE[day.weekday()]:
        if day == START and a < "14:00":
            continue
        p1_slots.append([day, a, b, ue])

budget = {}
for day, a, b, ue in p1_slots:
    budget[ue] = budget.get(ue, 0) + mins(a, b)

# --- lives et replays Studi rattachés aux leçons (champ "live" de l'élément, affiché sous la leçon)
WD_FR = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
def fdate(iso):
    d = D.fromisoformat(iso)
    return f"{WD_FR[d.weekday()]} {d.day:02d}/{d.month:02d}"
def fh(t):
    h, m = map(int, t.split(":"))
    return f"{h} h" + (f" {m:02d}" if m else "")
def is_late(e):
    return e.get("fin", e.get("debut", "")) > "20:00"
HINTS = {}
for e in EVENTS:
    if e.get("type") not in ("live", "replay"):
        continue
    if e["type"] == "replay":
        txt = f"Replay du {fdate(e['date'])} (Studi > Lives > Replays)"
    elif is_late(e):
        txt = f"Replay du live du {fdate(e['date'])} (Studi > Lives)"
    else:
        txt = f"Live le {fdate(e['date'])} à {fh(e['debut'])}, puis en replay (Studi > Lives)"
    for t in e.get("lecons", []):
        HINTS.setdefault((e["ue"], t), []).append(txt)
_used = set()
def hint(ue, t):
    h = HINTS.get((ue, t))
    if h: _used.add((ue, t))
    return " · ".join(h) if h else None

# --- files de contenu
def flatten(ue):
    out = []
    lim = 50 if ue == "UE12" else 95
    for mod, items in CURRICULUM[ue]:
        for (k, t, m) in items:
            lv = hint(ue, t)
            if m > lim and not (ue == "UE13" and k == "T"):
                parts = [{"k": k, "t": t + " (1re partie)", "m": m - m // 2, "mod": mod, "grp": t},
                         {"k": k, "t": t + " (2e partie)", "m": m // 2, "mod": mod, "grp": t}]
            else:
                parts = [{"k": k, "t": t, "m": m, "mod": mod}]
            for x in parts:
                if lv: x["live"] = lv
                out.append(x)
    return out

queues = {ue: flatten(ue) for ue in CURRICULUM}

def trim(ue, avail):
    """Marque des cas en bonus pour tenir dans le budget."""
    q = queues[ue]
    need = sum(i["m"] for i in q)
    if need <= avail:
        return 0
    cas_total = sum(i["m"] for i in q if i["k"] == "C")
    keep_ratio = max(0.0, (avail - (need - cas_total)) / cas_total)
    # par module : garder le 1er cas après chaque groupe de leçons, puis selon le ratio
    by_mod = {}
    for i in q:
        by_mod.setdefault(i["mod"], []).append(i)
    for mod, items in by_mod.items():
        mc = sum(i["m"] for i in items if i["k"] == "C")
        kept, prev, grp_keep = 0, None, {}
        for i in items:
            if i["k"] == "C":
                first_after_lesson = prev in ("L", None)
                if i.get("grp") in grp_keep:      # 2e partie : même sort que la 1re
                    if grp_keep[i["grp"]]: kept += i["m"]
                    else: i["bonus"] = True
                elif (first_after_lesson and kept < max(mc * keep_ratio, 1)) or kept + i["m"] <= mc * keep_ratio:
                    kept += i["m"]
                else:
                    i["bonus"] = True
                if i.get("grp"): grp_keep.setdefault(i["grp"], not i.get("bonus"))
            prev = i["k"]
    return need - sum(i["m"] for i in q if not i.get("bonus"))

# budget réel par UE en phase 1 (le créneau UE13 du dimanche bascule ensuite sur le rattrapage)
avail = dict(budget)
avail["UE1"] = avail["UE1"] + 4 * 120  # dimanches après le rapport UE13
trimmed = {ue: trim(ue, avail.get(ue, 0)) for ue in ["UE9", "UE12"]}

sessions = []

def sid(day, a):
    return day.isoformat() + "-" + a.replace(":", "")

carry = {}
def take(ue, S):
    q = queues[ue]
    got, total, bonus = [], 0, []
    target = S - carry.get(ue, 0)
    while q:
        i = q[0]
        if i.get("bonus"):
            bonus.append(q.pop(0)); continue
        # on remplit jusqu'à la durée du créneau, en reportant l'écart sur la séance suivante
        if total == 0 or total + i["m"] / 2 <= target:
            got.append(q.pop(0)); total += i["m"]
        else:
            break
    carry[ue] = carry.get(ue, 0) + total - S
    # les cas bonus qui suivent immédiatement
    while q and q[0].get("bonus"):
        bonus.append(q.pop(0))
    return got, bonus

def remaining(ue):
    return sum(i["m"] for i in queues[ue] if not i.get("bonus"))

FLEX_ORDER = ["UE1", "UE5", "UE8", "UE9", "UE7", "UE12"]

REV_ITEMS = [
    {"k": "T", "t": "Révise tes cartes Anki de la semaine (15 min)"},
    {"k": "T", "t": "Refais de tête un exercice que tu as raté cette semaine"},
    {"k": "T", "t": "Complète tes fiches : une page par chapitre terminé"},
]
BILAN_ITEMS = [
    {"k": "T", "t": "Coche ce que tu as fini cette semaine dans ton planning"},
    {"k": "T", "t": "Note ce qui t'a posé problème : je t'envoie une notification à 18 h 20 pour en parler"},
]

def module_title(items):
    mods = []
    for i in items:
        if i["mod"] not in mods:
            mods.append(i["mod"])
    if not mods:
        return ""
    return mods[0] if len(mods) == 1 else mods[0].split(" · ")[0] + " → " + mods[-1]

def add(day, a, b, ue, kind, title, items, note=None, extra=None):
    s = {"id": sid(day, a), "date": day.isoformat(), "start": a, "end": b, "ue": ue,
         "kind": kind, "title": title, "items": items, "week": week_start(day).isoformat()}
    if note: s["note"] = note
    if extra: s.update(extra)
    sessions.append(s)

def fill_content(day, a, b, ue):
    S = mins(a, b)
    got, bonus = take(ue, S)
    keep = lambda i, k: dict({"k": k, "t": i["t"], "m": i["m"], "mod": i["mod"]}, **({"live": i["live"]} if i.get("live") else {}))
    items = [keep(i, i["k"]) for i in got]
    items += [keep(i, "B") for i in bonus]
    kinds = {i["k"] for i in got}
    kind = "exercices" if kinds and kinds <= {"A", "C"} else ("rapport" if ue == "UE13" and "T" in kinds and "L" not in kinds else "cours")
    add(day, a, b, ue, kind, module_title(got), items)

# --- Phase 1
for day, a, b, ue in p1_slots:
    if ue == "BILAN":
        add(day, a, b, None, "bilan", "Bilan de la semaine", BILAN_ITEMS); continue
    if ue == "REV":
        add(day, a, b, None, "revision", "Révision de la semaine", REV_ITEMS); continue
    target = ue
    if not [i for i in queues[ue] if not i.get("bonus")]:
        rem = [(remaining(u) / max(budget.get(u, 1), 1), u) for u in FLEX_ORDER if remaining(u) > 0]
        if not rem:
            add(day, a, b, None, "revision", "Révision libre : fiches et exercices bonus", REV_ITEMS); continue
        # priorité au droit (UE1) qui a peu de créneaux, puis à l'UE la plus en retard
        target = "UE1" if remaining("UE1") > 0 else max(rem)[1]
    fill_content(day, a, b, target)

# --- Phases 2 et 3 : examens blancs
DUR = {"UE1": 3, "UE5": 4, "UE7": 4, "UE8": 4, "UE9": 3, "UE12": 3}
MOCKS = {
    D(2027, 3, 22): ("UE1", "Évaluation d'entraînement Studi"), D(2027, 3, 30): ("UE7", "Annale 2025"),
    D(2027, 4, 5): ("UE5", "Annale 2025"), D(2027, 4, 6): ("UE8", "Annale 2025"),
    D(2027, 4, 12): ("UE12", "Annale 2025"), D(2027, 4, 13): ("UE8", "Annale 2026"),
    D(2027, 4, 19): ("UE5", "Annale 2026"), D(2027, 4, 20): ("UE9", "Évaluation d'entraînement 1 Studi"),
    D(2027, 4, 26): ("UE9", "Évaluation d'entraînement 2 Studi"), D(2027, 4, 27): ("UE1", "Annale 2026"),
    D(2027, 5, 2): ("UE12", "Annale 2026"), D(2027, 5, 3): ("UE7", "Annale 2026"),
    D(2027, 5, 4): ("UE9", "Sujet zéro 2027"), D(2027, 5, 9): ("UE1", "Sujet zéro 2027"),
    D(2027, 5, 10): ("UE5", "Sujet zéro 2027"), D(2027, 5, 11): ("UE8", "Sujet zéro 2027"),
    D(2027, 5, 16): ("UE12", "Annale 2024"), D(2027, 5, 18): ("UE7", "Sujet zéro 2027"),
}
# deux certificats par dimanche : 13 h 15 – 14 h 15 et 14 h 15 – 15 h 30
CERTIFS = {D(2027, 3, 21): ["UE7", "UE1"], D(2027, 3, 28): ["UE8", "UE5"], D(2027, 4, 18): ["UE9", "UE12"]}

def hhmm(h, m=0):
    return f"{h:02d}:{m:02d}"

def is_eval(sujet):
    return sujet.startswith("Évaluation")

def mock_items(ue, sujet):
    n = ue[2:]
    if is_eval(sujet):
        first = f"Ouvre « {sujet[:-6]} » sur Studi (onglet Évaluations) et fais-la sur papier"
    elif sujet.startswith("Annale"):
        first = f"Ouvre l'énoncé « {sujet} » : Médiathèque > UE {n} > Corrigés Comptalia – Épreuve nationale du DCG UE{int(n):02d}"
    else:
        first = f"Ouvre le sujet 0 du nouveau programme : Médiathèque > UE {n} > Annales de l'UE {n}"
    return [
        {"k": "T", "t": first},
        {"k": "T", "t": f"Conditions réelles : {DUR[ue]} h chrono, sans cours, téléphone dans une autre pièce"},
        {"k": "T", "t": "Rédige comme le jour J, même si tu bloques sur une question"},
    ]

def correction_items(ue, sujet=""):
    if is_eval(sujet):
        return [
            {"k": "T", "t": "Dépose ta copie sur Studi : un formateur la corrige sous 7 jours"},
            {"k": "T", "t": "Relis ta copie à froid et note les questions où tu as hésité"},
            {"k": "T", "t": "Quand la correction arrive, note-toi sur 20 ici"},
        ]
    if sujet.startswith("Sujet"):
        n = ue[2:]
        return [
            {"k": "T", "t": f"Cherche le corrigé du sujet 0 : Médiathèque > UE {n} > Annales de l'UE {n}"},
            {"k": "T", "t": "Pas de corrigé ? Envoie-moi les photos de ta copie et je te corrige"},
            {"k": "T", "t": "Mets-toi une note sur 20 et liste les chapitres où tu as perdu des points"},
        ]
    return [
        {"k": "T", "t": "Corrige-toi avec le corrigé Comptalia et écoute le commentaire audio"},
        {"k": "T", "t": "Mets-toi une note sur 20 et liste les chapitres où tu as perdu des points"},
        {"k": "T", "t": "Option : envoie-moi les photos de ta copie et je te corrige"},
    ]

def reprise_items(ue, sujet=""):
    if is_eval(sujet):
        return [
            {"k": "T", "t": "Refais avec ton cours les questions où tu as hésité"},
            {"k": "T", "t": "Mets à jour tes fiches sur ces points"},
            {"k": "T", "t": "Quand la correction Studi arrive, refais les questions ratées"},
        ]
    return [
        {"k": "T", "t": "Relis les chapitres où tu as perdu des points et refais leurs applications"},
        {"k": "T", "t": "Refais au propre les questions ratées de l'examen blanc"},
        {"k": "T", "t": "Mets à jour tes fiches et tes cartes Anki"},
    ]

leftover_flag = []
for day in days:
    if day <= P1_END:
        continue
    phase = "Entraînement" if day <= P2_END else "Révisions finales"
    if day in OFF:
        add(day, "09:00", "18:00", None, "off", "Journée off", [], note=OFF[day]); continue
    wd = day.weekday()
    if day in MOCKS:
        ue, sujet = MOCKS[day]
        if wd == 6:
            end = hhmm(10 + DUR[ue], 30)
            add(day, "10:30", end, ue, "examen", f"Examen blanc · {sujet}", mock_items(ue, sujet))
            add(day, hhmm(11 + DUR[ue], 0), "15:30", ue, "correction", "Correction de l'examen blanc", correction_items(ue, sujet))
            continue
        add(day, "09:00", hhmm(9 + DUR[ue]), ue, "examen", f"Examen blanc · {sujet}", mock_items(ue, sujet))
        add(day, "14:00", "15:30", ue, "correction", "Correction de l'examen blanc", correction_items(ue, sujet))
        add(day, "15:45", "17:00" if wd == 0 else "17:45", ue, "reprise", "Reprise des points faibles", reprise_items(ue, sujet))
        if wd == 1:
            add(day, "17:50", "18:00", None, "bilan", "Bilan de la semaine", BILAN_ITEMS)
        continue
    if wd == 6:
        # dimanche sans examen blanc
        leftovers = [u for u in FLEX_ORDER + ["UE13"] if remaining(u) > 0]
        if leftovers and day != END:
            first_mock = {x: min([d for d, (uu, _) in MOCKS.items() if uu == x] or [END]) for x in leftovers}
            u = min(leftovers, key=lambda x: (first_mock[x], -remaining(x)))
            carry[u] = 0
            fill_content(day, "10:30", "12:30", u)
            sessions[-1]["title"] = "Fin du programme · " + sessions[-1]["title"]
            leftover_flag.append((day.isoformat(), u))
        elif day == END:
            add(day, "10:30", "12:30", None, "revision", "Dernière révision, en douceur",
                [{"k": "T", "t": "Relis tes fiches des 2 premières épreuves de la semaine"},
                 {"k": "T", "t": "Prépare ta convocation, ta pièce d'identité, ta calculatrice et tes stylos"},
                 {"k": "T", "t": "Couche-toi tôt : le sommeil fait partie de la révision"}])
            continue
        else:
            add(day, "10:30", "12:30", None, "revision", "Révision des fiches",
                [{"k": "T", "t": "Relis les fiches des 2 UE que tu maîtrises le moins (ta note la plus basse aux examens blancs)"},
                 {"k": "T", "t": "Refais 2 applications de ces UE sans regarder la correction"}])
        cert = lambda a, b, u: add(day, a, b, u, "certificat", "Certificat Studi (QCM)",
            [{"k": "T", "t": f"Passe le certificat Studi de l'{u} (onglet Évaluations) : il est obligatoire pour ton diplôme Studi"},
             {"k": "T", "t": "Relis d'abord tes fiches 10 minutes, puis réponds sans ton cours"}])
        # s'il reste plus de programme que de dimanches libres pour le finir : le créneau de 13 h 15 sert aussi
        later = [x for x in days if x > day and x.weekday() == 6 and x not in MOCKS and x != END]
        left = [u for u in FLEX_ORDER + ["UE13"] if remaining(u) > 0]
        if day in CERTIFS:
            cert("13:15", "14:15", CERTIFS[day][0])
        elif left:
            first_mock = {x: min([d for d, (uu, _) in MOCKS.items() if uu == x] or [END]) for x in left}
            u = min(left, key=lambda x: (first_mock[x], -remaining(x)))
            carry[u] = 0
            fill_content(day, "13:15", "14:15", u)
            sessions[-1]["title"] = "Fin du programme · " + sessions[-1]["title"]
            leftover_flag.append((day.isoformat() + " 13:15", u))
        else:
            add(day, "13:15", "14:15", None, "revision", "Révision de la semaine", REV_ITEMS)
        if day in CERTIFS:
            cert("14:15", "15:30", CERTIFS[day][1])
        else:
            add(day, "14:15", "15:30", None, "revision", "Cartes et fiches",
                [{"k": "T", "t": "Cartes Anki de toutes les UE"}, {"k": "T", "t": "Fiches de l'UE du prochain examen blanc"}])

sessions.sort(key=lambda s: (s["date"], s["start"]))

# --- semaines
weeks = {}
for s in sessions:
    weeks.setdefault(s["week"], []).append(s)

def phase_of(wk):
    d = D.fromisoformat(wk)
    return 1 if d <= D(2027, 3, 14) else (2 if d <= D(2027, 4, 18) else 3)

MILESTONES = [
    {"date": "2027-01-10", "t": "Dépôt des parties 1 et 2 du rapport UE13 et de la fiche de suivi n° 1 sur Studi"},
    {"date": "2027-01-17", "t": "Vérifie l'ouverture des inscriptions DCG sur Cyclades (en 2026 : du 19 janvier au 2 mars)"},
    {"date": "2027-01-26", "t": "Bilan décisif : on garde les 7 UE pour l'inscription, ou on en reporte une ?"},
    {"date": "2027-02-07", "t": "Dépôt de la partie 3 du rapport UE13 et de la fiche de suivi n° 2"},
    {"date": "2027-02-21", "t": "Dépôt du rapport UE13 intégral (limite Studi : fin février)"},
    {"date": "2027-03-16", "t": None},   # calculé plus bas
    {"date": "2027-03-28", "t": "Studi conseille de passer tes certificats avant fin mars. UE9 et UE12 : le 18 avril, quand leur programme est fini."},
    {"date": "2027-04-01", "t": "En avril, Studi propose des examens blancs « Objectif examen ». Envoie-moi leurs dates dès qu'elles sortent."},
    {"date": "2027-04-25", "t": "Si tu as de l'avance : l'évaluation d'entraînement 3 de l'UE9 (Studi > Évaluations)."},
    {"date": "2027-05-24", "t": "Écrits du DCG : en mai et juin (dates officielles à paraître). 48 h avant : convocation et pièce d'identité."},
    {"date": "2027-06-11", "t": "Chavouot (11 et 12 juin) : je vérifie qu'aucune épreuve ne tombe ce jour-là"},
    {"date": "2027-07-01", "t": "Juillet : mariage de ta sœur. Rien n'est prévu, profite !"},
    {"date": "2027-07-08", "t": "Résultats du DCG sur Cyclades (en 2026 : le 9 juillet à 12 h)"},
]

# --- fin du premier passage : ce qui est vraiment fini le 16/03
MOIS = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
last = {u: max(s["date"] for s in sessions if s["ue"] == u and s["kind"] in ("cours", "exercices", "rapport")) for u in CURRICULUM}
late_ues = sorted([u for u in last if last[u] > P1_END.isoformat()], key=lambda u: last[u])
def fday(iso):
    d = D.fromisoformat(iso); return f"{d.day}{'er' if d.day == 1 else ''} {MOIS[d.month]}"
ms16 = next(m for m in MILESTONES if m["date"] == "2027-03-16")
ms16["t"] = "Fin du premier passage : tout le programme est vu une fois" if not late_ues else \
    "Fin du premier passage, sauf " + " et ".join(f"{u} (fin le {fday(last[u])})" for u in late_ues)
# chaque UE finit son programme avant son premier examen blanc
for u in CURRICULUM:
    fm = [d.isoformat() for d, (uu, _) in MOCKS.items() if uu == u]
    if fm and last[u] >= min(fm):
        print(f"ATTENTION {u} : programme fini le {last[u]}, après son premier examen blanc ({min(fm)})")

# --- lives et dates Studi (src/studi) : dans l'agenda, sans toucher aux séances.
# Les replays passés sont rattachés aux leçons (HINTS) ; un live après 20 h devient « replay à regarder ».
def short(t, n=90):
    if len(t) <= n: return t
    cut = t[:n].rsplit(" ", 1)[0].rstrip(" ,;:.+")
    return cut + "…"
warnings = []
for e in sorted(EVENTS, key=lambda e: (e["date"], e.get("debut", ""))):
    if e.get("type") == "replay" or e["date"] < START.isoformat():
        continue
    d = D.fromisoformat(e["date"])
    m = {"date": e["date"], "ue": e["ue"], "kind": e.get("type", "info")}
    if e.get("type") == "live" and is_late(e):
        m["kind"] = "replay"
        m["t"] = "Replay à regarder · " + short(e["titre"])
        m["note"] = f"Live à {fh(e['debut'])} : trop tard pour toi. Regarde le replay un autre jour."
    elif e.get("type") == "live":
        m["t"] = "Live · " + short(e["titre"])
        m["start"], m["end"] = e["debut"], e["fin"]
        clash = [s for s in sessions if s["date"] == e["date"] and s["kind"] != "off" and s["start"] < e["fin"] and e["debut"] < s["end"]]
        m["note"] = "Pendant ta séance : regarde plutôt le replay." if clash else \
                    ("Facultatif. Si tu es au travail, regarde le replay." if d.weekday() in (2, 3, 4) and e["debut"] < "18:00" else
                     "Facultatif. Sinon, regarde le replay.")
    else:
        word = {"devoir": "À rendre", "quiz": "Quiz", "examen_blanc": "Examen blanc Studi", "examen": "Épreuve"}.get(e.get("type"), "À noter")
        m["t"] = e["titre"] if e.get("type") == "info" else word + " · " + short(e["titre"])
        if e.get("debut"): m["start"] = e["debut"]
        if e.get("fin"): m["end"] = e["fin"]
        if e.get("note"): m["note"] = e["note"]
    if m["ue"] is None: del m["ue"]
    MILESTONES.append(m)
    if d.weekday() == 5 or d in YOM_TOV:
        warnings.append(f"{e['date']} {m['t']} : tombe un samedi ou un Yom Tov")
    if m.get("end", "") > "20:00":
        warnings.append(f"{e['date']} {m['t']} : finit après 20 h")
for (ue, t) in HINTS:
    if (ue, t) not in _used:
        warnings.append(f"{ue} : la leçon « {t} » citée par un live n'existe pas")
MILESTONES.sort(key=lambda m: (m["date"], m.get("start", "")))

# --- tes contraintes : on vérifie chaque séance
for s in sessions:
    d = D.fromisoformat(s["date"])
    assert d.weekday() != 5 and d not in YOM_TOV, ("Shabbat ou Yom Tov", s["id"])
    assert s["end"] <= "20:00", ("après 20 h", s["id"])
    if s["kind"] != "off":
        assert any(a <= s["start"] and s["end"] <= b for a, b in WINDOWS[d.weekday()]), ("hors de tes créneaux", s["id"], s["start"], s["end"])

ue_meta = {u: {"name": UE_NAMES[u]} for u in UE_NAMES}

plan = {"generated": "2026-11-16", "start": START.isoformat(), "end": END.isoformat(), "exam": EXAM.isoformat(),
        "ues": ue_meta, "milestones": MILESTONES,
        "weeks": [{"id": wk, "phase": phase_of(wk), "n": i} for i, wk in enumerate(sorted(weeks))],
        "sessions": sessions}
json.dump(plan, open(os.path.join(HERE, "..", "plan.json"), "w"), ensure_ascii=False)

# --- rapport
print("sessions", len(sessions), "weeks", len(weeks))
print("budget P1 (h):", {k: round(v / 60, 1) for k, v in budget.items()})
print("trimmed min:", trimmed)
for ue in CURRICULUM:
    ss = [s for s in sessions if s["ue"] == ue and s["kind"] in ("cours", "exercices", "rapport")]
    print(ue, "fin du programme:", ss[-1]["date"] if ss else None, "séances:", len(ss),
          "reste:", remaining(ue))
print("leftovers:", leftover_flag)
print("événements Studi:", len(EVENTS), "dans l'agenda:", sum(1 for m in MILESTONES if m.get("kind")), "leçons avec live/replay:", len(_used))
for w in warnings: print("ATTENTION", w)
for key in ["Termine les parties 1 et 2", "seconde moitié", "rapport intégral sur Studi"]:
    for s in sessions:
        if any(key in i["t"] for i in s["items"]):
            print(key, "->", s["date"])
