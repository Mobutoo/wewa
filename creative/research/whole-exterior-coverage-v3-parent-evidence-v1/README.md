# Parents pour whole exterior coverage v3 — inventaire documentaire

Onze parents existants inspectés dans leurs sources natives, sans fabrication ni placement. Le SNS v3 compte **un parent** contenant quatorze unités liées, pas quatorze amortisseurs. Aucune source Blender sauvegardée ; empreintes avant/après identiques.

`inventory.json` donne les sources exactes, SHA256, collections, sélections explicites, matrices d’origine, coordonnées de repères déclarées et bounds évaluées. Ces bounds décrivent les candidats dans leur scène source : **ce ne sont ni des cotes OEM ni des positions montées sur la moto**.

| Parent | Collection / sélection utile | Repère de source et limite |
|---|---|---|
| sidecover-LH | WEWA_SIDE_COVER_LEFT_STUDY | Append skin collection plus separate Scene Collection fastener. No skin-only shortcut. |
| sidecover-RH | WEWA_SIDE_COVER_RIGHT_STUDY | Append skin collection plus separate Scene Collection head; do not mirror LH or infer matching axes in motorcycle world. |
| rear-sns-rest-assembly-v3 | WEWA_REAR_SNS_REST_COMPOSITION | ONE parent only. 14 linked units inside composition. Do not instantiate each child as extra shock, and do not generate a second installed shock. |
| chaincase-upper | WEWA_CHAINCASE_UPPER_ISOLATED | Partial shell, front ear incomplete; no installed chainline or fit to lower shell. |
| chaincase-lower | WEWA_CHAINCASE_LOWER_ISOLATED | Shared working envelope with upper only a hypothesis; no verified seam/overlap or cap. |
| rack-outer-rail | WEWA_RACK_OUTER_RAIL_STUDY | Outer U rail only; open review cuts, no brackets/weld/deck. Do not apply center_shift again. |
| rear-rack-deck | WEWA_REAR_RACK_DECK | Only recorded rack relation is proposed estimated translation[-.14,0,.084], not applied in source. Rotation needed to align outline axes to rack not documented. |
| front-footrest-left | WEWA_FRONT_FOOTREST_LEFT | Automatic attachment explicitly forbidden by interfaces. No frame anchors; rubber excluded. |
| front-footrest-right | WEWA_FRONT_FOOTREST_RIGHT | IndependentRH geometry, not mirroredLH. Automatic attachment forbidden; no installed transform. |
| centre-stand-main-frame | Scene Collection — objet explicite | No dedicated named asset collection in native. Select exact mesh by name from Scene Collection; exclude scene/cameras/lights. Deployment/pivot-world transform unknown. |
| front-brake-plate-v2 | WEWA_FRONT_BRAKE_PANEL_BODY | Use visible detailed casting ONLY. Inspection mesh in same collection is a masked alternative, not second part. Exclude editable CSG, rim/tyre fit candidates and studio. Do not add .290m a second time. |

Points utiles pour le diagnostic :

- **Caches LH/RH** : X arrière, Y haut, Z extérieur local. Les têtes visibles sont dans `Scene Collection`, hors des collections de peau : importer les deux meshes explicites de chaque cache. La tête LH a déjà une position source non nulle ; la tête RH porte son placement dans les sommets. Ne pas les recentrer ni les omettre.
- **SNS v3** : collection `WEWA_REAR_SNS_REST_COMPOSITION`, quatorze bibliothèques relatives présentes et vérifiées. Z vers l’œil opposé, axes d’œil Y ; centres déclarés des yeux à Z−0,1115 et Z+0,220m. Ce sont des positions locales candidates, sans ancrage cadre.
- **Carters chaîne** : datum de demi-arche arrière0 ; avant−Y, haut+Z, normale extérieure+X provisoire. Les passages de fixation candidats sont recopiés depuis les paramètres, avec statut estimé. Même datum de travail ne vaut pas emboîtement validé.
- **Rail/deck** : rail +X avant, Y latéral, Z vertical ; décalage de recentrage auteur `[.23,0,-.01]` déjà incorporé au mesh. Le deck reste centré dans son propre planXY. La proposition de translation `[-.14,0,.084]` vers le rail est explicitement **estimée, non appliquée**, rotation et raccord inconnus.
- **Repose-pieds** : tube local+X des deux côtés ; cela ne constitue pas une symétrie de montage. Repères des trous et de la patte RH fournis par `interfaces.json`, avec montage automatique interdit et matrices installées nulles.
- **Béquille centrale** : aucune collection asset dédiée dans ce fichier. Sélectionner uniquement `CENTRE_STAND_MAIN_FRAME_OPEN_PIVOT_PIERCED_WEB`. X latéral projeté, Y haut, Z profondeur. Origine de l’objet0 ; pivot installé et déploiement inconnus.
- **Flasque avant v2** : mesh visible `Front brake panel - editable casting` uniquement. Le mesh `Front brake panel - inspection export` est une alternative masquée dans la même collection. L’axe de roue est **déjà à Z0,290m dans les sommets** malgré object.location0 : ne pas rajouter0,290m. Les volumes CSG cachés, roue/pneu de comparaison et studio sont exclus. Le lien du pneu de contexte manque ; il n’est pas nécessaire à la sélection du corps et n’a pas été restauré.

Les cinq seuls binaires absents nécessaires à cette inspection ont été récupérés via `git show HEAD:chemin`, sans index/ref modifié : carters supérieur/inférieur, supports de repose-pieds LH/RH et flasque avantv2. Les README/paramètres absents ont été lus depuis Git en mémoire/copie scratch, sans restauration générale. Liste et SHA exacts dans l’inventaire. Les fichiers déjà présents n’ont jamais été écrasés.

Les relations non documentées restent `unknown` et `installed_motorcycle_transform:null`. Aucune rotation d’axe, position monde, placement miroir ou deuxième SNS n’est proposée. Les anciens wholecoveragev1/v2, registres et métadonnées partagées restent intacts.

Vérification : onze sources disponibles et inchangées après lecture ; quatorze entrées SNS comparées aux empreintes du build-report ; bounds calculées seulement sur les meshes détaillés sélectionnés. JSON et manifeste cohérents. Ce dossier ne produit ni assemblage ni rendu et ne vaut pas réception artistique.
