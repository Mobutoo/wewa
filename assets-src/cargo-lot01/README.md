# Sources historiques du lot01 refusé

**Lot refusé par l’utilisateur : aucune vue ni composant reçu comme réaliste.** Sources historiques conservées ; reprise moto seule, pièce par pièce, selon [le plan](../../creative/MOTORCYCLE_PLAN.md).
Création originale pour Viva Wewa : carton kraft plié, ruban adhésif, deux liens de ficelle et étiquette fictive. Aucun modèle ou photographie tiers n’est incorporé. Les matières papier, ruban et fibre sont fabriquées dans Blender puis cuites en textures PBR ; elles ne sont pas des scans photographiques.

Le carton nominal mesure 0,34 × 0,30 × 0,24 m. L’encombrement réel de l’ensemble, notamment les ficelles et leurs nœuds, est indiqué dans `provenance.json`. Origine au centre sous le carton. Repère Blender : Z haut, −Y avant ; glTF : Y haut, +Z avant.

Placement proposé dans le montage moto : Blender `(0, +0.67, +0.84)` m. Il s’agit d’une variante de chargement graphique à examiner ; elle ne représente pas l’inventaire effectif d’une partie du jeu. Le contrôle du dégagement avec le sac du pilote doit se faire dans l’assemblage complet.

La source `cargo-lot01.blend` conserve les matériaux procéduraux éditables et les textures cuites 2K intégrées au fichier. Le générateur produit un GLB avec textures 1K et cinq groupes de matériaux. Les rendus de contrôle Blender sont séparés des futures captures dans le moteur.

```bash
blender --background --python assets-src/cargo-lot01/generate_cargo.py
node assets-src/cargo-lot01/compress_cargo.mjs
node assets-src/cargo-lot01/validate_cargo.mjs
```

Les sorties vont par défaut dans `/workspace/wewa-assets/cargo-lot01`. La variable `WEWA_CARGO_OUTPUT` permet de changer ce répertoire.

La conversion WebP garde normales et rugosités sans perte ; les couleurs utilisent une qualité de 92. Elle nécessite Sharp disponible localement ou dans le répertoire désigné par `WEWA_SHARP_ROOT`. Les textures 2K sur disque servent de cache pour éviter toute nouvelle cuisson lors d’une correction de géométrie.

Le premier export autonome comporte 14 295 triangles et cinq matériaux, pour 3 384 132 octets après conversion. Le contrôle glTF donne zéro erreur et zéro avertissement. Le rapport UV distingue les surfaces principales et les tranches très fines : 80 triangles de tranche carton et 48 de film ont encore une aire UV nulle, sans valeur non finie ; les ficelles n’en ont aucune. Ces tranches sont à consolider, ainsi que le poids géométrique de l’encre et des cordes pour les LOD mobiles. Les liens actuels entourent le colis ; les ancrages à la moto ne sont pas finalisés.

Statut : **fabrication candidate, validation artistique utilisateur en attente**. Les contrôles glTF, UV et dimensions portent sur les fichiers ; ils ne valent ni acceptation artistique, ni qualification Safari physique.
