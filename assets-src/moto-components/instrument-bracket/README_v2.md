# Support de compteurs — candidat v2

Révision distincte du candidat PF402404 de variante BM150 liée. Les fichiers de la v1 manifestée restent inchangés. Le modèle actuel RDC125HD USB et son empilage ne sont pas identifiés avec certitude.

La correction porte sur la nervure du pont inférieur : ses côtés sont maintenant parallèles et ses extrémités arrondies, selon la photo Matriz et l’audit indépendant. Les deux petites nervures des bras restent distinctes ; leur largeur n’est pas déduite de celle du pont. Le contour en U, les trois passages ouverts, les deux têtes et les autres formes de travail sont conservés.

Les pointes documentaires approximatives sont(706,819) et(822,746) dans la photo1210², incertitude≈6px. La géométrie originale utilise une capsule triangulée avec points intérieurs avant formage, puis une union contrôlée. L’échelle artistique0,18mm/pixel n’est pas une calibration photo. Largeur4,8mm(plage3,6–6mm), saillie1,1mm(plage0,6–1,6mm), épaisseur2,3mm(plage1,8–3,2mm) : **estimations**. La section de pressage de la face cachée reste inconnue.

Source éditable : `instrument-bracket-v2.blend`. Export évalué : `instrument-bracket-v2-inspection.glb`. Collection `WEWA_INSTRUMENT_BRACKET_ISOLATED_V2`, plan localXY, face photographiée+Z, origine entre les deux centres de têtes. Aucune pose cockpit installée appliquée ni compatibilité OEM annoncée.

La matière noire conserve un microrelief original à échelle estimée ; aucun pixel photographique n’est utilisé. Les normales tangentielles et les canaux rugosité/métal sont effectivement embarqués. Les contrôles vérifient fermeture, volume, trois ouvertures, aires des vrais triangles et repères tangents. Ces résultats techniques ne réceptionnent ni la forme ni le montage.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instrument-bracket/build_v2.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instrument-bracket/material_v2.py
node assets-src/moto-components/instrument-bracket/check_export_v2.mjs
python assets-src/moto-components/instrument-bracket/inspect_material_v2.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instrument-bracket/render_v2.py
```
