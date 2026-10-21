# Dépendances de génération — visière v1 et protection de phare v2

Instantané : 2026-10-21T03:25:09.676928+00:00. Lecture seule : aucun modèle, rendu, manifeste ou registre modifié. Les cinq couples source/export correspondent aux empreintes de leurs rapports. La recette n’a pas été exécutée.

Les deux sources finales sont éditables et présentes. Leur publication seule ne ferme pas la recette de génération : les études et entrées nécessaires listées ci-dessous sont encore à joindre. Les SHA complets et les relations lecture/écriture sont dans `report.json`.

## Visière v1

Chaîne réelle : annotation numérique → contour v1 → grille v1 → coque grise v1 → grille/bord roulé v3 → coque grise v3 → matière v1 → conversion optique GLB. La v3 repart directement de v1 ; **l’étude v2 est diagnostique**. Le GLB gris v3 est réellement lu par la conversion finale.

## Protection avant de phare v2

Chaîne réelle : plan de forme G2 → constructeur gris v3 + worker Manifold v3 → source/rapport gris v3 → plan matière v2 → constructeur matière v2. Les études grises v1/v2 et la matière v1 ne sont pas des dépendances. Le GLB gris v3 reste une preuve utile, mais le constructeur matière lit seulement son `.blend` et son rapport.

## Fichiers nécessaires à publier

Rôle : `forme` = entrée/script/intermédiaire de la chaîne complète ; `matière` = nécessaire à la recette à partir de la source grise déjà gelée. Les intermédiaires peuvent se régénérer, mais les scripts actuels lisent ces chemins précis et vérifient les empreintes des `.blend` dans les rapports.

| Chemin réel | Rôle | État Git observé | SHA-256 |
|---|---|---|---|
| `assets-src/moto-components/headlamp/build_protector_material_v2.py` | matière | added_to_index | `76790deaf5239d82bf7c8bb95aefa8ac118f7d3fd9c3162fe275c158dac01c1f` |
| `assets-src/moto-components/headlamp/build_protector_study_v3.py` | forme | untracked | `8d7b4f4e6fc95b834eebf59336d084f97fa8cbecea04e9526e939fef7ebe03e9` |
| `assets-src/moto-components/headlamp/headlamp-front-protector-study-v3.blend` | forme, matière | untracked | `de8d2db0dca5b3c4a72cdc16a217eb47874c4dc411d6572c3d0a04ec1006cc49` |
| `assets-src/moto-components/headlamp/protector_csg_worker_v3.py` | forme | untracked | `4e17d2c0cf15c73d5f697547447e893b38aa415a95490cc198820177e30530c0` |
| `assets-src/moto-components/instrument-visor/build_material_v1.py` | matière | tracked_in_HEAD | `270d501a6b60e5c2f3af887364e3ee0d29e22a3fbe0161781fff7cbb5f65493a` |
| `assets-src/moto-components/instrument-visor/build_rolled_study_v3.py` | forme | untracked | `58876b266bcea3b7e404670f858b8e51fc3cd628bea6a990dd958ea307ee4cbc` |
| `assets-src/moto-components/instrument-visor/build_shell_study_v1.py` | forme | untracked | `039ce1ed95a7715745bfeeb77e36b6663ae780ed33e865d32b9231f0f0ee542a` |
| `assets-src/moto-components/instrument-visor/finalize_material_export_v1.mjs` | matière | tracked_in_HEAD | `6ef08e82d84ad722dda873737176c8cfe03a571ba98f196ec92b2b3021b41ab3` |
| `assets-src/moto-components/instrument-visor/instrument-visor-shell-study-v1.blend` | forme | untracked | `5ec0267d6f9128123721de74e04f6a3df070b5cb1d4567e153853225a3dc3849` |
| `assets-src/moto-components/instrument-visor/instrument-visor-shell-study-v3.blend` | forme, matière | untracked | `4e1674fbac66b922ae6a195a4210fd8843960d4e269318ce320612c2cecfd5e2` |
| `assets-src/moto-components/instrument-visor/instrument-visor-shell-study-v3.glb` | forme, matière | untracked | `4741baa476587e47db340fb70c2b31bf4823b169cda71feac4a076a171ae8b03` |
| `assets-src/moto-components/instrument-visor/outline-rounded-v3.json` | forme | untracked | `ffba99b89fd30dd8202f33a07db6e7b068daf5ece0491caf5cc5d211e4235b67` |
| `assets-src/moto-components/instrument-visor/outline-v1.json` | forme | untracked | `c9958f80e30e097b3ebd417089de4b41fb1f8fe461fe3e130e047a976c7311d6` |
| `assets-src/moto-components/instrument-visor/planar-grid-v1.json` | forme | untracked | `186bc45efe43059e791728737e01ff9c2fe082c8c5655d15e09a294a9fef62eb` |
| `assets-src/moto-components/instrument-visor/prepare_grid_v1.py` | forme | untracked | `32a9ced435496c14b8cc5716b38a267c40aa9e5293cdd4518c4822f96a0af23e` |
| `assets-src/moto-components/instrument-visor/prepare_outline_v1.py` | forme | untracked | `8b41f2f141b3089f72b680f916887feef2764ff4210415c6f893968eaea49ab7` |
| `assets-src/moto-components/instrument-visor/prepare_rounded_grid_v3.py` | forme | untracked | `5abd5ee027d888b4b87754080b2e0647aed1e07961e6b170784ac5da547075ce` |
| `assets-src/moto-components/instrument-visor/rounded-planar-grid-v3.json` | forme | untracked | `fd1a2a702984809e464af6deeca026922f0eb48ea790269506019026d665fa10` |
| `creative/research/headlamp/protector-material-plan-v2.json` | matière | added_to_index | `67151f01252429ef00bb013c0e45dcc9c23b7258d9c268defbde7298108e1d2c` |
| `creative/research/headlamp/protector-shape-plan-v1.json` | forme | tracked_in_HEAD | `5968bd5003f0e54bf9494141c0585986d9fe478eee935598b43aacb914f39045` |
| `creative/research/instrument-visor/bare-front-native-contour.json` | forme | added_to_index | `7fdc85335fccb603f905850dea2a619027beed97f5ecc8c54a7df2cb925da7c6` |
| `creative/research/instrument-visor/material-plan-v1.json` | matière | added_to_index | `0b022c096343fe072a9b10e1d957c82b2c3f98015c6604f56fb76918950bd94a` |
| `creative/reviews/headlamp-front-protector-study-v3/source-geometry-check.json` | forme, matière | untracked | `9ea1826a693a12bb203cecb1b3e71e6741a6ebae3e02c170d98b7457b12efdb9` |
| `creative/reviews/instrument-visor-shell-study-v1/source-geometry-check.json` | forme | untracked | `3d491c0375c40e3afcbad0d6fdd01446a673e5fc13b70bec69e54128cb4fd695` |
| `creative/reviews/instrument-visor-shell-study-v3/source-geometry-check.json` | forme, matière | untracked | `4d336f9ed97a71c68e3b7d601afe2edfc5f6b422d2f9d507e8a69cb87f07de10` |

## Portabilité à compléter

- `prepare_outline_v1.py` impose `/workspace/wewa-github` ; le finaliseur Node doit être lancé depuis la racine du dépôt.
- Le répertoire parent du GLB brut temporaire doit être créé : `/workspace/wewa-assets/work-in-progress/instrument-visor`. Ce brut est un résultat original régénéré, pas une texture privée à publier.
- La chaîne complète de préparation de visière demande NumPy, SciPy et Shapely avec triangulation contrainte (API Shapely 2.1+). Le Python courant possède SciPy 1.17.0 mais aucun Shapely ; le fichier de requirements actuel ne couvre que NumPy/Manifold. Les grilles numériques déjà présentes permettent de démarrer les étapes Blender sans refaire ces préparations.
- Les scripts matière utilisent les sémantiques d’export de Blender 4.3.2. Le worker de protection exige le `python` du PATH avec Manifold 3.3.2 / NumPy 2.3.5. Le finaliseur exige les modules glTF Transform 4.5.1 installés depuis le lockfile racine.
- Les `.blend` gelés et leurs rapports ferment la recette matière actuelle ; aucune reproduction binaire de toute la chaîne depuis zéro n’est démontrée. Une exécution ultérieure doit se faire dans une copie séparée.

## Déclarations et diagnostics

Les fichiers `parameters-v1.json`, `protector-parameters-v2.json`, contrôles, provenance et README sont nécessaires pour expliquer le candidat public, mais ne sont pas lus par les constructeurs de forme/matière. Les vrais paramètres lus sont les plans matière, le plan de forme de protection et les nombres intégrés aux scripts de visière. Ne pas substituer les JSON de déclaration à ces entrées.

Le JSON joint classe aussi les études v1/v2 devenues diagnostiques, la recherche de placement de visière, les GLB non consommés et leurs SHA. Les scripts de rendu, vérification, interfaces, EXR et clôture des finales ne sont pas nécessaires pour fabriquer la forme et la matière ; ils restent des preuves séparées. Les études de godet et boîtier de phare sont hors périmètre de ces deux candidats.

Aucun pixel de photo privée n’est ouvert dans ces neuf étapes de génération. Les chemins/hash photographiques contenus dans les annotations/plans sont documentaires ; les recettes consomment les coordonnées numériques relevées et les estimations. Les surfaces sont originales sans texture photographique. Ce constat ne constitue ni réception artistique ni conformité OEM.
