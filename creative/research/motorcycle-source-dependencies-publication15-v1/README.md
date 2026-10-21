# Source15 — audit préliminaire des recettes

Base immuable : `486a6493deb8db3d93e838bac36b734bb58bb608`. **Aucune coupe finale fixée** : le joint v1 reste un candidat technique en reprise G4 ; sa révision 2 et les finales du carter inférieur sont actives. Aucun stage, rendu, export, ouverture de maillage ou modification des sources/globaux.

Le [rapport](report.json), la [fermeture exacte](source-closure-v1.json) et les [entrées par phase](stable-recipe-inputs-v1.json) portent les chemins/SHA. Ils sont des relevés historiques bornés, pas des manifestes vivants du catalogue.

| Candidat | Entrées vérifiées | Reprise |
|---|---|---|
| Joint v1 | source 59 + revue 73 + root 20 | Maître géométrique + geometry-report/paramètres → material.py ; deux JSON header comme garde numérique, sans Library. |
| Carter inférieur v1 | source 34 | Restaurer G3master + trois contrôles dans une copie, conserver gray-review et material-plan, puis matière et contrôles actuels. |

**186 paires SHA/octets, 4 manifestes et 120 fichiers uniques** vérifiés, aucun écart. Aucun rendu actif n’est inclus dans ce pointage.

## Reprise et limites

Le joint a trois cartes originales, dont le quadrillage régulier est explicitement refusé en G4 par root. Rejouer material.py reproduirait ce défaut ; cela ne corrige pas la matière. Le joint est isolé à origine 0, sans matrice de pose moto. Épaisseur proposée 2 mm et gap header 1,2 mm restent un conflit d’estimations, sans compression ni déplacement pour le masquer.

Ses extractions UV/PNG WIP sont régénérées depuis le GLB par le checker Node. Les checkpoints 24 privés **et** leurs PNG/EXR ne sont exigés que par le script de fermeture historique record_preflight, pas par la matière ni le renderer 96. Copier seulement ces JSON serait insuffisant et inutile pour reprendre le rendu courant. Aucune copie privée n’a donc été créée. De nouvelles preuves demanderaient de nouvelles images réellement inspectées.

Pour le carter, les petits gray-review.json, source-geometry-check.json, geometry-check.json et source-interface-check.json ne sont pas tous dans source 34. Ils existent et sont listés, avec material-preview-review pour fermer les preuves et l’outil caméra commun déjà suivi. Le matériau n’est pas idempotent sur le PBR : restaurer les deux binaires gris et leurs contrôles aux chemins actifs dans une copie isolée avant application. Les images grises restent des preuves distinctes ; material.py ne les charge pas comme textures.

Aucun CSG appelé, aucune police, HDR ou photo documentaire nécessaire à ces deux recettes. Aucun href local manquant n’a été trouvé dans les README réellement présents dans cette fermeture. Les versions Blender 4.3.2, NumPy/Pillow/Node et scratchs absolus restent des prérequis ; aucun replay depuis clone propre n’est revendiqué.

## Reliquats des 18 lots

La base Source14 comporte 63 IDs. Le pointage V4 historique reste inchangé ; quatre constructions de Source14 sont prises en compte : pare-chaleur et fixation partielle au 17, carter supérieur au 16, housse/bourrelet de selle au 18. Le joint technique 64 et les travaux locaux suivants sont séparés.

| Lot / propriétaire | Travail physique et interfaces encore ouverts |
|---|---|
| 1 — A | DS181007 et Nyloc construits ; DS181008 non construit ; DS181009/10 et pile réelle toujours documentaires. |
| 2 — A | Support et compteurs construits ; liaisons/fixations et repères communs ouverts. Compteurs restent complément, aucun lot 19. |
| 3 — B | Commande/poignées construites ; câble sortant suivi une seule fois au10. |
| 4 — C | Commodo gauche construit ; fils au10 et variantes/interfaces ouverts. |
| 5 — C | Commodo droit construit ; identité/fonction de commande rouge et montage non certifiés. |
| 6 — B | Levier/support construits ; vis/écrous de bridage et câble 10 restent. |
| 7 — B | Levier/support construits ; vis/écrous de bridage et câble 10 restent. |
| 8 — C | Deux rétroviseurs distincts construits ; montage/fit/art ouverts, pas de miroir supposé. |
| 9 — B | Barillet/clé construits ; anneau et connecteur/départ 10 restent. |
| 10 — B | Trois gaines locales/boucle v2 construites ; parcours supérieurs, connecteurs, faisceaux et attaches restent. |
| 11 — C | Coque de visière construite ; retours/attaches cachés non documentés et raccords restent. |
| 12 — C | Coiffe/protecteur/boîtier construits ; optique/réflecteur/douille, clignotants avant et fixations restent. |
| 13 — A | Tés, tube, deux fourreaux et soufflets construits ; colonne/pile direction, bouchons/vis/joints et montage restent. |
| 14 — A | Quatre candidats avant anciens et valve approximative existants ; qualité/compatibilité, axes/pile et unités frein/compteur restent. |
| 15 — A | Six unités cadre et bras/bague/axe construits ; garde-boue, arceau distinct, cadre/pattes restants, écrou/patin/tendeurs et montage restent. |
| 16 — A ; SNS arrière C | Pneu v2, jante partielle et carter supérieur construits dans Source14. Carter inférieur possède maintenant source 34 mais pas encore livraison/record Source15 clos. Bouchon/carter fixations, chaîne/transmission, moyeu/pile/frein et SNS restent. |
| 17 — B | Pare-chaleur et fixation partielle sont construits dans Source14. Joint v1 construit localement, G4 quadrillage en reprise2 et G5 non monté : ni nouvelle absence ni pièce acceptée. Bride/supports, admission/HT/centre, repose-pieds/commandes/béquilles et cockpit restent. |
| 18 — C | Réservoir extérieur et housse/bourrelet/coutures de selle construits dans Source14 ; embase/mousse/appuis, attaches, bouchon/robinet/durite, caches, rack/éclairage/plaque restent. |

Les SNS arrière restent chez C. Les frontières pédale17B/tige16A, garde-boue15A/optique18C, carburant18C/arrivée17B et câbles10B/HT17B restent inchangées. Aucun groupe complet ni pourcentage déduit des IDs.

Repose-pied LH, embase de selle, patin et joint v2 non gelés restent hors de cet audit. Une future admission utilisera des fermetures réelles distinctes ; les gels et rapports antérieurs restent immuables.
