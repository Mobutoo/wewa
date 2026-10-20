# Flasque avant Wewa — corps moulé seul, candidat v1

La fabrication reprend sur une seule pièce : le corps de flasque. La jante et le pneu restent candidats sans réception artistique. Le levier, l’axe, les garnitures et les ressorts ne font pas partie de ce lot.

## Références et choix avant modélisation

L’éclaté Bajaj BM125UG, feuille PDF44, distingue le flasque22, le levier18, la came23 et l’axe8. Il donne `DZ151027` pour une version et `JA131605` pour UG5vitesses. Des photos recto/verso de **JA131605** sont retrouvées chez PartOnWheels ; deux autres vendeurs reprennent les mêmes clichés. Il y a deux directions de vue utiles, pas cinq captures indépendantes ou trois confirmations constructeur. [Observations, sources et empreintes](reference-observations.json).

Les photos montrent la collerette circulaire, une coupelle, le bossage central percé, la butée oblique à logement rectangulaire, l’alésage de came décentré, de petits bossages latéraux et les anneaux/nervures du dos. Ces formes guident la construction. Les photos constructeur RDC restent prioritaires pour vérifier la variante ; elles masquent une partie du flasque derrière la fourche. Le rapprochement JA131605/RDC n’est pas confirmé.

Les originaux documentaires restent hors du dépôt et ne servent pas de textures. La quantité «4» imprimée au catalogue pour ce flasque est inexpliquée et n’est pas transformée en quatre flasques sur la roue.

## Dimensions et protocole

Toutes les cotes propres au flasque sont estimées. Le rayon de travail72mm, la portée64,2mm, les épaisseurs, les petits alésages et les reliefs sont contraints par le moyeu candidat existant. Un diamètre de frein voisin130mm n’est pas une cote extérieure de flasque. Les caméras photo restent non calibrées ; aucun relevé millimétrique n’est annoncé.

Coordonnées : mètres, +X côté extérieur gauche de travail, +Y vers l’arrière de la moto, -Y vers l’avant, +Z haut ; axe de roue à Z0,290m. L’orientation du flasque autour de l’axe est une pose de comparaison, pas un montage de fourche validé.

La coupelle et les anneaux arrière sont tournés dans une section fermée continue. Les nervures, bossages et la butée restent des volumes modifiables ; leur fusion et les perçages sont calculés avec **Manifold3D3.3.2**, puis le résultat est repris dans Blender. La source conserve ces volumes de construction et le maillage résultant. Une modification des volumes demande de relancer le générateur ; ce n’est pas une pile booléenne Blender qui se met automatiquement à jour. Contrôler source évaluée, connexions, alésages et raccord au moyeu **avant** les vues détaillées. Les matières et le jeu de montage restent à recevoir.

## Fichiers et exécution

`build.py` produit source et exports sans lancer de rendus. `render.py` charge la source contrôlée pour les vues recto/verso/trois-quarts et le raccord provisoire. Les références de roue restent liées par chemins relatifs ; conserver les dossiers `front-rim` et `front-tyre` ensemble.

```sh
python -m pip install -r tools/requirements-assets.txt
blender --background --python-exit-code 1 --python assets-src/moto-components/front-brake-plate/build.py
node tools/check_front_brake_plate.mjs
blender --background --python-exit-code 1 --python assets-src/moto-components/front-brake-plate/inspect_casting.py
blender --background --python-exit-code 1 --python assets-src/moto-components/front-brake-plate/render.py
```

Sources originales du projet, aucune géométrie commerciale copiée. Exports d’inspection, sans qualification mobile ni réception artistique. La moto complète et son conducteur ne sont pas déclarés terminés.

## Corrections réellement contrôlées

Une première section se croisait près du contre-alésage. Après sa reprise, les unions booléennes Blender de renforts concentriques créaient encore des arêtes non jointives et des fragments internes. Les anneaux sont intégrés à la section, les volumes sont désormais calculés avec Manifold et chaque opération conserve un volume cohérent. Le contrôle final vérifie un corps connecté, des surfaces fermées, les passages d’axe/came, le fond du logement de butée et l’absence de traversée du moyeu candidat. Ces résultats ne prouvent pas la cote OEM ou le bon montage réel.
