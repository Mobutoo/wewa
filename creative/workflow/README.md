# Workflow de fabrication fidèle — Viva Wewa

Version 1, 20 octobre 2026. Procédure de production du projet, construite à partir de la [recherche moto](../MOTORCYCLE_RECONSTRUCTION_RESEARCH.md), de son [complément documentaire](RESEARCH.md) et des [sources consultées](sources.json). Les conditions de passage ci-dessous sont nos décisions de travail ; aucune source ne garantit le résultat à notre place.

Direction graphique choisie par l’utilisateur : [style2, réalisme cinématographique](../GRAPHIC_STYLE.md). L’utiliser comme cible de lumière et de matière ; les références techniques restent la base des formes et dimensions.

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
4. Au début d’une session, annoncer la pièce, le passage visé et le résultat vérifiable. Par défaut, garder une seule pièce en fabrication détaillée. Sur demande explicite de parallélisation de l’utilisateur, la présente reprise autorise trois composants indépendants du poste de conduite (tube, poignées, compteurs), chacun avec sa fiche, ses preuves et ses inconnues ; aucune réception ne se transmet entre eux. Les recherches sur d’autres familles restent possibles sans les annoncer fabriquées.
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

Faire un export évalué et un contrôle technique sans rendu avant les vues coûteuses : présence des pièces, sections, orientation, connexions et affectation effective des matériaux. Vérifier les buffers exportés, pas seulement les objets de construction ou les noms de matériaux dans la source. Un remeshing ou un export sans modificateurs peut supprimer des informations sans erreur de format. La [jante avant](../../assets-src/moto-components/front-rim/README.md) fournit un passage `--views none`, puis des contrôles indépendants source/GLB ; les captures moteur et la revue artistique viennent ensuite.

Pour un corps moulé, intégrer les détails de révolution dans une section continue et vérifier qu’elle ne se croise pas. Refuser une fusion ouverte avant remeshing : un maillage rendu fermé par voxelisation peut encore contenir des milliers de fragments. Le [flasque avant](../../assets-src/moto-components/front-brake-plate/README.md) utilise des volumes Blender originaux, des opérations Manifold contrôlées, puis des vérifications indépendantes du corps et des raccords. Lancer les scripts Blender avec `--python-exit-code 1` afin qu’une exception Python fasse échouer la commande. Ces contrôles restent distincts de la comparaison artistique et des dimensions documentées.

## Outils et limites actuels

Blender, outils de métadonnées/PDF, Python et glTF servent à préparer et fabriquer les sources ; Babylon.js sert au contrôle réel du jeu. fSpy/COLMAP restent des aides conditionnelles à la qualité des prises de vue. Le pipeline ne dépend pas d’un logiciel payant cité dans un article, ni d’un générateur automatique censé inventer les parties manquantes. Aucun nouveau logiciel payant ou matériel n’est acheté.

Le plan est applicable aux familles du dossier, mais leur recherche spécifique et leur décomposition restent à exécuter. Aujourd’hui : sept fiches de candidats séparés couvrent le pneu, la jante, le flasque avec matière v2, le levier de came, le guidon, les enveloppes de poignées et les compteurs ; aucune calibration complète ou réception artistique acquise. Pièce détaillée active : compteurs du poste de conduite. Les [vues de revue du cockpit](../reviews/cockpit-v1/README.md) réunissent seulement les trois derniers candidats. Prochain travail : comparaison photographique, commodos, leviers, supports, rétroviseurs et visière ; la documentation des sections de came, de l’axe et de la compatibilité du frein reste ouverte. La moto seule précède toujours le conducteur.

Pour une tôle mise en forme, répartir les sommets dans la surface avant de la courber : une grande face non plane peut produire des cassures diagonales de reflets. Une triangulation contrainte avec points intérieurs doit encore exclure les triangles extérieurs et vérifier que son aire conserve le contour. Le [levier avant](../../assets-src/moto-components/front-brake-lever/README.md) conserve cette correction. Examiner les reflets dans la source et dans les buffers réellement exportés.

Pour les matières, contrôler les pixels et canaux des textures réellement embarquées, leur espace couleur, l’échelle UV et le repère tangent. Des cartes identiques ne prouvent pas des rendus identiques : conserver les avertissements d’export et la comparaison artistique ouverte. Voir le [flasque v2](../reviews/front-brake-plate-v2/README.md).

## Reprise parallèle du poste de conduite

L’utilisateur demande explicitement de paralléliser, puis donne la priorité au guidon et aux compteurs pour sa vue embarquée. Les [trois candidats réunis pour revue](../reviews/cockpit-v1/README.md) restent distincts ; leurs sources sont liées, leurs volumes/exports contrôlés et les aiguilles manipulées dans Babylon.js. Les sources officielles du cockpit ont été retrouvées avant la construction. Les recherches séparées sur [l’axe](../research/front-axle-v2/README.md) et [la came](../research/front-brake-cam/README.md) restent de la documentation, pas des pièces fabriquées. La matrice de variantes de frein interdit de déclarer le flasque/levier JA déjà compatibles avec la jante moulée sans confirmation RDC.

## GO des18lots

L’utilisateur autorise la séquence complète du [plan détaillé](motorcycle-execution-18.json). La limite reste trois composants détaillés simultanés, avec recherche indépendante des lots suivants. Cette autorisation étend le périmètre de travail ; elle ne réceptionne aucun ancien candidat. Les groupes composites sont décomposés avant fabrication, les interfaces communes n’ont qu’un propriétaire et les sources historiques manifestées restent immuables.

Le contrôle des corps CSG lit aussi l’aire des triangles dans l’export : une fermeture et un volume positifs peuvent masquer des milliers de triangles dégénérés issus d’un congé. Corriger ces coutures dans la source, comparer les sommets et la surface, puis refaire fermeture, ouvertures et interfaces avant de rendre. Sur les pontets, ce nettoyage a supprimé les réparations de tangentes précédemment expérimentées. Les tangentes inutilisées d’une primitive sans carte normale peuvent être retirées de l’export avec preuve d’invariance des autres buffers ; cela ne prouve pas la fidélité des matériaux.

La revue de forme exige un cadrage entier de la pièce. Une inspection très rapprochée reste un complément. L’inspecteur v2 conserve un champ vertical fixe pour les écrans en paysage ; les anciens outils et leurs preuves restent versionnés séparément.

Vérifier aussi les triangles UV effectivement utilisés par une carte normale : une lèvre annulaire plane peut recevoir par erreur une projection cylindrique qui écrase ses coordonnées. Des tangentes de norme correcte ne suffisent pas à détecter cette erreur. Le [contrôle UV](../../tools/check_motorcycle18_uv.mjs) lit le jeu de coordonnées déclaré par chaque matière, refuse les triangles UV exactement aplatis et conserve les petites aires comme mesures diagnostiques. Il ne certifie ni la densité de texture ni la qualité artistique.
