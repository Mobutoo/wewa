# Reproduire fidèlement la Boxer : méthode documentée avant fabrication

Cette recherche complète le [plan de la moto seule](MOTORCYCLE_PLAN.md). Elle porte sur la manière de reconstruire les pièces, pas sur une nouvelle fabrication déjà exécutée. Moto, variante et cotes de référence sont conservées. Aucun conducteur, aucune nouvelle géométrie, aucun changement du jeu à ce stade.

## Choix de méthode et sources examinées

**Méthode retenue pour les données présentes : modélisation mécanique par composants, contrainte par les dimensions fiables et par plusieurs caméras rapprochées des photos.** La calibration photographique est une étape propre, à vérifier avant le travail de forme. C’est une décision de production adaptée à notre dossier, pas une garantie que huit images déterminent toutes les dimensions.

| Méthode | Décision pour cette moto | Motif |
|---|---|---|
| Modélisation par pièces avec références multiples et cotes | Base retenue | Permet de garder des sections, épaisseurs, ajours et liaisons éditables, et d’identifier les dimensions estimées. |
| fSpy | Aide conditionnelle au réglage des caméras | Sa documentation exige des directions de fuite appropriées. Une moto détourée, faite de courbes et de pièces inclinées, n’offre pas automatiquement des axes orthogonaux utilisables. [S1–S2] |
| Photogrammétrie COLMAP | Étude facultative d’alignement, pas base de livraison promise | Recouvrement, détails stables et surfaces réfléchissantes limitent les résultats. Huit vues commerciales ne démontrent pas un jeu de capture suffisant. [S3–S4] |
| Reconstruction automatique depuis une image générée | Écartée pour les cotes et les détails mécaniques | Les moodboards sont des directions de rendu ; ils ne mesurent pas une moto et peuvent inventer des pièces. |
| Ajustement pour une seule belle vue | Écarté pour l’asset jouable | La forme doit rester cohérente sur le tour complet. Un auteur décrit explicitement les limites de son modèle de composition à un seul angle ; ce raccourci ne convient pas ici. [S7] |

Les retours d’Eldar Seydamet sur une Honda de jeu et d’Alexa Ranzola sur une Harley décrivent une organisation utile : proportions, composants distincts, détail, matières puis export contrôlé. Nous adaptons ces principes dans Blender ; nous ne reprenons ni leurs géométries, ni leurs budgets de triangles, ni leurs durées, ni leurs logiciels payants comme exigences. [S5–S6]

Le [registre des sources](library/motorcycle-methods-sources.json) distingue documents lus, retour d’artiste et simple présentation de cours. La page publique CG Cookie a été lue, pas les leçons payantes : ses outils répétitifs sont pertinents, sa liberté de s’écarter du modèle n’est pas retenue pour cette reproduction. [S10]

## 1. Dossier d’observations et de mesures

Conserver les originaux, URLs et empreintes ; ne pas mesurer sur le moodboard ni sur une image agrandie artificiellement. Les huit vues de tour sont à 1000 × 700 px. L’inspection des fichiers confirme des images WebP avec alpha, malgré leur suffixe `.png`, sans données EXIF disponibles : focale et distance de prise de vue restent inconnues. Leurs profils ICC sont présents ; cela ne fournit pas la calibration optique ni la couleur mesurée des matières.

Établir par pièce une fiche avec identifiant, variante, vues visibles, cotes et origine de chaque information : constructeur, mesure physique, déduction photographique ou estimation. Chaque valeur estimée garde sa plage plausible et sa dépendance au réglage de caméra. Les dimensions globales de 2 016 × 740 × 1 134 mm et l’empattement de 1 285 mm sont déjà documentés ; ils ne cotent pas le réservoir ou le moteur.

Le diamètre nominal de jante de 17 pouces concerne la portée du pneu. Le contour extérieur visible de la jante et celui du pneu ne valent pas 431,8 mm. Les désignations2.75-17 et3.00-17 ne suffisent pas à établir nos profils gonflés, sculptures et marquages exacts.

Chercher d’abord des vues de dessus, commandes/compteurs, flancs de pneus et raccords cachés ; vérifier que plans de pièces et notices correspondent à la variante choisie. Les éclatés renseignent les assemblages, sans devenir des dessins à l’échelle. Une dimension critique inconnue reste ouverte ou explicitement estimée ; elle ne devient pas officielle parce que le modèle semble plausible.

## 2. Relever les repères avant de dessiner les surfaces

Annoter les centres d’axes visibles, extrémités identifiables de selle et de réservoir, ancrages de fourche/amortisseurs et centres d’optiques. Pour chaque point, conserver l’image, sa position 2D, l’objet réel correspondant et l’incertitude de lecture. Ne pas annoter un point masqué comme s’il était visible. Les artefacts de détourage ne sont ni la silhouette mécanique ni un détail à reproduire.

Dans Blender, régler les unités, conserver le repère d’export et placer seulement les axes, plans et guides de gabarit utiles. Ces repères ne constituent pas une nouvelle moto globale simplifiée. Vérifier les conventions de largeur et de hauteur du constructeur avant d’utiliser les rétroviseurs comme contrainte. Ne pas supposer identiques les hauteurs des centres avant/arrière si les pneus diffèrent.

## 3. Rapprocher les caméras des photos

Créer une caméra par vue, avec image non étirée et résolution correspondante. Ajuster focale/champ, pose, cadrage et éventuel décentrement selon les repères de gabarit ; distinguer un recadrage commercial d’un changement réel de focale. Ne pas supposer que les huit images sont des vues orthographiques, qu’elles ont exactement 45° d’écart ou qu’elles partagent toutes la même calibration.

fSpy pourra fournir une initialisation si les directions nécessaires sont justifiées ; sinon, ajuster les caméras sur des repères 3D contraints. Une seule longueur connue ne donne pas une solution unique de caméra et de profondeur. Ne pas inventer des parallèles pour obtenir un résultat numérique. [S1–S2]

Verrouiller les caméras obtenues avant de détailler les pièces. Si plusieurs vues demandent des déformations incompatibles, réexaminer d’abord les repères, la variante et le cadrage. Le forum Blender Artists consulté montre qu’une mauvaise focale peut provoquer ce type de discordance ; son exemple n’est pas une preuve de calibration de nos images. [S8]

Garder deux trois-quarts pour un premier contrôle séparé, après initialisation de leurs caméras sur les mêmes guides indépendants des surfaces détaillées. Les utiliser ensuite pour détecter une forme ajustée à un seul profil. Une modification ultérieure des caméras doit être consignée et refaire les comparaisons ; ces vues ne sont pas une vérité métrologique indépendante des photos d’origine.

## 4. Fabriquer une pièce à la fois, selon sa construction

| Pièce | Construction prévue | Examen déterminant |
|---|---|---|
| Pneu | Section flanc/épaule/bande/talon, révolution autour de l’axe ; rainures et motif documentés sur un secteur avant répétition | Profil et largeur vus de face, continuité de sculpture, contact sur jante ; aucun pavé inventé pour remplir la surface |
| Jante et moyeu | Section de jante ; une branche moulée correcte puis répétition radiale ; ajours, raccords, axe et valve distincts | Ouvertures et épaisseur vues des deux côtés, pas seulement nombre de branches |
| Fourche, tubes et échappement | Sections et courbes avec rayons/raccords contrôlés, puis surfaces et attaches | Diamètres, cintrages, zones d’emboîtement, implantation des fixations |
| Réservoir, caches et garde-boue | Surfaces de contrôle, boucles de soutien et arrondis locaux ; épaisseur réelle des bords | Silhouette sur plusieurs angles, reflet continu sans pincement et raccord selle/réservoir |
| Moteur et transmission | Carters séparés, ailettes et organes visibles documentés ; répétition après réception de l’exemplaire | Volumes asymétriques, jonctions, vides, visserie et liaisons plausibles |
| Selle, optiques et commandes | Formes et couches propres à chaque objet ; grain, coutures, verre/reflecteur et détails de commande | Gros plan, épaisseur, finesse des arêtes et raccord aux pièces voisines |

Les opérations de répétition, courbes et subdivision sont des moyens d’obtenir ces formes ; elles ne constituent pas un contrôle de fidélité. Conserver une version éditable avant fusion ou application destructive. Le détail circulaire est conçu sur un secteur correctement raccordé ; le motif et son pas doivent venir de notre référence, pas être copiés d’un autre modèle de moto. [S5, S10]

Un ensemble de repères commun reste nécessaire pour vérifier les interfaces de pièces, mais une seule pièce passe en fabrication détaillée. Première pièce après préparation : pneu avant ; jante et moyeu suivront leur propre fiche. Réservoir, moteur ou optique ne sont pas reçus implicitement avec une roue.

## 5. Vérifier les formes avec des preuves comparables

Produire par pièce un rendu gris, un examen de reflets sous grandes lumières et une comparaison au cadrage de référence. Conserver côte à côte photo, rendu, superposition des contours et défauts annotés. Décrire séparément erreur de caméra, de forme et partie inconnue.

Protocole proposé pour notre contrôle, à exécuter plus tard :

- **Repères 2D :** relever les écarts de projection en pixels, par vue, seulement pour les points visibles ; fixer la tolérance en fonction de la netteté et de l’incertitude d’annotation de chaque photo.
- **Contours et ajours :** comparer les limites de pièce et les vides internes, en excluant les parties masquées et les artefacts de détourage. Une silhouette extérieure correcte ne suffit pas à recevoir une jante.
- **Cotes :** vérifier les valeurs publiées ou réellement mesurées selon leur convention et leur précision. Ne pas convertir uniformément tous les pixels d’une photo en millimètres : profondeur et perspective varient.
- **Vues de contrôle :** rechercher les défauts qui apparaissent sur l’autre côté ou un trois-quarts ; reprendre la pièce si sa correction d’un angle en dégrade un autre.
- **Incertitude :** conserver les plages plausibles pour les dimensions inférées ; ne pas annoncer une précision millimétrique inaccessible aux images.

Aucun seuil en pixels, taux de réalisme ou résultat de calibration n’est annoncé aujourd’hui : les points ne sont pas encore annotés et les caméras ne sont pas encore résolues. Les critères ci-dessus sont notre protocole de travail proposé, pas une norme industrielle empruntée aux sources.

## 6. Matières et lumière après la forme

Créer une version propre de contrôle avec matériaux séparés. Examiner rugosité, relief, couche de vernis et transmission sous éclairage neutre fixe puis rasant ; la lumière chaude du moodboard intervient dans une seconde présentation. Les dimensions de grain et l’usure suivent les références observables.

Le guide Khronos distingue couleur, métal, rugosité, relief et extensions de matière. Nous nous appuyons sur cette séparation pour transporter les matériaux vers le moteur, sans attendre qu’une texture corrige la géométrie. [S9] La photographie commerciale contient son éclairage : ne pas traiter un reflet blanc comme une tache de couleur permanente.

## 7. Dériver la version de jeu et contrôler la moto seule

Préserver la source détaillée puis construire la version de jeu. Garder en géométrie les contours extérieurs, les ajours importants et les éléments proches du guidon ; cuire seulement les détails qui peuvent l’être sans dégrader l’apparence utile. Pour les normales, contrôler la projection pièce par pièce, les UV, les tangentes et les artefacts de cuisson ; ne pas transférer une ombre de contact statique sur une pièce qui doit tourner. [S5, S9]

Exporter les matières prises en charge par glTF, avec couleur et données de surface dans leurs espaces corrects ; relire le fichier dans Babylon.js sous un éclairage de contrôle. Comparer avant/après cuisson, compression et LOD, puis présenter huit angles et une rotation/braquage de la moto seule. Réception visuelle et performance iPhone restent deux contrôles distincts. Aucun budget d’un exemple UE4/UE5 n’est transféré automatiquement au navigateur.

## Cas où une nouvelle capture aiderait réellement

Si une moto de la variante retenue devient accessible, une prise de vues dédiée améliorerait surtout les zones manquantes : mesure des dimensions de pièces, vues dessus/dessous, flancs, sculpture et commandes. Pour tenter une reconstruction photographique, prévoir plusieurs hauteurs, des vues proches entre elles, netteté sur l’objet et éclairage diffus stable ; masquer le fond si l’objet tourne. Les surfaces vernies, transparentes ou peu texturées restent difficiles. C’est une possibilité ultérieure, pas une capture existante ni une obligation immédiate faite à l’utilisateur. [S3–S4]

## Livrables et conditions avant la première pièce

| Passage | Livrable attendu | Situation actuelle |
|---|---|---|
| Références → calibration | Matrice des cotes connues/estimées/manquantes ; repères annotés et leur visibilité | Cotes globales et images disponibles ; annotations et cotes de pièces à compléter |
| Calibration → pneu | Scène de caméras/guides, comparaisons sur plusieurs vues, incertitudes ouvertes | Non exécuté ; aucune précision annoncée |
| Pneu → jante | Source du pneu, vues grises, matières et comparaison documentée ; fiche des écarts | Non exécuté ; source de sculpture/flanc à identifier |
| Pièces → moto seule | Contrôles individuels puis interfaces, huit angles et mouvements mécaniques | Non exécuté |
| Moto → conducteur | Réception de la moto et version de jeu comparée | Non exécuté ; conducteur différé |

Prochain travail concret : dossier de repères et calibration, sans géométrie détaillée globale. Il sera suivi du pneu avant lorsque ses informations critiques seront suffisantes ou que ses estimations seront explicitement cadrées. Le lot précédent demeure refusé ; la recherche n’en change pas le statut artistique.

## Sources

- **S1** — [fSpy : principes et limites](https://fspy.io/basics/).
- **S2** — [fSpy : guides et distance de référence](https://fspy.io/tutorial/).
- **S3** — [COLMAP : acquisition et reconstruction multivue](https://colmap.github.io/tutorial.html).
- **S4** — [Agisoft : capture d’objets proches](https://agisoft.freshdesk.com/support/solutions/articles/31000149340-close-range-objects-scanning).
- **S5** — [Eldar Seydamet : Honda CX650 destinée au jeu](https://80.lv/articles/making-a-honda-bike-with-maya-ue4).
- **S6** — [Alexa Ranzola : reproduction d’une Harley](https://80.lv/articles/how-to-model-a-realistic-bike-based-on-a-2013-harley-davidson-sportster).
- **S7** — [Lautaro Iglesias : limites d’un modèle de composition à une seule vue](https://www.blendernation.com/2020/02/14/behind-the-scenes-futuristic-racing-motorcycle/).
- **S8** — [Blender Artists : alignement de la perspective d’un produit](https://blenderartists.org/t/aligning-object-perspective-from-an-image-to-the-same-object-in-blender/1149106).
- **S9** — [Khronos : matières PBR dans glTF](https://www.khronos.org/gltf/pbr) et [spécification glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html).
- **S10** — [CG Cookie : présentation publique du cours de modélisation moto](https://www.cgcookie.com/courses/modeling-a-motorcycle/), description seulement.

Les pages du manuel Blender recherchées sur bevel, subdivision et cuisson n’ont pas pu être ouvertes par l’outil web (réponses 402). Elles ne sont pas comptées comme documentation intégralement consultée. Les principes de fabrication ci-dessus reposent sur les retours d’auteurs effectivement lus et notre protocole proposé ; aucune formation payante ni licence logicielle n’a été achetée.
