# Instruments v2 — candidat de correction

La v1 reste intacte. Cette révision remplace le capuchon USB ovale exposé par une embase contournée, une lèvre et une face capsule en retrait ; son symbole rectangulaire/oblique est redessiné sans lui attribuer un sens. Les bandes discontinues et grandes graduations sont reconstruites, le pictogramme carburant a son ajour, le triangle son point d’exclamation et GEAR son orientation verticale. Les angles et pivots restent ceux de la v1 : la recherche projective indépendante ne permet pas de les recalibrer sûrement.

Toutes les dimensions sont estimées. La photo officielle est publiée sur la page RDC 125HD mais son nom contient BM150 ; le numéro exact de l’ensemble reste inconnu. Les états 1–5 servent uniquement à démontrer l’affichage, sans certifier le nombre de rapports de la moto RDC. Le capuchon reste fermé ; connecteur, charnière et câblage cachés ne sont pas inventés. Odomètre statique.

La source comporte 27 corps structurels fermés, et des marquages plans. L’export réel compte 56615 triangles sans aire nulle. 135 nœuds protégés conservent leurs buffers/matrices/matières bit-identiques à la v1 ; seules 8 faces FONT exactement nulles ont été retirées de 4 marquages, avec conservation des coins de toutes les faces positives. Les 117 attributs tangents inutilisés sont retirés sans réparer les tangentes utiles ; la transmission/IOR des vitres reste identique au précédent export. Ces preuves techniques ne certifient pas la parité visuelle.

Les études USB r2 ont été examinées en diffus et en reflets avant l’intégration. Les deux aperçus de l’ensemble à 8 échantillons emploient les caméras finales et passent le cadrage réel avec marge 2,5%. Les rendus 96 et leurs checkpoints sont produits par `render_v2.py` ; leur présence effective est documentée dans la revue, pas présumée par ce fichier.

`parameters-v2.json`, `controls-v2.json` et `provenance-v2.json` décrivent le contrat. Les contrôles source, export réel et interfaces figurent dans `creative/reviews/instruments-v2/`. Les axes glTF locaux des deux aiguilles sont [0, 1, 0], deltas après quaternion de repos. Aucune réception artistique, mesure constructeur détaillée ou qualification iPhone physique acquise.

Commandes depuis la racine :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instruments/build_v2.py
node assets-src/moto-components/instruments/check_export_v2.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instruments/check_interfaces_v2.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/instruments/render_v2.py
```
