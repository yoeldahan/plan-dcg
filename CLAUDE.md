# Plan DCG 2027 : consignes pour Claude

Appli de planning de révision du DCG de Yoel (UE1, UE5, UE7, UE8, UE9, UE12 et UE13, session 2027), installée sur son iPhone depuis https://yoeldahan.github.io/plan-dcg/ (GitHub Pages, branche `main`).

## Qui l'utilise
- Yoel révise le lundi (9 h – 13 h, 14 h – 17 h), le mardi (9 h – 13 h, 14 h – 18 h) et le dimanche (10 h 30 – 15 h 30). Mercredi à vendredi : alternance.
- Jamais de séance le samedi (Shabbat) ni pendant Yom Tov (Pessah : 22, 23, 28 et 29 avril 2027 ; Chavouot : 11 et 12 juin 2027).
- Toute l'interface est en français, au tutoiement, avec des phrases courtes et simples : il se perd vite dans les longs textes.

## Où est quoi
- `src/app.html` : toute l'appli (écrans, design, moteur qui replace ce qui n'est pas fait). Le plan y est injecté à la place de `__PLAN__`.
- `src/pwa_store.js` : la sauvegarde (téléphone + GitHub) et la fiche « Relier à GitHub ».
- `src/build.py` : fabrique `index.html` et `weeks/*.json` à partir de `src/` et `plan.json`.
- `src/studi/UE*.json` : le programme Studi (modules, leçons, cas, durées) et les événements (lives, devoirs, examens blancs). Format et état dans `src/studi/studi.md`.
- `src/curriculum.py` lit `src/studi/` ; `src/gen.py` fabrique `plan.json` (créneaux, examens blancs, jalons, événements) et vérifie tes créneaux (rien le samedi, ni pendant Yom Tov, ni après 20 h).
- `calendrier.ics` (fabriqué par `build.py`) : le calendrier à ajouter dans l'iPhone (lives, examens blancs, certificats, dates limites ; jamais de rappel pendant Shabbat ou Yom Tov).
- Onglets : Aujourd'hui, Agenda (semaine ou mois), À faire (jalons `todo` du plan, cochés en `progress/<id>` avec des id stables `ms-…` ou `ev-…`), Progrès (une fiche par matière), Méthode.
- `sw.js` (hors ligne), `manifest.webmanifest`, `icon-*.png`, `logo.svg` : l'appli installable.
- `tests/compat.sh` : vérifie que l'appli écrit pour le coach exactement les mêmes données que la version d'avant la refonte (`computed/schedule`, `history`, `done`). Il doit afficher COMPATIBLE. Il marche sur Mac (Chrome) et sous Linux (Playwright, `tests/compat_run.js`), et fait tourner les deux versions avec le plan actuel.

## Style « Cordée » (refonte de novembre 2026)
- En haut, le ciel de l'aube et la montagne : le drapeau « Toi » monte avec le programme, en passant des camps (0, 25, 50, 75 %, puis « Les écrits »). En dessous, un agenda net façon carnet. Titres en Sora, texte en Inter ; l'or veut dire « fait ».
- À partir de 1 024 px : version ordinateur (menu de côté, fiches en panneau à droite).
- Récompenses, série de jours réussis, mode concentration 25 / 5 et phrases d'encouragement (constante `CHEER` dans `src/app.html`, facile à modifier).
- Série : un jour réussi = toutes les séances prévues cochées le jour même. Samedi, Yom Tov, jours sans séance et journées reportées ne cassent jamais la série.
- L'état d'interface reste sur l'appareil, sous des clés `dcg-ui-*` (jamais `dcg2-`, qui part sur GitHub).

**Ne modifie jamais `index.html` ni `weeks/` à la main.** Modifie `src/`, puis lance `python3 src/build.py`. Si tu changes le programme ou les créneaux : `python3 src/gen.py` puis `python3 src/build.py`.

## Données (branche `data`, à ne pas casser)
- `state.json` : la progression, écrite par l'appli avec la clé GitHub de Yoel. Ne l'écris jamais à la main.
  Format : `{updatedAt, userAt, docs: {"done/<UE>", "progress/<id>", "skips/<id>", "extras/<id>", "scores/<id>", "bilans/<weekId>", "history/<date>", "computed/schedule"}}`.
- `coach.json` : le mot de la semaine (`meta.message`) et les ajustements (`overrides`), écrits par les tâches planifiées du dimanche (9 h 35) et du mardi (18 h 20).
- Ces tâches lisent `computed/schedule` et les clés ci-dessus. Si tu changes ce format, préviens Yoel : leurs consignes devront être mises à jour.

## Avant de pousser
1. `python3 src/build.py`
2. Teste en local : `python3 -m http.server 8765`, puis ouvre la page à 390 px de large, en mode clair et en mode sombre, et à 1 280 px, et vérifie qu'il n'y a aucune erreur dans la console. Lance `tests/compat.sh` : il doit afficher COMPATIBLE.
3. Si tu modifies `sw.js`, change le nom du cache (`V`).
4. Pousse sur `main` : GitHub Pages met l'appli à jour en une minute environ.

Une modification à la fois, et dis à Yoel en deux phrases ce qui a changé.
