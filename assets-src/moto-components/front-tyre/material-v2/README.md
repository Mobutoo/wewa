# Pneu avant v2 — conversion de matière seulement

Cette révision reprend notre pneu d’inspection `front-tyre-v1`, sans modifier sa géométrie, ses UV, ses dimensions estimées ou son motif de sculpture encore à recevoir. L’ancienne source détaillée et les anciens exports/manifests restent intacts. Le [plan de transfert](../../../../creative/research/front-tyre-material-v2/material-transfer-plan-v1.json) épingle leurs empreintes avant conversion.

Le donneur est le vrai matériau procédural original de la source : bruit3D en coordonnées objet, échelle4300, détail2, Bump0,18/distance55µm ; bruit de rugosité57, rampe0,50–0,67. Il ne s’agit pas de mesures de caoutchouc OEM. La désignation avant2.75-17 est publiée sur la [page constructeur RDC](https://www.bajajauto.com/fr-cd/bikes/boxer-125hd) ; fournisseur, moule, section gonflée et contact chargé restent inconnus. Aucun pixel photographique, marque de pneu ou saleté n’a été ajouté.

`build.py` charge seulement l’objet d’inspection nommé et le matériau donneur depuis la source historique épinglée. Il vérifie triangles/UV avant de cuire les normales tangentes en16K×2K et la rugosité en4K×512 sur **le même maillage et les mêmes UV0**. Le Bump natif est inclus dans la carte ; la force finale est1, sans seconde atténuation. La rugosité est cuite linéairement via une copie temporaire en émission, puis stockée en ORM(R255/Gvaleur/B0). Le writerPNG conserve les données8bits sans AgX/gamma, en retournant explicitement les lignes Blender vers PNG. Les deux images finales sont NonColor, packed, avec compagnons relatifs réels.

Le bake est une discrétisation. La résolution finie et la quantification peuvent filtrer les octaves fines ; la densité varie avec les UV et les épaules. L’indicateur de0,111mm/texel sur la circonférence n’est pas une densité uniforme certifiée. Aucun résultat de parité parfaite avec le shader continu, de budget mobile ou d’essai iPhone n’en découle. Les cartes de29,4Mo et0,53Mo servent à la revue détaillée ; une version de livraison sera un travail séparé et mesuré.

`check_export.mjs` lit les vrais anciens/nouveaux buffers. POSITION/NORMAL/UV0/indices et matrice sont strictement identiques ; les tangentes sont nouvelles car l’ancien export n’en avait pas. Il contrôle leur repère et les UV réellement utilisés, les triangles, les images réellement embarquées et glTF. Il ne répare aucun buffer.

`render_compare.py` affecte en mémoire le matériau donneur puis la carte sur **la même inspection**, avec caméra/lumière/exposition identiques. Les deux macros du pneu et le cadrage entier servent uniquement à l’étude : les marches/facettes héritées aux jonctions interdisent toute nouvelle finale96 avant repriseG3 distincte. Ni la source détaillée plus dense ni une autre géométrie ne sont substituées à l’un des témoins.

Reproduire dans un checkout de travail séparé, jamais en écrasant un gel reçu :

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/front-tyre/material-v2/build.py -- --preflight-only
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/front-tyre/material-v2/build.py
node assets-src/moto-components/front-tyre/material-v2/check_export.mjs
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/front-tyre/material-v2/render_compare.py
```

Blender4.3.2 et son numpy natif servent au bake ; les dépendances Node sont celles du lockfile racine. Les PNG8bits sont écrits par Python standard/numpy. Les checkpoints ne réutilisent une cuisson qu’après accord des empreintes de source, géométrie, paramètres donneurs et fichierPNG. Le microrelief n’est pas un déplacement physique de la roue. Les anciennes limites G1/G2/G3/G5 restent ouvertes.

La lecture des deux témoins de sculpture a confirmé une dette visible G3 déjà présente dansv1. Cettev2 est conservée comme **étude de transfert**, sans finale96 ni nouveau candidat de production reçu. `record.py` ne peut fermer qu’un manifeste d’étude où la reprise de forme est explicitement requise. Unev3 corrige les raccords sans inventer de nouveau dessin de sculpture ; toute surface changée exige une nouvelle cuisson.
