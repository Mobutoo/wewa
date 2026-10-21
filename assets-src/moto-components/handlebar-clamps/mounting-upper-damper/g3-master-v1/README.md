# Source géométrique avant matière

Copie exacte du G3 original 73962d8c / c5c20525, sans pixels photographiques. Le constructeur original est `../build.py` et sa section `../profile_shape.py`. `../material.py` ouvre ce master et exige la revue gris/reflets rattachée à ses SHA. Les sorties PBR sont séparées dans le dossier parent, avec chemins //textures sans remapping.

Le contrôle natif G3 reste `creative/reviews/handlebar-mount-upper-damper-v1/source-inspection-check.json` : digest, normales et témoin BVH. `../check_material_preservation.mjs` compare réellement tous attributs/indices et matrices G3→PBR, sans réparation des buffers.

Revers, dimensions, section, orientation et contacts sont estimés/non reçus ; le dessin D15 n’est pas à l’échelle.
