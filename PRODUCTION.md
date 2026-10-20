# Viva Wewa — production par phases

Référence : [plan complet](WEWA_Developpement_Web/docs/PLAN_DE_PRODUCTION.md). Le lien public est une version de travail ; sa disponibilité ne ferme aucune phase.

Après le nouveau refus du rendu de la version 3, suivre aussi l’[audit et la fabrication artistique](creative/ART_PRODUCTION.md). La collecte de sources est séparée de leur adaptation dans Blender et de leur réception dans le moteur. Aucun nouveau déploiement artistique dans cette passe : la version 3 reste la préalpha publique.

Le [lot moto/pilote est refusé](creative/reviews/hero-lot01/README.md) : aucun de ses composants n’a atteint le réalisme demandé. La reprise suit la [fabrication pièce par pièce](creative/COMPONENT_WORKFLOW.md), à commencer par le pneu avant et ses références de détail. La [liste rapprochée du dossier](creative/DOSSIER_ASSET_LIST.md) conserve les 92 fiches AS et les compléments du concept ; les 112 familles préparatoires ne couvraient pas entièrement ce dossier. Les lots et leurs états sont dans le [registre de fabrication](creative/library/fabrication-register.json). Aucun élément n’est déclaré reçu artistiquement avant retour utilisateur.

| Phase du plan | Production présente | Critères encore ouverts |
|---|---|---|
| P1 — socle | Babylon.js 9.31.0 / WebGL2, build gelé, géographie importée, instrumentation | Safari physique iPhone 15/16, audit local des routes, benchmark matériel |
| P2 — moteur de conduite | Simulation fixe 60 Hz et interpolation, joystick unique, clavier remappable, frein/recul, collisions balayées indexées, reprise après choc, nitro, deux caméras, effet périphérique facultatif, surface/suspension à deux contacts | Sol actuel plat ; la compatibilité et les performances physiques restent à qualifier |
| P3 — boucle de jeu | Trafic sur voies orientées, files et cession de passage de jeu, piétons groupés, livraison de six colis, poursuite de 1 300 m, recherche récupérable, checkpoints locaux versionnés, Rush 30 s, profil/records/réputation/pièces, deux itinéraires alternatifs et jetons | Priorités locales, agrément et conduite humains sur appareils ; pas une réception complète V0 |
| P4 — production 3D | Douze travées de façade, vingt objets de rue, deux objets de collecte, douze LOD de façade, moto/pilote/taxi/minibus ; sources Blender et exports conservés | Rue étalon exacte, références des façades réelles, personnages animés, éclairage précalculé, examen artistique en mouvement |
| P5 — assemblage V1 | Fondation de sauvegarde et streaming existante | Roulage/convoi, contact, concert et halte fluviale géographiquement validés, parcours de quinze minutes |
| P6 — qualification | Tests logiciels et Chromium avec émulation tactile | Réseau froid/chaud, session longue, profils physiques, panel et bêta |
| P7 — extension/commercial | Aucun paiement réel | Nouvelles zones, catalogue et services commerciaux après validation et budget |

## Moteur du jeu

Le moteur de rendu Babylon.js est conservé. Les systèmes propres au jeu sont dans `app/src/engine/` :

- `roads.ts` : voies orientées depuis les sources, recherche de trajet, rejet des voies intersectant les emprises ;
- `traffic.ts` : progression fixe, distances de sécurité, files, croisements, piétons et graine réinitialisable ; le rendu lit ces états ;
- `spatial.ts` : index des obstacles statiques, sans suppression des cours intérieures ;
- `surface.ts` : surfaces d’adaptation séparées, deux contacts de roues et inclinaison ; aucun relief fin imaginaire livré comme mesure ;
- `missions.ts` : livraisons pour Mado, message, taxi, perte de vue récupérable et indice ;
- `checkpoint.ts` : contrat de sauvegarde, validation et reprise atomique ;
- `profile.ts` : records par règles/graine, profil, récompenses de fin uniques, monnaie distincte ;
- `bindings.ts` : remappage clavier et alias ZQSD/WASD ;
- `speed-effects.ts` : flou périphérique optionnel, désactivé par le mode Confort ;
- `dressing.ts` : instanciation et niveaux de détail des éléments Blender.

Les priorités conservatrices du trafic ne sont pas présentées comme des panneaux de Kinshasa documentés. Les emprises et coordonnées sources ne sont pas déplacées.

## Chaîne Blender

Les sources modifiables sont versionnées dans `assets-src/`, séparées des fichiers livrés au navigateur. La bibliothèque de rue a cinq matériaux partagés, des fenêtres et encadrements géométriques, balcons, rideaux et brise-soleil. Les façades sont des propositions réutilisables : elles ne certifient pas la forme réelle de chaque bâtiment.

1. `blender --background --python assets-src/street-kit/generate_street_kit.py`
2. `blender --background --python assets-src/street-kit/lod1/generate_lod1.py`
3. `node tools/pack-street-kit.mjs`
4. `python tools/prepare_street_dressing.py` (environnement Python avec Shapely)
5. `npm run build`

Les exports individuels restent dans `assets-src/street-kit/exports/`. La bibliothèque web déduplique matériaux/textures et conserve les noms d'assets. Le manifeste donne dimensions, triangles, droits et empreintes. Les LOD proches sont réservés aux deux niveaux inférieurs à moins de 45 m ; les autres travées utilisent les LOD légers jusqu’à 200 m. Cela ne constitue pas une mesure de FPS.

Les vérifications exécutées et captures réelles sont dans `WEWA_Developpement_Web/validation/`. Les tâches bloquées conservent leur cause et leur prochaine action ; aucune phase n’est close sur la seule existence de tests unitaires.
