# Workflow de fabrication fidèle — Viva Wewa

Version 1, 20 octobre 2026. Procédure de production du projet, construite à partir de la [recherche moto](../MOTORCYCLE_RECONSTRUCTION_RESEARCH.md), de son [complément documentaire](RESEARCH.md) et des [sources consultées](sources.json). Les conditions de passage ci-dessous sont nos décisions de travail ; aucune source ne garantit le résultat à notre place.

**Une pièce observable et vérifiable constitue l’unité de fabrication.** Un véhicule, une façade ou un personnage est un assemblage de pièces. Une entrée du catalogue peut couvrir plusieurs objets ; plusieurs entrées peuvent désigner le même objet. Le [routage du dossier](coverage.json) conserve les 92 fiches AS et les 67 compléments CON sans les transformer en 159 modèles distincts.

La priorité reste la moto seule, puis ses composants successifs. Le conducteur attend sa réception. Le lot 01 demeure refusé ; les moodboards sont des intentions, jamais des références de mesure ni des rendus du moteur.

## Boucle de travail à exécuter

| Étape | Travail concret | Preuve nécessaire pour passer | Si le résultat échoue |
|---|---|---|---|
| G0 — Identifier et décomposer | Relier aux IDs du dossier ; définir modèle, marché, époque, état, usage et distances de caméra ; isoler les composants et leurs interfaces | Fiche d’identité, liste des pièces, dépendances, critères visibles de fidélité | Corriger le périmètre avant de fabriquer |
| G1 — Documenter | Rechercher documents techniques, vues opposées, dessus/dessous, détails, matières ; relever contradictions et droits | Matrice sources/vues/cotes, inconnues critiques résolues ou estimations bornées justifiées | Recherche ciblée sur le manque ; aucune invention silencieuse |
| G2 — Mettre à l’échelle et préparer la comparaison | Fixer unités, repères, caméra ou protocole de capture adapté à la famille | Guides, points annotés, paramètres et incertitudes ; vues de contrôle ; plan de mesure des écarts | Réexaminer caméra, recadrage et variante avant de déformer la pièce |
| G3 — Construire la forme isolée | Sections, épaisseurs, courbures, ajours, raccords, asymétries et fixations ; conserver la source éditable | Rendus gris et reflets, références comparables, contours/repères, défauts annotés et corrigés | Retour à G2 ou G3 ; aucune matière pour masquer la forme |
| G4 — Construire la matière | UV à l’échelle ; couleur, rugosité, métal, relief et couches ; commencer propre avant l’usure | Gros plans sous éclairage neutre et rasant ; échelle du grain et séparation des matières ; origine des textures | Corriger UV, relief ou réponse lumineuse ; refaire G3 si nécessaire |
| G5 — Vérifier la fonction et les interfaces | Mouvements mécaniques, attaches, contacts, déformations ou comportement propre à l’élément | Séquence montrant les amplitudes utiles et les raccords ; aucun défaut critique ouvert | Reprendre la pièce concernée, sans recevoir tout l’assemblage |
| G6 — Comparer dans le moteur | Exporter un candidat séparé ; contrôler échelle, pivots, normales, couleurs et rendu dans Babylon.js | Capture réelle, même cadrage utile, matériaux et mouvement ; contrôle glTF séparé du jugement visuel | Corriger conversion/export ; conserver une comparaison source/export |
| G7 — Optimiser puis recontrôler | Produire LOD, textures et compression adaptés au coût mesuré ; garder la source détaillée | Comparaisons avant/après, coût en scène représentative, appareil et conditions précisés | Réduire autrement ou réviser le budget avec preuve |
| G8 — Présenter et recevoir | Présenter la pièce seule, ses références et ses limites ; obtenir la décision utilisateur | Revue datée rattachée à la révision exacte ; réception artistique explicite | État « à reprendre », défauts et prochaine correction enregistrés |

Un composant peut être examiné avec les guides de son assemblage, sans que les autres pièces soient déclarées terminées. Répéter un motif ou générer des variantes seulement après réception de son exemplaire. L’assemblage complet reçoit ensuite ses propres contrôles : des pièces reçues séparément peuvent mal se raccorder.

## Recherche : comment décider si le dossier suffit

Chercher dans cet ordre : document de la variante exacte, référence physique mesurée, document constructeur d’une variante voisine, photographie attribuée et datée, retour technique de son auteur. Un forum peut expliquer une difficulté ; il ne certifie pas une cote de notre objet. Un catalogue de pièces peut révéler un assemblage sans être un plan à l’échelle.

Chaque affirmation porte : identifiant, propriété, valeur/unité, objet concerné, source et passage/page, marché/révision, statut et conséquence. Utiliser les statuts `documented_exact_variant`, `measured`, `documented_related_variant`, `photo_inferred`, `estimated`, `unknown`, `rejected`. Une mesure physique indique instrument, conditions et incertitude ; une estimation indique méthode, plage et vues qui la contraignent. Ne pas attribuer de précision inventée à un constructeur.

Pour chaque inconnue : identifier la pièce et le passage bloqués, la prochaine recherche utile, ce qui permettrait de la clore. Arrêter une piste après constat documenté de mauvais modèle, contenu inaccessible ou absence de donnée nouvelle ; conserver le résultat négatif. Rechercher davantage là où cela change la fidélité : silhouette, ajours, premier plan, raccord ou mouvement. Le volume de fichiers téléchargés n’est pas un critère de suffisance.

Les informations d’une variante voisine restent conditionnelles. Une donnée contradictoire n’est ni moyennée ni choisie parce qu’elle facilite le modèle. Le rapprochement doit expliquer année, marché, pièce et état. Si l’information reste absente, poursuivre la préparation indépendante et conserver la pièce concernée bloquée. Une estimation visible importante doit être présentée comme telle dans la revue.

Les originaux documentaires sont conservés hors du dépôt public et du bundle si leur redistribution n’est pas établie. Le registre conserve URL, auteur, date, empreinte et usage permis. « Gratuit à consulter » ne signifie pas « utilisable comme texture ». Pour un asset adapté, préserver la licence, l’attribution et les modifications.

## Fichiers utilisés à chaque reprise

1. Lire cette procédure, la [recette de la famille](RECIPES.md), le registre de fabrication et la dernière décision utilisateur.
2. Copier [asset-template.json](templates/asset-template.json) dans `records/` ; créer une fiche par composant actif. Copier [review-template.md](templates/review-template.md) pour les preuves de revue.
3. Remplir les sources, cotes, vues, inconnues et critères **avant** les surfaces détaillées. La [fiche du pneu avant](records/moto-tyre-front-001.json) montre un dossier commencé et réellement bloqué.
4. Au début d’une session, annoncer la pièce, le passage visé et le résultat vérifiable. Garder une seule pièce en fabrication détaillée. Les recherches sur d’autres familles restent possibles sans les annoncer fabriquées.
5. À chaque passage, enregistrer preuves, révision, méthode de comparaison et décision. Le vérificateur ci-dessous contrôle les déclarations et les empreintes locales ; il ne juge pas le réalisme des images.
6. À la fin, consigner terminé / exécuté / manquant / prochain travail ; mettre à jour GitHub et le PRD Ewutelo. Aucun travail permanent n’est supposé continuer entre sessions.

```sh
python tools/check_asset_workflow.py
python tools/check_asset_workflow.py --ready-for G3 creative/workflow/records/moto-tyre-front-001.json
```

La première commande doit accepter un dossier cohérent même s’il est bloqué. La seconde doit refuser un passage dont les prérequis n’ont pas de preuves. `pending`, `blocked`, `rework`, `passed` et `not_applicable` sont distincts. Une non-applicabilité doit être motivée par la recette ; elle ne dispense pas de présenter la preuve équivalente nécessaire.

## Protocole de contrôle visuel

Avant fabrication, fixer les vues, éclairages, distances utiles et tolérances justifiables. Présenter photo documentaire et rendu identifiés, jamais une image générée comme preuve. Examiner silhouette, sections, vides, joints, reflets et détails à leur taille d’affichage réelle. Noter les écarts par vue et leur cause probable. Une moyenne de projection ne doit pas cacher un gros défaut local.

Pour une pièce mécanique, contrôler les cotes publiées et les raccords ; mesurer les écarts de projection seulement après calage documenté. La netteté et l’incertitude des annotations déterminent les tolérances : aucun seuil universel de pixels ou « score de réalisme » n’est imposé. Pour une surface, garder un repère d’échelle ; pour un personnage, une séquence de déformation ; pour un son, une écoute isolée puis en contexte. Détails dans les recettes.

Une modification de variante, de caméra, de forme ou de texture invalide les preuves qui en dépendent. Noter les passages à refaire et conserver l’historique. Ne pas réutiliser une réception d’une ancienne révision pour un export différent. Contrôle automatique, revue artistique et qualification Safari physique sont trois résultats séparés.

## Outils et limites actuels

Blender, outils de métadonnées/PDF, Python et glTF servent à préparer et fabriquer les sources ; Babylon.js sert au contrôle réel du jeu. fSpy/COLMAP restent des aides conditionnelles à la qualité des prises de vue. Le pipeline ne dépend pas d’un logiciel payant cité dans un article, ni d’un générateur automatique censé inventer les parties manquantes. Aucun nouveau logiciel payant ou matériel n’est acheté.

Le plan est applicable aux familles du dossier, mais leur recherche spécifique et leur décomposition restent à exécuter. Aujourd’hui : documentation et workflow produits ; aucune nouvelle calibration, géométrie ou matière reçue. Prochain livrable moto : repères annotés, guides et caméras comparés, puis pneu avant lorsque ses inconnues critiques seront cadrées.
