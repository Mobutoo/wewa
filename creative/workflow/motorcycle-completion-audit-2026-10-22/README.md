# Revue complète de la moto — 22 octobre 2026

**La moto n'est pas terminée.** L'extérieur détaillé est largement présent, mais la transmission finale, des raccords/fixations, le fonctionnement mécanique et l'intégration au jeu restent ouverts.

Périmètre relu : **205 fiches candidates, 18 lots, 30 paquets et 162 parents de l'assemblage v4**. 140 ressources courantes vérifiées par taille et SHA-256. Les fiches historiques ne sont pas des pièces physiques terminées.

L'assemblage comporte 502 nœuds maillés, 541 occurrences de primitives et 25,463,261 triangles. Aucun skin ni clip d'animation. Les 541 maillages indiqués dans les captures Babylon correspondent ici aux occurrences de primitives après découpage à l'import, pas à 541 pièces physiques.

Le moteur et l'optique concave sont déjà corrigés en v4. Le jeu charge encore l'ancien lot01 dans `app/public/models/motorcycle.glb`. Le modèle détaillé est une livraison de revue séparée.

Nouvel élément réalisé : [candidat LOD](../../../assets-src/moto-components/motorcycle-lod-review-v1/motorcycle-lod.glb), **843,358 triangles**, 39.18 Mo, zéro erreur glTF. [Méthode et comparaison](../../reviews/motorcycle-lod-review-v1/README.md). Les mêmes 162 parents et toutes les primitives sont conservés ; cela ne clôt pas le budget de la scène ni les essais mobiles.

## Les trente paquets confrontés à l'assemblage courant

Chaque ligne reste ouverte. La colonne « manque » distingue les études isolées et les éléments réellement assemblés ; les sources/poses exactes de tous les parents sont dans le rapport JSON.

| Paquet | État vérifié et manque restant | Donnée nécessaire |
|---|---|---|
| P01 — Cache latéral gauche | Retours, attaches arrière, épaisseur et montage sur la variante RDC à confirmer. | Revers et chants du cache, vue montée et points de fixation. |
| P02 — Porte-bagages | Plateforme et rails présents en candidat ; variante de plateau, terminaisons, ancrages et soudures non qualifiés. | Dessus et dessous du plateau RDC retenu, macros des ancrages. |
| P03 — Garde-boue avant | Coque, bavette et renfort présents ; fixations, station montée et garde à la roue non vérifiées. | Dessous et profil montés, mesures de dégagement avec fourche et roue. |
| P04 — Cache latéral droit | Peau extérieure présente ; fond, pattes de retenue et pose réelle ouverts. | Revers et profils de la pièce exacte, montage visible. |
| P05 — Support de feu arrière | Support présent ; empilage du silentbloc, collier et gaine non validés comme montage. Une étude isolée ne prouve pas sa présence dans cet assemblage. | Collier physique, gaine face/dos/profil et empilage comprimé monté. |
| P06 — Phare principal | Réflecteur concave, ampoule extérieure et vitre striée déjà corrigés en v4 ; identité exacte, profondeur, douille et contacts non certifiés. | Optique exacte démontée recto/verso/profil, profondeur et siège de douille mesurés. |
| P07 — Feu arrière | Corps et lentille présents ; source lumineuse, reliefs optiques et retenues non qualifiés. | Lentille démontée et fixation séparée, vues opposées du feu monté. |
| P08 — Support de plaque | Traverse et arceau présents ; sièges, écrous, soudures et assemblage réel non reçus. Les jeux de présentation restent des hypothèses. | Macros opposées des jonctions, filetage/sièges et empilage réel. |
| P09 — Clignotants avant | Deux extérieurs présents avec répétition provisoire autorisée ; transition corps/tige, conducteurs, ampoules et fixations ouverts. | Vues opposées des racines, sorties de fils et faces de fixation. |
| P10 — Clignotants arrière | Deux tiges indépendantes et extérieurs répétés présents ; corps/lentilles repris de l'avant à titre provisoire, adaptateurs et fixations non qualifiés. | Références arrière exactes, vues des reliefs optiques et des montages. |
| P11 — Plaque et accessoires arrière | Plaque et catadioptre présents ; visserie, éclairage et empilage réel encore à établir. | Plaque montée, visserie et accessoires réellement observés sur la référence. |
| P12 — Bouchon et alimentation du réservoir | Réservoir et enveloppe du bouchon présents ; robinet et levier étudiés séparément, trajet de durite et interfaces non assemblés/qualifiés. | Robinet exact face/dos/profil et trajet monté continu de la durite. |
| P13 — Dessous et supports de selle | Dessous observé, patte et socle présents ; nervures/attaches complètes, tampons et variante exacte encore ouverts. | Sous-face et profil de la selle RDC, points de contact et fixations montés. |
| P14 — Sélecteur de vitesses | Extérieur du sélecteur présent ; cannelures, serrage et retenues non qualifiés. | Macros arrière/profil du moyeu, vis de serrage et axe réel. |
| P15 — Pédale et tringlerie de frein arrière | Pédale et huit éléments de tringlerie assemblés avec correction d'axe ; filetage, goupilles/empilages et course réelle non vérifiés. | Extrémités et empilages montés, séquence de débattement du frein. |
| P16 — Repose-pieds | Supports, parties métalliques et caoutchoucs présents ; enveloppes caoutchouc estimées, charnières/axes/goupilles et contacts à qualifier. | Dessous du caoutchouc exact et charnières isolées puis montées. |
| P17 — Béquilles et ressorts | Corps extérieurs présents ; ressorts/gaines et quincaillerie étudiés séparément, conflits et empilages de pivots non résolus dans l'ensemble. | Pivots et ressorts montés, vues isolées des gaines et butées. |
| P18 — Moteur extérieur | Volume supérieur/arrière désormais complété et relié au pied du cylindre ; joints des carters apparentés et variante RDC non qualifiés. Le moteur n'est plus décrit comme entièrement absent. | Macros des joints et dessous/avant sans occultation, identification des carters exacts. |
| P19 — Carburateur | Corps, cuve et entrée de câble présents ; patte/pivot de commande, durites, clips et raccords restent partiels. | Revers de commande et trajet monté des durites, macros des raccords. |
| P20 — Admission et échappement | Boîte à air, manchon, admission et échappement présents ; axes, colliers, attaches et empilages non qualifiés. | Manchon exact monté et revers du support d'échappement. |
| P21 — Moyeu arrière et porte-couronne | Face de porte-couronne présente en étude ; section inverse, poche masquée et amortisseurs de couple non assemblés/qualifiés. | Revers/section du porte-couronne et montage comprimé des caoutchoucs. |
| P22 — Couronne, pignon et chaîne | Transmission finale absente de l'assemblage v4. Les études isolées ne résolvent pas la couronne six trous face au porte-couronne quatre trous, le pignon ou la chaîne articulée complète. | Identifier le couple couronne/porte-couronne RDC compatible, déport, entraxes et chaîne exacts avant fabrication/répétition. |
| P23 — Axe arrière et tendeurs | Axe, tendeurs et flasque présents ; colliers, racines des tiges, perçages et empilages réels non qualifiés. | Pièces exactes déposées et vues axiales, montage et liaisons réelles des tiges. |
| P24 — Axe avant et frein de roue | Axe borné 225 mm, levier, flasque et roue présents ; variante des colliers, entraînement compteur et compatibilité fourche/frein non établis. | Empilage exact UG/RDC démonté puis monté, références et sièges de l'entraînement compteur. |
| P25 — Fourche et direction | Deux côtés et direction présents ; raccord soufflet/coulisseau, empilage/sièges et support de phare non qualifiés. | Sections et variante compatibles, dessous/profil des bouchons et support physique exact. |
| P26 — Cadre, bras oscillant et pare-moteur | Cadre intérieur/batterie et racine observée de l'oreille de carter de chaîne ajoutés ; revers/siège/vis, autres soudures et liaisons non qualifiés. | Macros opposées de l'attache nue, pivot et jonctions du cadre/bras/protection. |
| P27 — Amortisseurs arrière | Paire présente par répétition provisoire autorisée ; ancrages, vis/rondelles et débattement non qualifiés. | Fixations montées gauche/droite et course sous compression. |
| P28 — Fixations guidon et leviers | Guidon, pontets et commandes présents ; études isolées de silentblocs/rondelles ne prouvent pas leur montage/compression, fixations et dégagements ouverts. | Dessous/profil axial des pièces exactes et empilage comprimé mesuré. |
| P29 — Câbles et faisceau | Départs et continuations visibles A/B présents ; rôle des branches, extrémités, clips, trajet complet et mou au braquage non établis. | Parcours continus montés de bout en bout et vues en butées de direction. |
| P30 — Visière et cockpit | Instruments, visière, rétroviseurs et contacteur présents ; retours, fixations, entraxes et dégagements à qualifier. Pas de rig de conduite dans l'assemblage statique. | Revers de visière, fixations macro, centres mesurés et contrôle des mouvements du cockpit. |

## Vérifications transversales

- **Gabarit et conventions de mesure** : L'export détaillé occupe environ 1,976 m de long, 0,811 m de large et 1,371 m de haut avec tous ses éléments. Le dossier constructeur indique 2,016 × 0,740 × 1,134 m ; la convention des rétroviseurs et de hauteur n'est pas précisée. Ce gabarit reste à qualifier ; aucune déformation globale n'est faite pour forcer un accord.
- **Pneus, jantes et pièces de base** : Candidats présents dans les 205 fiches et l'assemblage ; sections, portées et identité de variante ne sont pas reçues. Leurs réserves restent dans l'inventaire complet.
- **Mouvements et interfaces** : L'assemblage v4 n'a ni skin ni animation glTF. Braquage, rotation des roues, suspension et continuité des câbles restent à produire avec pivots et courses justifiés.
- **Intégration au jeu** : app/src/world.ts charge app/public/models/motorcycle.glb, ancien lot01 refusé. La moto détaillée et son LOD sont des candidats séparés ; l'intégration exige repères/pivots, coût mesuré et contrôle de conduite.
- **Optimisation** : Nouvelle dérivation allégée avec mêmes pièces/poses et comparaison visuelle ; coût de tous les passages, scène représentative et essais Safari physiques restent à qualifier.
- **Réception artistique** : Aucune réception artistique explicite de cette révision n'est enregistrée. Les contrôles automatiques n'attribuent pas cette réception.

[Inventaire lisible de toutes les fiches et des 18 lots](INVENTORY.md) · [Rapport complet : 162 parents, ressources et empreintes](report.json) · [Périmètre et constats éditables](scope.json) · [Livraison détaillée v4](../../reviews/motorcycle-assembled-v4/README.md).

Le contrôle documentaire ne prétend pas une nouvelle inspection visuelle de chaque ancien rendu. Les variantes, estimations et inconnues restent explicites. Aucun paquet n'est clôturé par un contrôle automatique.

```sh
python tools/check_motorcycle_completion.py --write
```
