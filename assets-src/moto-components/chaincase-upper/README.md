# Demi-carter supérieur de chaîne — candidat partiel apparenté PF181202

La feuille formée, ses retours, la demi-arche ouverte, les trois passages certains et le relief circulaire plein sont construits. **L’oreille avant probable n’est pas entièrement construite** : son raccord et sa relation aux trois axes restent inconnus. Aucun quatrième axe ou dessous caché n’est inventé. Ce candidat partiel n’est ni une coque complète reçue, ni un montage avec le bras, la chaîne ou la demi-coque inférieure.

Deux vraies photographies du kit36PF0011 groupées par le vendeur : [vue1040836](https://motozilla.com.ua/wa-data/public/shop/products/82/76/227682/images/1040836/1040836.970.jpg), [vue1040837](https://motozilla.com.ua/wa-data/public/shop/products/82/76/227682/images/1040837/1040837.970.jpg). Leur code de demi-coque et un numéro de série ne sont pas lisibles. D15kit21 relie36PF0011 à PF181202supérieur/PF181200inférieur ; l’attribution supérieure reste conditionnelle par la demi-arche ouverte vers le bas et l’absence du grand trou d’inspection. Le carter fermé argenté partiellement visible sur la125HD RDC ne certifie pas seul cette identité.

Aucune cote constructeur ou mesure physique obtenue. Toutes les dimensions sont des estimations bornées dans `parameters.json` : profil de paroi590mm avant rebords, rayonAR105mm/ouverture74mm, retour48mm, feuille0,9mm. Le profil hors tout formé est plus grand à cause du retour extérieur3mm et de la demi-épaisseur ; les vraies bounds viennent du source/GLB. Les trois bouches sont estimées7mm ; le cercle fermé reste plein. L’encoche du bord libre avant, absente du premier contour, a été corrigée après relecture documentaire indépendante. Ses6mm de profondeur/24mm de haut sont des valeurs candidates bornées, jamais une échelle tirée du vendeur.

Repère en mètres : datum de demi-arche arrière0, avant−Y, haut+Z, normale extérieure de paroi+X ; pose montée et ligne de chaîne inconnues. Collection `WEWA_CHAINCASE_UPPER_ISOLATED`. Le studio séparé `LOCAL_NEUTRAL_STUDIO_NOT_EXPORT` n’est pas exporté. Une feuille native distribuée avant formage : CDT contraint avec trous et vérification d’aire, champ de nervure/pressages original, vrais retours partagés à90°, deux peaux d’épaisseur finie et parois des chants ouverts. Aucun fond fermant artificiellement la cavité, aucune pièce téléchargée ni correction des buffers GLB. La région inboard reste réellement ouverte.

Le premier état f59f7f1e…/9c092bc8… et ses six gris/reflets sont conservés en diagnostic ; les renvois exacts figurent dans `creative/research/chaincase-upper/first-g3-review.json`. Après l’encoche, le champ additionné nervure/bossage a été remplacé par une fusion positive L8 bornée et une liaison de nervure C2 pour éviter un renflement d’auteur. Le bouton demeure plein et les trois centres restent identiques ; la triangulation peut changer et aucune conservation générale des anciens indices n’est revendiquée. Le contrôle d’offsets2D écarte des croisements stricts aux seules coupes échantillonnées0…3,45mm ; ce n’est pas un certificat de formabilité ou d’auto-intersection3D.

## Reproduction dans une copie isolée

Blender4.3.2 avec numpy embarqué, dépendances Node du dépôt, Python/Pillow/numpy pour images et manifestes. Lancer depuis la racine ; remplacer BLENDER par son binaire. Les commandes écrasent les fichiers actifs et ne doivent jamais être rejouées sur un gel historique.

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-upper/build.py
node assets-src/moto-components/chaincase-upper/check_export.mjs
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-upper/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-upper/render.py -- --view=outer-quarter --view=outer-side --view=inner-quarter
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-upper/render.py -- --reflection --view=rear-return-detail --view=rib-detail --view=front-edge-detail
```

Trois passages réels, arche ouverte, relief fermé, épaisseur témoin et ouverture inboard sont contrôlés dans le source et les vrais buffers. Le retour avant−Y a son témoin frontal RAM pour exposer la morsure ; le premier témoin trop sombre est conservé, pas présenté comme preuve de déformation. Les images restent des lectures de candidat, sans score de fidélité.

Le plan de matière prévoit un fini argent peint propre original : base linéaire(.43,.45,.47), métal0, rugosité≈.32 et couche claire estimée. Ni teinte, peinture, chimie, grain ni réflectance réels ne sont mesurés. Aucune usure, étiquette ou texture photographique recopiée. La matière n’autorise aucune réception de l’oreille manquante ou du montage. Les étapes G4 et suivantes ne concernent que la surface effectivement construite ; réception artistique, LOD et iPhone restent ouverts. Les futures preuves Babylon restent attribuées à root et ne sont pas collectées automatiquement dans notre manifeste.


Pour rejouer la matière sans recalculer la géométrie, dans une copie isolée restaurer les deux binaires et trois contrôles de `g3-master-v1/` à leurs emplacements actifs, conserver `gray-review.json` et ses SHA G3, puis lancer `material.py`, `check_export.mjs`, `check_material_preservation.mjs`, `inspect_material.py` et `inspect_interfaces.py`. Le contrôle de conservation exige les attributs et indices G3 exactement identiques. `check_front_offsets.py` reproduit séparément le contrôle limité des sept offsets du contour ; il ne modifie aucun maillage.

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-upper/material.py
node assets-src/moto-components/chaincase-upper/check_export.mjs
node assets-src/moto-components/chaincase-upper/check_material_preservation.mjs
python assets-src/moto-components/chaincase-upper/inspect_material.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-upper/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-upper/render.py -- --material-preview --view=outer-quarter --view=inner-quarter --view=rear-return-detail --view=front-edge-detail
python assets-src/moto-components/chaincase-upper/record.py --freeze
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-upper/render.py -- --final --view=outer-quarter --view=outer-side --view=inner-quarter --view=rear-return-detail --view=front-edge-detail
python assets-src/moto-components/chaincase-upper/record.py
```

Le dernier enregistrement exige une lecture réelle consignée des cinq PNG 96 échantillons. G3 et G5 du composant complet restent ouverts pour l’oreille avant manquante, même si la surface partielle est techniquement contrôlée. Les finales ne transforment pas ce périmètre en coque complète. Le script historique `diagnostics/render-before-front-witness.py` est une copie d’octets : le restaurer en `render.py` dans une copie isolée avant de le rejouer, car sa résolution des chemins suppose son emplacement d’origine.
