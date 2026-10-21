# Arceau de protection moteur — tube seul, candidat en gris

Pièce tubulaire native originale, appuyée sur les vues officielles [RDC125HD](https://www.bajajauto.com/fr-cd/bikes/boxer-125hd) et deux vraies photographies isolées apparentées PF231201 chez Crosland, attribuées dans [recherche](../../../creative/research/crash-guard-15-v1/README.md). Le catalogue [BM125X](https://www.bajaj.club/catalog_file/BOXER-BM-125-X.pdf), feuille55/planche44, distingue cet arceau du crochet JA231201 et de l’entretoise JA231202. Identité/code courant RDC non certifiés ; aucun pixel photographique redistribué ou utilisé comme texture.

**Tube seul** : traverse supérieure continue d’apparence, six cintres arrondis vers deux retours inférieurs, parois finies et deux bouches latérales observées près des futures terminaisons. La platine centrale et les deux embouts pliés soudés sont encore **non fabriqués** et seront traités séparément ; le second trou de l’embout vu de chant ne devient pas un miroir certifié. Aucun crochet, entretoise ou boulon incorporé. Les bouts de tube sont laissés réellement creux en attente des embouts ; cela ne prétend pas décrire un garde complet fini. Nombre réel de tronçons et soudures cachées inconnu.

Toutes dimensions sont estimées : diamètre20mm [17–26], paroi1,5mm [1,2–2,5], enveloppe construite535,6×20×275mm. Les photos ne donnent pas une métrologie. Les angles et rayons de cintre55/65mm sont des paramètres originaux, pas une norme de cintrage attribuée à Bajaj. Repère : X gauchepilote, +Y arrière, Z haut ; origine au milieu de l’axe de traverse supérieure, pose non installée. Le planY0 est une approximation de travail, pas un relevé. La largeur nominale du pneu/17pouces et l’empattement ne servent pas de mesures de ce tube.

`generate_tube.py` crée un centreline par lignes/cintres circulaires C1, sections160points, longueur échantillonnée2mm, paroi annulaire et deux ouvertures vers le lumen sur la seule paroi observée. Manifold est une opération de construction originale ; son résultat est une entrée auteur traçableNPZ, pas un maillage tiers. Une phase de demi-secteur du cutter évite les sommets exactement superposés de la première tentative ; aucune suppression de triangle dans les buffers. `build.py` importe cette géométrie auteur en mesh éditable, construit les normales analytiques des vrais tubes/coupes/annuli et UV physiques de référence10mm. Aucun smoothing hérité ou réparation GLB.

Depuis la racine dans une copie isolée :

```sh
python assets-src/moto-components/engine-protection-hoop/generate_tube.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-hoop/build.py
node assets-src/moto-components/engine-protection-hoop/check_export.mjs
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-hoop/render.py -- --view=quarter --view=front --view=reverse-quarter
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-hoop/render.py -- --reflection --view=bend-detail --view=mouth-detail --view=terminal-lumen-detail
```

Collection `WEWA_ENGINE_PROTECTION_HOOP_TUBE_ISOLATED` ; studio séparé non exporté. Les sources ne lient aucune bibliothèque Blender externe. Le contrôle GLB lit vrais buffers : fermeture/χ−4/volume/conservation source, pas d’aire ou UV nulle, normales/tangentes ; les cinq rayons vérifient bouches, paroi intacte et lumens, sans qualifier montage, résistance ou protection de personne. Un objet valide ne vaut pas réception artistique ni fidélité de variante. Pas de LOD/iPhone physique ou réception artistique acquis.

## Peinture candidate et baseline préservée

La baseline publique `g3-master-v1` conserve les deux binaires et contrôles gris exacts avant G4. La matière propre est une interprétation optique : base linéaire(.006,.007,.008), métal0, rugosité.24, couche.18/rough.12, grain estimé RMS.3µm, normalstrength.10. Deux cartes originales512², tuileauteur10mm, seed15201 ; pixels embarqués comparés aux originaux, pas poussière ou défaut de photo. La finition intérieure non vue reste estimée, sans grade de peinture/acier ou réflectance mesurés. Les grands reflets blancs du studio ne sont pas de l’albédo copié dans la couleur.

Après restitution de la baseline et revue rattachée à ses SHA, dans une copie isolée :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-hoop/material.py
node assets-src/moto-components/engine-protection-hoop/check_export.mjs
node assets-src/moto-components/engine-protection-hoop/check_material_preservation.mjs
python assets-src/moto-components/engine-protection-hoop/inspect_material.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-hoop/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-hoop/render.py -- --material-preview --view=quarter --view=reverse-quarter --view=bend-detail --view=mouth-detail
```

Le comparateur vérifie POSITION/NORMAL/UV/TANGENT/indices/matrices effectivement identiques G3→PBR, pas seulement le volume. Le préflight caméra est évalué avant rendu ; première recette de macro trop proche conservée dans `diagnostics/render-first-camera.py` et diagnostic de recherche. Les vues entières et le premier reflet de cintre restent attribués à cette recette ancienne, les deux macros de bouche reculent leur caméra sur le même axe sans déformer la source.

Après lecture des aperçus et gel explicite `record.py --freeze`, cinq vues1400×1000/96samples checkpointées :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-hoop/render.py -- --final --view=quarter --view=front --view=reverse-quarter --view=bend-detail --view=mouth-detail
```

`record.py` conserve une liste explicite des seuls inputs/proofs auteur, avec recherche indépendante attribuée à son auteur ; jamais de collecte récursive des preuves moteur ROOT. Les cinq PNG doivent être effectivement relus avant fermeture de revue. Un tube construit ne termine pas le garde complet : platines/embouts et soudures manquent encore, montage et fonction ouverts.
