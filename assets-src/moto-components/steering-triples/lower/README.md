# Corps inférieur de direction — candidat DS181020 lié

Un seul corps métallique original, reconstruit après lecture des vuesSCL0/1/2 et des catalogues liésD04/D15. Les deux bagues fendues, leurs oreilles de serrage, le siège central, deux petits bossages, deux projections et les évidements/nervures du revers sont distincts. **Colonne, vis, écrous et roulements ne sont pas inclus.** Le procédé et l’alliage réels ne sont pas confirmés ; le nom interne«casting» décrit l’apparence de travail.

La quatrième photoSCL présente une colonne avec deux zones de filetage différentes et une provenance visuelle Alibaba. Son appariement n’est pas établi : elle reste exclue des cotes/filets. Les trois autres vues ne donnent aucune mesure physique actuelleRDC.

Repère local : Xtransverse(+gauche pilote),+Ypilote,Zhaut, origine au milieu des deux axes de fourche. Aucune pose installée. Centres de travailX±87,5mm, déport du siège de colonneY45mm, alésages de fourcheØ31,1mm autour du tube candidat31mm : **estimations**, pas des cotesRDC. Plage d’entraxe150–190mm, déport30–55mm, hauteur des bagues12–22mm pour15mm de travail. Siège centralØ25mm de travail(plage23–28), trous des petits bossagesØ5,4mm estimés, fonctions et filetages non certifiés.

Les oreilles portent des entrées de perçageØ10,4mm estimées. D04 cite des boulonsM10x1,25 pour une variante liée ; cela ne mesure ni la portée ni le fond caché. Une terminaison intérieure aveugle de travail est conservée, sans filetage femelle détaillé et sans précharge ou serrage qualifié. Les deux projections supérieures ne sont pas déclarées butées de direction fonctionnelles.

Le revers comporte deux poches originales réellement soustraites. Leurs fonds de travail àZ−1,5mm se distinguent du web àZ−4,5mm ; leur profondeur3mm et la section restante sont estimées. Les petits arrondis du pont0,65mm, oreilles0,6mm et bossages0,35mm sont construits avant union. Une surépaisseur de pré-alésage évite les parois exactement coïncidentes avec les forets ; les alésages finaux gardent leur valeur de travail.

Collection `WEWA_STEERING_LOWER_BODY_ISOLATED`. Source `steering-lower-v1.blend`, export évalué `steering-lower-inspection.glb`. Un seul solide fermé positif, cinq ajours axiaux, deux fentes et les entrées de serrage contrôlés dans les vrais buffers, avec lecture des fonds de poches. Les triangles, normales et matrices restent identiques entre gris et matière.

La finition extérieure noire utilise deux cartes originales512², référence de projection16mm, hauteur RMS≈5,38µm avant intensité0,7, rugosité≈0,18–0,383. Les portées photographiées plus lisses ont une matière séparée sans micrograin. Ces échelles, couleurs, rugosités et valeurs métal sont des réglages d’apparence ; aucun pixel photographique, relevé chimique ou rugosité mesurée.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/steering-triples/lower/build.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/steering-triples/lower/material.py
node assets-src/moto-components/steering-triples/lower/check_export.mjs
node assets-src/moto-components/steering-triples/lower/check_geometry_preservation.mjs
python assets-src/moto-components/steering-triples/lower/inspect_material.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/steering-triples/lower/render.py
```

La compatibilité avec le té supérieur, le siège/bearing de colonne et les tubes actuels, le montage, les amplitudes mécaniques, les LOD/coûts mobiles et la réception artistique restent ouverts.
