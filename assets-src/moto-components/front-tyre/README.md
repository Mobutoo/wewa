# Pneu avant — première pièce isolée

Cette source Blender amorce la moto seule après le choix du style cinématographique. Elle ne représente ni une moto complète, ni une reproduction OEM reçue, ni un pneu prêt pour le budget mobile.

## Reconstruction et contrôle

`parameters.json` distingue désignation nominale, cotes converties et estimations bornées. Le diamètre de portée de 17 pouces est documenté ; diamètre extérieur de 580 mm, largeur de 71 mm, section gonflée et pas de sculpture sont des hypothèses de travail. Le fournisseur et le moule exact demeurent inconnus. Aucune marque de fournisseur ni numéro réglementaire n’est inventé.

`build.py` construit une section fermée éditable : couronne, épaules, flancs, talons et doublure intérieure. Les rainures sont des creux dans la surface, pas des pavés ajoutés autour d’un tore. La source détaillée et l’export d’inspection restent séparés. Les répétitions de sculpture demeurent schématiques : elles ne sont pas présentées comme un motif OEM confirmé.

Après examen rapproché, la grille initiale produisait des crans sur les diagonales. La construction déplace maintenant ses lignes angulaires pour suivre les rainures ; des lignes supplémentaires suivent les bords et le fond des canaux longitudinaux. Cette correction porte sur la topologie, pas seulement sur le nombre de polygones ou la résolution du rendu.

Le caoutchouc est un matériau procédural original avec rugosité et microrelief à l’échelle. Aucun visuel constructeur n’est utilisé comme texture. Le micrograin procédural n’est pas encore cuit pour glTF : la comparaison dans Babylon.js doit garder cette différence visible et le passage d’export matière reste ouvert.

`inspect_references.py` relève en lecture seule quatre arcs visibles des images officielles. Ses ajustements de cercle sont des diagnostics de contour, sans caméra photographique calibrée et sans conversion uniforme px/mm. Une erreur de cercle en pixels n’est pas une précision de reproduction mécanique.

## Exécuter

Depuis la racine du dépôt :

```sh
python assets-src/moto-components/front-tyre/inspect_references.py
blender --background --python assets-src/moto-components/front-tyre/build.py -- --samples 96 --resolution 1200
node_modules/.bin/vite --host 127.0.0.1 --port 4142
```

Ouvrir ensuite `/tools/asset-lab/` sur le serveur local pour examiner l’export dans Babylon.js. Ce laboratoire est distinct du jeu public. Il n’est pas une mesure de performance iPhone.

Les rendus, défauts observés et limites sont dans la [revue de pièce](../../../creative/reviews/front-tyre-v1/README.md). Conserver les calages photographiques ouverts et corriger avant de déclarer la forme fidèle. La direction graphique choisie ne réceptionne pas automatiquement cette pièce.
