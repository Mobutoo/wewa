# Source15 — complément statique labo4 et diagnostic matière

Ce complément est séparé du [premier audit15](../motorcycle-source-dependencies-publication15-v1/README.md). Le [rapport](report.json) et la [liste exacte des entrées](stable-inputs-v1.json) décrivent des dépendances ; aucune capture, géométrie ou source n’a été modifiée.

Le labo4 importe réellement **v2 → v1**, le module de conservation local et Babylon 9.31.0 ; aucun import v3/SSAO. Les fichiers v3 restent toutefois des entrées protégées dont le captureur vérifie les SHA. Les nouveaux outils et la préparation restent une **expérience non adoptée**, pas un gel d’unité ou une nouvelle pièce.

Les deux spécifications de caméra, source/GLB/HDR, rapports natifs et PNG warm existants sont vérifiés. Le GLB est réellement chargé par le navigateur ; le BLEND est seulement un garde d’empreinte du captureur, sans nouvelle ouverture de bibliothèques Blender. Les huit fichiers API installés et deux package.json appartiennent à l’installation Babylon 9.31.0 : réutiliser le package-lock public, **ne pas publier node_modules**. Aucun bootstrap propre n’a été exécuté ici.

Les deux caméras et leurs huit sorties attendues sont contrôlées par le script, mais la sortie `upper-engine-sun-shadow-v4` reste active et n’a été ni lue ni figée par cet audit. Le statut « prepared-not-executed » de la préparation reste historique. Le progrès de la première caméra rapporté par root n’est pas converti en succès global. Les assertions de conservation, projection, casters/receivers, matériaux et contrôle neutre ne valent ni réception visuelle ni équivalence Blender/Babylon ou iPhone.

Le diagnostic du joint est distinct : son **diagnostic-manifest.json gelé comporte 14 entrées, dont 3 EXR totalisant 7 718 468 octets**. Si ce manifeste est admis, ces trois EXR originaux sont imposés par sa fermeture. Ils ne sont ni des photos documentaires ni une raison d’aspirer d’autres EXR. Aucune preuve n’est supprimée ou recopiée.

Les rapports B/root attribuent le quadrillage dominant à la normale cuite : il disparaît dans leur contrôle « normal-unlinked-only » et demeure quand seule la rugosité devient constante. Cette attribution est reprise comme leur lecture réelle ; aucune nouvelle image n’a été ouverte par cet audit. Le contrôle sans normale n’est pas une matière de remplacement acceptée. Source1/gels59/73 restent intacts, la correction2 reste distincte et hors de cette fermeture.

Le script diagnostic utilise le vrai checkpoint macro 96 et les mêmes caméra/lumières, change des liens seulement en mémoire et sauve ses propres trois variantes 12 spp. Source/GLB, protocole et checkpoint originaux sont les entrées nommées de reprise. Les cinq href locaux de la préparation sont vérifiés ; aucun ancien rapport Source14 n’est reconstruit ni modifié. Aucun cutoff final Source15 ou nouvelle unité n’est annoncé.
