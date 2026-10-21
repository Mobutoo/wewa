# Soufflet v2 — candidat de grande bouche

La révision ajoute un vrai profil de lèvre/gorge, un épaulement intérieur et quatre ponts radiaux conditionnels. Elle préserve l’historique v1, ses formes de revue et son outil tangent. La source reste une pièce isolée, sans collier supérieur ni pose de montage certifiée.

Les [photos apparentées et leurs limites](../../research/front-fork/bellows-interface-role-study-v1.README.md) soutiennent ces détails de section. Elles ne certifient pas la référence RDC, les dimensions ni la fonction mécanique du retour. Les [paramètres et six photos effectivement ouvertes](../../research/front-fork/bellows-v2-plan.json) conservent les estimations avant la construction. Le diamètre vendeur50mm est contradictoire et n’a pas été adopté.

La [coupe des vrais triangles exportés](actual-buffer-sections.png) distingue le pont local à0° et la gorge à45°. Le [contrôle source](source-geometry-check.json), les [buffers GLB](geometry-check.json) et la [comparaison de matière](material-preservation-check.json) séparent forme, export et cartes. Une coque fermée est la matière du soufflet : ses deux entrées restent ouvertes autour de l’axe.

Le [raccord conditionnel](conditional-interface-check.json) garde une entrée libre46mm contre un col candidat48mm. La chambre49mm ne suffit pas à prouver l’insertion : position axiale, rôle de lèvre et déformation élastique sont inconnus. Les morphs110/125/140mm sont des amplitudes de revue visuelle estimées, pas des courses homologuées.

La matière reprend des cartes originales de caoutchouc sombre non métallique,512², grain de référence≈120µm, relief RMS≈1,27µm et rugosité estimée. Leur échelle varie avec le rayon et le paramétrage du retour ; aucune réflectance OEM n’est mesurée. Les gris et la macro de reflets précèdent cette matière. Les fichiers de checkpoints lient chaque vue finale à la source, à l’export, à la caméra, aux lampes et au nombre réel d’échantillons.

Les contrôles numériques, la revue de forme, le rendu moteur et la réception utilisateur restent distincts. La pièce détaillée d’inspection n’est pas un LOD mobile qualifié ; ni FPS iPhone, ni montage réel, ni réception artistique ne sont déclarés.

Quatre vues finales Cycles CPU96 + OIDN réellement ouvertes : [entier](quarter.png), [grande bouche](lower-opening.png), [compression estimée](compression-estimated.png), [extension estimée](extension-estimated.png). Les images sont rattachées au gel exact par leurs checkpoints.
