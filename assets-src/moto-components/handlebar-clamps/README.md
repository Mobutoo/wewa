# Pontets et boulons — candidat v1

Deux unités de serrage séparées du guidon, d’après les photographies du set voisin **36DS1801** et les catalogues D04/D15. Chaque unité contient une demi-coquille supérieure profilée, une inférieure avec goujon, et deux boulons à tête hexagonale/flasque. **Huit solides**, pas un bloc représentant le mécanisme.

Les [sources inspectées](../../../creative/research/handlebar-clamps/reference-observations.json) montrent des corps argentés arrondis, le logement semi-circulaire du tube, deux passages latéraux et un goujon inférieur. Les deux vues PartOnWheels sont petites ; la photo BajajMatriz est plus détaillée. Aucune caméra, cote de profil ou identité RDC actuelle n’est confirmée. Photos conservées hors dépôt, aucun pixel repris comme texture.

Les [paramètres](parameters.json) fixent des **estimations bornées** : centres X=±45 mm, alésage de tube R11,25 mm autour du guidon candidat, largeur de corps26 mm, entraxe des boulons43 mm. D04 mentionne M6 pour les boulons UG5gear et M10 pour les écrous Nyloc ; cela reste une donnée de variante voisine. Les longueurs, pas, profondeurs et dimensions de tête sont des choix de travail, pas une définition fabricant.

La source conserve les profils et outils de découpe cachés ; leurs volumes originaux sont traités par Manifold3D. Les surfaces évaluées avec petits congés sont exportées. Les goujons portent un relief hélicoïdal extérieur estimé ; les filetages femelles des demi-coquilles et ceux cachés des boulons ne sont pas construits. Les amortisseurs, rondelles inférieures et écrous Nyloc restent séparés et absents ; aucun couple, précharge ou empilage mécanique n’est validé.

Repère : +X gauche du pilote, −X droite, +Y pilote, Z haut. Collection à lier : `WEWA_HANDLEBAR_CLAMPS_SEPARATE_PARTS`. Pas de guidon ou d’ancien candidat incorporé dans l’export.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/handlebar-clamps/build.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/handlebar-clamps/material.py
python assets-src/moto-components/handlebar-clamps/repair_tangents.py
node assets-src/moto-components/handlebar-clamps/check_export.mjs
python assets-src/moto-components/handlebar-clamps/inspect_material.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/handlebar-clamps/render.py
```

Les [rendus réels](../../../creative/reviews/handlebar-clamps-v1/README.md) sont des preuves de candidat. Les contrôles portent sur chaque coque, ses ouvertures, les volumes et les vrais buffers exportés. Les matières PBR ne constituent pas une mesure du revêtement ; aucune réception artistique ou qualification mobile acquise.

La petite dépression circulaire du fond du berceau inférieur est reproduite par une découpe sphérique originale, après observation sur Matriz. Fonction inconnue ; rayon et profondeur estimés, aucun pion supposé. Le premier profil facetté a été rejeté avant gel puis lissé dans son plan YZ. La vraie cambrure transversale reste non contrainte : le candidat conserve une couronne extrudée avec bords arrondis. Ce défaut de connaissance reste ouvert, sans prétendre à un relevé conforme.

G4 reprend le grain de revêtement observé sans en copier les pixels : deux cartes originales1024², tuile20mm, hauteur RMS estimée8,55µm et corrélations0,22/0,65mm, rugosité0,31–0,55. Le goujon et les boulons gardent une finition plus lisse, sans cette normale. Métallique0,65 pour les corps,0,92 pour l’acier : choix de rendu, pas analyses chimiques. La source conserve exactement ses positions et sa topologie après ajout UV/matière. Le nettoyage des coutures après congé élimine les faces d’aire quasi nulle, sans déplacement des sommets retenus. La variation relative de volume reste inférieure à1,8×10⁻¹⁰ et celle d’aire à9,5×10⁻¹⁰. Chaque demi-coquille inférieure compte33 190 triangles au lieu de110 150. Le candidat final ne demande **aucune réparation de tangente** ; le script au nom historique `repair_tangents.py` ne fait désormais qu’un contrôle strict et refuse les vecteurs invalides. Le rapport garde zéro correction et l’égalité des empreintes entrée/sortie. Les UV physiques20mm et l’orthogonalité des tangentes des corps sont aussi relus dans les buffers.

Les secteurs lisses/séparés sont conservés par l’identité de face et de coin pendant le nettoyage ; les mêmes normales pondérées sont ensuite calculées sur la surface propre. Une simple moyenne après soudure avait créé de faux reflets triangulaires dans le berceau : cet état a été refusé en revue. Les aperçus corrigés ont contrôlé la face plane, le congé et la section courbe avant le calcul des images finales. Aucun vecteur exporté n’est retouché.

La portée cylindrique en contact avec le tube possède maintenant une finition satinée séparée, sans carte normale ni rugosité texturée, réglée à0,27 par observation visuelle. Cette valeur n’est pas une mesure. Les surfaces extérieures conservent le micrograin ci-dessus, les vis leur acier lisse. La comparaison indépendante des regroupements de matières prouve que les triangles orientés, positions, normales et matrices sont inchangés dans les vrais buffers.
