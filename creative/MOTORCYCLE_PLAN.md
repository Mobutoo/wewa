# Moto seule — plan de conception avant fabrication

Voir aussi le [complément documentaire](workflow/RESEARCH.md), les [25 groupes de composants à développer](workflow/motorcycle-assembly.json) et le [workflow réutilisable](workflow/README.md). Les nouvelles informations des versions apparentées restent conditionnelles ; le conflit de largeur et l’interface pneu/jante ne sont pas résolus.

**Complément de recherche :** appliquer la [méthode documentée de reconstruction](MOTORCYCLE_RECONSTRUCTION_RESEARCH.md). La prochaine étape est l’annotation des repères et le rapprochement des caméras aux photos, avant le premier pneu détaillé. Les guides de calibration ne constituent pas une nouvelle moto globale simplifiée. Aucune reconstruction photographique automatique ni précision millimétrique n’est acquise.

## Mandat actuel

Le lot 01 est refusé dans toutes ses vues. L’utilisateur demande la moto seule, chaque composant avant tout conducteur, les vraies dimensions et une explication du processus avant de coder. Cette étape livre un plan et un dossier de références ; aucune nouvelle géométrie ni modification du jeu. La fabrication sera conduite par pièce, avec relecture de la moto complète avant travail du conducteur.

## Référence et dimensions

Base documentaire : **Bajaj Boxer125HD du catalogue RDC**, même famille que la référence fournie. Utiliser une variante cohérente, sans importer implicitement les cotes d’une BoxerX125, BM125 historique ou d’une TVSHLX. La page RDC actuelle utilise une série de huit vues rouges « red-long-visor », code modèle de page `00JL22`. Ce code de page n’est pas présenté comme un VIN, un millésime ni un numéro de pièce constructeur.

Page constructeur [Bajaj RDC](https://www.bajajauto.com/fr-cd/bikes/boxer-125hd), relue et récupérée le 20 octobre2026 :

| Donnée publiée | Valeur | Usage |
|---|---|---|
| Longueur | 2016mm | Gabarit longitudinal |
| Largeur | 740mm | Gabarit transversal ; convention des rétroviseurs non précisée |
| Hauteur | 1134mm | Gabarit vertical ; convention de mesure non précisée |
| Empattement | 1285mm | Distance entre axes des roues |
| Pneu avant | 2.75-17 | Désignation nominale, pas mesure complète du profil gonflé |
| Pneu arrière | 3.00-17 | Désignation nominale distincte de l’avant |
| Jantes | 17pouces | Diamètre nominal de portée du pneu : 431,8mm par conversion ; pas diamètre extérieur du pneu |

La hauteur de selle, le diamètre extérieur des pneus, la chasse/angle de direction, les sections du cadre, les dimensions de réservoir, de carters, de phare et des fixations ne sont pas confirmés par cette fiche. Chercher plans/manuels cohérents ou mesures réelles ; à défaut, marquer chaque estimation. Ne pas déformer une pièce pour faire entrer une mesure globale dans une tolérance artificielle. Le catalogue de pièces éclaté pourra aider à comprendre les assemblages, mais un dessin éclaté n’est pas automatiquement coté ni à l’échelle.

## Images effectivement examinées

Les quatorze fichiers constructeur sont récupérés hors du dépôt public et hors du jeu, avec URLs et empreintes dans le [manifeste](library/motorcycle-reference-views.json). Ce sont des références documentaires, sans licence établie pour les redistribuer ou en faire des textures. Aucun nouveau visuel généré n’est utilisé pour prouver la forme mécanique.

| Fichiers de la série constructeur | Vue et usage |
|---|---|
| `rotation-00.png`, `rotation-04.png` | Profils droit/gauche : silhouette, axes, réservoir/selle, échappement et transmission asymétriques |
| `rotation-02.png`, `rotation-06.png` | Face/arrière : largeur, centrage, phare, pneus, amortisseurs, porte-bagages |
| `rotation-01.png`, `rotation-03.png` | Trois-quarts avant droit/gauche : volume du réservoir, fourche, capotage, roue et carter |
| `rotation-05.png`, `rotation-07.png` | Trois-quarts arrière gauche/droit : selle, feu, porte-bagages, chaîne et échappement |
| `alloy-wheels.webp`, `headlight.webp`, `engine.webp` | Formes de jante/moyeu, optique et carters/ailettes |
| `wider-seat.webp`, `suspension.webp`, `strong-chasis.webp` | Coupe visible de selle, amortisseurs, tubes et raccords du cadre |

Les huit vues font1000×700px et les six détails1000×600px. Certains détails sont visiblement des agrandissements/recadrages ; ils n’apportent pas un relevé macro. La transparence et le détourage présentent des artefacts : ne pas les reproduire. Focale et positions de caméra inconnues ; aucune de ces images n’est déclarée plan orthographique. Les huit angles couvrent le tour de la moto, pas son dessus ni son dessous.

À compléter avant les pièces concernées : dessus du réservoir/selle, compteur/commandes lisibles, gros plans de sculpture/flanc de pneu, valves, optiques et raccords masqués ; plan coté ou mesures pour les dimensions non publiées. Les photos de motos en usage à Kinshasa serviront ensuite à documenter poussière et usure ; elles ne doivent pas mélanger les variantes mécaniques ni justifier une patine arbitraire. L’image cible utilisateur fixe le niveau de rendu et la lumière, pas les cotes de la moto.

## Fabrication planifiée et preuves

| Étape | Travail prévu | Preuve et condition de passage |
|---|---|---|
| 1. Verrouiller les références | Identifier la variante, classer les vues et les cotes par composant ; compléter les manques | Fiche par pièce : source, dimensions officielles/mesurées/estimées, vues utilisables et inconnues explicites. Une forme critique non documentée reste ouverte. |
| 2. Construire les repères | Régler Blender en mètres ; placer les axes de roues et des guides de gabarit, puis rapprocher les caméras des huit vues | Guides de contrôle, pas un nouveau modèle global de primitives proposé à réception. Vérifier le cadrage avant de conclure à une erreur de proportion. |
| 3. Fabriquer une pièce | Modéliser la section, silhouette, épaisseur, raccords, ajours et fixations réels ; conserver les objets distincts et la source éditable | Gros plans sans textures, profil, face et trois-quarts comparables. Corriger les défauts de forme avant la matière. Aucune réception implicite des pièces voisines. |
| 4. Terminer sa matière | UV, relief, rugosité, transparence et détails observés ; distinguer peinture, alliage, caoutchouc, plastique et vinyle | Même pièce sous lumière neutre et rasante. Pas de bruit uniforme ni de grain photographique masquant une mauvaise géométrie. Version propre de référence avant patine. |
| 5. Examiner et corriger | Photo/rendu de cadrage proche, liste d’écarts précise, reprise de chaque défaut critique | Dossier de comparaison et décision par pièce ; les tests techniques ne peuvent pas le faire passer. Présenter un exemplaire abouti, sans réclamer une permission à chaque opération intermédiaire. |
| 6. Assembler la moto seule | Réunir les pièces ayant passé leur contrôle, vérifier contacts, dégagements et asymétries ; roues en rotation et direction articulée | Tour complet, huit vues, dessus et gros plans. Pas de conducteur, sac ou colis ; les éléments mécaniques doivent rester inspectables. |
| 7. Qualifier dans le moteur | Dériver l’export de jeu, cuire les petits reliefs utiles, réduire et compresser ; contrôler éclairage neutre puis celui de jeu | Comparaison avant/après export et optimisation, gros plans au guidon/arrière, aucune perte majeure de silhouette ou matière. Les budgets de jeu sont à mesurer, pas à promettre. |
| 8. Faire recevoir la moto | Présenter sources, références, vues comparables et séquence de rotation/direction, réserves restantes | Réception utilisateur de la moto. Le conducteur n’entre en fabrication qu’après cette étape. |

Ordre de fabrication prévu, avec une seule pièce active : **pneu avant → jante avant → moyeu/frein et axe → fourche/soufflets/tés → garde-boue avant → ensemble arrière (chaque pièce séparément) → cadre/bras oscillant/amortisseurs → moteur/carters/ailettes et liaisons visibles → transmission/chaîne/carter → échappement/protection → réservoir/bouchon/caches → selle/porte-bagages → phare/capotage/clignotants/feu arrière → guidon/poignées/leviers/commutateurs/compteurs/rétroviseurs/câbles → repose-pieds/pédales/béquille/fixations**. Le découpage détaillé et les références de chaque sous-pièce restent à renseigner avant sa fabrication.

Une petite pièce utile au rendu peut être cuite dans une texture plutôt que rester en géométrie mobile. Cette décision vient après la référence détaillée et sa comparaison ; le modèle du jeu reste contrôlé à la distance où le joueur le voit.

## État au terme de la planification

Dimensions globales revérifiées, huit angles et six détails téléchargés et examinés, manques identifiés, méthode définie. Aucun nouveau modèle réaliste déclaré livré. Le lot 01 reste rejeté ; ses matériaux, pièces et rendu ne sont pas un étalon accepté. Prochaine étape : annoter les repères et vérifier le calage des caméras sur les guides dimensionnés, puis compléter le dossier du pneu avant et de son interface avec la jante avant de construire cette seule pièce.
