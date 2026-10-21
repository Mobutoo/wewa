# Source21 — front-tyre-material-v3

Base métadonnées45 `7741d73f54782dc5746b715b3c21f01279dbd9d1`. Aucune coupe ni sélection Source21. [Rapport](report.json), [fermeture](source-closure-v1.json), [entrées utiles](stable-recipe-inputs-v1.json) : **107 paires SHA/octets vérifiées**, **78 entrées stables**. Les tables historiques des rapports ne sont pas des manifestes vivants.

## construction matiere

Le builder lit le maîtreG3corrigé335788/GLBb5eb exacts, son gel33 complet et la lecture des trois nouvelles vues de forme. Il append l’objet corrigé, puis charge séparément le matériau procédural original depuis front-tyre-v1.blend33bf2d29…. Aucun ancienatlasv2, ancien modèle de réparation rejetée, photo, police ou matériau externe n’est consommé. L’ancien donneur est une vraie entrée ; le master courant et ses maps suffisent pour les rendus sans reconstruire G3.

## cuisson reelle

Cycles fait une nouvelle cuisson tangentNORMAL16384×2048 et une cuissonEMIT4096×512 de la rampe de rugosité sur la même géométrie corrigée,1sample/marge4. RGB normal+MR sont écrits en PNG8bit brut avec inversion explicite bottomup→topdown, sans AgX sur les données ; R_MR=255, B_métal=0 et G_rugosité. Le shader constant reprend base/IOR du donneur ; la normale cuite est appliquée une seule fois, strength1. Les deux checkpoints publics signent donneur, digest de géométrie, shader, dimensions et paramètres ; s’ils existent ils doivent matcher les vraisPNG, sinon une nouvelle cuisson a lieu. Aucun checkpoint privé nécessaire.

## preservation et limite optique

Le digest natif protège positions/normales/UV/topologie/matrice pendantG4. Le checker glTF fourni compare les vrais coins orientés P/N/UV et matrices à G3 ; des tangentes requises et de nouveaux splits de sommets peuvent changer les indices bruts sans déplacer de coin. Aucun calcul géométrique rejoué ici. Les cinq comparaisons24 déjà gelées constatent un grain plus doux/grossi dans l’atlas, particulièrement sur le flanc avec étirement de filtrage ; la recette ne prouve pas l’égalité d’un shader continu ni un caoutchoucOEM.

## portabilite chemins

Le builder packe les deux images, les marque NonColor et garde des compagnons //textures/…, sauvegarde sans remappage absolu. La preuve source-portability-check exacte constate0Library,2images packées/relatives avec compagnonsSHA, et le donneur natif intégré. Cette preuve et ses contrôles de hash sont relus, mais aucun nouveau Blender ou checkout déplacé n’est ouvert ici. Lecture indépendante du vrai GLB : un seulbufferBIN, deuxPNG embarqués, aucuneURI externe ; chacun est byte-identique à son compagnon. Samplers effectifs linéaire/trilinéaire et Repeat sur deuxaxes, tailles/bitdepth relus dans IHDR. Détail attribué dans le nouveau rapport de transport, aucune réparation ou export.

## baseline et preuves G3

Le petit diagnostic-gray-baseline.json reste réellement requis par le renderer grisG3 :3338octets SHAff51f32a4078119b8b3facb78c82bb4f52cbc5cd8985ecfadfa37e04e186f50d. Il est hors33 et72, listé explicitement ici ; ses anciens PNG/EXR/master ne sont pas nécessaires. coordinator-g3-review-v1.json et coordinator-g3-manifest-v1.json sont les deux preuves racine additives reprises avec leurs vraisSHA, sans modifier33 ni l’auditG3 antérieur. Le rayon/largeur protégés, l’empreinte élargie et l’ancien20µm non reçu restent ceux de cet audit.

## reprise rendus et environnement

render.py vérifie réellement les72membres, lit material-build-report et material-preview-review ready_for_final96, ouvre le source packé et utilise le helper caméra local. Les checkpoints finals sont des sorties facultatives, jamais des inputs privés initiaux ; aucun96 actif n’est lu ou pinné ici. run_final.py nomme Blender4.3.2 absolu et écrit sa trace sous /workspace/wewa-assets/work-in-progress : ce répertoire et l’exécutable sont des prérequis d’environnement, pas des bibliothèques de modèle manquantes. Node lockfile et requirements numpy2.3.5/Pillow12.3.0 fournis pour les checkers ; aucune installation exécutée.

## garde et histoire

Le builder matière peut réécrire son propre résultat et ne refuse pas automatiquement source-freeze72 : ne jamais le lancer dans le dossier gelé, reprendre dans une copie de travail isolée. Refaire les cuissons peut changer les octets selon environnement ; aucune reprise propre/bit-identique exécutée. record.py --freeze compare une fermeture existante et refuse de l’écraser si différente. Ancienv1/v2, diagnostics rejetés et preuves historiques restent inchangés ; les deux sources42Mo/G3 existantes nécessaires sont référencées, jamais dupliquées.

## perimetre

Source matière72 seulement, mêmeID MOTO-TYRE-FRONT-001 et0nouveau composant. Aucun état des96/worker/render-report actifs, aucun cutoff, stage ou réception artistique/fit/mouleOEM/iPhone/LOD. Atlas16384×2048 est un master de revue, pas une qualification mobile.

Aucun builder/checker/rendu/export ou Blender lancé ; aucun modèle, ancien gel, audit antérieur, registre ou index modifié. Aucun replay propre, ajustement mécanique/OEM, iPhone ou réception artistique revendiqué. Aucun duplicata de modèle ni pixel documentaire privé ajouté.
