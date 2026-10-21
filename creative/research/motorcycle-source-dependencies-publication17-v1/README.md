# Source17 — admission statique de quatre recettes

Base publique Source16 `e43a112526b1ae00ec89f8f149fca79fbed57e63`, métadonnées `b8552068739dc0792b123a12946c69df24888db3`. Ce relevé vérifie **162 paires SHA/octets** des gels sources35/30/35/62, soit160 chemins distincts, et nomme113 entrées stables de recette et de contrôle. Aucun générateur, Blender, rendu ou export n’a été exécuté. Aucun index, global, ancien gel ou modèle modifié. Les deux seules nouvelles copies sont le checkpoint numérique et la mire originale explicitement autorisés ci-dessous.

Le [rapport](report.json), la [fermeture des quatre gels](source-closure-v1.json) et les [entrées stables nommées](stable-recipe-inputs-v1.json) séparent les obligations d’archive et les fichiers utilisés pour reprendre la fabrication. Ces tables sont des instantanés de cette lecture ; elles ne sont pas des manifestes vivants du catalogue ou des registres globaux.

| Recette | Reprise de forme et matière | Limite de cette coupe |
|---|---|---|
| [Tube d’arceau](../../../assets-src/moto-components/engine-protection-hoop/README.md) | Paramètres→générateur Manifold→NPZ auteur→source native ; maître G3 public et contrôles assortis à restaurer avant `material.py`, avec `gray-review.json` | Source35/revue78/root21 closes ; tube seul, embouts/assemblage absents |
| [Tige de clignotant](../../../assets-src/moto-components/indicators-front/left-stalk/README.md) | Builder gris autonome, puis BLEND gris/report/permission et roughness originale ; le comparateur exige aussi le GLB gris | Source30/revue39/root19 closes ; peau extérieure et deux interfaces ouvertes, pas signal complet |
| [Platine centrale](../../../assets-src/moto-components/engine-protection-centre-plate/README.md) | Paramètres+`profile_shape.py`→CDT natif/pli analytique ; maître G3 fourni, `gray-review.json` et contrôles de source à restaurer avant matière | Source35 seule figée dans cet audit ; cinq finales encore actives au lancement du relevé, pas de revue finale imaginée |
| [Support droit](../../../assets-src/moto-components/front-footrest-right/README.md) | Construction indépendante, helpers `control_geometry.py`→CSG host `front-brake-plate/csg.py`/Manifold3.3.2 ; maître géométrie/report/revue grise puis cartes originales | Source62 seule figée ici ; sept finales actives au lancement, pas de miroir du gauche ni montage acquis |

Pour tube/platine, la matière écrase le chemin courant du composant : restaurer les deux binaires G3 dans **une copie de travail isolée**, ainsi que leurs contrôles G3 aux chemins de revue attendus, puis utiliser la permission grise attribuée à ces SHA. Le dépôt livre le maître de reprise ; cette lecture ne prétend pas qu’une reconstruction depuis un clone vierge a été exécutée. Pour RH, `recipe.py`, `build.py` et `material.py` refusent volontairement un dossier déjà muni du préflight figé ; préparer un nouvel espace de travail, conserver les originaux et adapter le chemin d’installation Blender, sans supprimer leur gel.

## Entrées omises des gels sources, désormais nommées

La reprise matière de la tige lit réellement quatre fichiers hors source30 : `indicator-front-left-stalk-study-v1.blend` (2 799 366octets, `ff8c92fa…`), son GLB gris (3 717 548octets, `e2462b68…`), `creative/reviews/indicator-front-left-stalk-study-v1/build-report.json` (31 916octets) et `gray-reflection-reading.json` (2 034octets). Leurs SHA concordent avec les deux baselines déclarées dans le candidat courant. Aucun ancien gel d’étude ni archive entière n’est nécessaire à ces lectures.

Les permissions grises tube/platine sont aussi des entrées de `material.py`. Celle du tube est déjà couverte par sa revue78 ; celle de la platine et les contrôles actuels sont nommés séparément en attendant sa vraie clôture. Les scripts de contrôle RH extraient eux-mêmes les UV et images embarquées vers leur scratch privé : ces fichiers générés ne sont pas des maîtres manquants à publier. La forme RH, ses deux helpers transitifs, les trois cartes originales et leurs rapports sont déjà dans62. Les shaders tube/platine et cartes tige/RH sont procéduraux originaux ; aucune police, atlas, photo documentaire ou maillage vendeur n’est lu comme matériau.

## Deux entrées exactes des rendus historiques de la tige

Le renderer studio final lit **inconditionnellement** le checkpoint des aperçus pour comparer caméra/vue/source. Le renderer neutre final vérifie **inconditionnellement** le SHA de la mire18% originale à travers le rapport de prévisualisation figé. Cette seconde lecture est un contrôle d’octets ; le renderer final réutilise l’exposition numérique1,517820695996414EV et ne redécode pas les pixels de mire pour la remesurer. La mire est un rendu original du projet, pas une photo documentaire.

| Copie publique exacte | Octets | SHA256 |
|---|---:|---|
| [Checkpoint des aperçus](replay-inputs/stalk-preview-render-checkpoints.json) | 7 736 | `c207b4035819ecd2de24f28e5ee3218451e2b5cba5a24a74e7f89da49bd2e163` |
| [Mire18% originale EXR](replay-inputs/stalk-neutral-graycard-original.exr) | 38 205 | `851a6db46849bff1210b7f4af7f38762e05b7559200d32572cf6e2d47fd271c8` |

Les deux copies ont été comparées octet par octet à leurs originaux. Le [plan de restauration](replay-inputs/restoration-map.json) conserve les chemins littéraux attendus par les renderers non modifiés. Dans l’environnement isolé de reprise, depuis la racine du dépôt :

```sh
mkdir -p /workspace/wewa-assets/work-in-progress/indicator-front-left-stalk-v1/previews
cp creative/research/motorcycle-source-dependencies-publication17-v1/replay-inputs/stalk-preview-render-checkpoints.json /workspace/wewa-assets/work-in-progress/indicator-front-left-stalk-v1/previews/render-checkpoints.json
mkdir -p /workspace/wewa-assets/render-raw/material-lighting-review
cp creative/research/motorcycle-source-dependencies-publication17-v1/replay-inputs/stalk-neutral-graycard-original.exr /workspace/wewa-assets/render-raw/material-lighting-review/indicator-front-left-stalk-v1-neutral-lighting-graycard.exr
```

Les chemins de PNG/EXR d’anciens aperçus présents dans les rapports restent des citations historiques ; ils ne déclenchent pas de collecte récursive. Le HDR neutre est la dépendance précédemment publique sous `app/public/materials/`, sans mutation de l’application. Les PNG de mire et de prévisualisation neutre déjà produits dans la revue sont nommés comme contexte de lecture, séparément du seul EXR imposé. Aucune autre copie de raster privé n’a été réalisée.

## Proposition bornée et réserves

Admettre les quatre gels sources exacts et leurs seules entrées complémentaires nommées ; prendre les revues78/39 et racines21/19 déjà closes pour tube/tige. Attendre les vraies fermetures platine/RH avant de sélectionner leurs rapports finaux. Le ressort SNS apparu depuis le démarrage reste hors de cet audit à quatre recettes ; ni sa revue finale ni son inscription ne sont présumées.

Ce relevé ne régénère ni les anciens aperçus, ni leurs EXR, ni toutes les archives de réception auteur. Le spec d’origine de la prévisualisation neutre n’est pas une entrée du renderer final fourni : celui-ci lit son spec final public, le rapport de prévisualisation et la mire exacte. Aucune reconstruction complète du protocole de prévisualisation d’origine n’est revendiquée. Les préflights, rendus et assemblages réels restent du ressort de leurs preuves attribuées ; aucune réception artistique, variante OEM, fonction protectrice, pose installée, LOD mobile ou essai iPhone n’est acquis ici.
