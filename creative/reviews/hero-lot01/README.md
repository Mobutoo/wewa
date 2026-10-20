# Viva Wewa — lot 01 refusé

**Décision utilisateur : toutes les vues sont refusées pour manque de réalisme et fabrication trop globale.** Les fichiers ci-dessous sont des preuves historiques du lot rejeté, pas des composants reçus ni une nouvelle demande de validation. Reprise selon le [contrôle pièce par pièce](../../COMPONENT_WORKFLOW.md).

**Premier lot de modèles, pas une nouvelle version du jeu complet.** La ville, ses façades et son ambiance restent à fabriquer selon la liste du dossier. Le jeu public n’est pas remplacé par ces modèles pendant cette réception.

Le lot comprend la moto utilitaire au gabarit de référence, le pilote articulé, la tenue veste/denim et les chaussures, un casque, un sac et un colis avec ruban et liens. Les manches/mains ont aussi un export séparé pour la vue au guidon. L’anatomie et les vêtements sont adaptés de sources CC0 documentées ; le casque, le sac et la géométrie de moto sont des créations du projet.

| Vue | Fichier | Ce qu’elle permet de juger |
|---|---|---|
| Arrière trois quarts | [Rendu Blender](blender-rear-quarter.png) | Rapport pilote/moto, casque, sac, allure générale |
| Colis seul | [Rendu Blender](blender-cargo-rear-quarter.png) | Plis, ruban, ficelles et étiquette fictive |
| Profil | [Rendu Blender](blender-side.png) | Assise, jambes, roues et gabarit |
| Avant trois quarts | [Rendu Blender](blender-front-quarter.png) | Posture, poignées et silhouette avant |
| Modèle dans le moteur | [Capture Babylon.js](engine-rear-quarter.png) | Apparence avec les matériaux et l’éclairage actuels du jeu |
| Guidon et mains | [Capture du cadrage proposé](engine-handlebar-proposal.png) | Lecture des instruments, position des mains et visibilité de la route |

Les images de studio sont calculées à partir des vrais modèles dans Blender. Les images dans la rue proviennent de Babylon.js : les réponses des fichiers GLB sont remplacées **localement** pour examiner le lot. La ville visible derrière reste celle de la préalpha. Le cadrage au guidon est une proposition de réception, pas un réglage déjà appliqué au jeu public.

## Demande de retour initiale — archivée après refus

Examiner les proportions de la moto et du pilote, la posture, le casque, le sac et les couleurs. Signaler les éléments à conserver et ceux à reprendre. Cela reçoit une direction de fabrication ; cela ne clôt ni W17, ni la qualité photographique de toute la scène.

La tenue source est actuellement plus longue et structurée que la veste souple de la référence. La coupe, les optiques, la carrosserie, la prise fine des doigts et les matières demandent encore une finition. Le colis est une variante visuelle chargée pour cette réception ; il ne commande pas encore l’inventaire des missions. Les points d’ancrage des liens à la moto restent à finir. Les autres véhicules et personnages, les décors de rue et la patine générale ne sont pas dans cette réception.

## Fichiers de travail et contrôles

- [Scène Blender modifiable](../../../assets-src/hero-lot01/hero-lot01.blend).
- [Moto GLB](../../../assets-src/hero-lot01/exports/motorcycle.glb), [pilote GLB](../../../assets-src/hero-lot01/exports/rider.glb), [mains/manches GLB](../../../assets-src/hero-lot01/exports/firstperson.glb), [colis GLB utilisé dans les captures](../../../assets-src/hero-lot01/exports/cargo.glb).
- [Colis : source et matières originales](../../../assets-src/cargo-lot01/README.md).
- [Liste issue du dossier](../../DOSSIER_ASSET_LIST.md) et [registre de fabrication](../../library/fabrication-register.json).
- [Provenance et reproduction](../../../assets-src/hero-lot01/README.md).

Les exports ont été chargés dans le moteur avec leurs textures et leurs squelettes. Un déplacement de la moto de trois mètres conserve le rattachement du pilote. Les modèles sont contrôlés par le validateur glTF ; les avertissements conservés sont enregistrés dans les rapports des exports. Ces contrôles ne constituent pas une réception artistique ou une mesure sur iPhone. Les performances, les LOD/KTX2, les transitions d’animation et la conduite humaine sur Safari restent à qualifier.
