# Jante avant Wewa — source modifiable, candidat v1

La jante est fabriquée seule avant le contrôle avec le pneu existant. La moto complète, son conducteur, le flasque amovible du frein et l’axe ne sont pas fabriqués par ce lot. [Vues et contrôle](../../../creative/reviews/front-rim-v1/README.md).

## Construction

Blender 4.3.2, mètres, X axe de roue, Y longitudinal, Z haut, centre Z = 0,290 m. Une section fermée de jante est tournée, puis réunie au logement creux de tambour et à cinq branches courbes à section en I. Les profils, branches et unions exactes restent modifiables. Le remeshing à 0,65 mm et un lissage léger corrigent les raccords ; ils ne constituent pas un relevé de pièce usinée. Une valve approximative reste séparée.

La source lie `../front-tyre/front-tyre-v1.blend` avec un chemin relatif. Conserver les deux dossiers ensemble pour ouvrir la vue de raccord. Un champ Geometry Nodes réaffecte les surfaces usinées après remeshing, qui effaçait leurs indices de matériau. La jante isolée ne dépend pas d’une texture constructeur. Les photographies et le catalogue sont des documents, pas des textures redistribuées.

## Cotes et inconnues

| Donnée | État |
|---|---|
| Désignation 17 pouces / diamètre nominal de portée 431,8 mm | Spécification RDC ; diamètre extérieur de jante différent |
| Cinq branches moulées | Observées dans les vues officielles |
| Largeur 1,40 pouce / 35,56 mm | Catalogue BM125 UG voisin, non adoptée comme cote RDC |
| Largeur de travail 44 mm | Estimée pour la séparation de 44 mm des talons du pneu candidat ; plage 35–47 mm |
| Rayon extérieur 226,5 mm, section, courbure des branches | Estimations de fabrication |
| Cavité de tambour, roulements, valve | Hypothèses ; pas un frein fonctionnel ni un montage certifié |

Le premier essai à 35,56 mm laissait 4,22 mm d’écart axial par talon par rapport au profil de pneu candidat. Le passage à 44 mm ferme cet écart nominal ; ni l’un ni l’autre des profils n’est une section fabricant confirmée. L’interférence locale, le serrage et l’étanchéité tubeless restent à contrôler. Les caméras des photos constructeur ne sont pas calibrées ; aucune précision millimétrique de reproduction n’est annoncée.

## Refaire

```sh
blender --background --python assets-src/moto-components/front-rim/build.py -- --views none
node tools/check_front_rim.mjs
blender --background --python assets-src/moto-components/front-rim/inspect.py
blender --background --python assets-src/moto-components/front-rim/build.py -- --samples 64 --resolution 1100
node tools/check_front_rim.mjs
blender --background --python assets-src/moto-components/front-rim/inspect.py
```

Le premier passage sans rendu vérifie la vraie géométrie exportée et l’affectation des matériaux avant les vues coûteuses. Le second crée les rendus ; les contrôles sont reliés à ses empreintes finales. Le générateur produit les exports avant de calculer les vues afin de permettre ce contrôle précoce.

`python tools/check_rim_preflight.py` teste aussi ce passage dans un dossier temporaire, sans écraser les sources ou vues de la revue courante.

`front-rim-v1.blend` conserve construction détaillée et copie réduite d’inspection. `front-rim-inspection.glb` évalue les modificateurs et réduit explicitement la surface pour examen. `front-wheel-fit-inspection.glb` ajoute le pneu d’inspection. Ces exports ne sont pas des LOD mobiles reçus. Les rendus Cycles utilisent la source détaillée, 64 échantillons, sans débruitage ; l’image générée de moto complète reste une cible artistique distincte.

Le nom du jeu sur le futur réservoir sera **WEWA**. La jante n’ajoute aucun logo inventé. Les noms constructeur sont conservés dans les sources documentaires.
