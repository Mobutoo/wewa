# Haut moteur — comparaison à caméra commune v1

Deux cadrages Blender ont été transférés tels quels dans un inspecteur Babylon séparé. Il ouvre le GLB de revue déjà publié, sans déplacer ni modifier les sept composants. Les huit coins de l’enveloppe réelle servent uniquement de témoins de projection logicielle : écart maximal **0,000330 pixel** sur les deux vues, sous la borne de contrôle de 0,05 pixel. Ce résultat ne mesure aucune fidélité à une photographie.

| Cadrage | Blender natif, HDR neutre | Babylon, véritable canvas |
|---|---|---|
| Quart avant | [PNG natif](../upper-engine-material-lighting-v1/neutral-outdoor.png) | [PNG moteur](front/actual-babylon-same-camera.png) |
| Côté opposé | [PNG natif](../upper-engine-material-lighting-opposite-v1/neutral-outdoor.png) | [PNG moteur](opposite/actual-babylon-same-camera.png) |

Le moteur paraît plus sombre et les bandes des ailettes plus marquées. **L’apparence reste à reprendre.** Le fichier HDR, son intensité déclarée et le facteur d’exposition sont communs ; leur orientation, filtrage, BRDF et transformation d’affichage ne sont pas étalonnés ensemble. Blender emploie AgX Medium High Contrast, Babylon ACES. Les arrière-plans diffèrent. Ces images ne prouvent donc pas une parité photométrique ni une réception artistique.

Les deux exports ont réellement été chargés dans Chromium/SwiftShader ; leurs octets HTTP et ceux du HDR ont été vérifiés. Les captures comportent respectivement 86 493 et 108 434 pixels différents du fond. Les sept sources liées ont été revérifiées par empreinte. Aucun fichier source n’a été enregistré, aucun matériau ni binaire GLB modifié, aucune intégration au jeu public, aucun test iPhone physique.

Les [observations](coordinator-reading-v1.json), les [paramètres avant](front-camera.json), les [paramètres opposés](opposite-camera.json), les [mesures avant](front/engine-check.json) et les [mesures opposées](opposite/engine-check.json) restent attachés aux révisions exactes. La liste figée figure dans [manifest.json](manifest.json).

Reproduction dans deux nouvelles destinations, depuis la racine du dépôt :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python tools/prepare_material_camera_comparison_v1.py -- --spec creative/research/upper-engine-material-lighting-v1.json --output creative/reviews/nouvelle-comparaison/front-camera.json
python tools/capture_material_camera_comparison_v1.py creative/reviews/nouvelle-comparaison/front-camera.json creative/reviews/nouvelle-comparaison/front
```

Le serveur Vite de revue doit servir le dépôt sur localhost:4143. Refaire pour la spécification `creative/research/upper-engine-material-lighting-opposite-v1.json`, dans une autre destination. Les outils refusent de remplacer une preuve existante. Le chemin du binaire Blender ci-dessus est celui de cet environnement, sans dépendance à un asset privé.
