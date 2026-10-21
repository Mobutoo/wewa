# Commodo gauche v3 — contours lissés des pictogrammes

La v2 conserve la bonne structure des symboles mais ses contours reprennent des marches de raster. Cette révision remplace uniquement les trois pictogrammes visibles par des boucles Bézier cubiques lisses et éditables. Les cinq rayons de chaque phare, les ajours des D et la boucle du klaxon restent présents. Les sources/exports v1 et v2 restent historiques.

Source `switchgear-left-v3.blend`, SHA256 `a8cde7758ea9c96f2eac7c2d7ba817b4a353935a0a62ac2d53d0003e8e9bdeea` ; export `switchgear-left-v3-inspection.glb`, SHA256 `25fe15ea6d6d5aeebf64300f6428b683596d9f3fbff0f3b236ee9c5177059280`. Collection `WEWA_SWITCHGEAR_LEFT`. Commandes `controls-v3.json`, provenance `provenance-v3.json`.

Les D et le klaxon utilisent des splines cubiques périodiques C2 ajustées aux contours documentaires v2. Les dix rayons sont ajustés individuellement comme des capsules à côtés droits et extrémités cubiques circulaires, avec six nœuds chacune ; ces jonctions sont tangentes G1, sans prétendre à une continuité C2. Cette contrainte retire les ondulations issues du raster. Les écarts symétriques maximaux sont contrôlés sur les vraies courbes cubiques : borne1,3px pour les rayons,1px pour les D et1,25px pour le klaxon. Avec la simplification v2 de0,65px, le majorant observé reste1,82px, dans notre incertitude native de travail2px. Ce ne sont ni des mesures physiques ni une certification de variante.

Le registre `creative/research/switchgear-left/marking-vector-contours-v3.json` contient points, poignées, bornes, aires orientées et absence de croisements des16boucles. La photo liéeJB401400 reste privée et aucune phototexture n’est utilisée. L’identité exacte du commodo RDC actuel n’est toujours pas établie.

La preuve `creative/reviews/switchgear-left-v3/annotation-only-change-check.json` compare les buffers réels : sept corps rigides, TURN et deux flèches bit-identiques à la v2, avec positions/normales/UV/tangentes utiles/indices/matières/images/matrices et commandes conservés. Les preuves de corps/interfaces restent valables par cette identité ; aucune réception artistique n’est héritée. `glyph-structure-check.json` sonde les traits, les quatre espaces entre eux et les ajours dans les vrais maillages. `actual-triangle-area-check.json` teste toutes les primitives, encre comprise : aucune aire nulle. Export22230triangles, glTF0erreur/0avertissement. Seules les tangentes inutilisées sans normalmap sont retirées ; aucune tangente utile réparée.

Deux vues rapprochées réelles96échantillons sont sauvegardées et relues pour cette correction seulement : les deux phares, puis le klaxon. Elles sont enregistrées dans `render-checkpoints.json` après sauvegarde effective, avec SHA source/configuration/PNG/EXR et canaux lus dans l’en-tête EXR. Les rendus de corps inchangés restent dans leurs révisions précédentes. Aucun test sur iPhone physique ni réception artistique n’est acquis.

```sh
OPENBLAS_NUM_THREADS=1 python assets-src/moto-components/switchgear-left/smooth_markings_v3.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/build_markings_v3.py
node assets-src/moto-components/switchgear-left/check_export_v3.mjs
node assets-src/moto-components/switchgear-left/check_annotation_diff_v3.mjs
node assets-src/moto-components/switchgear-left/check_areas_v3.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/check_glyphs_v3.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/render_markings_v3.py
```
