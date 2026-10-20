# Carter extérieur droit — candidat isolé v1

`MOTO-ENGINE-COVER-RIGHT-001` : une seule fonderie creuse, avec grand bossage arrière et siège de filtre avant. Le bouchon de filtre, le kick, les vis, le bouchon d’huile, la commande et les pièces internes restent séparés. Le graphisme constructeur visible sur les photos n’est pas copié.

La silhouette provient d’annotations des vues officielles RDC, relues avec engine/strong-chasis et les rotationsR00/R01/R07. Le catalogue BM125 voisin explique la séparation des pièces, sans certifier la variante actuelle. Les recherches ciblées de couvercle nu n’ont donné ni nouvelle photo utile ni dimensions physiques. Le choix de travail est une coque d’environ253×190×47mm, paroi3mm ; toutes ces dimensions, la profondeur des bossages et les deux stations de fixation retenues restent estimées. Une troisième station hors contour, possiblement liée à la protection moteur, a été rejetée. Le nombre complet de fixations n’est pas connu.

La source construit un loft asymétrique continu, des couronnes et un raccord lissé entre bossages. Les ouvertures sont réellement soustraites ; la cavité arrière est testée par rayon. Les nervures internes et les interfaces cachées ne sont pas récupérées. Le congé global d’une première version de travail a été refusé pour défaut de fermeture ; les larges rayons restent dans les sections d’origine. Le nettoyage du candidat n’a déplacé aucun sommet ni changé la surface ou le volume. Aucun correctif de tangente n’est utilisé.

Collection `WEWA_ENGINE_COVER_RIGHT`, objet `RH clutch cover hollow casting - editable candidate`, parent `Engine RH cover provisional datum`. Datums estimés dans [parameters.json](parameters.json), axes locaux u=avant−Y, v=haut+Z, w=droite−X. Le GLB ne contient que cette pièce. La source détaillée conserve construction et studio masqués séparément. Le coût élevé du candidat d’inspection n’est pas un budget de jeu mobile.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-cover-right/build.py
node assets-src/moto-components/engine-cover-right/check_export.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-cover-right/render.py
python assets-src/moto-components/throttle-control/record_checkpoint_review.py engine-cover-right
```

Le PBR argent peint est une hypothèse originale, sans texture photographique ni mesure de matière. Les [références et limites](../../../creative/research/engine-cover-right/reference-observations.json) et la [revue](../../../creative/reviews/engine-cover-right-v1/README.md) distinguent technique, comparaison visuelle et réception. Aucun ajustement mécanique certifié, LOD, test iPhone physique ou accord artistique utilisateur n’est acquis.
