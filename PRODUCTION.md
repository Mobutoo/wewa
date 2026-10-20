# Viva Wewa — production par phases

Le 20 octobre 2026, le style2 est choisi : [réalisme cinématographique](creative/GRAPHIC_STYLE.md). Une [référence générée de la moto seule](creative/direction/motorcycle-wewa-style-02-generated-reference.png) est distincte de la [première pièce Blender](assets-src/moto-components/front-tyre/README.md), un pneu avant candidat encore à reprendre. La jante avant à cinq branches et son raccord estimé au pneu sont maintenant des [candidats Blender isolés](assets-src/moto-components/front-rim/README.md), sans réception artistique. Un [corps de flasque avant](assets-src/moto-components/front-brake-plate/README.md), d’après des photos JA131605 de variante apparentée, poursuit cette fabrication isolée ; il n’inclut pas encore levier, axe ou frein fonctionnel. Le réservoir de la cible générée porte **WEWA**, conformément à la demande utilisateur. La sélection du style ne réceptionne pas la géométrie et ne constitue pas une nouvelle moto3D complète.

Référence : [plan complet](WEWA_Developpement_Web/docs/PLAN_DE_PRODUCTION.md). Le lien public est une version de travail ; sa disponibilité ne ferme aucune phase.

Le [workflow de fabrication fidèle](creative/workflow/README.md) définit les neuf passages et leurs preuves par composant, les [recettes de famille](creative/workflow/RECIPES.md), les fiches réutilisables et le contrôle des déclarations. Le [complément documentaire](creative/workflow/RESEARCH.md) conserve les nouvelles sources, conflits de variantes et manques moto. Les 92 fiches AS et 67 lignes CON sont routées vers ces recettes, sans prétendre que leur recherche ou fabrication est achevée.

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
# Reprise — flasque v2 et levier avant séparé

La fabrication progresse sur deux incréments distincts : [matière du flasque v2](creative/reviews/front-brake-plate-v2/README.md) et [levier de came avant v1](creative/reviews/front-brake-lever-v1/README.md). Le levier est la pièce détaillée active ; le flasque conserve ses versions et ses preuves. Les dimensions et identités RDC restent à documenter. Les quatre composants candidats (pneu, jante, flasque, levier) ne constituent pas une moto finie et ne sont pas reçus artistiquement. La prévisualisation publique du jeu reste à sa version3.
# Reprise parallèle — poste de conduite

À la demande explicite de l’utilisateur, guidon, poignées et compteurs sont fabriqués comme trois candidats indépendants. La [revue du poste de conduite](creative/reviews/cockpit-v1/README.md) réunit leurs sources liées et leurs vrais exports. Les aiguilles sont manipulables dans Babylon.js ; les nouveaux rendus Blender emploient un débruitage documenté. Les dimensions restent estimées, les fixations et commandes complètes sont absentes, aucune réception artistique ou qualification iPhone n’est acquise. La recherche sur la came révèle des variantes de frein avant à ne pas mélanger avec la jante moulée sans confirmation RDC. Jeu public version3 inchangé.
