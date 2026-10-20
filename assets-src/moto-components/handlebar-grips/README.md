# Poignées caoutchouc seules — candidat v1

Deux enveloppes séparées, placées dans le repère partagé du guidon : X transversal, +Y vers le conducteur, Z haut ; origine au centre du serrage du tube. Les axes et extrémités reprennent les paramètres de travail du guidon `handlebar-v1` sans importer ni modifier son fichier.

La recherche a distingué les vraies poignées du kit de silentblocs présenté par un vendeur sous le titre ambigu « handle rubber kit ». Le catalogue BM125 UG, feuille PDF 48, items 4/5, distingue JV161001/JV161002 standard et DU191009/DU191003 UG5gear. Les photos isolées DU191009 gauche et DU191003 droit sont des références voisines ; leur compatibilité avec la 125HD RDC actuelle reste inconnue. [Observations et sources](../../../creative/research/handlebar-grips/reference-observations.json).

Formes construites : corps légèrement profilé, canaux longitudinaux à bouts arrondis réellement creusés dans la surface, deux petits anneaux de col, évasement intérieur et fermeture extérieure candidate. Le nombre de canaux, leur sens de relief, leurs dimensions, les profils et les faces cachées restent des estimations. Les photographies ne constituent pas un plan mesuré.

La longueur de travail est 120 mm ; corps Ø29,6 mm et collerette Ø41 mm. Alésage gauche Ø22,4 mm autour du tube candidat Ø22,2 mm ; alésage droit Ø25,4 mm avec espace réservé au manchon d’accélérateur absent. Ces valeurs sont des paramètres estimés, pas des cotes constructeur ou une certification d’ajustement. Le fond des cavités est situé 1 mm à l’extérieur des bouts du tube afin que les fermetures candidates ne traversent pas le tube.

Les volumes sont fermés, chacun connexe et de volume positif. Le matériau est un caoutchouc noir non métallique avec carte originale de rugosité ; aucun pixel de photo vendeur ou constructeur ne sert de texture. Aucun microrelief de normal map ou moulage exact n’est déclaré reproduit.

```sh
blender --background --threads 2 --python-exit-code 1 --python assets-src/moto-components/handlebar-grips/build.py
node assets-src/moto-components/handlebar-grips/check_export.mjs
blender --background --threads 2 --python-exit-code 1 --python assets-src/moto-components/handlebar-grips/render.py
```

[Source Blender](handlebar-grips-v1.blend) · [export évalué](handlebar-grips-inspection.glb) · [paramètres et limites](parameters.json) · [revue réelle](../../../creative/reviews/handlebar-grips-v1/README.md).

Ne sont pas inclus : manchon et came d’accélérateur, câbles, commodos, leviers, rétroviseurs, mécanisme ou animation de commande. L’export sert à l’inspection et n’est pas un LOD mobile qualifié. Aucune réception artistique ou validation Safari physique acquise.
