# Instruments v3 — normales des deux vitres

La v3 corrige les reflets segmentés observés sur la v2. Les cinq témoins Cycles conservés montrent que le lissage héritait de la tranche verticale jusque dans la face du verre. Séparer ces transitions corrige les segments sous les mêmes sources de lumière ; cacher la lèvre ne les corrige pas. La lunette opaque conserve son lissage, car son durcissement expérimental rendait la bordure angulaire.

Seules les arêtes de normales des deux vitres sont séparées dans la source. Le seuil de travail 30° est une règle de construction, aucune spécification constructeur. Profils, épaisseurs, géométrie, UV, matières/IOR/transmission, graphismes, pose et commandes restent inchangés. Dans le GLB, chaque vitre reçoit 384 sommets supplémentaires pour porter les normales discontinues : les buffers de positions/indices sont réorganisés, mais les positions de tous les coins de triangles physiques restent bit-identiques. Les 173 autres nœuds de maillage conservent leurs attributs, indices, matières, images et matrices bit-identiques. L’export conserve 56615 triangles, tous d’aire positive.

Les études USB r2, leur grain original et les marquages v2 sont conservés. Les variantes constructeur restent conditionnelles : la photo publiée sur la page RDC 125HD porte un nom BM150 ; les états 1–5 sont une démonstration d’affichage, pas une certification du nombre de rapports. Toutes les dimensions physiques, courbures et matières détaillées restent estimées. Odomètre statique, capuchon fermé, câblage et connecteur cachés non inventés.

Source `instruments-v3.blend`, export `instruments-v3-inspection.glb`. Contrat `controls-v3.json`, paramètres `parameters-v3.json`, provenance `provenance-v3.json`. Revue `creative/reviews/instruments-v3/`. Les sources v1/v2 restent intactes ; les rendus v2 sont des preuves historiques du défaut optique. Les vues v3 sont déclarées réalisées uniquement après leurs checkpoints PNG/EXR et relecture. Aucun contrôle technique ne vaut réception artistique ou qualification iPhone physique.

Commandes depuis la racine :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instruments/build_v3.py
node assets-src/moto-components/instruments/check_export_v3.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instruments/check_interfaces_v3.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instruments/render_v3.py -- --preview
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instruments/preview_optics_v3.py
```
