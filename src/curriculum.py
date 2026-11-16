# Programme DCG (parcours Studi « DCG 2026 »), lu dans src/studi/UE*.json (un fichier par UE).
# Pour changer le programme : modifie ces fichiers JSON (voir src/studi/studi.md), puis
#   python3 src/gen.py && python3 src/build.py
# Chaque élément devient (type, titre, minutes) avec le type : L=leçon, A=application/méthodo, C=cas, V=vidéo, T=tâche.
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
STUDI = os.path.join(HERE, "studi")
ORDER = ["UE1", "UE5", "UE7", "UE8", "UE9", "UE12", "UE13"]
TYPES = {"lecon": "L", "application": "A", "cas": "C", "video": "V", "tache": "T"}
DEFAULT_MIN = {"lecon": 45, "application": 45, "cas": 30, "video": 15, "tache": 30}


def load(ue):
    return json.load(open(os.path.join(STUDI, ue + ".json"), encoding="utf-8"))


DATA = {ue: load(ue) for ue in ORDER}
UE_NAMES = {ue: DATA[ue]["nom"] for ue in ORDER}


def modules(ue):
    out = []
    for m in DATA[ue]["modules"]:
        items = []
        for e in m["elements"]:
            t = e["type"]
            if t not in TYPES:
                raise ValueError(f"{ue} · {m['titre']} : type inconnu « {t} »")
            items.append((TYPES[t], e["titre"], int(e.get("minutes") or DEFAULT_MIN[t])))
        out.append((m["titre"], items))
    return out


CURRICULUM = {ue: modules(ue) for ue in ORDER}

# lives, devoirs, examens blancs… : [{"ue", "type", "titre", "date", "debut"?, "fin"?, "note"?}]
EVENTS = [dict(e, ue=e.get("ue") or ue) for ue in ORDER for e in DATA[ue].get("evenements", [])]
