# Passenger rubber outer envelope v2 — clos en lecture seule

**Aucune source géométrique v2 créée. Aucun fragment de remplacement. Conserver les deux JK et leurs poses actuelles pour la livraison.**

Après lecture de la vraie vue PBR96 `creative/reviews/whole-exterior-material-preview-v7/material-left-quarter.png`, aucune pointe métallique extérieure n'est clairement isolée. L'apparence du gris ne motive donc pas de lissage ou de déplacement du caoutchouc.

## G2 avant toute géométrie

Lecture effective des deux sources natives PEG/JK et des poses des 140 parents v19. Les axes longitudinaux +X sont correctement alignés sur les deux côtés. Dans le repère du JK, le PEG est translaté d'environ −26 mm sur X, sans décalage latéral ou défaut d'axe significatif. Le rayon maximal du métal dans la zone du corps est d'environ 14,50 mm, inférieur au rayon extérieur de travail du caoutchouc de 15 mm. Ces valeurs sont des estimations de source, pas une mesure de jeu fonctionnel. Elles ne prouvent ni une pointe métallique visible, ni une correction rigide nécessaire. Détails et matrices exactes : `G2-pose-diagnosis.json`.

## G1 : limite précise

Les deux vraies photos JK ont été relues : oblique russe et profil Mundi. Elles bornent les colliers évasés et les côtes des faces exposées. L'oblique ne montre pas tout le dessous ; le profil conserve une bande longitudinale sombre dont la nature reste ambiguë. Les colliers complets des extrémités ne prouvent pas à eux seuls la continuité ni la section extérieure de la bande entre eux.

Interpoler et fermer le quartier inférieur ajouterait donc une hypothèse de surface/topologie non résolue par ces vues, même en omettant les rainures, l'alésage et la rétention. G1 n'est pas forcé. Le seul élément manquant susceptible de clore cette question serait une vue attribuée du dessous/opposé du même exemplaire, ou un relevé de sa section extérieure, montrant explicitement la continuité ou l'interruption de cette bande entre les colliers.

Le diagnostic historique à 90° reste intact et reste qualifié **omission de revue, pas fente physique**. Il ne faut pas le reclasser comme caractéristique réelle. Les anciennes sources, paramètres, builders et preuves n'ont pas été écrits. Aucun contrôle PV/UV/normales après modification n'est requis puisqu'aucune modification n'a eu lieu ; la lecture native constate zéro couche UV et aucune normale personnalisée dans le JK historique.

`G0-G2-read-only-verdict.json` contient le verdict, les URL/SHA/observations des photos sans pixels redistribués, et la référence PBR réellement lue. `old-immutable-inputs.json` conserve les empreintes des sources historiques consultées. Aucun Blender, GLB, rendu ou motif nouveau n'est produit. Aucun G8/OEM/montage fonctionnel n'est déclaré reçu.
