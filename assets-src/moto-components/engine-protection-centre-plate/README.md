# Platine centrale de l’arceau — candidat isolé

Source originale de la tôle à deux ouvertures visible sur [Crosland PF231201](https://www.croslandrepuestos.pe/protector-de-piernas-pf231201/p), photographies174419/174418, et dessin [BM125X](https://www.bajaj.club/catalog_file/BOXER-BM-125-X.pdf) feuille55/planche44. Ces vues sont réellement ouvertes, URLs/SHA complets dans [recherche indépendante](../../../creative/research/crash-guard-15-v1/README.md). Code/montageRDC exacts non établis. Aucun pixel de photo ou maillage tiers.

La face centrale, les deux trous et le bord inférieur arrondi sont observables. Le retour supérieur, l’envers et sa liaison soudée sont partiellement occultés : le pli90° de section constante est une **estimation originale**, pas un relevé caché. Largeur100mm [85–115], hauteur hors tout35,5mm, épaisseur2mm [1,5–3], rayon moyen3,5mm [2–6], trous7mm [6–10], entraxe80mm estimé. Le M6 de crochet ne cote pas automatiquement ces trous. Les parois, retours et chants0,12mm sont géométriques, pas un bloc plein ni un motif dessiné.

Collection `WEWA_ENGINE_PROTECTION_CENTRE_PLATE_ISOLATED`, repère localX largeur/gauchepilote,+Yversretour/arrière,Zhaut, origine centre de faceplane de travail. Aucune pose installée ou contact au tube acquis. Le tube, les deux embouts, les cordons, le crochet/entretoise et les écrous ne sont **pas** inclus ; sources séparées, pas garde complet.

`profile_shape.py` garde les vrais bouts d’arcs et échantillonne le contour développé avant cintrage. `build.py` produit capCDT contraint, deux vrais ajours, rayons de chant à indices partagés et épaisseur finie ; la transformation du pli et des normales est analytique avec facteur métrique. Les vrais plans utilisent leurs normales géométriques plates ; les courbes conservent l’interpolation auteur. Source éditable sans bibliothèque externe ni patch de buffers.

Dans une copie isolée depuis la racine :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-centre-plate/build.py
node assets-src/moto-components/engine-protection-centre-plate/check_export.mjs
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-centre-plate/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-centre-plate/render.py -- --view=quarter --view=front --view=reverse-quarter
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-centre-plate/render.py -- --reflection --view=fold-detail --view=hole-detail --view=lower-edge-detail
```

Les premiers gris c01266a7/ba70455d restent en diagnostic : de longs contours non subdivisés formaient des faces diagonales sous le retour. Cette géométrie est reprise avant matière. Les deux anciennes recettes dans `diagnostics/` doivent être restaurées à leur nom d’origine dans une copie isolée pour rejeu, jamais sur un gel. L’échantillonnage actuel129232triangles supprime ces faux retours ; l’epsilonCDT n’a pas été augmenté.

Les plans géométriques ont composante transverse0, mais les normales de coin stockées gardent4,823e−6 mesurés : l’ancienne cible1e−6 est explicitement non atteinte, pas remplacée par une mesure OEM ou une réception artistique. Les reflets et la silhouette restent les critères de décision. Fermeture, volume+,rayons de trous, UV et tangentes ne prouvent ni montage, résistance, métriqueRDC, LOD ni iPhone physique.

## Matière et revue finale

Peinture noire candidate cohérente avec le tube, sans réflectance mesurée : base linéaire(.006,.007,.008), métal0, rough.24, coat.18/rough.12. Deux cartes512² originales (tile10mm, seed15202, relief RMS estimé.3µm/normalstrength.10), aucune usure ou albédo photo. Pixels embarqués et canaux glTF vérifiés ; POSITION/NORMAL/UV/TANGENT/indices/matrices exactement conservés depuis la baseline publique `g3-master-v1`.

Après restauration de cette baseline et de sa revue gris dans une copie isolée :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-centre-plate/material.py
node assets-src/moto-components/engine-protection-centre-plate/check_export.mjs
node assets-src/moto-components/engine-protection-centre-plate/check_material_preservation.mjs
python assets-src/moto-components/engine-protection-centre-plate/inspect_material.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-centre-plate/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-centre-plate/render.py -- --material-preview --view=quarter --view=reverse-quarter --view=fold-detail --view=hole-detail
```

Le premier macro de pli sans bande spéculaire utile est conservé `diagnostic-unhelpful-fold-reflection`, avec recette dans `diagnostics/render-before-fold-camera.py`. Le témoin corrigé aligne caméra/strip original àX.040 pour lire la vraie courbure, uniquement en diagnostic de reflets, sans modifier la géométrie ou la matière source. Les anciens gris et deux autres macros sont attribués à leur recette initiale préservée.

Après lecture des quatre aperçus et gel explicite `record.py --freeze`, cinq vues1400×1000/96samples checkpointées :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-protection-centre-plate/render.py -- --final --view=quarter --view=front --view=reverse-quarter --view=fold-detail --view=hole-detail
```

Listes d’inputs/proofs explicites dans `record.py`, recherche indépendante attribuée séparément. Aucune collecte des preuves ROOT ni réception automatique par validité numérique. La platine seule et son profil estimé ne terminent pas l’arceau ou ses interfaces.
