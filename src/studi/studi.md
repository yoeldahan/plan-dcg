# Studi : ce qu'on sait, ce qui manque

Un fichier par UE : `UE1.json`, `UE5.json`, `UE7.json`, `UE8.json`, `UE9.json`, `UE12.json`, `UE13.json`.
`src/curriculum.py` les lit, puis `python3 src/gen.py` et `python3 src/build.py` refont le plan.

## État au 16/11/2026
- **Programme (modules, leçons, cas, durées)** : relevé sur Studi le 16/11/2026. C'est ce que l'appli utilise.
- **Pas encore relevé** : le calendrier des lives et replays, les devoirs et leurs dates limites, les dates des examens blancs Studi, la liste des e-books, quiz et exercices.
  La fouille de Studi avec Claude in Chrome n'a pas pu se faire : Chrome du PC n'était pas joignable depuis la session.
- **Écrits du DCG 2027** : dates officielles pas encore publiées (arrêté attendu au Bulletin officiel de l'enseignement supérieur). Le plan vise fin mai 2027.

## Épreuves (d'après Studi)
| UE | Matière | Durée | Format |
|---|---|---|---|
| UE1 | Fondamentaux du droit | 3 h | Cas pratiques |
| UE5 | Économie contemporaine | 4 h | Dossier documentaire et question problématisée |
| UE7 | Management des organisations | 4 h | Analyse managériale et question problématisée |
| UE8 | Système d'information de gestion | 4 h | Situations pratiques |
| UE9 | Comptabilité | 3 h | Situations pratiques et exercices |
| UE12 | Anglais des affaires | 3 h | Traduction, synthèse et rédaction |
| UE13 | Communication professionnelle | — | Rapport déposé sur Studi (intégral : fin février), oral en juin |

## Format d'un fichier
```json
{
 "ue": "UE1", "nom": "Fondamentaux du droit", "releve_le": "2026-11-16",
 "epreuve": {"duree_h": 3, "format": "Cas pratiques"},
 "modules": [
  {"titre": "M2 · Rechercher les règles applicables", "elements": [
   {"type": "lecon", "titre": "La règle de droit", "minutes": 45},
   {"type": "application", "titre": "Application : …", "minutes": 45}
  ]}
 ],
 "ressources": [{"type": "ebook", "titre": "E-book UE1", "ou": "Médiathèque > UE1"}],
 "evenements": [
  {"type": "live", "titre": "Live : les contrats", "date": "2027-01-12", "debut": "18:00", "fin": "19:00", "note": "Replay ensuite dans Lives"},
  {"type": "devoir", "titre": "Devoir 1 à rendre", "date": "2027-01-31"},
  {"type": "examen_blanc", "titre": "Examen blanc Objectif examen", "date": "2027-04-10", "debut": "09:00", "fin": "12:00"}
 ],
 "a_verifier": ["…"]
}
```
- `type` d'un élément : `lecon`, `application`, `cas`, `video`, `tache`. `minutes` : la durée indiquée par Studi (sinon 45 pour une leçon, 30 pour un cas).
- `type` d'un événement : `live`, `replay`, `devoir`, `quiz`, `examen_blanc`, `examen`, `info`. `debut` et `fin` sont facultatifs.
- Les événements apparaissent dans l'agenda de l'appli (Aujourd'hui, Semaine, Dates clés). Ils ne changent pas les séances.
- **Attention** : ajouter, enlever ou déplacer un élément du programme décale les coches déjà faites (elles sont rangées par numéro dans `done/<UE>`). Ne touche au programme que pour ce qui n'est pas encore coché, ou préviens Yoel.
