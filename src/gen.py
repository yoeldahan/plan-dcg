import json, datetime as dt, sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from curriculum import CURRICULUM, UE_NAMES

D = dt.date
START = D(2026, 11, 16)
END = D(2027, 5, 23)
P1_END = D(2027, 3, 16)   # fin du premier passage (mardi)
P2_END = D(2027, 4, 20)
OFF = {
    D(2027, 3, 23): "Mariage de ton frère : pas de révision.",
    D(2027, 3, 29): "Lundi de Pâques (férié) : repos, ou rattrapage si tu es en retard.",
    D(2027, 5, 17): "Lundi de Pentecôte (férié) : repos, ou rattrapage si tu es en retard.",
}

def mins(a, b):
    h1, m1 = map(int, a.split(":")); h2, m2 = map(int, b.split(":"))
    return (h2 * 60 + m2) - (h1 * 60 + m1)

P1_TEMPLATE = {
    0: [("09:00", "10:45", "UE9"), ("11:00", "13:00", "UE8"), ("14:00", "15:30", "UE5"), ("15:45", "17:00", "UE1")],
    1: [("09:00", "10:45", "UE9"), ("11:00", "12:15", "UE8"), ("12:15", "13:00", "UE12"), ("14:00", "15:45", "UE7"),
        ("16:00", "17:15", "UE5"), ("17:15", "18:00", "UE12"), ("18:00", "18:10", "BILAN")],
    6: [("10:30", "12:30", "UE13"), ("13:15", "14:15", "REV"), ("14:15", "15:30", "UE9")],
}

# --- dates d'étude
days = []
d = START
while d <= END:
    if d.weekday() in (0, 1, 6):
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

# --- files de contenu
def flatten(ue):
    out = []
    lim = 50 if ue == "UE12" else 95
    for mod, items in CURRICULUM[ue]:
        for (k, t, m) in items:
            if m > lim and not (ue == "UE13" and k == "T"):
                out.append({"k": k, "t": t + " (1re partie)", "m": m - m // 2, "mod": mod})
                out.append({"k": k, "t": t + " (2e partie)", "m": m // 2, "mod": mod})
            else:
                out.append({"k": k, "t": t, "m": m, "mod": mod})
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
        kept, prev = 0, None
        for i in items:
            if i["k"] == "C":
                first_after_lesson = prev in ("L", None)
                if (first_after_lesson and kept < max(mc * keep_ratio, 1)) or kept + i["m"] <= mc * keep_ratio:
                    kept += i["m"]
                else:
                    i["bonus"] = True
            prev = i["k"]
    return need - sum(i["m"] for i in q if not i.get("bonus"))

# budget réel par UE en phase 1 (le créneau UE13 du dimanche bascule ensuite sur le rattrapage)
avail = dict(budget)
avail["UE1"] = avail["UE1"] + 4 * 120  # dimanches après le rapport UE13
trimmed = {ue: trim(ue, avail.get(ue, 0) * 1.05) for ue in ["UE9", "UE12"]}

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
    items = [{"k": i["k"], "t": i["t"], "m": i["m"], "mod": i["mod"]} for i in got]
    items += [{"k": "B", "t": i["t"], "m": i["m"], "mod": i["mod"]} for i in bonus]
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
    D(2027, 3, 22): ("UE1", "Annale 2025"), D(2027, 3, 30): ("UE7", "Annale 2025"),
    D(2027, 4, 5): ("UE5", "Annale 2025"), D(2027, 4, 6): ("UE8", "Annale 2025"),
    D(2027, 4, 12): ("UE12", "Annale 2025"), D(2027, 4, 13): ("UE9", "Annale 2025"),
    D(2027, 4, 19): ("UE5", "Annale 2026"), D(2027, 4, 20): ("UE9", "Annale 2026"),
    D(2027, 4, 26): ("UE8", "Annale 2026"), D(2027, 4, 27): ("UE1", "Annale 2026"),
    D(2027, 5, 2): ("UE12", "Annale 2026"), D(2027, 5, 3): ("UE7", "Annale 2026"),
    D(2027, 5, 4): ("UE9", "Sujet zéro 2027"), D(2027, 5, 9): ("UE1", "Sujet zéro 2027"),
    D(2027, 5, 10): ("UE5", "Sujet zéro 2027"), D(2027, 5, 11): ("UE8", "Sujet zéro 2027"),
    D(2027, 5, 16): ("UE12", "Sujet zéro 2027"), D(2027, 5, 18): ("UE7", "Sujet zéro 2027"),
}
CERTIFS = {D(2027, 3, 21): "UE1", D(2027, 3, 28): "UE7", D(2027, 4, 4): "UE5", D(2027, 4, 11): "UE8",
           D(2027, 4, 18): "UE12", D(2027, 4, 25): "UE9"}

def hhmm(h, m=0):
    return f"{h:02d}:{m:02d}"

def mock_items(ue, sujet):
    src = "dans la Médiathèque : UE > « Corrigés Comptalia – Épreuve nationale du DCG »" if sujet.startswith("Annale") \
        else "officiel du nouveau programme (si Studi ou le site du DCG ne l'a pas, prends l'annale 2024 dans la Médiathèque)"
    return [
        {"k": "T", "t": f"Ouvre l'énoncé « {sujet} » {src}"},
        {"k": "T", "t": f"Conditions réelles : {DUR[ue]} h chrono, sans cours, téléphone dans une autre pièce"},
        {"k": "T", "t": "Rédige comme le jour J, même si tu bloques sur une question"},
    ]

def correction_items(ue):
    return [
        {"k": "T", "t": "Corrige-toi avec le corrigé Comptalia et écoute le commentaire audio"},
        {"k": "T", "t": "Mets-toi une note sur 20 et liste les chapitres où tu as perdu des points"},
        {"k": "T", "t": "Option : envoie-moi les photos de ta copie et je te corrige"},
    ]

def reprise_items(ue):
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
            add(day, hhmm(11 + DUR[ue], 0), "15:30", ue, "correction", "Correction de l'examen blanc", correction_items(ue))
            continue
        add(day, "09:00", hhmm(9 + DUR[ue]), ue, "examen", f"Examen blanc · {sujet}", mock_items(ue, sujet))
        add(day, "14:00", "15:30", ue, "correction", "Correction de l'examen blanc", correction_items(ue))
        add(day, "15:45", "17:00" if wd == 0 else "17:45", ue, "reprise", "Reprise des points faibles", reprise_items(ue))
        if wd == 1:
            add(day, "18:00", "18:10", None, "bilan", "Bilan de la semaine", BILAN_ITEMS)
        continue
    if wd == 6:
        # dimanche sans examen blanc
        leftovers = [u for u in FLEX_ORDER + ["UE13"] if remaining(u) > 0]
        if leftovers and day != END:
            u = max(leftovers, key=remaining)
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
        add(day, "13:15", "14:15", None, "revision", "Révision de la semaine", REV_ITEMS)
        if day in CERTIFS:
            u = CERTIFS[day]
            add(day, "14:15", "15:30", u, "certificat", "Certificat Studi (QCM)",
                [{"k": "T", "t": f"Passe le certificat Studi de l'{u} (Évaluations > DCG 2026) : il est obligatoire pour ton diplôme Studi"}])
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
    {"date": "2027-01-10", "t": "Dépôt des parties 1 et 2 du rapport UE13 sur Studi"},
    {"date": "2027-01-17", "t": "Vérifie l'ouverture des inscriptions DCG sur Cyclades (en 2026 : du 19 janvier au 2 mars)"},
    {"date": "2027-01-26", "t": "Bilan décisif : on garde les 7 UE pour l'inscription, ou on en reporte une ?"},
    {"date": "2027-02-07", "t": "Dépôt de la partie 3 du rapport UE13"},
    {"date": "2027-02-21", "t": "Dépôt du rapport UE13 intégral (limite Studi : fin février)"},
    {"date": "2027-03-16", "t": "Fin du premier passage : tout le programme est vu une fois"},
    {"date": "2027-04-01", "t": "Examens blancs Studi « Objectif examen » en avril : je les intègre dès que tu as les dates"},
    {"date": "2027-05-24", "t": "Écrits du DCG : fin mai à début juin (dates officielles à paraître)"},
    {"date": "2027-06-11", "t": "Chavouot (11 et 12 juin) : je vérifie qu'aucune épreuve ne tombe ce jour-là"},
]

ue_meta = {u: {"name": UE_NAMES[u]} for u in UE_NAMES}

plan = {"generated": "2026-11-16", "start": START.isoformat(), "end": END.isoformat(),
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
for key in ["Termine les parties 1 et 2", "seconde moitié", "rapport intégral sur Studi"]:
    for s in sessions:
        if any(key in i["t"] for i in s["items"]):
            print(key, "->", s["date"])
