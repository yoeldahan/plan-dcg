# Studi : ce qu'on sait, ce qui manque

Un fichier par UE : `UE1.json`, `UE5.json`, `UE7.json`, `UE8.json`, `UE9.json`, `UE12.json`, `UE13.json`.
`src/curriculum.py` les lit, puis `python3 src/gen.py` et `python3 src/build.py` refont le plan.

## État au 17/11/2026
- **Relevé Studi du 17/11/2026** (Claude in Chrome, lecture seule) : `releve-2026-11-17.json`, tel quel.
- **Programme** : comparé module par module avec le relevé du 16/11. Tout concorde, sauf deux points corrigés :
  UE9, documents de synthèse : 4 leçons et 4 cas (et non 6 leçons) ; UE13, rapport et soutenance : une 3e leçon.
  Les titres des modules sont maintenant ceux de Studi.
- **Lives** (jusqu'au 22/12/2026) : dans l'agenda de l'appli. Un live qui finit après 20 h devient « replay à regarder ».
  Chaque live et chaque replay est rattaché à sa leçon (`lecons`) : la leçon l'affiche dans l'appli.
- **Lives d'accompagnement DCG (toutes UE)** et rappels communs : `commun.json`.
- **Évaluations** : aucune date limite sur Studi. Elles sont placées dans le plan :
  - évaluation d'entraînement UE1 : examen blanc du 22 mars ; UE9 n° 1 et n° 2 : examens blancs des 20 et 26 avril (après la fin du programme UE9) ; UE9 n° 3 : en plus, si tu as de l'avance ;
  - certificats (QCM, obligatoires) : UE7 et UE1 le 21 mars, UE8 et UE5 le 28 mars (Studi conseille avant fin mars), UE9 et UE12 le 18 avril (après la fin de leur programme), UE13 après le rapport ;
  - UE13 : fiches de suivi n° 1 et n° 2 avec les dépôts du rapport, entraînement à l'oral après le rapport intégral.
- **E-books** : Médiathèque > Parcours > DCG 2026 > UE > Introduction (pas d'e-book pour l'UE13). Les séances d'introduction le disent.
- **Annales** : Médiathèque > UE > Corrigés Comptalia (2020 à 2026, ancien référentiel) ; sujet 0 du nouveau programme dans Annales de l'UE (pas pour l'UE12).
- **Écrits du DCG 2027** : dates pas encore publiées (ni sur Studi, ni au Bulletin officiel). En 2026 : mai et juin, résultats le 9 juillet. Le plan vise le 24 mai.
- **« Promo MAI 2029 »** sur Studi : c'est le rythme Studi sur 3 ans (`periode_studi`), pas ta date d'examen. Ton plan vise la session 2027.
- **À relever plus tard** : les lives de janvier (rappel le 20/12 dans l'appli), les dates des examens blancs « Objectif examen » (avril).

## Épreuves (d'après Studi)
| UE | Matière | Épreuve |
|---|---|---|
| UE1 | Fondamentaux du droit | Écrit 3 h : situations pratiques, commentaire de documents ou questions |
| UE5 | Économie contemporaine | Écrit 4 h : dossier documentaire et question problématisée |
| UE7 | Management des organisations | Écrit 4 h : analyse managériale et question problématisée |
| UE8 | Système d'information de gestion | Écrit 4 h : situations pratiques ou questions |
| UE9 | Comptabilité | Écrit 3 h : situations pratiques, exercices ou questions |
| UE12 | Anglais des affaires | Écrit 3 h : traduction, résumé ou note, rédaction en anglais |
| UE13 | Communication professionnelle | Oral 1 h au plus : soutenance du rapport (dépôts avant fin février) |

## Consignes Studi utiles
- Le certificat Studi (QCM) est obligatoire à la fin de chaque UE. Certaines évaluations ne s'ouvrent qu'après un module terminé.
- Corrections des devoirs : 7 jours après l'affectation d'un formateur.
- Examens : inscription sur Cyclades ; convocation par courrier ; 48 h avant, prépare convocation et pièce d'identité ; pas de téléphone.
- Report de session : seulement par le bouton « Reporter ma session » (onglet Planning).

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
  {"type": "live", "titre": "Les contrats", "date": "2027-01-12", "debut": "18:00", "fin": "19:00", "lecons": ["La validité du contrat"]},
  {"type": "devoir", "titre": "Devoir 1 à rendre", "date": "2027-01-31"},
  {"type": "examen_blanc", "titre": "Examen blanc Objectif examen", "date": "2027-04-10", "debut": "09:00", "fin": "12:00"}
 ],
 "a_verifier": ["…"]
}
```
- `type` d'un élément : `lecon`, `application`, `cas`, `video`, `tache`. `minutes` : la durée indiquée par Studi (sinon 45 pour une leçon, 30 pour un cas).
- `type` d'un événement : `live`, `replay`, `devoir`, `quiz`, `examen_blanc`, `examen`, `info`. `debut` et `fin` sont facultatifs.
  Sans `date`, un événement n'apparaît pas dans l'agenda (il faut le placer dans le plan, dans `gen.py`).
  `lecons` : les titres exacts des leçons concernées ; `gen.py` signale un titre qui n'existe pas.
- Les événements apparaissent dans l'agenda de l'appli (Aujourd'hui, Semaine, Dates clés). Ils ne changent pas les séances.
- **Attention** : ajouter, enlever ou déplacer un élément du programme décale les coches déjà faites (elles sont rangées par numéro dans `done/<UE>`). Ne touche au programme que pour ce qui n'est pas encore coché, ou préviens Yoel.
