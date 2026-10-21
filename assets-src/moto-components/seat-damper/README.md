# Tampon de selle DP211009 apparenté — peau de contact candidate v1

Un seul exemplaire extérieur est construit d'après la photographie attribuée
DP211009 : contour rectangulaire arrondi, cinq vallées géométriques, lèvre
extérieure arrondie et bouche centrale. La source représente la face de contact
et deux parois de revue, **sans revers, tenon, fond ou état borgne/traversant
inventé**. La profondeur de coupe de 6 mm est un choix de présentation ; elle
ne mesure ni l'épaisseur de la pièce ni la profondeur d'un trou réel.

Les paramètres préparatoires v1 restent conservés. La v2 garde les dimensions
de travail estimées de 40 × 27 mm et affine la tessellation de la bouche. Les
premiers essais créaient de mauvaises facettes aux raccords des rainures :
la correction contraint les bandes de surface jusqu'à leurs intersections
explicites avec le cercle. `construction-corrections.json` conserve les constats
des essais refusés. Le paramètre de grille locale conservé dans la v2 documente
une piste intermédiaire ; la recette finale emploie les contraintes de bandes.

Le modèle de 95 284 triangles a deux bords ouverts déclarés : contour arrière
extérieur et paroi tronquée de la bouche. Ce sont des limites de revue. Aucun
volume caoutchouc complet, ajustement mécanique ou montage reçu n'est déduit de
la peau. Les sept tampons d'une variante apparentée ne sont pas multipliés :
leur implantation et la réception de cet exemplaire restent à faire.

La matière noire propre originale utilise RGB linéaire (0,012 ; 0,013 ; 0,012),
rugosité 0,47, métal 0 et IOR 1,46. Dureté, chimie, grain et teinte OEM ne sont
pas mesurés. Les reflets du studio et du ciel ne sont pas incorporés à la
couleur. Les vrais buffers P/N/UV/indices et matrices restent ceux du gris.

La recette suit `geometry` → contrôle des buffers → `gray` → lecture réelle
avant `material` → `preview` → lecture réelle avant `final`. Exemple, depuis la
racine, avec Blender officiel 4.3.2/Cycles/OIDN CPU :

```sh
blender --background --python-exit-code 1 --python tools/build_moto_remaining_batch_v1.py -- seat-damper geometry
node tools/check_remaining_surface_exports_v1.mjs seat-damper --gray-only
blender --background --python-exit-code 1 --python tools/build_moto_remaining_batch_v1.py -- seat-damper gray
```

Les sources, GLB, PNG, EXR linéaires générés et preuves restent liés par leurs
empreintes. Les textes de scripts conservés dans les instantanés `protocols/`
servent à la provenance ; ils ne prouvent pas une reconstruction vierge.
Les photographies documentaires restent privées. Aucune réception artistique,
compatibilité courante RDC, fonction d'appui ni qualification iPhone n'est acquise.
