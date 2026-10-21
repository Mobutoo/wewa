# Recette — carénage phare PBR v1

**Le maître gris14 fourni suffit à reprendre le PBR1 avec ses JSON publics. La reconstruction intégrale des études13/14 depuis leurs propres entrées ne doit pas être déclarée fermée par les seuls gels16/25.** Audit additif pour une coupe suivante ; le cowl reste hors publication11. [Le JSON](report.json) donne les chemins, SHA, rôles et couvertures exactes des dépendances stables.

Le candidat clos est source `78f2af6e…`, GLB `7ac45db7…`. Aucun rendu, modèle ou test n’a été lancé, aucun gel ou README existant modifié.

## Reprise matière et vues PBR

`build_candidate_v1.py` ouvre **le BLEND gris14** `1a789dfa…`, lit `source-geometry-check.json`14, vérifie l’existence de son gel et lit `material-plan-v1.json`. Ce maître contient la forme, les UV/normales, les attributs de classe de surface et le studio local. Aucun pixel privé, texture, normal map, bake ou bibliothèque externe n’est lu. Deux jeux de paramètres constants créent le rouge et le polymère sombre ; le masque de peinture repose sur la classe de face et un seuilY estimé, pas sur une photo.

Les gels PBR16/25 incluent **le manifeste**14, mais pas le BLEND14 et son rapport eux-mêmes : ces fichiers sont listés dans le gel14 séparé. Une publication de recette doit donc inclure ces vrais fichiers, en plus de leur témoin SHA.

`render_candidate_v1.py` lit le candidat PBR, son rapport, `native-camera-exploration-v1.json` et le helper public `tools/blender_component_camera_preflight.py`. Le mode final lit aussi la revue de prévisualisation et le contrôle d’export. Le JSON caméra et le helper sont hors gels16/25 et doivent accompagner la recette. Les chemins de photos dans ce JSON servent à sélectionner les cas8494/8495 ; le rendu final n’ouvre pas leurs pixels. `controls.json` décrit une pièce statique, sans contrôle et sans pose montée confirmée ; il n’est pas lu par la fabrication matière.

## Ce que lisent réellement les formes13/14

| Étape | Maître et rapport réellement ouverts | Autres entrées nécessaires |
|---|---|---|
| `build_shell_study_v14.py` | **Source13** `d4b6c85a…` et son `source-geometry-check.json` | `remaining-partial-ribs-plan-v14.json`, workerCSG **pad_v5** |
| `build_shell_study_v13.py` | **Source12** `d923a277…` et son `source-geometry-check.json` | `first-central-rib-plan-v13.json`, workerCSG **pad_v4** |

Tous ces fichiers existent localement. Les plans numériques sérialisent les points/normales/sections estimés : leur consommation par les builders ne demande pas de photo privée. Leurs préparateurs utilisent le maître précédent, le JSON caméra et les annotations publiques de l’addendum, sans lire les photos.

Mais le gel14 ne liste pas son maître13/rapport13 ; le gel13 ne liste pas son maître12/rapport12. Le lien direct vers13 du pointage `remaining-physical-work-v3` ne ferme donc pas la recette13 et ne remplace pas la dépendance14→13. Remonter plus loin demanderait notamment source11 et les propres entrées de12 ; cette chaîne antérieure n’a pas été auditée intégralement ici. La présence locale ou un manifeste imbriqué ne certifie pas une fermeture publique de toutes les entrées.

## Recherche caméra et diagnostics privés

Rejouer les **caméras numériques déjà fournies** suffit aux vues PBR. Recalculer ce JSON depuis la recherche originale est un autre travail : `native-camera-exploration-v1.py` ouvre les photos privées8494/8495, utilise Pillow/scipy et lit `/tmp/wewa-cowl-source3-points.json`. Cette recherche originale n’est pas déclarée reconstructible depuis les seuls fichiers publics.

L’ancien `preview_native_cameras_v14.py` lit aussi `/tmp/wewa-cowl-source14-points.json` et extrait seulement la fonction `project()` du script de recherche, sans en exécuter les ouvertures de photos. Ces points sont un dérivé géométrique du GLB, pas un maître de forme ; aucun producteur spécifique du dump n’a été trouvé parmi les scripts inspectés. Leur chaîne de diagnostic reste donc explicitement non close. Les deux autres macros14 lisent le plan14, sans ce dump.

Les prévisualisations privées, caches de CSG rejeté et EXR finaux sont des sorties/preuves, jamais des textures ou maîtres lus par la matière. Aucun pixel privé n’a été publié. Une éventuelle reprise doit utiliser une copie isolée : les builders écrasent leurs noms actifs.

Les SHA et les manifestes existants ont été rapprochés en lecture seule. Aucun clone propre ou déplacé n’a été reconstruit ; l’identité RDC, la calibration photographique, les cotes, la matière mesurée, la réception artistique et l’iPhone ne sont pas validés par cet audit.
