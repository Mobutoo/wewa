# Source géométrique indépendante avant matière

Copie byte-identique du premier gris construit, sans pixels photographiques. Le constructeur `../build.py` génère cette forme originale ; `../material.py` ouvre ce master et exige la revue gris/reflets qui correspond exactement à ses SHA. Les sorties PBR vont dans le dossier parent, ce master n’est pas écrasé. `../check_material_preservation.mjs` compare réellement tous POSITION/N/UV/T/indices et matrices monde avant/après.

167988 triangles, deux vrais passages, tôle finie et deux plis. Métriques, section exacte, côté installé et soudure restent estimés/non reçus. Le contrôle BVH ne certifie ni les coplanaires ni les adjacences. La copie n’est pas une réception artistique.
