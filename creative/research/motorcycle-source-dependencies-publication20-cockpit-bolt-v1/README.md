# Source 20 — boulon de bridage des commandes, audit de reprise

La base de Source 20 attend le suivi 44. Cet audit est séparé des sept unités arrêtées de Source 19. [Rapport](report.json), [fermeture](source-closure-v1.json) et [entrées stables](stable-recipe-inputs-v1.json) : **60 paires SHA/octets** vérifiées et **32 entrées stables**. Source `629448fe0b7cfa693b339dc5e3db4a05e9811bc83409d6ca6bbc325e31984691`, GLB `c7e009e0e7ac5293c593231056cefe85f418257b61feb7272adb00df32027716`. Les quatre finales 96 sont encore actives à la borne de mission ; aucun report, checkpoint ou gel final n’est pinné.

## Construction

build.py lit ses paramètres et les fonctions mesh_object/material/check_mesh/export/studio du helper control_geometry. Il construit une seule surface de tête hexagonale, intersection analytique du cône, congé et filet hélicoïdal aligné. Aucun CSG, Manifold, ancien maillage, police ou image n’est chargé par le constructeur. Le helper possède une fonction CSG inutilisée ici : front-brake-plate/csg.py et ses archives ne sont pas des dépendances de cette recette.

## Materiau

material.py vérifie le maître gris exact et geometry-preview-review avant ouverture. Il modifie seulement les valeurs Principled : base linéaire(.50,.53,.56), métal1, rugosité.27. Images0, aucune normalmap, atlas raster, grain ou police. L’atlas UV analytique est géométrique et n’exige aucune texture externe.

## Reprise

Le maître G3 public permet la matière. recipe.py, build.py et material.py refusent un preflight-manifest présent : préserver le gel 60 original, travailler uniquement dans une copie de travail non figée. recipe.py nomme le Blender4.3.2 externe sous /workspace/wewa-tools ; disponibilité et environnement ne sont pas reconstitués par cet audit. Refaire le gris peut changer les octets et la lecture attribuée doit être revue ; aucun clean replay affirmé.

## Protection historique

check_head_preserved.py charge explicitement le BLEND du diagnostic de marches et ses paramètres, déjà inclus dans60. Il compare le préfixe3264 sommets tête/congé et les paramètres protégés avec le gris courant. Ce diagnostic est donc une vraie entrée de CE checker ; il ne devient pas le maître de construction ou matière. Les autres anciens scripts/GLB/proofs des marches sont des membres historiques imposés par60, pas une demande d’aspirer leurs sorties privées. Aucun checker n’est relancé ici.

## Eclairage

Le protocole gris initial, le protocole de réflexion et le PBR courant sont distincts. render.py courant place la clé à la puissance.0075W ; l’ancien render.py à.12W est archivé dans diagnostics/overbright-key-study et n’est pas importé par le courant. lighting-control-comparison.json conserve la comparaison existante, sans que cet audit ouvre ou copie ses images. Une correction de protocole n’établit pas la rugosité physique du boulon.

## Rendu

render.py lit build-report, export-check et le source courant, puis importe les helpers locaux camera_preflight et render_checkpoint. Aucun checkpoint d’aperçu imposé, HDR ou mire18% requis. Les checkpoints finaux sont facultatifs : le helper les lit seulement s’ils existent et peut produire de nouveaux PNG/EXR. Les quatre finales actives et leur render-report ne sont ni lus pour SHA ni pinnés.

## Limites

M6×1 est le nominal publié de la branche BM150 liée, pas une certification125HD/RDC. Longueur, tête, profil et finition sont estimés. Conflit diamétral1,7mm avec les perçages4,3mm estimés des supports : aucun emboîtement, écrou, rondelle, pivot ou correction de support construit par cet audit.633984 triangles restent une source détaillée de revue, pas un budget mobile.

Aucune copie de checkpoint, mire, raster documentaire ou scratch n’est nécessaire. Le gel 60 fournit déjà le maître gris et les deux entrées historiques du checker de protection de tête. Les seules entrées numériques supplémentaires sont le package et le lockfile Node déjà publiés.

Aucun constructeur, checker, rendu, export ou ouverture de Blender exécuté. Les40 fichiers des sept auditsSource 19 restent byte-identiques ; le curateur19 n’est pas modifié par cet audit. Modèles, gels et registres globaux restent intacts. Aucun cutoff ou sélecteur Source 20 n’est préparé ici.
