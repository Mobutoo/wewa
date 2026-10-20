# Levier de came du frein avant — candidat v1

Pièce séparée reconstruite dans Blender d’après deux photographies de **JA131607**. Cette référence figure au catalogue BM125 UG5gear, feuille PDF44, item18. Son identité pour la Boxer125HD RDC actuelle n’est pas confirmée. Ne pas confondre ce levier avec la commande au guidon ni avec JW131601, levier arrière écarté après vérification du catalogue.

Les [observations documentaires](reference-observations.json) conservent les URLs et empreintes. Les photos originales restent dans le dossier privé de recherche ; aucune image vendeur n’est redistribuée ou appliquée comme texture. Elles montrent le même côté sous deux angles, sans fournir une vue arrière ni une échelle mesurée.

La fabrication comprend une silhouette courbe, un déport progressif de la lame aux extrémités, un siège d’arbre ouvert et cannelé, un œillet percé et de petits rayons de bord. L’épaisseur de travail est 2,5 mm, l’entraxe de travail 88 mm ; toutes les cotes et le rythme des 20 cannelures sont des estimations explicites dans [parameters.json](parameters.json). Ce ne sont pas des spécifications Bajaj.

Le [script](build.py) crée les volumes originaux et leurs découpes avec Manifold3D3.3.2, conserve les constructions cachées, contrôle connexité/volume/ouvertures, produit les UV et exporte une copie évaluée. La source visible contient les bords évalués ; l’objet de construction conserve le modificateur de congé. Les textures originales donnent une apparence de métal traité, avec variations statiques jaune/vert. La chimie du revêtement n’est pas mesurée et aucune iridescence dépendant de l’angle n’est simulée.

```sh
blender --background --threads 4 --python-exit-code 1 --python assets-src/moto-components/front-brake-lever/build.py
node tools/check_front_brake_lever.mjs
blender --background --threads 4 --python-exit-code 1 --python assets-src/moto-components/front-brake-lever/render.py
```

[Revue et rendus réels](../../../creative/reviews/front-brake-lever-v1/README.md). Ni boulon, ni axe de came, ni câble ou frein opérationnel ne sont inclus. Aucune réception artistique, optimisation mobile ou qualification iPhone acquise.
