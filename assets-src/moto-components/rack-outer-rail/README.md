# P02 — rail extérieur du porte-bagages

Première étude du U extérieur et de ses bras, source originale et dimensions
estimées. Ni porte-bagages complet, ni pose sur la moto, ni réception artistique.

- [Source grise](rack-outer-rail-study-v1.blend) et [GLB gris](rack-outer-rail-study-v1.glb).
- [Source matière](rack-outer-rail-candidate-v1.blend) et [GLB matière](rack-outer-rail-candidate-v1.glb).
- [Paramètres courants](parameters-study-v3.json) ; v1/v2 conservent les décisions précédentes.
- [Dossier documentaire](../../../creative/research/rack-p02/G0-G2-plan-v1.json).
- [Images et contrôles](../../../creative/reviews/rack-outer-rail-study-v1/README.md).

Collection `WEWA_RACK_OUTER_RAIL_STUDY`, objet `RACK_OUTER_RAIL`.
Repère local +X vers l’avant, +Y latéral, +Z vertical, origine recentrée pour revue.
Rayon extérieur de travail7,5mm, plage estimée6–9mm ; dimensions et points du
polygone de contrôle non mesurés (incertitude de travail25%). La référence isolée
PF231405 est une variante apparentée, pas une certification actuelle RDC.

Le tube est une surface extérieure sans épaisseur interne déclarée ; ses deux
extrémités sont des coupes de revue ouvertes avant les terminaisons aplaties à
documenter. Plateforme, équerres, perçages, terminaisons, soudures et autres
attaches ne sont pas compris dans cet enfant. La symétrie est une hypothèse
bornée, pas une identité démontrée entre côtés.

Le premier tracé interpolant formait un repli ; le premier tracé B-spline avait
un échantillonnage dégénérant aux extrémités. Les deux sources rejetées sont
conservées en revue. La correction utilise une B-spline et un rééchantillonnage
de longueur d’arc à2mm, puis un contrôle indépendant des triangles/normales réels.

Depuis la racine, avec Blender4.3.2 officiel Cycles CPU/OIDN :

```sh
blender --background --python-exit-code 1 --python tools/build_rack_outer_rail_p02.py -- geometry
blender --background --python-exit-code 1 --python tools/build_rack_outer_rail_p02.py -- gray
# Lire les gris et consigner gray-review.json avant material.
blender --background --python-exit-code 1 --python tools/build_rack_outer_rail_p02.py -- material
blender --background --python-exit-code 1 --python tools/build_rack_outer_rail_p02.py -- preview
# Lire les aperçus et consigner preview-review.json avant final.
blender --background --python-exit-code 1 --python tools/build_rack_outer_rail_p02.py -- final
node tools/check_rack_outer_rail_p02.mjs
node tools/check_motorcycle18_exports.mjs rack-outer-rail-study
python tools/capture_motorcycle18_v3.py rack-outer-rail-study
```

Ne pas écraser cette révision publiée pour une correction suivante ; produire de
nouveaux chemins et preuves. Aucun rejeu propre complet ou résultat iPhone acquis.
