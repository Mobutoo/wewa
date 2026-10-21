# Contrôle indépendant — matière et éclairage du soufflet

Aucun défaut d’albédo blanc, de métallic ou de conversion n’est établi dans les données contrôlées. Les deux rendus se lisent pourtant très clairs et satinés par rapport aux photographies RDC. [Rapport, données et empreintes](bellows-material-independent-audit.json), 21 octobre 2026.

Le GLB a été relu directement : facteur de couleur **linéaire0,010/0,012/0,015**, métallique effectif **0**, rugosité effective **107–150/255** (environ0,42–0,59). Les deux images embarquées sont identiques aux PNG auteurs. Les cartes sont déclarées `Non-Color` dans la fabrication ; G alimente la rugosité et B le métallic. La phase matière recrée les nœuds du gris provisoire. La phase rendu ne réintroduit pas ce gris.

Le studio hérité comporte quatre grands disques AREA à proximité de la pièce de125mm, ainsi qu’un monde gris. Les calculs linéaires précèdent la transformation de vue AgX/Medium High Contrast et le PNG. De grands reflets diélectriques blancs peuvent couvrir les couronnes d’un caoutchouc noir sans matériau métallique. Cette explication est plausible ; aucune isolation des contributions ne démontre un «suréclairage» ou sa responsabilité exclusive. L’exposition et le gamma ne sont pas explicitement fixés dans les scripts ni détaillés dans les checkpoints : ils n’ont pas été lus directement dans Blender pendant cet audit.

Les différences visibles de lecture sont donc conservées comme problème de présentation à étudier. La réflectance et la rugosité du véritable composé restent non mesurées. Une étude d’éclairage séparée sur source inchangée, avec HDR commun et mires18%/80%, est prévue par le coordinateur. Rien ne justifie ici un assombrissement aveugle de l’albédo ou une suppression des reflets.

Les quatre images réellement ouvertes sont `quarter.png`, `lower-opening.png`, la photo officielle `suspension.webp` et le profil frontal `rotation-02.png`. Le JSON contient leurs SHA256 et les empreintes des scripts lus. Les textures ont été décodées et comparées comme données, sans être comptées comme images visuellement ouvertes. Aucun processus Blender, nouveau rendu, changement de modèle ou modification d’ancienne preuve n’a été exécuté. Les documents privés restent privés ; aucune réception artistique ou mesure du matériau réel n’est accordée.

Source figée : `fc97e6507c8a757698c39c794fdb38f4ecfc2eab7278d3b1f97a83c66bd7da2c`.

SHA256 du rapport JSON : `1342ab1cafd98c2de7f999c44b928c1f7f61f7402ff0f962c933807db42c57a2`.
