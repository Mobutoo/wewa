# Té supérieur — candidat isolé DS181005 lié

Plaque indépendante originale reconstruite à partir de deux photos commerciales réelles. Le contour festonné, le creux supérieur, les cinq passages moyens/grand et les deux petits passages sont observés. Leur fonction, leur diamètre OEM et leur empilage ne sont pas attribués depuis la seule photo.

La largeur de travail≈218,5mm(plage190–250) résulte d’une échelle artistique0,88mm/pixel. **Elle n’est pas calibrée sur un tube31mm.** Le grand trou inférieur fait28,16mm de travail, les quatre autres16,72–17,6mm, les deux petits7,04mm ; toutes ces valeurs restent des estimations. Épaisseur centrale2,2mm(plage1,5–3,5), bord descendant jusqu’à4,7mm de hauteur totale, petit adoucissement des perçages0,15mm : sections de candidat, aucune coupe d’embouti fabricant.

La face arrière photographiée montre un bord formé, mais sa section cachée n’est pas établie. La source représente un retour arrondi continu dont l’épaisseur varie au bord ; elle ne revendique pas un emboutissage à épaisseur constante qualifié. Le raccord a reçu des rangées de points rapprochés avant triangulation, puis a été relu en gris pour éviter de masquer un défaut de forme par la peinture.

Collection `WEWA_STEERING_UPPER_ISOLATED`. Repère localXY de présentation, origine au grand trou inférieur, face photographiée+Z. Aucune pose cockpit appliquée, aucun côté asymétrique ou montage compatible annoncé. Le diamètre31mm de la variante liée concerne seulement la recherche du tube, pas une mesure de ces trous.

Un seul solide fermé positif, sept passages réellement ouverts, source éditable et export évalué. Les contrôles lisent aussi les aires des triangles et des UV, les normales/tangentes et les pixels réellement embarqués. La source conserve ses positions, triangles et normales entre revue grise et matière ; le studio a été réglé pour éviter qu’un reflet de panneau masque la peinture dans la vue arrière.

Le revêtement noir utilise deux cartes512² originales, sans pixel photographique, tuile12mm et hauteur RMS≈3,16µm avant intensité0,7 : estimations d’apparence. Métallique0,25 et rugosité variable≈0,27–0,43 ne sont pas des analyses du revêtement réel.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/steering-triples/upper/build.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/steering-triples/upper/material.py
node assets-src/moto-components/steering-triples/upper/check_export.mjs
node assets-src/moto-components/steering-triples/upper/check_geometry_preservation.mjs
python assets-src/moto-components/steering-triples/upper/inspect_material.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/steering-triples/upper/render.py
```

Identité actuelleRDC, calage physique des tés, visserie, contacts de guidon/compteurs, course de direction, coût mobile et réception artistique restent ouverts. Les rendus séparés ne réceptionnent pas une fourche complète.
