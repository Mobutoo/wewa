# Tige du clignotant avant droit — candidat extérieur v1

La nouvelle source développe un profil indépendant d'après la photographie
PF401002. Elle réemploie la technique analytique de révolution à raccords C2,
pas le maillage réfléchi de la tige gauche. Les paramètres préparatoires v1
publiés restent intacts ; les choix indépendants sont dans
`parameters-study-v2.json`. La longueur de travail de 61,5 mm, les diamètres,
la courbure et la profondeur des trois rainures restent estimés.

Le maillage de 130 176 triangles représente seulement la peau extérieure. Les
deux anneaux ouverts sont des coupes de revue à des interfaces couvertes,
pas des extrémités industrielles ou une preuve de passage intérieur. Tenon,
filetage, câble, racine de raccord à la coque et montage restent séparés.
L'axe local +X va du côté support vers la tête hypothétique ; ce repère n'est
pas une pose sur la moto ni une certification de symétrie gauche/droite.

La matière noire propre est originale : RGB linéaire (0,012 ; 0,013 ; 0,012),
rugosité 0,40, métal 0 et IOR 1,46. Chimie, dureté et grain réels ne sont pas
mesurés. Aucune photographie n'est incorporée comme texture. Les positions,
normales, UV, indices et matrices exportées sont identiques au gris sauvegardé.
Les reflets clairs du studio et la réponse bleu sombre sous ciel neutre sont
conservés séparément, sans retouche de couleur entre les vues.

Depuis la racine, avec **Blender officiel 4.3.2**, Cycles CPU et OIDN :

```sh
blender --background --python-exit-code 1 --python tools/build_moto_remaining_batch_v1.py -- right-stalk geometry
node tools/check_remaining_surface_exports_v1.mjs right-stalk --gray-only
blender --background --python-exit-code 1 --python tools/build_moto_remaining_batch_v1.py -- right-stalk gray
```

La lecture réelle des gris et des reflets précède `gray-review.json`, puis les
étapes `material` et `preview`. Après lecture des aperçus et de la carte diffuse
18 %, `material-preview-review.json` permet l'étape `final` à 96 samples.
Ces fichiers consignent une décision de travail de l'agent ; ils ne sont pas
une réception artistique utilisateur. Les contrôles GLB lisent les vrais
buffers ; les captures Babylon sont distinctes des rendus Blender.

Les sources éditables, les deux GLB, les PNG, les EXR linéaires générés et leurs
rapports sont sauvegardés. Les instantanés de texte dans `protocols/` identifient
les scripts effectivement employés à chaque passage. Ils ne constituent pas
une reconstruction vierge automatiquement exécutée. La recette courante est
dans `tools/`, à lancer depuis la racine. Ni cette pièce isolée ni son coût
d'inspection ne qualifient un clignotant complet ou un LOD iPhone.
