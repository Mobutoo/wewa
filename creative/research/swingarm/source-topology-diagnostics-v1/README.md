# Témoins et méthodes refusés pour le corps de bras

Ce dossier conserve les diagnostics antérieurs au gel du corps. Ils ne sont pas des preuves de réception.

Le témoin `BVHTree.find_nearest` de Blender renvoie jusqu’à0,204mm sur un centroïde comparé à son propre triangle très mince. Il n’est donc pas utilisé comme métrologie de cette surface ; le diagnostic à soi-même reste conservé.

Le témoin de remplacement emploie des calculs point/triangle en float64 : inclusion dans le plan et projections clampées des trois arêtes. Les candidats sont bornés par leur AABB et la distance à un sommet effectivement présent sur la surface. Les positions et triangles identiques sont prouvés coïncidents ; les autres sommets et centroïdes sont échantillonnés. L’identité sur96centroïdes de chaque surface revient à environ2e−17m. Cette mesure échantillonnée n’est pas une preuve de distance de Hausdorff globale.

La simplification générale Manifold demandée à0,5µm est refusée : le témoin relève1,94µm dans un sens et73,7µm dans l’autre, au-delà de la borne de travail fixée à1µm. L’annonce de tolérance de la bibliothèque ne remplace pas ce contrôle. Cette simplification et les essais de fusion globale BMesh ne sont pas adoptés dans la recette finale.

Le traitement suivant porte seulement sur les arêtes adjacentes minuscules du corps brut fermé : condition de lien topologique, rejet des plis et rayon maximal du groupe d’anciens sommets autour de son sommet conservé. La fermeture, les déplacements, le volume et les vraies tangentes sont à vérifier avant adoption. Les fichiers de production ne doivent pas utiliser les résultats refusés de ce dossier comme réception artistique.
