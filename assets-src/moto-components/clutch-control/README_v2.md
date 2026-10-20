# Embrayage au guidon — candidat v2

Référence de levier voisine DJ191083, catalogue D04 et photographies de produit documentées. Le contour est tracé à partir de proportions photographiques non calibrées. Les sections, le support, les oreilles de pivot, le bossage de miroir, le siège de câble et les réglages restent estimés. Le support ne prétend pas reproduire une variante RDC identifiée.

Collection `WEWA_CLUTCH_CONTROL` : six volumes distincts (levier, support, barillet creux de réglage, contre-écrou, axe et écrou de pivot). Pivot monde [0.22231034934520721, -0.015389963984489441, 0.10899999737739563] m. Rotation monde Z de signe 1 et amplitude partielle 0–12°. Cinq poses sans croisement de surfaces avec les pièces fixes, le tube et la poignée ; le contrôle clairsemé de distance ne vaut pas calcul exhaustif de tolérances. Les deux leviers ont des contours indépendants.

Soufflet non fabriqué faute de détail fiable. La commande avant est à câble/tambour : aucun réservoir, maître-cylindre ou flexible hydraulique. La compatibilité du frein JA/DS et la course réelle complète ne sont pas établies.

Source : [clutch-control-v2.blend](clutch-control-v2.blend), export évalué [clutch-control-v2-inspection.glb](clutch-control-v2-inspection.glb), [paramètres](parameters-v2.json), [provenance](provenance-v2.json), [recherche](../../../creative/research/clutch-control/reference-observations.json). Les collections de guides sont liées en lecture seule et masquées par leur collection locale persistante, hors export et hors rendu isolé.

Chaque volume source est fermé, connexe et positif ; le GLB est contrôlé à partir de ses buffers et possède une animation de rotation. Ces preuves concernent l’intégrité technique. Les matières PBR sont originales et estimées ; pas de photo utilisée comme texture. Aucune réception artistique ou vérification physique iPhone, aucun LOD mobile qualifié.

Construction : Blender officiel 4.3.2 `--background --threads 1 --python-exit-code 1 --python assets-src/moto-components/clutch-control/build_v2.py`. Contrôle : `node assets-src/moto-components/clutch-control/check_export_v2.mjs clutch-control`. Le générateur partagé `throttle-control/control_geometry.py` et le CSG existant `front-brake-plate/csg.py` sont des dépendances ; les deux leviers partagent aussi `clutch-control/lever_builder.py`. Les empreintes du manifeste doivent être relues avant reconstruction.

La relecture réelle a révélé des reflets triangulaires artificiels sur la bague CSG. Les arêtes franches et normales pondérées corrigent ce défaut sans changer les positions ou volumes. Le protocole de lumière est réduit pour conserver la lecture de la peinture noire. Les reliefs de moulage non lisibles et le soufflet restent non reproduits.

La v1 est conservée comme preuve historique refusée : ses congés évalués contenaient des triangles dont deux sommets avaient la même position. La v2 nettoie cette topologie après évaluation, garde une copie de diagnostic masquée et refait la fermeture, le volume, les poses et les buffers. Aucun sommet conservé n’est déplacé ; la déviation des anciens sommets vers la surface nettoyée reste inférieure à10nm. Les normales sont reconstruites avec vraies arêtes franches, sans retoucher des tangentes.
