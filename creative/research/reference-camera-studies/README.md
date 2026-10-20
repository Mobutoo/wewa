# Caméras de comparaison R00 / R04 — préparation G2 réservée

Deux caméras Blender de travail explicites sont disponibles dans [camera-studies.json](camera-studies.json) et [create-working-cameras.blender.py](create-working-cameras.blender.py). Elles servent à comparer les prochains composants dans le repère commun du cockpit. **Ce ne sont pas des caméras photographiques calibrées.** Les guides, annotations et modèles figés n’ont pas été modifiés.

Les photos natives officielles 00/04 (1000×700) ont réellement été regardées, ainsi que leurs surimpressions privées. Les trois repères utilisés sont les axes de roue avant/arrière et le centre estimé de serrage du guidon. Les positions 3D des guides sont estimées ; seule la séparation d’axes de 1,285 m est une contrainte publiée. Aucun rayon provisoire de pneu ni contour de pneumatique n’entre dans l’ajustement.

| Caméra de travail | Position XYZ dans le repère commun, m | Échelle orthographique Blender, m | Résidu guidon (u,v), px |
|---|---|---|---|
| R00, côté droit / caméra −X | (−4 ; +0,304184 ; −0,388880) | 2,438330 | (−0,25 ; +0,51) |
| R04, côté gauche / caméra +X | (+4 ; +0,269964 ; −0,406595) | 2,315315 | (+19,40 ; −13,61) |

La résolution est 1000×700, pixels carrés, `sensor_fit=HORIZONTAL`. L’échelle orthographique indique la largeur horizontale du cadre Blender. La distance latérale de 4 m est arbitraire et n’influence pas cette projection. Les orientations/quaternions et tous les paramètres sont explicites dans le JSON ; aucune focale réelle n’est attribuée à ces vues.

Les deux axes de roues s’alignent exactement par construction. L’accord presque parfait du guidon R00 **n’est pas une validation indépendante** : les guides historiques ont déjà été construits à partir de cette image. Le résidu R04 dépasse les intervalles de lecture du guidon (±12 px). Il reste visible et réservé. Les axes portent chacun ±5 px de lecture ; ces intervalles n’incluent pas une erreur de projection, de profondeur ou de position 3D des guides. Ne pas déformer les composants ou déplacer les anciens guides pour absorber cet écart.

Une famille perspective bornée a aussi été essayée : focales Blender de 35/50/85/120 mm sur capteur horizontal de 36 mm, lacet ±20°, tangage ±15°, roulis ±5°, distance de travail 1,3–15 m. Ces bornes sont des hypothèses d’exploration. R00 peut être ajustée presque exactement sous les quatre focales ; R04 admet plusieurs accords à l’intérieur des intervalles de lecture. Le tangage atteint la borne −15° dans deux essais R04. Trois points donnent six contraintes image, alors que pose et focale libres ont au moins sept paramètres ; de plus, les points 3D utilisés sont estimés. Une petite erreur de projection ne sélectionne donc pas la caméra réelle. Aucun de ces essais perspective n’est adopté comme calibration ou solution métrique.

[R00-working-guides.svg](R00-working-guides.svg) et [R04-working-guides.svg](R04-working-guides.svg) sont des surimpressions transparentes à poser sur les originaux sans redimensionnement : repères observés en vert, guides projetés en jaune et résidus en rouge. Les huit segments ouverts réservoir/selle de chaque vue sont repris en cyan, uniquement comme annotations 2D existantes. Ils ne ferment pas les parties masquées et ne deviennent pas des sections 3D. Les PNG avec pixels photographiques restent temporaires et privés, aux chemins consignés dans le JSON.

Reproduire l’étude :

```sh
python tools/fit_motorcycle_reference_cameras.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python creative/research/reference-camera-studies/check-working-cameras.blender.py
```

La seconde commande a réellement été exécutée, sans rendu : [blender-projection-check.json](blender-projection-check.json) confirme que les projections des caméras Blender correspondent aux équations à moins de 0,001 px. Ce seuil vérifie l’implémentation des caméras, pas la fidélité aux photographies. Aucun fichier source existant n’a été ouvert/modifié pour ce contrôle.

Pour utiliser ces vues, placer une copie de travail du composant dans le repère commun (origine : axe central de serrage du guidon ; +X gauche pilote, +Y arrière, +Z haut), puis ajouter les caméras sans déplacer les guides figés. Une pièce encore en repère local nécessite d’abord une pose d’assemblage explicitement estimée. Comparer les seuls contours visibles ; conserver l’écart R04 et les profondeurs inconnues. Aucune cote de pièce, fixation cachée, rayon de pneu ou réception G2/G3/G8 ne se déduit de cette étude.
