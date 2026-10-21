# Audit indépendant du kick — cannelures et raccord de tige

**Les cannelures internes sont documentées ; leur débordement sur la charnière constitue un défaut visible du candidat.** Audit de `/root/inventory_trace`, 21 octobre 2026. [Rapport attribué et empreintes](kickstarter-independent-visual-audit.json).

La photo BikeboxPA621203 montre un alésage réellement cannelé. Le nombre28 et la profondeur du candidat restent estimés, avec compatibilité125RDC non certifiée. Dans la macro du candidat, des stries gagnent le pont et l’oreille basse hors de cet alésage (zone approximative x390–500,y530–610 du PNG1100×850). Aucune photo ouverte ni l’éclaté n’appuie cette bande dentée de charnière. La variante incertaine ne suffit donc pas à la présenter comme forme réelle ou estimation défendable.

La lecture seule de `build.py:30–41` corrobore une fuite possible du découpage : le cutter cannelé de portée w±60mm est soustrait après union du moyeu, des oreilles et des ponts. Aucun booléen ou maillage n’a été réévalué ici. La reprise doit conserver les cannelures du moyeu et rétablir la surface de liaison de charnière dans une nouvelle version ; les preuvesv1 restent intactes.

Le raccord tige/œil mobile montre aussi un resserrement et une cassure locale de reflet. Ce point mérite une revue de finition, sans preuve de fissure, collision ou séparation géométrique. Les jeux entre fourchette fixe et œil mobile sont fonctionnels : ils ne doivent pas être effacés pour lisser toute la base. Les photos ne donnent ni section ni rayon de congé mesurés.

Onze images ont réellement été ouvertes et hashées : quatre PNG finaux, les deux photos de produit attribuées, l’éclatéBM125D04:29 et quatre vuesRDC. Les attributions contradictoires PA621203 (BM150BS3/V12-V15/UG5gear) restent explicites dans le JSON. Aucun pixel privé n’est recopié. Source`6fade26e…` et GLB`eeeaa1e8…` ont été vérifiés inchangés en fin de revue.

Constats transmis directement à B (`/root/lever_visual_audit`) et au coordinateur. Aucun nouveau rendu, changement de source, ancienne preuve, manifeste ou registre partagé. Aucune réception artistique, mesure de variante ou certification mécanique accordée.

SHA256 du rapport JSON : `c2c711344a1defb740dee69179ff57b306c910b453b520b99813c9e954f229f4`.
