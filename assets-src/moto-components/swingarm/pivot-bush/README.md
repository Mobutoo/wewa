# Bague de pivot apparentée DP171006 — candidat isolé

Une unité visible, composée de trois enveloppes fermées séparées : tube extérieur clair, anneau sombre et tube intérieur percé. La photo physique [Matriz](https://bajajmatriz.com/producto/buje-horquilla-trasera-pulsar-ns-125-135-ls-discover-125-boxer-150-bajaj) montre cette stratification ; son identité125HD RDC, le revers, les cotes, la composition, la liaison et la rigidité restent inconnus. D04/D15 donnent la référence et deux unités sur des variantes apparentées. Leur seconde image de montage est un rendu, jamais utilisée comme deuxième photo physique.

Toutes les dimensions sont estimées et bornées dans `parameters.json` : extérieur26×30mm, intérieur18,4mm/alésage14,4mm/longueur32mm. Le corps de bras n’incluait pas ces bagues ; aucune compatibilité avec son logement26mm ou le fût14mm vendeur n’est certifiée. Les interfaces idéales se touchent sans recouvrement radial positif au seuil numérique, qui n’est pas une tolérance mécanique. Aucun modèle élastique, liaison collée ou montage physique n’est simulé. Le revers non photographié prolonge provisoirement les sections.

Repère en mètres : centre0, axeX, face de revue+X ; +Yarrière, +Zhaut. Collection `WEWA_SWINGARM_PIVOT_BUSH_ISOLATED`. Studio séparé `LOCAL_NEUTRAL_STUDIO_NOT_EXPORT`, jamais exporté. Trois maillages natifs à sections arrondies analytiques, 384secteurs ; 82 944triangles, véritables parois et alésages traversants. Pas de géométrie importée, de modificateur caché ni de correction des buffers GLB. Les normales auteur dérivent de la section ; plans annu­laires et courbes gardent leur continuité.

Six cartes512² originales : normale tangentielle et ORM pour chacun des trois matériaux, NonColor, répétées et embarquées. Base extérieure linéaire(.50,.52,.55), métal1/roughness≈.34 ; intérieur(.60,.61,.63), métal1/≈.32 ; anneau sombre(.008,.009,.010), métal0/≈.58. Ce sont des réponses candidates estimées, aucune composition ou réflectance mesurée. Tuile de bruit nominale5mm ; l’échelle circonférentielle varie avec le rayon et est consignée par enveloppe. Le premier fini intérieur trop ponctué reste archivé en diagnostic privé ; la correction conserve exactement positions/normales/UV/tangentes/indices.

## Reproduction dans une copie isolée du dépôt

Blender4.3.2, Node avec dépendances du dépôt et Python/Pillow/numpy. Lancer depuis la racine ; remplacer BLENDER par son chemin local. Les commandes écrasent les sorties actives et ne doivent jamais être appliquées sur un gel historique.

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/pivot-bush/build.py
node assets-src/moto-components/swingarm/pivot-bush/check_export.mjs
```

La revue G3 existante exige exactement les empreintes de ses binaires. Pour rejouer la matière de cette révision, restaurer dans la copie isolée les deux binaires `g3-master-v1/` et son `source-geometry-check.json` vers les chemins actifs/revue avant `material.py` ; ne pas tenter de réappliquer la matière sur le source PBR. Le master est l’entrée géométrique exacte, et la recette native reste éditable. Puis :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/pivot-bush/material.py
node assets-src/moto-components/swingarm/pivot-bush/check_export.mjs
node assets-src/moto-components/swingarm/pivot-bush/check_material_preservation.mjs
python assets-src/moto-components/swingarm/pivot-bush/inspect_material.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/pivot-bush/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/pivot-bush/render.py -- --final --view=quarter --view=front --view=lip-detail
```

Les ouvertures et la fermeture sont contrôlées dans les vrais buffers, avec rayons dans l’axe et dans les parois ; images embarquées comparées aux pixels auteur ; aucune bibliothèque externe et six chemins relatifs/embarqués. Chaque PNG96 a son checkpoint source/export/script/lumière/préflight. Les PNG ne valent ni réception utilisateur, ni qualification de montage, charge, usure, LOD ou iPhone. Les preuves Babylon restent à root et ne sont pas aspirées dans notre manifeste.
