# Visière fumée — candidat v1

Panneau seul original WEWA, issu de l’étude grise v3 à bord roulé explicite. Le corps, les normales, UV et indices sont inchangés ; la matière transparente fumée remplace le gris. Collection `WEWA_INSTRUMENT_VISOR`, racine `VISOR_PANEL_MOUNT_ESTIMATED`, sans commande mobile.

Les quatre aperçus ont été réellement ouverts : face, profil, intérieur et détail du bord inférieur. Ils autorisent les rendus Cycles96, sans réception artistique. Les paramètres détaillés de forme et de matière sont des estimations bornées ; aucune cote constructeur de la visière n’est disponible. Centres/diamètres des fixations, retours cachés et quatre jeux de vis/rondelles/écrous liés restent non fabriqués faute de références suffisantes. Le lot11 est incomplet.

La matière est propre, sans texture photographique ni micrograin inventé. IOR1,52, rugosité0,12 et absorption RGB cible à2,5mm sont des choix estimés. L’export brut Blender4.3.2 emploie une sémantique d’absorption différente ; `finalize_material_export_v1.mjs` convertit seulement `attenuationColor = exp(CyclesColor−1)` et vérifie les autres attributs, indices, matrices et propriétés. Le témoin réel EXR à1,25/2,5/5mm vérifie la loi d’absorption à IOR1, pas l’apparence finale ni une mesure physique.

Preuves : `creative/reviews/instrument-visor-v1/`. Les EXR et photos documentaires sont privés. La source/export et le protocole sont gelés avant les quatre finales. Contrôles Babylon, montage complet et Safari physique restent distincts.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instrument-visor/render_material_v1.py
```
