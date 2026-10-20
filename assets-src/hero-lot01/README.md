# Viva Wewa — premier lot de fabrication à valider

Ce lot contient une moto utilitaire au gabarit de référence Boxer 125 HD, un adulte assis articulé, une tenue veste/denim, des chaussures noires, un casque et un sac. Un export séparé fournit les manches et les mains pour examiner la vue au guidon. Il ne représente ni toute la liste du dossier, ni la rue étalon achevée, ni une réception artistique.

Les fichiers et captures à recevoir sont décrits dans [la fiche de validation](../../creative/reviews/hero-lot01/README.md). Le [registre de fabrication](../../creative/library/fabrication-register.json) conserve les identifiants AS et les compléments du concept.

## Fabrication réelle

Le pilote utilise des données graphiques anatomiques MakeHuman/MPFB sous CC0, ajustées à une stature de travail de 1,74 m. Le maillage de vêtements et les chaussures sont des sources CC0 du pack officiel moderne, ajustés par leurs liaisons barycentriques et transférés sur le squelette. Il s’agit d’une adaptation de sources autorisées, pas d’une sculpture entièrement créée sans base externe.

La posture est réglée sur les commandes et les repose-pieds, puis conservée comme pose de repos éditable avec 53 os. Les mains et les manches de première personne dérivent de cette même surface. Le casque et le sac sont des modèles originaux ; la moto reprend et corrige la géométrie originale du projet : roues moulées à cinq branches, capot de phare formé et réservoir affiné. Aucun logo ou cliché constructeur n’est inclus.

Les matériaux conservent les UV, les images diffuse et normales des vêtements/chaussures et la peau sous CC0. Deux normales de matières Poly Haven CC0 servent au grain de selle et au sac. Les valeurs de rugosité sont des réglages artistiques, pas des mesures de matériaux réels. La teinte sombre de la tenue est explicitement conservée dans l’export glTF car le multiplicateur du shader Blender n’est pas repris automatiquement par son exporteur.

## Sources et reproduction

Les sources utiles et leurs droits sont dans `vendors/`, séparées des exports. Les SHA-256 sont dans `source-files.json`, avec les manifests de provenance d’origine. Les anciens en-têtes AGPL des miroirs historiques ne sont pas utilisés : les vêtements proviennent du pack moderne explicitement relicencié CC0 en septembre 2020. Aucun code programme MakeHuman n’est copié dans le moteur.

Outils utilisés : Blender 4.3.2, glTF Transform CLI 4.5.1, validateur glTF installé dans le projet. Reproduction depuis la racine :

```sh
python3 tools/rebuild_hero_lot.py --out /workspace/wewa-assets/hero-lot01-rebuild --gltf-transform /chemin/vers/gltf-transform
```

`--cargo /chemin/cargo-lot01.glb` ajoute le colis à la scène de réception. Pour les captures moteur, placer aussi cet export dans `cargo/cargo-validation.glb` du répertoire de sortie.

`--no-render` construit les modèles sans les trois rendus Cycles. Le rendu utilise le CPU et 64 échantillons ; le Blender installé ne dispose pas d’OpenImageDenoise, donc aucun débruitage inexistant n’est annoncé. Le master assemblé a été rouvert et ses images de fichier sont toutes intégrées, contrôle conservé dans `blend-images.json`. Les fichiers Blender préservent les sources et images de travail ; les exports de validation utilisent des textures limitées à 1 024 px et WebP. WebP réduit le transfert, pas la mémoire GPU comme le ferait KTX2.

Pour le contrôle dans le moteur, lancer le serveur local habituel, puis :

```sh
python3 tools/capture_hero_review.py --lot /workspace/wewa-assets/hero-lot01-rebuild --out /workspace/wewa-assets/hero-lot01-rebuild/engine
```

Ce contrôle remplace localement les réponses des modèles par les fichiers à examiner. Il ne modifie pas les assets du jeu public. La proposition de cadrage au guidon est identifiée dans le rapport et n’est pas appliquée aux réglages publics.

## Réception encore ouverte

Le gabarit et les éléments d’équipement sont à examiner par l’utilisateur. La veste source est plus longue et structurée que la veste souple de la référence ; la coupe et les détails restent à adapter selon cette comparaison. La carrosserie, les optiques et les matières de la moto nécessitent encore une passe de détails et d’usure. Le colis et ses liens sont fabriqués séparément dans `../cargo-lot01/` et assemblés pour les vues de réception. Leur présence est une variante visuelle, sans modification de l’inventaire des missions. Les liens autour du carton ne constituent pas encore un arrimage final aux points d’ancrage de la moto. L’animation d’attente ne remplace pas les transitions de conduite, la direction des mains, la déformation dynamique des vêtements ou les autres PNJ.

La scène de ville, son éclairage final et sa densité ne sont pas reçus. Les LOD, KTX2, collisions spécifiques et performances sur iPhone 15/16 restent à qualifier. Le contrôle d’intégrité d’un fichier ne clôt aucun de ces critères.
