# Assemblage de revue haut moteur — contrôle indépendant v1

Les **sept bibliothèques exactes et12 copies physiques** ont été ouvertes et évaluées dans Blender, puis comparées au vrai GLB de livraison `d0b1a121…`. Les positions locales, triangles, UV, normales de coins et attributs des copies sont identiques aux sources. Les matériaux appartiennent aux bibliothèques prévues. Aucun placement/binding ou modèle ajouté, aucune source sauvegardée ni rendu effectué.

Les **657316 triangles dessinés** correspondent exactement, avec orientation et multiplicité conservées. Les positions locales du GLB sont exactes dans les deux sens, y compris les découpes par matière et les doublons de couture. La différence avec les587164 triangles uniques du contrôle strict root est le second couvercle de visite partagé :70152 triangles. Les12 nœuds physiques fournissent14 primitives dessinées ; ce ne sont pas14 nouvelles pièces.

Les matrices ne sont pas comparées bit à bit : source→copie, l’écart maximal par composante monde est59,60nm et le coefficient de matrice diffère au plus de1,4901e−7. Source/copie→GLB, le coin le plus éloigné est à69,68nm ; les positions locales exactes et les transformations réellement lues permettent d’attribuer cet écart à l’évaluation float32 et à la sérialisation TRS. Le résidu de cette décomposition est1,17e−16m. Le garde de coefficient1e−6 du builder existant est conservé, sans inventer une tolérance de jeu mécanique ni recycler aveuglément les50nm de l’ancien outil cockpit.

Les contrôles de contact cylindre/culasse, couvercles/culasse, embout OHC et capuchon2/bougie2/culasse3 sont **réutilisés**, avec leurs SHA et limites, plutôt que recalculés. Le rapport ne revendique pas zéro contact dans un nouveau test global, aucune cote OEM, aucun jeu minimal ou moteur complet reçu. Les anciens contrôles bougie2/capuchon1 ne sont pas présentés comme contrôles du capuchon2.

`evaluated-source-assembly.json` et `evaluated-arrays.npz` sont la nouvelle extraction Blender. `delivery-buffer-arrays.json` est la lecture des vrais buffers GLB. `oriented-triangle-parity.json` et les scripts donnent le calcul. Les trois échecs diagnostiques et leurs versions de script sont conservés : noms tronqués, propriété des matériaux liés, puis maillage partagé des deux couvercles. Ils ne démontraient pas un défaut de la pièce.

Aucune image ouverte dans cette passe, aucune réception artistique, aucune mesure physique ou validation iPhone. Les captures/rendus et le contrôle strict de root restent des preuves séparées.
