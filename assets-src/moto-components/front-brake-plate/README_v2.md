# Révision matière v2 disponible

La [revue v2](../../../creative/reviews/front-brake-plate-v2/README.md) conserve la géométrie v1 et ajoute des UV à l’échelle ainsi que des cartes originales de grain et de rugosité partagées avec l’export. La source `front-brake-plate-v2.blend` et les GLB portant `v2` sont séparés ; les [preuves v1](README.md) restent historiques et intactes. Reconstruction : `material_v2.py`, puis `inspect_material_v2.py`, `node tools/check_front_brake_plate.mjs v2` et `render_v2.py`. Le contrôle des données matière est `python tools/check_brake_material.py`.

L’export sans tangentes explicites conserve une alerte glTF : le moteur calcule son repère tangent. Les cartes transférées sont identiques, mais la parité visuelle entre moteurs et les raccords UV restent à examiner. Aucune réception artistique supplémentaire n’est déduite de ce contrôle.
