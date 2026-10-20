# Support de compteurs — candidat isolé v1

Reconstruction originale du support voisin **PF402404**, d’après une photo commerciale réelle et le catalogue BM150 D15. Ce n’est pas une pièce RDC125HD certifiée. La tôle fourchue, les trois ajours, deux têtes circulaires et trois petites nervures observées sont réellement construits, avec épaisseur et formage faible. Les tiges arrière sont conditionnelles à l’illustration D15 ; leur relief hélicoïdal est un choix de travail.

Les [paramètres](parameters.json) gardent le contour manuel de photo, le facteur d’échelle non calibré, les plages d’épaisseur1,8–3,2mm et les autres estimations. L’écart entre les deux têtes est environ108mm dans ce candidat. Aucune cote photographique n’est annoncée comme mesure du constructeur. Une photo oblique ne restitue pas la perspective, les profondeurs et la face arrière avec fidélité garantie.

La source conserve la tôle triangulée avant formage, ses reliefs et cutters originaux. Les unions/découpes Manifold3D produisent une enveloppe fermée avec trois vrais trous. La matière noire possède des cartes originales de normale tangentielle et de rugosité/métallique. Tuile10mm, grain RMS estimé5,42µm avant force0,7 : ces paramètres sont des choix visuels et non des mesures de revêtement. Le modèle fusionne les colliers à la tôle comme enveloppe visuelle ; leur constitution réelle et les éventuelles pièces élastiques distinctes ne sont pas confirmées.

Collection à lier : `WEWA_INSTRUMENT_BRACKET_ISOLATED`. Source et GLB sont **isolés**, dans le planXY, face photographiée vers+Z, origine entre les deux têtes. Les paramètres rappellent le repère cockpit commun (+X gauche pilote, −X droite, +Y pilote, Zhaut) et celui des compteurs, mais **aucune pose de montage n’est appliquée**. Le contact reste dans une zone ouverte en U. Empilage, visserie d’installation et compatibilité USB actuelle restent à documenter.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instrument-bracket/build.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instrument-bracket/material.py
node assets-src/moto-components/instrument-bracket/check_export.mjs
python assets-src/moto-components/instrument-bracket/inspect_material.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instrument-bracket/render.py
```

[Recherche et limites](../../../creative/research/instrument-bracket/README.md) · [revue réelle source](../../../creative/reviews/instrument-bracket-v1/README.md). Les contrôles vérifient fermeture, connexité, volumes, ajours et vrais buffers ; ils ne valent pas réception artistique, conformité mécanique ou test mobile.

Correction G3 : les petits rayons des colliers sont faits avant les unions ; le congé global après CSG a été retiré car il créait de minces faces et des reflets en facettes. Les triangles CSG restent conservés, avec nettoyage de coutures au seuil1µm. Les positions de cette source sont ensuite inchangées par G4 ; la triangulation de sortie permet les tangentes explicites sans avertissement. Les pixels des deux images embarquées sont comparés aux PNG originaux.
