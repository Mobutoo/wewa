# Source17 — complément de recette du ressort extérieur noir

Base `b8552068739dc0792b123a12946c69df24888db3`. Audit limité au [ressort extérieur noir](../../../assets-src/moto-components/rear-sns/outer-spring/README.md) `dcf116f2…` / `458fb158…`, source33. L’[audit précédent162/113](../motorcycle-source-dependencies-publication17-v1/README.md) et ses sept fichiers restent byte-identiques. Aucun Blender, générateur, export, rendu, checker ou Git de mutation exécuté.

Le [rapport](report.json), la [fermeture source](source-closure-v1.json) et les [entrées stables](stable-recipe-inputs-v1.json) vérifient **44 paires SHA/octets**, soit source33 et son gel gris11 réellement consommé. Les onze cibles grises sont toutes déjà présentes dans33 ; aucun autre ancien maître ou archive n’est requis par cette chaîne. Les36 entrées stables nommées incluent les onze cibles effectivement hashées par le builder matière, les deux entrées de rendu copiées et les dépendances communes déjà publiques. Les tables sont des instantanés de cette lecture, pas des manifestes globaux vivants.

## Construction et matière

`build_study_v1.py` lit `parameters-study-v1.json` et exige le plan G0–G2 fourni. Il construit un fil balayé à pas variable avec Blender/mathutils, UV et normales auteur ; aucun CSG, modèle tiers ou photo n’est importé. Le candidat conserve un nombre de tours, une main, des dimensions et des extrémités estimés. Les disques terminaux sont des fermetures de calcul, pas un meulage ou un appui mesuré. Les bornes d’écartement/courbure sont des contrôles de la forme au repos, pas une qualification physique de compression.

`build_candidate_v1.py` ouvre le maître gris fourni et vérifie **chaque SHA du gel gris11** avant de lire les paramètres de matière. Le maître et ses rapports concordent avec les baselines du candidat courant. La matière est un jeu original de constantes Principled noir : aucune texture, carte normale, police ou atlas. Les deux GLB nécessaires au comparateur de buffers sont fournis. Les outils Node utilisent le lockfile existant ; le seul helper local du renderer est `tools/blender_component_camera_preflight.py`, déjà publié.

La reprise depuis le maître gris suffit pour refaire cette matière dans une copie isolée. Recréer le gris peut changer ses octets et exige une nouvelle revue attribuée ; cela ne permet pas d’hériter silencieusement d’une ancienne permission. Aucun replay depuis clone propre n’a été exécuté ici.

## Deux entrées historiques imposées aux renderers finaux

Le studio final lit inconditionnellement le checkpoint d’aperçus pour comparer source/vue/matrice de caméra. Le neutre final vérifie inconditionnellement le hash de la mire18% originale citée dans son rapport de prévisualisation. Il réutilise l’exposition numérique **1,508596132978224EV** ; il ne décode pas la mire pour la remesurer. Cette mire est un rendu du projet, sans photo documentaire.

| Copie publique exacte | Octets | SHA256 |
|---|---:|---|
| [Checkpoint numérique](replay-inputs/spring-preview-render-checkpoints.json) | 7 715 | `b06b3dc24fd209af088850fb71c73f9fa549ec16dfc19afc2d9959656c82e052` |
| [Mire18% originale EXR](replay-inputs/spring-neutral-graycard-original.exr) | 38 195 | `dae6b8135287741aca1bf662205c05dc82190fe21c0cacc19060d22675ff7e6b` |

Copies comparées octet par octet, autorisées uniquement pour ces entrées. Le [plan de restauration](replay-inputs/restoration-map.json) conserve les chemins attendus par les renderers non modifiés. Depuis la racine d’une copie de travail isolée :

```sh
mkdir -p /workspace/wewa-assets/work-in-progress/rear-sns-outer-spring-v1/previews
cp creative/research/motorcycle-source-dependencies-publication17-spring-v1/replay-inputs/spring-preview-render-checkpoints.json /workspace/wewa-assets/work-in-progress/rear-sns-outer-spring-v1/previews/render-checkpoints.json
mkdir -p /workspace/wewa-assets/render-raw/material-lighting-review
cp creative/research/motorcycle-source-dependencies-publication17-spring-v1/replay-inputs/spring-neutral-graycard-original.exr /workspace/wewa-assets/render-raw/material-lighting-review/rear-sns-outer-spring-v1-neutral-lighting-graycard.exr
```

Le HDR est l’asset précédemment public sous `app/public/materials/`, sans modification de l’application. Les deux PNG de mire/prévisualisation neutre aux chemins publics sont nommés comme contexte ; aucun autre raster privé, EXR de finale ou photo documentaire copié. Les citations privées d’anciens gris/reflets dans leurs rapports restent historiques et ne déclenchent pas de collecte récursive. La recréation complète du protocole d’origine de prévisualisation n’est pas revendiquée ; le renderer final a son spec public, le rapport figé et la mire exacte.

Les trois finales96, leurs rapports et leur clôture ne sont **pas** sélectionnés ni présumés par cet addendum. Ressort orange, manchon, amortisseur, coupelles, œillets, second ensemble et garde-boue restent hors périmètre. Ce relevé ne reçoit ni l’ensemble SNS, ni sa pose, sa raideur, sa variante OEM, une optimisation mobile, un essai iPhone ou l’aspect artistique.
