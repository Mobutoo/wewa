# Viva Wewa

Jeu solo de moto à Kinshasa pour navigateur PC et mobile. Le premier secteur réutilise les routes et modèles de Gombe fournis dans le dossier de reprise.

## Jouer et relire

L’identité de la prévisualisation publique est conservée dans `.openai/hosting.json`. Son URL confirmée et les preuves sont dans `WEWA_Developpement_Web/validation/STATUS.json`.

Le carnet public `/relecture.html` et `creative/review-register.json` rassemblent les personnages, dialogues, missions et scènes inventés. La direction vise le réalisme photographique. La couverture générée est une image artistique distincte des captures moteur ; le moteur utilise désormais des matières photographiques CC0, un ciel HDR, des textures originales de façades/palmes et des véhicules originaux. Le rendu est toujours en deçà de la référence : variété architecturale, piétons et animations restent à produire et valider.

Modes du prototype : Rush de 30 secondes, tournée de six colis, introduction narrative avec poursuite d’un taxi et indice, balade libre.

## Développer

Node.js 24, versions gelées dans le lockfile :

```sh
npm ci
npm test
npm run build
npm run dev
```

Source dans `app/`, sortie statique dans `dist/`. Tests navigateur : Python 3.12, Playwright et Chromium.

```sh
python -m pip install playwright
python -m playwright install --with-deps chromium
npm run test:browser
```

Les captures et rapports sont dans `WEWA_Developpement_Web/validation/browser/`. L’émulation tactile Chromium ne constitue pas une validation Safari sur iPhone. Les iPhone 15 et 16 sont prioritaires ; aucune cadence matérielle n’est encore déclarée atteinte.

Le workflow `.github/workflows/ci.yml` exécute tests, build et vérification navigateur.

## Commandes

ZQSD / WASD ou flèches : conduire. Espace : frein ; Maj : nitro ; C : caméra ; H : klaxon ; R : reprise ; P / Échap : pause. Sur téléphone : joystick unique au pouce gauche. Haut : accélérer ; bas : freiner puis reculer ; gauche/droite : diriger simultanément. Nitro et klaxon à droite, indépendants. Portrait et paysage pris en charge.

Pause ou perte de focus libère les commandes. Réglages : confort, champ de vision, vibrations, musique originale et appels parlés facultatifs via la voix française du navigateur. Record et réglages locaux ; jouer sans stockage persistant reste possible.

## Sources

- `WEWA_Developpement_Web/` : cadrage R9 / plan 1.2, backlog, configurations et données de référence préservés.
- `tools/prepare_world.py` : dérivé métrique du graphe et emplacements de jeu, avec copie des GLB existants. Dépendances Python : celles du kit.
- `app/public/world/` : dérivé navigateur et cellules chargées progressivement.
- `assets-src/` : scripts Blender originaux de la moto, du pilote et du minibus. Sortie dans `generated/`, ou `VIVA_WEWA_ASSET_OUTPUT` si défini.
- `creative/` : références, provenance et relecture.

Les géodonnées complètes et archives volumineuses restent dans le dossier d’importation et sur le partage fourni, hors du bundle et de Git ordinaire. Récupération : https://drop.ewutelo.cloud/StoryEngine-UI-2026-09-08/Wewa%20/ (espace final dans le nom du dossier).

## État et limites

Prototype jouable : tracé d’environ 1,50 km contrôlé contre les emprises bâties ; hauteurs, voirie, priorités et fidélité locale à qualifier. Façades, palmiers et commerces ajoutés constituent une couche artistique fictive. Trafic et traversées simplifiés.

Le backlog conserve ses dépendances de validation : essais Safari iPhone 15/16, relecture kinoise, finition artistique, performances matérielles et panel utilisateurs. Aucun paiement réel, compte obligatoire, télémétrie distante ou classement public.

Géographie : © contributeurs OpenStreetMap, source ODbL ; voir les crédits du kit et `app/public/world/CREDITS*.txt`. Les références historiques Ewutelo sont dans `context/ewutelo/` ; les décisions actuelles Viva Wewa et la correction photographique figurent dans le PRD actuel et le carnet.
