# Programme DCG (parcours Studi "DCG 2026") relevé sur la plateforme le 16/11/2026.
# Chaque item : (type, titre, minutes)  type: L=leçon, A=application/méthodo, C=cas, V=vidéo, T=tâche
# Pour les cas, minutes = durée indiquée par Studi (30 si non indiquée).

def L(t, m): return ("L", t, m)
def A(t, m=45): return ("A", t, m)
def C(t, m=30): return ("C", t, m)
def V(t, m): return ("V", t, m)
def T(t, m): return ("T", t, m)

UE_NAMES = {
    "UE1": "Fondamentaux du droit",
    "UE5": "Économie contemporaine",
    "UE7": "Management des organisations",
    "UE8": "Système d'information de gestion",
    "UE9": "Comptabilité",
    "UE12": "Anglais des affaires",
    "UE13": "Communication professionnelle",
}

def ue1():
    l = 45
    return [
        ("Introduction", [T("Survole l'e-book UE1 (sommaire) et le guide de l'épreuve : 3 h, cas pratiques", 20)]),
        ("M2 · Rechercher les règles applicables à la situation du client", [
            L("La règle de droit", l), L("Les différentes sources du droit", l),
            L("La résolution d'un conflit de normes", l),
            A("Application : Rechercher les règles applicables à la situation du client")]),
        ("M3 · Déterminer le mode de résolution adapté à un litige", [
            L("La juridiction compétente dans un litige de droit privé", l),
            L("Les conditions de recevabilité de l'action en justice", l),
            L("L'organisation judiciaire nationale", l),
            L("Les modes de résolution judiciaires et alternatifs des litiges", l),
            A("Application : Déterminer la juridiction et le mode de résolution d'un litige")]),
        ("M4 · Qualifier la personne juridique et ses biens", [
            L("La personne juridique : existence, attributs et capacité", l),
            L("Le patrimoine et la classification des biens", l),
            A("Application : Qualifier la personne juridique et ses biens")]),
        ("M5 · Accompagner un entrepreneur individuel dans son activité", [
            L("L'entrepreneur individuel et le statut du commerçant", l),
            L("Les types d'entrepreneurs et les conditions d'exercice d'une activité indépendante", l),
            L("Le statut du conjoint de l'entrepreneur et le régime juridique du couple", l),
            L("Les formalités de création d'une entreprise individuelle", l),
            A("Application : Accompagner un entrepreneur individuel")]),
        ("M6 · Déterminer l'étendue du droit d'une personne sur ses biens", [
            L("Le droit de propriété : prérogatives et limites", l),
            L("La protection par le brevet et la marque", l),
            L("La protection par le droit d'auteur", l),
            A("Application : Déterminer l'étendue du droit d'une personne sur ses biens")]),
        ("M7 · Accompagner le client dans ses relations contractuelles", [
            L("La phase précontractuelle du contrat", l), L("La validité du contrat", l),
            L("La portée d'un engagement contractuel", l), L("Les clauses contractuelles", l),
            L("Les sanctions de l'inexécution du contrat", l),
            A("Application : Accompagner le client dans ses relations contractuelles")]),
        ("M8 · Accompagner le client dans ses contrats courants", [
            L("Les contrats de vente, d'entreprise et de consommation", l),
            C("Cas Mme D contre Mme K", 90),
            L("La protection des parties pour chacun des contrats", l),
            L("Le choix d'une sûreté et ses principaux effets", l),
            A("Application : Accompagner le client dans ses contrats courants")]),
        ("M9 · Mesurer les conséquences des responsabilités civiles", [
            L("Responsabilité civile et responsabilité pénale", l),
            L("Mise en œuvre de la responsabilité civile et causes d'exonération", l),
            L("Produits défectueux et responsabilité environnementale", l),
            A("Application : Apprécier les conséquences des responsabilités civiles")]),
        ("M10 · Établir la preuve des droits", [
            L("La preuve des droits", l), A("Application : Établir la preuve des droits")]),
    ]

def ue5():
    l = 50
    return [
        ("Introduction", [T("Survole l'e-book UE5 et la méthode de l'épreuve : dossier documentaire + question problématisée (4 h)", 30)]),
        ("M2 · Appréhender les fondements de la science économique", [
            L("Ressources rares et besoins illimités", l), L("Les relations entre les agents économiques", l),
            L("La répartition primaire des revenus et la valeur ajoutée", l),
            L("L'histoire des principaux faits économiques", l),
            L("Tertiarisation de l'économie et désindustrialisation", l),
            A("Application : Les fondements de la science économique")]),
        ("M3 · Comprendre le fonctionnement des marchés", [
            L("Économie de marché et libéralisme économique", l), L("Les dynamiques des marchés concurrentiels", l),
            L("Le marché : rôle et fonctionnement", l), L("Les défaillances du marché", l),
            L("Les monopoles", l), L("Les oligopoles et la concurrence monopolistique", l),
            L("La régulation des marchés et de la concurrence", l),
            A("Application : Le fonctionnement des marchés")]),
        ("M4 · Financer l'activité économique", [
            L("Besoins et capacités de financement par agent", l), L("L'épargne des ménages", l),
            L("Les déterminants de l'investissement des entreprises", l),
            L("Les modalités de financement de l'investissement", l),
            L("La monnaie et le rôle des banques", l), L("Les différents marchés de capitaux", l),
            A("Application : Financer l'activité économique")]),
        ("M5 · Identifier les enjeux de la croissance économique", [
            L("La croissance économique et ses limites", l), L("Croissance : le rôle des facteurs de production", l),
            L("Croissance : le rôle du progrès technique", l), L("Les théories de la croissance endogène", l),
            L("Les moteurs de la croissance", l), L("Le développement durable", l),
            L("Soutenabilité de la croissance et nouvelles logiques économiques", l),
            A("Application : Les enjeux de la croissance")]),
        ("M6 · Analyser la régulation publique", [
            L("Les organes de l'action publique", l), L("Les fonctions économiques et sociales de l'État", l),
            L("Le budget de l'État", l), L("Le déficit public et la dette publique", l),
            L("Objectifs et typologie des politiques économiques", l),
            L("Politique de la demande et politique de l'offre", l),
            L("La politique monétaire européenne", l),
            L("La coordination des politiques conjoncturelles dans la zone euro", l),
            L("Les politiques structurelles nationales et européennes", l),
            A("Application : Analyser la régulation publique")]),
        ("M7 · Les politiques sociales face aux déséquilibres du marché du travail", [
            L("Le marché du travail", l), L("Les indicateurs de l'emploi et du chômage", l),
            L("Chômage classique, keynésien, conjoncturel et structurel", l),
            L("Les effets de la révolution numérique sur l'emploi", l), L("Les politiques de l'emploi", l),
            L("Caractériser et mesurer la pauvreté", l), L("Les différentes formes d'inégalités", l),
            L("Pourquoi et comment lutter contre les inégalités", l), L("Les modèles de protection sociale", l),
            A("Application : Les politiques sociales et le marché du travail")]),
        ("M8 · Les effets et les enjeux de la mondialisation", [
            L("Les transformations du commerce mondial", l), L("La balance des paiements", l),
            L("Les FTN et les IDE", l), L("Le libre-échange", l), L("Les théories et pratiques protectionnistes", l),
            L("Politiques commerciales stratégiques, compétitivité et attractivité", l),
            L("Le débat libre-échange / protectionnisme", l), L("La gouvernance mondiale", l),
            A("Application : Les enjeux de la mondialisation")]),
    ]

def ue7():
    l = 50
    return [
        ("Introduction", [T("Survole l'e-book UE7 et la méthode : analyse managériale + question problématisée (4 h)", 30)]),
        ("M2 · Le contexte et les enjeux du management des organisations", [
            L("Les organisations : buts, objectifs et action collective", l),
            L("La place du management dans la performance", l), L("Les différents profils des décideurs", l),
            L("Les spécificités des différentes organisations", l), L("Les problématiques managériales actuelles", l),
            L("L'environnement actuel des organisations", l), L("Continuité et changements organisationnels", l),
            L("La diversité des gouvernances", l), L("Parties prenantes et RSE", l),
            A("Application : Les enjeux du management des organisations")]),
        ("M3 · Le management stratégique", [
            L("La démarche stratégique", l), L("Les outils d'analyse de l'environnement", l),
            L("Les outils d'analyse interne", l), L("Les stratégies de domaine", l),
            L("Spécialisation et diversification", l), L("Le développement de l'entreprise", l),
            A("Application : Le management stratégique")]),
        ("M4 · Le management organisationnel", [
            L("La place de l'humain dans les pratiques managériales", l), L("Le comportement organisationnel", l),
            L("Conflits, crise et résilience organisationnelle", l), L("La nécessité d'animer une organisation", l),
            L("Les moyens pour animer une organisation", l), L("Les structures classiques", l),
            L("Les théories de la contingence structurelle", l), L("Les configurations de Mintzberg", l),
            L("Les organisations contemporaines", l), A("Application : Le management organisationnel")]),
        ("M5 · Le management opérationnel", [
            L("La fonction marketing", l), L("Les fonctions production et logistique", l),
            L("La recherche et développement", l), L("La fonction ressources humaines", l),
            L("La fonction financière et le contrôle de gestion", l), L("L'analyse de la chaîne de valeur", l),
            L("Le modèle économique Canvas", l), L("Les processus décisionnels", l),
            L("Pouvoir, autorité et leadership", l), A("Application : Le management opérationnel")]),
    ]

def ue8():
    l, p = 45, 55
    m = lambda t: A("Méthodologie DCG UE8 : " + t, 50)
    return [
        ("Introduction", [T("Survole l'e-book UE8 et le guide de l'épreuve : situations pratiques (4 h)", 20)]),
        ("M2 · Le SI dans son environnement : son rôle", [
            L("La qualité de l'information", l), L("Le système d'information (SI)", l),
            L("Les rôles du SI : opérationnel, tactique, stratégique", l),
            L("La nature et le rôle des ressources du SI", l), L("Les composantes et niveaux du SI", l),
            m("discerner le rôle du SI dans les organisations")]),
        ("M3 · Le SI dans son environnement : les acteurs", [
            L("Les acteurs internes : rôles et responsabilités", l), L("Les acteurs externes", l),
            L("Les interactions des gestionnaires du SI avec les utilisateurs", l),
            L("La Direction des systèmes d'information (DSI)", l),
            L("Les interactions de la DSI avec les autres directions", l),
            L("Les compétences numériques attendues des utilisateurs", l), m("identifier les acteurs du SI")]),
        ("M4 · L'infrastructure technique du SI", [
            L("Les moyens d'accès au SI", l), L("La localisation des données et applications", l),
            L("Les serveurs : principes fonctionnels", l), L("Réseaux publics et réseaux privés", l),
            L("Les modalités d'accès et les services réseaux", l), L("Le rôle des protocoles", l),
            m("comprendre l'infrastructure technique")]),
        ("M5 · Les solutions informatiques du SI", [
            L("Solutions standardisées ou développées", l), L("La gestion de projets numériques", l),
            L("L'interopérabilité et les formats d'échange", l), L("Les échanges dématérialisés", l),
            L("Les documents électroniques légaux", l), m("étudier les échanges de données")]),
        ("M6 · Les choix organisationnels liés au SI", [
            L("L'audit du système d'information", l), L("Externaliser ou internaliser le SI", l),
            L("Les impacts de la transition numérique", l), L("Le rôle des ESN", l),
            L("Les contrats de prestations de services", l), m("analyser la dimension organisationnelle du SI")]),
        ("M7 · Structurer et manipuler des données : les bases de données", [
            L("La collecte des données et les dépendances fonctionnelles", p),
            L("Le modèle relationnel et les formes normales", p), L("L'implémentation d'une base de données", p),
            L("Requêtes simples (SQL)", p), L("Requêtes complexes (SQL)", p), L("La mise à jour des données", p),
            m("manipuler les données d'une base")]),
        ("M8 · Traiter des données avec le tableur", [
            L("Introduction à l'usage du tableur", p), L("Fonctions arithmétiques", p),
            L("Fonctions statistiques et logiques", p), L("Fonctions de dénombrement et de dates", p),
            L("Fonctions de recherche", p), L("L'ergonomie de la feuille de calcul", p),
            L("Le tableur, outil d'aide à la décision", p), L("Les cellules de paramètres", p),
            L("L'audit d'une feuille de calcul", p), L("La programmation au service du tableur", p),
            m("maîtriser le tableur")]),
        ("M9 · Le SI et la performance des processus", [
            L("Les processus et leur typologie", l), L("Le diagramme BPMN", l),
            L("Les catégories d'IA et leurs enjeux sur le SI", l), L("Processus et bases de données", l),
            L("Les progiciels au service des processus", l), L("Les technologies émergentes et la performance du SI", l),
            m("étudier les processus")]),
        ("M10 · Les défis du SI : réglementation et durabilité", [
            L("CNIL et obligations du responsable des traitements", l), L("Les droits des personnes", l),
            L("La mise en conformité de l'organisme (RGPD)", l), L("Les aspects réglementaires des logiciels", l),
            m("réglementation et durabilité du SI")]),
        ("M11 · Les défis du SI : la sécurité", [
            L("Sécurité du SI : leçons 1 et 2 du module (voir plateforme)", 2 * l),
            L("Sécurité du SI : leçons 3 et 4 du module", 2 * l),
            L("Sécurité du SI : leçons 5 et 6 du module", 2 * l),
            m("sécurité du SI")]),
    ]

def ue9():
    l = 40
    return [
        ("Introduction", [T("Survole l'e-book UE9 et le guide de l'épreuve : situations pratiques et exercices (3 h)", 20)]),
        ("M2 · Les dimensions de la comptabilité", [
            L("La comptabilité et ses domaines dans une perspective historique", l),
            L("L'objet de la comptabilité et le système d'information comptable", l),
            L("La profession comptable : experts-comptables et commissaires aux comptes", l),
            L("La profession comptable : les comptables salariés", l),
            L("La profession comptable dans le public", l),
            L("La normalisation et la réglementation comptable", l)]),
        ("M3 · Le compte de résultat et le bilan", [
            L("La présentation d'un compte de résultat", l), L("Les charges du compte de résultat (partie 1)", l),
            L("Les charges du compte de résultat (partie 2)", l), L("Les produits du compte de résultat", l),
            C("Cas Vincent", 60), C("Cas Pelat", 30), C("Cas Tachet", 60),
            L("La présentation d'un bilan", l), L("L'actif (partie 1)", l), L("L'actif (partie 2)", l),
            L("Le passif : capitaux propres et autres fonds propres", l), L("Le passif : provisions et dettes", l),
            C("Cas Louis", 20), C("Cas Alpha", 30), C("Cas Gama", 90), C("Cas Dulac", 45),
            C("Cas Lachepaille", 20), C("Cas Léon", 30)]),
        ("M4 · Les mécanismes de la partie double", [
            L("Les écritures comptables", l), C("Cas Z", 45), L("Les enregistrements comptables simples", l),
            L("La présentation de la comptabilisation des opérations", l),
            C("Cas JP", 30), C("Cas Louis 2", 45), C("Cas Malo", 45), C("Cas Piman", 60), C("Cas Roland", 60),
            L("L'établissement d'une balance comptable", l), C("Cas Jacques", 10), C("Cas Pierre", 30),
            L("Une balance comptable à partir d'un exemple concret", l),
            L("Le compte de résultat et le bilan à partir d'une balance", l),
            C("Cas Fargue", 60), C("Cas Luchot", 90), C("Cas DB", 30), C("Cas Tio Pepe", 30)]),
        ("M5 · La TVA : mécanisme et enregistrements", [
            L("Le principe de la TVA", l), L("Déductibilité, fait générateur et exigibilité", l),
            L("Comptabiliser la TVA : biens, et prestations avec option sur les débits", l),
            L("Comptabiliser la TVA : prestations selon le droit commun", l),
            L("Le calcul et la comptabilisation de la TVA à décaisser", l),
            C("Cas Spot"), C("Cas Fox", 30), L("Les arrondis de TVA à décaisser", l), C("Cas Prat"),
            L("Les différents régimes de TVA", l), L("La TVA intracommunautaire", l),
            C("Cas Septfonds", 30), C("Cas Déco"), L("Les importations et exportations", l),
            C("Cas Intraco", 20), C("Cas Paillon"), C("Cas Trillard"), C("Cas Barsac"), C("Cas Oliver"), C("Cas Sigmond"),
            L("Avances et acomptes sur biens", l), L("Avances et acomptes sur prestations et travaux", l),
            C("Cas Novino"), C("Cas Lador", 20), C("Cas Govin", 30)]),
        ("M6 · Établir et enregistrer les factures", [
            L("Les factures « de doit »", l), L("L'enregistrement d'une facture de doit", l),
            L("Frais de port et sous-traitance", l), L("Les factures d'avoir chez les fournisseurs", l),
            L("Les factures d'avoir chez les clients", l),
            C("Cas AB", 15), C("Cas Camille", 30), C("Cas Gustave", 60), C("Cas VM", 30), C("Cas Web", 30),
            L("L'enregistrement des acquisitions d'immobilisations", l),
            C("Cas Clatin", 30), C("Cas Larive", 30), C("Cas Perrouse", 30), C("Cas Vedant", 30)]),
        ("M7 · Les transactions courantes", [
            L("La consignation et la reprise des emballages", l), C("Cas Vallor"),
            L("Si le client ne rend pas les emballages consignés", l), C("Cas Laplace"), C("Cas Dargent"),
            L("Généralités sur les fiches de paie", l), L("Les éléments d'une fiche de paie", l),
            L("La comptabilisation des charges de personnel", l),
            C("Cas Calman", 30), C("Cas ESCA", 30), C("Cas Plassard", 30), C("Cas Trepalet", 30),
            L("Les modes de règlement des créances et des dettes", l), L("La lettre de change relevée (LCR)", l),
            C("Cas Dupuis", 30), C("Cas Golf"), L("L'affacturage", l), C("Cas Despar"), C("Cas Malicorne"),
            L("Les états de rapprochement bancaire", l), L("Les rapprochements bancaires : cas complexes", l),
            C("Cas Champest", 45), C("Cas Platic", 60),
            L("Le suivi des comptes clients", l), L("Le suivi des comptes fournisseurs", l)]),
        ("M8 · Les amortissements", [
            L("Généralités sur les travaux d'inventaire", l), L("La notion d'amortissement", l),
            L("La terminologie des amortissements", l), L("Le plan d'amortissement linéaire", l),
            C("Cas Jacson", 30), C("Cas Robert", 15), C("Cas David", 20), C("Cas Marchand", 20),
            L("Le plan d'amortissement par unités d'œuvre", l), C("Cas Palin", 45),
            L("La comptabilisation des amortissements", l), C("Cas Balgue", 45), C("Cas Damien", 30), C("Cas Sirtex", 30)]),
        ("M9 · Les dépréciations et les provisions", [
            L("Dépréciations et provisions : définition et enregistrement", l),
            L("La dépréciation des immobilisations corporelles", l), C("Cas Cador", 30),
            L("Les créances douteuses et irrécouvrables", l), L("La procédure des créances douteuses", l),
            L("Application concernant les créances douteuses", l),
            C("Cas Missou", 30), C("Cas Tertio", 45), C("Cas Sardi", 45), C("Cas Carmot", 45),
            L("Les provisions pour risques et charges et réglementées", l), C("Cas Rousseau", 5), C("Cas Rendon", 5),
            L("Les titres et leurs revenus", l), L("Les dépréciations des titres", l),
            C("Cas Bissont", 20), C("Cas Morteau", 20)]),
        ("M10 · Les cessions d'immobilisations et de VMP", [
            L("Les écritures de cession d'immobilisations", l), L("Les cessions d'immobilisations en pratique", l),
            L("Les cessions de titres immobilisés", l), L("Les cessions de VMP", l), L("Synthèse des cessions de titres", l),
            C("Cas Lazare"), C("Cas Revel"), C("Cas Houffard", 60), C("Cas Terron", 75), C("Cas Manuel", 25)]),
        ("M11 · Les autres opérations d'inventaire", [
            L("Les variations de stocks : généralités", l), L("Les écritures de variation de stocks", l),
            C("Cas Lacroix", 20), C("Cas Marcel", 20), C("Cas Romain", 20), C("Cas Norbert", 25),
            L("Charges à payer et produits à recevoir", l), L("Charges et produits constatés d'avance", l),
            C("Cas Memoranda", 20), C("Cas Trésorus", 20), C("Cas Limont", 30), C("Cas Grivas", 20), C("Cas Belin", 20),
            L("Emprunts in fine et par amortissements constants", l), L("Emprunts par annuités constantes", l),
            L("Comptabiliser un emprunt : cas simple", l), L("Comptabiliser un emprunt : cas complexe", l),
            C("Cas Carnon", 30), C("Cas Pastor", 30), C("Cas Tarina", 30), C("Cas Volpone", 30),
            L("Les logiciels", l), L("Subventions et livraisons à soi-même", l),
            C("Cas Reval"), C("Cas Dumoulin"), C("Cas Maxard"),
            L("Indemnités d'assurance et crédit-bail", l), C("Cas Laborde", 60), C("Cas Lepic", 60),
            L("La comptabilisation de l'impôt sur les sociétés", l), C("Cas Bartin", 60),
            L("L'établissement des comptes annuels", l), C("Cas Prisson", 45), C("Cas Valentin", 120),
            C("Cas Prochiffra", 90), C("Cas Velopassion", 60)]),
        ("M12 · Les documents de synthèse", [
            L("Documents de synthèse : leçons 1 à 3 du module (voir plateforme)", 3 * l),
            L("Documents de synthèse : leçons 4 à 6 du module", 3 * l),
            C("Documents de synthèse : applications du module", 90)]),
        ("M13 · L'environnement numérique de la comptabilité", [
            L("Dématérialisation et conservation des pièces comptables", l),
            L("Logiciel comptable et PGI", l), L("L'impact de la dématérialisation", l),
            L("Sauvegarde et confidentialité des données comptables", l)]),
    ]

def ue12():
    l = 30
    v = lambda t, m: V(t, round(m * 2))
    return [
        ("Introduction", [T("Survole l'e-book UE12 et la méthode : traduction, synthèse, rédaction (3 h)", 20)]),
        ("M2 · Méthodologie et bases grammaticales", [
            v("Méthodologie : la note de synthèse (vidéo 21 min)", 21), v("Méthodologie : la rédaction en anglais (vidéo 17 min)", 17),
            v("Grammaire : syntaxe et expressions (14 min)", 14), v("Grammaire : prétérit et present perfect (20 min)", 20),
            v("Grammaire : présent simple et BE + V-ING (16 min)", 16), v("Grammaire : l'expression du futur (11 min)", 11),
            v("Grammaire : les modaux (13 min)", 13), v("Grammaire : le conditionnel, IF, WHETHER (7 min)", 7),
            v("Grammaire : l'obligation et le devoir (7 min)", 7), v("Grammaire : la capacité (9 min)", 9)]),
        ("M3 · Companies and their stakeholders", [
            L("The main actors of a company", l), L("Company organization", l),
            L("Business forms and leadership styles", l), L("How to fund a business", l),
            A("Application : Organizing a company")]),
        ("M4 · Corporate Social Responsibility", [
            L("Corporate Social Responsibility", l), L("Environmental, social and governance factors", l),
            L("Corporate ESG strategies", l), L("Challenges and benefits of implementing CSR", l),
            A("Application : the corporate citizen and the social and solidarity economy")]),
        ("M5 · Corporate culture and working conditions", [
            L("Corporate culture", l), L("Human resources and quality of working life", l),
            L("The specificities of digital firms", l), A("Application : Implementing corporate culture"),
            C("Cas Work-life balance", 60), C("Cas Ageism", 90)]),
        ("M6 · Communication and strategies to be competitive", [
            L("Strategies for growth", l), L("Current challenges", l), L("Assessment tools", l),
            L("Communication with stakeholders", l), L("Effective communication", l),
            L("Fair competition policies", l), L("Innovation and intellectual property", l),
            A("Application : corporate strategy and competitiveness")]),
        ("M7 · The digital revolution", [
            L("The age of digital society", l), v("New technologies (vidéo 30 min)", 30),
            v("What the future holds in store (vidéo 18 min)", 18), v("Customer-centric (vidéo 13 min)", 13),
            L("Digital tools and assets in the business world", l), L("Big tech controversies", l),
            C("Cas Robots are taking our jobs", 90)]),
        ("M8 · Understanding what is at stake with energy", [
            L("A double constraint", l), L("Towards the end of fossil fuels", l),
            L("Shifting to renewable energies", l), L("Energy, geopolitics and social justice", l),
            A("Application : what is at stake with energy")]),
        ("M9 · Globalisation and development", [
            L("Globalization (+ 4 vidéos)", 60), C("Cas « Is free trade being threatened? »", 90),
            L("At an international level", l), v("Free Trade Areas (vidéo 25 min)", 25),
            A("Application : Challenging unfair competition"), C("Cas CETA", 60),
            L("Slowbalization and deglobalization", l)]),
        ("M10 · Social policies", [
            L("The basic forms of social protection", l), L("Current societal issues", l),
            L("Political reforms and social models", l),
            A("Application : social protection and demographic dynamics")]),
    ]

def ue13():
    return [
        ("Introduction", [T("Lis l'introduction UE13 et les consignes des dépôts (onglet Évaluations)", 30)]),
        ("M2 · Rechercher et analyser l'information", [
            L("Rechercher des informations : la recherche documentaire", 40),
            L("Rechercher des informations : la démarche d'enquête", 40)]),
        ("M4 · Le rapport et la soutenance", [
            L("Le rapport de stage", 45), L("La soutenance", 45)]),
        ("Rapport · Préparer", [
            T("Choisis ta situation de communication chez Fidexia et note les faits (qui, quoi, quand, quel support)", 60),
            T("Fais le plan du rapport : parties 1, 2 et 3", 60)]),
        ("Rapport · Parties 1 et 2", [
            T("Rédige la partie 1 : présentation de Fidexia (activité, organisation, ton poste)", 120),
            T("Rédige la partie 2 : la situation de communication (contexte, acteurs, outils, analyse)", 120),
            T("Termine les parties 1 et 2, relis et dépose-les sur Studi (Évaluations > UE13)", 120)]),
        ("M2 · Rechercher et analyser l'information (suite)", [
            L("L'analyse des informations : le travail collaboratif", 40),
            L("Assurer une veille informationnelle", 40)]),
        ("Rapport · Partie 3", [
            T("Partie 3 : choisis ton thème structuré et fais ton plan détaillé", 120),
            T("Rédige la partie 3 : première moitié", 120),
            T("Rédige la partie 3 : seconde moitié, relis et dépose-la sur Studi", 120)]),
        ("M3 · Les principes de la communication professionnelle", [
            L("Les enjeux de la communication", 40), L("Les outils de la communication écrite", 40),
            L("Les outils de la communication orale", 40)]),
        ("Rapport · Version intégrale", [
            T("Assemble le rapport intégral : introduction, conclusion, sommaire, annexes", 120),
            T("Relis tout, mets en page et dépose le rapport intégral sur Studi (limite : fin février)", 120),
            T("Passe le certificat Studi UE13 (QCM, onglet Évaluations)", 45)]),
    ]

CURRICULUM = {"UE1": ue1(), "UE5": ue5(), "UE7": ue7(), "UE8": ue8(), "UE9": ue9(), "UE12": ue12(), "UE13": ue13()}
