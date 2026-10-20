# Commodo gauche v2 — correction des pictogrammes

La photo liéeJB401400 montre5rayons par pictogramme phare, une formeDavec arc, et un pavillon de klaxon allongé avec boucle ovale ajourée. Les symboles génériques à3traits/triangle de lav1 ont été remplacés par des contours vectoriels éditables. La fonction reste celle d'une variante liée ; le numéro exact du commodoRDC actuel n'est pas certifié.

Source `657ecbdb13f48f9eb59a354ed7ebfba2ab05a7ac7d6b6e7c7ced8cb33b610ea4` ; export `145a1464a83b0454eb2116e0c8b18cd51c972a9c5b74d5e5ca08624b2bd8f1d3` ; 16414triangles, glTF0erreur/0avertissement.

- La sourcev1 est ouverte par empreinte et conservée intacte. Seules10anciennes courbes de pictogrammes sont remplacées par3maillages de contours ; leurs courbesBézier originales restent éditables dans une collection de construction masquée.
- Le [registre vectoriel](../../research/switchgear-left/marking-vector-contours-v2.json) conserve les boîtes natives, composantes et boucles fermées de la photo privée1000×1000. Le seuil155 et la simplification0,65px aident le traçage, sans prétendre à un relevé physique/calibrage. Aucune phototexture.
- Chaque sommet d'encre est reprojeté sur la peau réelle avec une épaisseur18µm estimée. Les positions/échelles restent des hypothèses ; le pictogramme supplémentaire de la variante liée n'est pas ajouté comme certitude.
- `annotation-only-change-check.json` prouve que10nœuds exportés sont bit-identiques :7corps rigides, TURN et les2flèches. Positions/normales/UV/tangentes/indices, matières/images et matrices sont identiques. Les pivots et commandes ne changent pas. `source-geometry-check.json` contient aussi les signatures source avant/après.
- Les preuves de forme, matières et cinématique des corps renvoient à lav1 avec cette identité explicite ; aucun passage artistique n'est hérité. Les tangentes inutilisées des matières sans normalmap sont supprimées ; aucune réparation sur corps n'est requise.
- `glyph-structure-check.json` sonde les maillages réels : les cinq traits de chaque phare existent, les quatre intervalles et les intérieurs des D/du klaxon sont vides. L’encre ne fait pas l’objet d’une qualification de solide mécanique.
- Les deux vues ciblées réellement produites sont listées progressivement dans `render-report.json` : `markings-front.png` et `markings-grazing.png`,1100×1000/Cycles96/OIDNCPU. Les vues de corps lav1 restent dans leur révision ; pas de rendu complet superflu.

Reproduction depuis la racine :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/build_markings_v2.py
node assets-src/moto-components/switchgear-left/check_export_v2.mjs
node assets-src/moto-components/switchgear-left/check_annotation_diff_v2.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/render_markings_v2.py
```

Commandes exportées : `assets-src/moto-components/switchgear-left/controls-v2.json`. CapturesBabylon gérées séparément par la revue commune. Pas de réception artistique, de qualification électrique ou d'iPhone physique acquise.
