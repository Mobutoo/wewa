# Reprise après refus du lot 01

Procédure opérationnelle commune : [workflow de fabrication fidèle](workflow/README.md), [recettes](workflow/RECIPES.md), [complément documentaire](workflow/RESEARCH.md). Ces fichiers détaillent et prolongent les conditions ci-dessous ; les fiches de composants et preuves sont conservées dans `workflow/records/`.

Périmètre actuel : **moto seule, plan avant fabrication ; conducteur après réception de la moto**. Le [plan spécifique](MOTORCYCLE_PLAN.md) précise les vues réellement examinées, les dimensions vérifiées et les manques.

L’utilisateur refuse toutes les vues du lot 01 et le travail trop global. Ce lot reste une étude rejetée ; ses contrôles glTF, ses cotes globales et ses sources Blender ne prouvent aucun réalisme. Aucun de ses composants n’est reçu artistiquement. Les fichiers précédents sont conservés pour comparaison, pas comme exemplaires à multiplier.

## Unité de travail

Une famille du catalogue n’est pas une pièce prête à fabriquer. Décomposer chaque objet proche du joueur en composants observables, chacun avec références, source modifiable, matériaux et décision. Pour la moto : pneu avant, jante avant, moyeu/frein avant, fourche, garde-boue, puis leurs équivalents arrière, cadre, moteur/carter, transmission, échappement, réservoir, selle, porte-bagages, phare, clignotants, commandes, compteurs et rétroviseurs. Pour le pilote : anatomie/posture, chaque vêtement, chaussures, casque, sac et attaches. La même règle s’applique ensuite aux façades et objets de rue. Cette première décomposition doit encore être développée pour toutes les familles du dossier.

Travailler sur une pièce active. La réplication procédurale et l’assemblage viennent après l’examen de l’exemplaire. Le script est un outil de construction ; ajouter des primitives ou augmenter leur résolution ne constitue pas une preuve de fidélité.

## Conditions de passage

1. **Référence suffisante.** Identifier l’objet et la variante, distinguer cotes publiées et estimations ; disposer des vues utiles de face, profil et détails. Inscrire ce qui reste inconnu. Une photo globale ne justifie pas d’inventer les détails invisibles.
2. **Forme isolée.** Construire la silhouette, les sections, épaisseurs, ajours, raccords et fixations. Examiner d’abord un rendu sans textures. Comparer à des références de cadrages proches, sans prétendre à une superposition métrique quand la focale est inconnue. Corriger avant le matériau.
3. **Matière isolée.** UV à l’échelle, couleur, rugosité, relief et détails localisés. Distinguer caoutchouc, peinture, métal brut/poli, plastique ou tissu. Les variations doivent suivre leur fabrication et leur usage ; un bruit uniforme ne remplace pas la matière. Conserver droits et provenance.
4. **Relecture visuelle.** Vues rapprochées frontale, latérale et trois quarts, lumière fixe, photo documentaire distincte du rendu. Noter chaque écart et sa correction. Une lacune critique de forme ou matière renvoie à l’étape concernée. Pas de score arbitraire de réalisme.
5. **Vérification moteur.** Inspecter la même pièce, sous éclairage de contrôle puis dans son assemblage. Contrôler normales, reflets, ombres, alpha, points de contact et mouvement utile. Le rendu studio seul ne clôt pas cette étape.
6. **Optimisation contrôlée.** Après l’exemplaire détaillé, dériver géométrie, textures et LOD de jeu. Comparer à nouveau après cuisson et compression, à la distance du joueur. Le fichier léger doit préserver l’apparence utile.

Tenir séparément intégrité technique, comparaison visuelle interne et réception utilisateur. Continuer les corrections déjà autorisées sans demander une permission pour chaque vis. Présenter une pièce de référence lorsque ses défauts critiques connus ont été traités, avec les réserves encore ouvertes. Ne pas demander de recevoir un assemblage dont les pièces ne passent pas cet examen.

## Première pièce : pneu avant

Le [contrôle de départ](library/component-production.json) décrit la pièce `MOTO-TYRE-FRONT-001`. Statut actuel : références de détail insuffisantes, reconstruction à faire ; aucun nouveau pneu réaliste livré.

Sources effectivement examinées : photo Boxer 125 HD extraite du dossier (`pdf-page-16-image-3.png`, référence documentaire Bajaj) et rendu de profil du lot refusé ; générateur `assets-src/hero-lot01/build_motorcycle.py`, section roues. Le [manifeste constructeur](motorcycle-reference.json) conserve la page source et les cotes publiées. La photo n’est pas intégrée comme texture ni redistribuée dans ce document.

Constats vérifiables du modèle refusé :

- Section de pneu circulaire créée par un tore à 36 segments principaux et 8 secondaires ; elle ne décrit pas séparément flanc, épaulement, bande de roulement et portée de talon.
- Avant et arrière utilisent le même rayon de section de 40 mm. La variable `width` de la boucle n’est pas utilisée ; le modèle ne différencie donc pas leurs sections selon leurs dimensions nominales respectives.
- Quarante-deux répétitions de petits pavés sont ajoutées sans référence de dessin de sculpture. Leurs arêtes et espacement produisent un aspect artificiel.
- Couleur sombre et rugosité constantes ; pas de distinction documentée entre bande de roulement, flanc, relief de marquage ou usure.
- La source mentionne 2.75-17 à l’avant, 3.00-17 à l’arrière. Le diamètre nominal de jante de 17 pouces vaut 0,4318 m. Cette désignation ne suffit pas à déterminer le diamètre extérieur mesuré, le profil exact, le fabricant ou la sculpture du pneu.

Références encore nécessaires : flanc lisible et identification de variante, vue de face du profil, gros plan de sculpture, relation talon/jante. Les détails non identifiés restent inconnus ; ni marquage ni motif inventé ne sera présenté comme constructeur. Les ajustements artistiques éventuels resteront explicitement signalés.

Le pneu isolé sera le premier exemplaire à reconstruire après ce cadrage documentaire. La jante, le moyeu et les autres pièces suivront leur propre contrôle ; ils ne seront pas reçus implicitement avec le pneu.
