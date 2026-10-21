# Kick — révision v2 candidate

ID `MOTO-KICKSTARTER-001`. La v1 reste conservée avec ses preuves et son défaut confirmé : la découpe cannelée traversait le pont et l’oreille basse de charnière. La fente de serrage débordait aussi du moyeu. Les deux découpes de v2 s’arrêtent aux faces du volume original du moyeu (w −10 à +18 mm estimés), avec 50 µm de dépassement numérique de chaque côté. Ce dépassement est une tolérance de calcul, pas une cote constructeur.

`build_v2.py` fabrique `kickstarter-v2.blend` et `kickstarter-v2-inspection.glb`. Collection `WEWA_KICKSTARTER`, deux parents articulés inchangés. `gltf-node-map-v2.json` donne les axes après conversion Blender/glTF ; les conditions d’utilisation restent déploiement puis course. Le carter RH v2 est lié comme guide immuable caché, sans certification de montage.

Les sept volumes sont fermés et connexes. Les 57 poses sont contrôlées par croisements de surfaces, les trois états d’un vrai sommet sont comparés source/export. Les six pièces autres que le moyeu ont les mêmes triangles orientés Float32 que v1. Le centre d’alésage est libre ; 336 rayons contrôlent ses sections et deux rayons vérifient le retour de matière sur le pont inférieur. Ces tests ne prouvent pas les jeux physiques ni les formes de faces invisibles.

Les photos PA621203 sont des variantes apparentées BM150BS3/V12/V15 ; la référence exacte125RDC, les cotes, les 28 cannelures, leur profondeur, les angles et les épaisseurs restent estimés. Aucun pixel documentaire n’est utilisé comme matière. Chrome, zinc et caoutchouc sont des réglages PBR originaux non mesurés. Aucun mécanisme moteur interne n’est fabriqué.

Les aperçus gris/reflets/PBR précèdent le gel et les vues96. La réception artistique, l’identité OEM et la qualification Safari physique restent ouvertes.
