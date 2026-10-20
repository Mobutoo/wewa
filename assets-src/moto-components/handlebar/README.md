# Guidon nu — candidat v1

Tube de guidon seul, à l’échelle métrique, construit dans Blender. Références : vues officielles Boxer125HD RDC et photo de cockpit servie par cette page ; deux photos isolées du guidon voisin **DU181021**, également listé au catalogue BM125UG5gear. La variante standard du catalogue porte PF151000. **Aucun numéro de pièce ni aucune cote du guidon RDC actuel n’est certifié.**

Les [observations et empreintes](../../../creative/research/handlebar/reference-observations.json) distinguent ces sources. Les originaux restent hors dépôt public. Le fichier officiel de cockpit contient `bm150` dans son nom malgré son emplacement sur la page125HD ; cette ambiguïté est conservée. Aucune photo n’est utilisée comme texture.

La géométrie originale comprend un tube à paroi réelle, deux cintres circulaires par côté, des raccords tangents continus et deux zones moletées de serrage au centre. Le fond du tube n’est pas rempli : les deux ouvertures restent accessibles. Les petits chanfreins de coupe sont géométriques. Les poignées, commodos, leviers au guidon, miroirs et pontets ne font pas partie de cette pièce.

Les [paramètres](parameters.json) fixent un candidat : entraxe des bouts 680 mm, relève 105 mm, recul 85 mm, diamètre extérieur 22,2 mm, paroi 2 mm, rayon de cintre 38 mm. **Toutes ces dimensions sont estimées**, avec plages conservées ; le diamètre conventionnel 22,2 mm n’est pas présenté comme une donnée fabricant. Le motif, la profondeur et la position du moletage sont également provisoires. La largeur extérieure du maillage atteint environ 688,76 mm à cause de l’épaisseur du tube et de l’obliquité des extrémités.

Repère commun au cockpit : X transversal, +Y vers le conducteur, −Y vers l’avant, Z vers le haut. Origine au milieu de la partie droite serrée. Bouts : `(±0.340, 0.085, 0.105)` m. Axe entrant droit : `(-0.916695, -0.399587, 0)` ; gauche : `(0.916695, -0.399587, 0)`. Environ 180 mm de section droite sont laissés disponibles pour les pièces séparées de commandes, sans valider leur montage.

```sh
blender --background --threads 2 --python-exit-code 1 --python assets-src/moto-components/handlebar/build.py
node assets-src/moto-components/handlebar/check_export.mjs
blender --background --threads 2 --python-exit-code 1 --python assets-src/moto-components/handlebar/render.py
python assets-src/moto-components/handlebar/record.py
```

Le [contrôle source](../../../creative/reviews/handlebar-v1/source-geometry-check.json) vérifie le volume de paroi, une seule coque fermée, les raccords et les passages courts aux deux ouvertures. Le [contrôle glTF](../../../creative/reviews/handlebar-v1/geometry-check.json) inspecte les buffers réellement exportés, leur transformation, le volume, les matériaux et ces mêmes passages. La source et le GLB gardent toute la géométrie fine du moletage : cet export d’inspection n’est pas un LOD mobile.

Les matières PBR constantes donnent une apparence de chrome et d’acier intérieur sous lumières de studio ; elles ne représentent pas une mesure de réflectance. L’UV longitudinale préparatoire n’a pas de texture appliquée ; son raccord circulaire doit être repris avant une matière texturée. Les mesures, caméra documentaire, sections exactes, implantation des pontets et compatibilité des commandes restent ouvertes. Aucune réception artistique ou qualification iPhone acquise.

[Revue avec rendus réels](../../../creative/reviews/handlebar-v1/README.md).
