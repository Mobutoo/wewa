# Rétroviseur gauche — candidat détaillé v1

La coque à galbe composé suit le contour gauche observé dans la rotation officielle RDC. Les vues isolées DJ221003/004 documentent une construction liée : dos, lèvre, verre côté droit, col, caches et tige coudée. L’identité de pièce RDC exacte et les cotes ne sont pas confirmées. La vue isolée du verre gauche manque. Toutes les cotes, la profondeur, la courbure et le chemin de tige hors plan sont des estimations ; les paramètres et leurs plages restent dans `parameters-left.json`.

Source : `mirror-left-v1.blend`, SHA256 `bdd8a799b6a5ae07a5c076ba0c5a1019f6477ff9a4be5995229e13c2def3c6d0`. Export : `mirror-left-v1.glb`, SHA256 `fb796f4bbe842b7080ba5310aeab653a5fbc72d647f3a2c113309e27f256f8fa`. Collection `WEWA_MIRROR_LEFT`. Provenance `provenance-left.json`, commandes `controls-left.json`.

Le candidat contient dix corps fermés : coque creuse et col moulé ; verre bombé fini de2,5mm ; couche réfléchissante arrière de60µm séparée par20µm ; bande de bord conditionnelle ; une tige métallique continue avec rotule et goujon hélicoïdal cosmétique ; rondelle ; écrou à chanfreins formés ; cache creux de base ; cache inférieur fixe de col ; cache supérieur mobile. Le diamètre/pas/sens de filetage et l’articulation réelle restent inconnus : les dimensions de travail ne qualifient aucun assemblage constructeur.

La coque conserve ses sections originales, une paroi finie et un passage de col interne courbe. L’ancienne sortie ovale de perçage parasite est refusée dans l’étude initiale ; la révision de gris `shell-gray-back-v2.png` et le balayage BVH du dos documentent sa correction. Aucun trou vu sur le RH lié n’est transféré automatiquement au LH. Les logos vendeur et marques d’homologation ne sont pas copiés.

Le verre est un vrai solide courbe distribué radialement, et la couche arrière un solide métallique séparé. Les reflets proviennent du studio réel, jamais d’une image de décor collée. La source comporte le polymère noir à grain original de2µm RMS sur une tuile physique de10mm, le verre/IOR1,52/transmission, le métal arrière, l’acier peint, les fixations et les caches. Ce grain et ces matières sont des hypothèses originales, pas des mesures.

Les contrôles dans `creative/reviews/mirror-left-v1/` portent sur les surfaces réelles : dix solides fermés et connectés ; export de112204triangles sans aire nulle ; glTF0erreur/0avertissement ; normales et tangentes utiles contrôlées ; textures réellement embarquées identiques, canaux métal/rugosité décodés. Ce maillage de revue détaillé n’est pas optimisé ni qualifié pour iPhone.

`motion-mount-check.json` vérifie les45couples de corps au repos, neuf combinaisons yaw±10°/pitch±7°, cinq poses du levier embrayage lié et les axes réellement ouverts des rondelle/écrou/cache. Aucun croisement dans ces poses. Le bossage emprunte la source embrayagev2 `586b41d08fd0cb8a9caad66e7cbe83af1592aad42e6def823135f99b6f200059`, dont l’alésage8,8mm reste estimé. Ces tests de surfaces ne valent pas certification mécanique ou électrique.

Les images et réglages réels sont enregistrés après chaque vue dans `head-render-checkpoints.json` / `final-render-checkpoints.json`, avec SHA source, configuration, PNG et EXR privé. Le script reprend uniquement les vues absentes/incohérentes. Les quatre corps de tête source/export sont bit-identiques entre l’étude de tête et le miroir complet (`head-to-full-identity-check.json`). La hauteur du sol de studio diffère ; aucune identité visuelle source/moteur n’est déduite de cette preuve.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/mirrors/build_left_full.py
node assets-src/moto-components/mirrors/check_export.mjs mirror-left-v1
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/mirrors/check_motion_mount.py -- left
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/mirrors/render_mirror.py -- left final
```

La réception artistique et le test sur iPhone physique restent ouverts. Les captures Babylon sont réalisées dans la revue commune, séparément des contrôles glTF et des images Blender.

La première vue entière provisoire est refusée pour la rotule trop exposée et l’écrou masqué ; son diagnostic et ses empreintes sont conservés dans `rejected-joint-gap.json`. Le cache de base a ensuite reçu les deux étages cylindriques observés, le col ses deux lèvres/rainures et un emboîtement creux contrôlé. Le goujon et le départ de tige ont été ajustés pour exposer l’intervalle fileté au-dessus de l’écrou ; la position de l’écrou reste une configuration installée estimée, contrairement à la pièce isolée posée en boîte.
