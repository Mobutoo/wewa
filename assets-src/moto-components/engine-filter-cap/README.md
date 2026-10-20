# Bouchon du filtre à huile — candidat isolé v1

`MOTO-ENGINE-FILTER-CAP-001` : capuchon avant du carter droit, séparé de la fonderie, du filtre, du joint et des vis. La photo officielle montre une petite face circulaire et un anneau concentrique. Le catalogue BM125 voisin distingue capuchon, joint et trois vis ; les trois oreilles de ce candidat sont donc conditionnelles, sans certification sur le modèle RDC actuel.

La source originale construit face, anneau, paroi et emmanchement arrière dans une section continue. Les trois oreilles sont fusionnées et réellement percées. Le nettoyage a retiré les triangles effondrés issus de petites lèvres arrondies, avec0 déplacement de sommet retenu et écart de surface maximal4,7nm. Le GLB possède un seul volume positif fermé et connexe, sans triangle nul ni erreur glTF. Aucune tangente n’a été réparée.

Toutes les dimensions sont estimées : face Ø80mm, oreilles jusqu’à environ87mm, insertion et jeu radial0,5mm, jour axial candidat0,5mm. Les entraxes et orientations ne sont pas mesurés. La vérification contre le carter figé démontre0 croisement de surfaces ; elle ne démontre ni les trous filetés correspondants du carter, ni un assemblage réel étanche. Aucun filtre, joint torique, vis, filetage ou intérieur fonctionnel n’est fabriqué.

Collection `WEWA_ENGINE_FILTER_CAP`, objet `RH oil filter cap - editable candidate`, parent `RH oil filter cap provisional datum`. Le repère et la référence du carter sont liés en lecture seule dans une collection locale masquée, sans mutation de la bibliothèque. Le GLB exporte le capuchon seul. Le PBR argent peint est original et non mesuré ; aucun pixel photographique n’est utilisé.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-filter-cap/build.py
node assets-src/moto-components/engine-filter-cap/check_export.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-filter-cap/render.py
python assets-src/moto-components/throttle-control/record_checkpoint_review.py engine-filter-cap
```

Voir [paramètres](parameters.json), [documentation](../../../creative/research/engine-filter-cap/reference-observations.json) et [revue](../../../creative/reviews/engine-filter-cap-v1/README.md). Pas de réception artistique, de variante exacte certifiée, de LOD ou de qualification iPhone physique.

Les premières vues de travail ont révélé des normales personnalisées pondérées héritées malgré la suppression du modificateur. Elles ont été explicitement effacées avant le gel : les plans sont plats et seules les zones courbes interpolées. La source gelée vérifie `custom_normals_present=false`.
