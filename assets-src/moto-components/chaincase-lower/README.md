# Demi-carter inférieur apparenté PF181200 — construction isolée

Cette pièce est construite séparément de la coque supérieure, avec un nouveau contour inférieur, la grande ouverture de bouchon, deux petites bouches de fixation candidates et une demi-arche ouverte vers le haut. Aucun miroir du maillage supérieur, bouchon, vis, chaîne ou mécanisme caché n'est intégré. Les retours, raccords de fixation et pressages observés sont examinés en gris/reflets avant matière ; aucun gel ne réceptionne la pièce entière.

Références physiques : [kit36PF0011 vue extérieure1040836](https://motozilla.com.ua/wa-data/public/shop/products/82/76/227682/images/1040836/1040836.970.jpg) et [face opposée1040837](https://motozilla.com.ua/wa-data/public/shop/products/82/76/227682/images/1040837/1040837.970.jpg). D15kit21 relie ce kit à PF181202/PF181200 ; le code individuel et un numéro de série ne sont pas lisibles sur la photo. La forme avec le grand trou est attribuée conditionnellement à l'inférieur. L'identité 125HD RDC n'est pas établie par ces vues BM/BMX150 apparentées.

Toutes les dimensions sont des estimations bornées dans `parameters.json`, sans calibration pixel→mm : profil nominal590mm avant rebords, arrière105/74mm de rayons, feuille0,9mm et profondeur47mm. La grande ouverture38mm et les petits passages7mm ne sont pas des cotes du fabricant. L'égalité de quelques valeurs d'enveloppe avec le candidat supérieur est une hypothèse de contexte et ne démontre aucun emboîtement. La bouche du bouchon est réellement ouverte ; son siège exact et le bouchon restent distincts/inconnus.

Repère en mètres : centre de demi-arche arrière0, avant−Y, haut+Z, normale extérieure+X provisoire. La pose, ligne de chaîne, engagement des vis et recouvrement supérieur restent ouverts. Collection `WEWA_CHAINCASE_LOWER_ISOLATED`. Le studio indépendant n'est pas exporté. Source native par contour contraint/trous et points distribués, surfaces formées, deux peaux finies partagées et chants de fermeture ; aucun fond masquant la cavité.

Dans une copie isolée, depuis la racine :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-lower/build.py
node assets-src/moto-components/chaincase-lower/check_export.mjs
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-lower/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-lower/render.py -- --view=outer-quarter --view=outer-side --view=inner-quarter
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-lower/render.py -- --reflection --view=rear-return-detail --view=front-hole-detail --view=inspection-hole-detail
```

Blender4.3.2, numpy embarqué, dépendances Node verrouillées du dépôt. Ne jamais rejouer sur un gel historique. Aucune réception artistique, matière mesurée, montage, résistance, LOD ou iPhone physique n'est acquise.


Le panneau rectangulaire est un relief original borné sans étiquette, texte ou pixels vendeurs. Les deux bandes C lisibles correspondent au pressage extérieur et au bord de demi-arche retourné ; leurs profils exacts restent inconnus. La grande bouche a seulement le chant de la feuille, sans siège caché inventé. Le col avant est un volume continu de surface candidat, non une preuve que la vraie pièce est emboutie plutôt qu'assemblée.

Les premières constructions ont été arrêtées avant rendu sur un petit croisement de Bézier puis une rupture de tangente arc→chant. Les corrections sont faites dans les courbes auteur et recontrôlées, sans réparation du GLB ni hausse de tolérance. La recherche conserve les diagnostics et archives privées. Les sept offsets2D échantillonnés ne certifient pas toute auto-intersection3D ni la formabilité.


La finition candidate reprend uniquement la palette de revue du supérieur : base linéaire(.43,.45,.47), métal0, rugosité.32, couche claire.12/rough.20. Deux cartes périodiques originales512² NonColor, graine16121 et tuile de référence10mm ; RMS de hauteur.2µm avant strength.12, jamais une mesure d'OEM. Les pixels photo/étiquette ne sont pas employés. La densité UV physique reste approximative dans les retours formés.

Pour rejouer PBR dans une copie isolée, restaurer les deux binaires de `g3-master-v1/` à la racine du composant, ses trois JSON de contrôle dans la revue, conserver gray-review.json avec ses SHA G3 et les sept vrais PNG ; puis lancer :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-lower/material.py
node assets-src/moto-components/chaincase-lower/check_export.mjs
node assets-src/moto-components/chaincase-lower/check_material_preservation.mjs
python assets-src/moto-components/chaincase-lower/inspect_material.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-lower/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-lower/render.py -- --material-preview --view=outer-quarter --view=inner-quarter --view=front-hole-detail --view=inspection-hole-detail
python assets-src/moto-components/chaincase-lower/record.py --freeze
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/chaincase-lower/render.py -- --final --view=outer-quarter --view=inner-quarter --view=rear-return-detail --view=front-hole-detail --view=inspection-hole-detail
python assets-src/moto-components/chaincase-lower/record.py
```

Le contrôle de conservation exige positions, indices, matrices, normales, UV et tangentes G3 identiques dans les vrais buffers après matériau. Les Library Blender externes sont refusées et les images nécessaires doivent être packées et relatives. `record.py` ne collecte que ses listes explicites A, jamais les rapports moteur ROOT. Son dernier passage exige la lecture réellement consignée des cinq finales96 et leurs checkpoints. Il ne réceptionne ni les cotes, ni la fabrication/forme exacte du col, ni le siège de bouchon absent, ni la moto assemblée.
