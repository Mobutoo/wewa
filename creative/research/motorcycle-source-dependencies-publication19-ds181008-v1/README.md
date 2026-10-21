# Amortisseur supérieur DS181008 — dépendances de reprise

BaseSource19 `a2aa4bc04d5c6fff242de160d806cd4fdc91313b`. [Rapport](report.json), [fermeture](source-closure-v1.json) et [entrées stables](stable-recipe-inputs-v1.json) : **41paires SHA/octets**, **26entrées** nommées. Source `ae6ed5f4f3b05881dab49fa650083c600fe52ba50d3733f1938c3e2d02ba5f8c`, GLB `336c5090772a4213586fe275bf20a106afe7c8304ea5b4ea46e7a5453a7fdcbd`. Aucun gel final encore actif n’est pinné.

## Construction

Le constructeur lit parameters.json et profile_shape.py. Il crée un profil annulaire original, des transitions quintiques, un vrai passage et un revers plat estimé. Les indices sont partagés et les normales courbes sont analytiques ; les faces réellement planes restent plates. Aucun insert ou autre amortisseur DS181009/010 importé.

## Materiau

material.py ouvre le maître G3 public et vérifie les deux SHA contre gray-review. Le plan original génère deux cartes Non-Color de512², normales et ORM, champ FFT RMS0,8µm estimé et tile6mm synthétique. Aucune image de la photo quadrillée ni police ; packed et chemins relatifs conservés. Métal0, rugosité de base0,52, normale0,15 proposés, pas dureté ou matière physique mesurée.

## Reprise

Le maître G3 permet une reprise matière. build.py écrit un nouveau gris au chemin parent, mais ne le promeut pas automatiquement dans g3-master-v1 et ne réécrit pas la lecture attribuée. Un gris reconstruit peut changer d’octets : il impose une nouvelle revue.

## Rendu

render.py exige source et GLB courants, source-geometry-check et geometry-check, puis le helper caméra local. Le studio est dans la source. Les checkpoints des cinq PNG finaux servent seulement à reprendre une sortie existante ; aucune mire, HDR, entrée privée ou EXR préalable n’est imposée.

## Finalisation

record.py exige ensuite les lectures attribuées, les anciennes paires gris/reflets/previews et les cinq finales. Ces sorties de revue ne sont pas des entrées nécessaires au nouveau rendu. Le gel auteur final encore actif n’est pas pinné ici.

## Limites

L’identité DS181008 est apparentée BM/BMX150. Tous diamètres, section, revers, orientation et compression sont estimés. Une fiche publiée auparavant ne prouvait pas un modèle fabriqué ; cette identité ne sera comptée qu’à son inscription racine, sans ajouter une seconde fiche.

Aucun modèle, ancien gel, registre global ou Git modifié. Aucun constructeur, checker, rendu, export ou ouvertureBlender exécuté. Les29 fichiers des cinq auditsSource19 antérieurs restent byte-identiques. Cette lecture statique ne prouve pas une reprise complète sur un environnement vierge et ne vaut aucune réception artistique ou mécanique.
