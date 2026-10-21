# Source 20 — Anneau de clé, dépendances réelles de reprise

Référence Source19 `47755ce9e83741006f03f4a8e64c1d1b0b6c6acb` ; sa métadonnée finale est encore attendue. La base Source20 reste inconnue. [Rapport](report.json), [fermeture](source-closure-v1.json), [entrées stables](stable-recipe-inputs-v1.json) : **55 paires SHA/octets** et **32 entrées**. Le gel auteur final71 est vérifié par octets, sans ouverture de pixels ni réception artistique.

## Construction

Le constructeur vérifie et lit ignition-lock-v1.blend, instruments-v3.blend et le rapport structurel exact des instruments, tous dans55. Il charge les objets explicitement nommés pour capturer positions/triangles monde et la matrice de repos du pivot. Après read_factory_settings, il reconstruit des guides numériques propres en gris, sans importer matières/images/liens. Ces ancêtres sont des vraies entrées de construction ; les remplacer par instruments-v5 changerait la recette.

## Forme

Un fil plat à section arrondie suit une hélice de2,02 tours avec extrémités fermées distinctes. Rayon, pas, section, clocking et pose sont estimés ; aucun tore soudé ou ressort élastique certifié. Le helper fournit mesh/check/export/studio et BVH ; sa fonction CSG n’est pas appelée, donc aucune dépendance Manifold/CSG supplémentaire.

## Matiere

Le maître G3 et geometry-preview-review sont vérifiés puis seule une proposition Principled constante change : base linéaire(.42,.45,.48), métal.92, rugosité.25. Les signatures géométriques et matrices sont protégées. Aucune texture, normalmap, police, HDR ou image privée.

## Guides et controles

La source finale est autonome : guides de clé/boîtier/instruments en snapshots numériques intégrés, aucun Library/image d’après le contrôle fourni. Les rendus ouvrent seulement cette source et font apparaître les deux guides de clé dans la vue de contexte. check_key_passage lit les mêmes snapshots et teste les poses rigides proposées, sans recharger les deux ancêtres. Les écarts de sérialisation du datum sont décrits dans saved-datum-check ; ni ajustement physique ni nouvelle tolérance ne sont inventés. Aucun contrôle rejoué.

## Rendu

render.py exige le source/build-report et export-check, puis les helpers locaux caméra/checkpoint. Les checkpoints finaux sont optionnels ; leur absence conduit à de nouvelles sorties PNG/EXR. Aucun checkpoint d’aperçu ni mire obligatoire, aucune copie privée nécessaire.

## Reprise et histoire

Les stages recipe/build/material refusent un preflight-manifest présent et nomment Blender4.3.2 externe : reprendre dans une copie de travail isolée non figée, sans toucher au gel original. Le maître G3 évite de recharger les ancêtres pour la seule matière. Le diagnostic initial de section et l’échec de témoin rayon sont conservés dans55, mais aucun ancien modèle ou log privé supplémentaire n’est requis. Les preuves de passage restent conditionnelles, pas un montage de cockpit reçu.

Aucun constructeur, checker, rendu ou export lancé. Aucun modèle, ancien gel, fichier global ou Git modifié. Les11 fichiers des audits Source20 boulon/œil opposé restent byte-identiques. Aucune archive de partenaire ou pixel documentaire aspiré. Cette lecture statique ne vaut ni clean replay, nouveau contrôle mécanique ni réception artistique.
