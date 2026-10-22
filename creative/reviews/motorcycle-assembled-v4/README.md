# Moto WEWA — moteur et phare corrigés, assemblage v4

![Moto actuelle, rendu Blender](../whole-exterior-material-preview-v9/material-left-quarter.png)

[Gros plan moteur gauche](inspection-whole-v3/engine-engine-left.png) · [Moteur droit](inspection-whole-v3/engine-engine-right.png) · [Phare monté](inspection-whole-v3/engine-headlamp.png) · [Face entière](inspection-whole-v3/engine-front.png).

## Corrections livrées

Le vide signalé venait d’une enveloppe supérieure/arrière du carter incomplète et de surfaces trop en retrait, pas de l’absence de tout le moteur. Un nouveau corps extérieur rejoint le pied du cylindre et complète ce volume. Les vrais espaces du cadre restent ouverts. [Avant/après, source et contrôles](../../../assets-src/moto-components/engine-exterior-completion-v3/README.md). Les joints entre carters issus de variantes apparentées restent à qualifier.

Le phare est reconstruit à partir de la photo officielle de face du modèle RDC et de photographies de face/trois quarts d’une optique DJ201051 apparentée. Il comprend un réflecteur réellement concave, ses ouvertures et retours, l’enveloppe visible de l’ampoule et les stries verticales de la vitre. Recul retenu **38 mm**, plage estimée **26–50 mm** : une reconstruction d’apparence, sans cote constructeur ni prescription optique revendiquée. Les reflets photographiques ne sont pas transformés en fausses facettes. [Source et limites](../../../assets-src/moto-components/headlamp-front-photo-reconstruction-v1/README.md) · [Rendu rapproché Blender](../headlamp-front-photo-reconstruction-v1/denoised-96/oblique.png).

## Vérifications

162 instances liées : 160 sources/poses conservées, une optique remplacée dans le même repère, un corps moteur ajouté. **Trois rendus Blender96**, 960×675 avec EXR FLOAT32, et **six captures Babylon réelles**, dont trois gros plans. 541 maillages, 25 463 261 triangles ; ces nombres ne comptent pas des pièces physiques finies.

[Source rouverte et dépendances vérifiées](../whole-exterior-material-preview-v9/native-reopen-check.json) · [Contrôle Babylon](inspection-whole-v3/engine-check.json) · [Comparaison native/export](../../research/motorcycle-assembled-v4/native-runtime-bounds-comparison.json) · [Contrôle glTF](../../../assets-src/moto-components/motorcycle-assembled-v4.gltf.proof.json).

Zéro erreur glTF/page/HTTP. L’avertissement de tangentes générées du flasque avant est identique à la livraison v3. Les bornes natives/export concordent à 2,802 µm au maximum : cohérence numérique, sans mesure physique du véhicule. [Trois vues avec matières](../whole-exterior-material-preview-v9/README.md) · [Assemblage gris](../whole-exterior-coverage-v22/README.md).

## Récupérer les fichiers

[Blender principal](../../../assets-src/moto-components/whole-exterior-material-preview-v9/whole-exterior-material-preview-v9.blend) · [glTF assemblé](../../../assets-src/moto-components/motorcycle-assembled-v4.gltf) · [Manifeste exact](../../research/motorcycle-assembled-v4/portable-files.json).

317 ressources, 1 597 306 931 octets, vérifiées localement. Les bibliothèques et tampons liés sont nécessaires : conserver l’arborescence. Aucun téléchargement distant intégral neuf n’est prétendu ; les originaux photographiques restent privés.

```sh
python tools/fetch_motorcycle_model_v1.py --manifest creative/research/motorcycle-assembled-v4/portable-files.json --destination /chemin/moto --format all
```

`native` ou `runtime` permettent une récupération séparée. Visualiseur local : `/tools/motorcycle-complete-review-v2/?model=/assets-src/moto-components/motorcycle-assembled-v4.gltf`.

Les fichiers détaillés restent destinés à la revue. Les interfaces mécaniques, les joints de variantes, la prescription optique, les LOD mobiles et Unity ne sont pas certifiés ; aucune réception artistique utilisateur n’est présumée. Les anciennes versions restent conservées.
