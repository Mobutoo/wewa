# Coque du garde-boue arrière — fabrication par sections

Création originale apparentée à JV181408, d’après deux photographies attribuées [Crosland](https://www.croslandrepuestos.pe/guardafango-posterior-jv181408/p) et [Matriz](https://bajajmatriz.com/producto/salpicadera-trasera-boxer-150), les planches D04/D15 et les rotations officielles RDC. URLs, empreintes et limites : [dossier documentaire](../../../creative/research/rear-mudguard-15-v1/README.md) et [observations d’auteur](../../../creative/research/rear-mudguard-shell-15/reference-observations-v1.json). Aucun pixel photographique ni modèle de vendeur importé.

La coque est une paroi finie, avec arche et plage haute, grande marche transversale, rigole et nez étagé. L’étude initiale `*-study-v1` conserve la forme avant ajours/reliefs. Le stade `*-features-v1` ajoute cinq passages réels (deux au toit dans une disposition longitudinale estimée, deux latéraux observés sous des obliques différentes, un au nez), un anneau extérieur, deux bandes obliques paramétrées séparément, deux nervures d’épaule et des chants arrondis à indices partagés. Les reliefs extérieurs ne sont pas dupliqués en nervures cachées sous la coque.

Toutes les cotes et sections sont des estimations originales. Longueur de domaine 740mm, largeur maximale environ216mm et épaisseur nominale de travail2mm ne sont pas des mesures constructeur. Diamètres/axes/entraxe, arrondi de chant, profil caché et affectation des vues aux côtés restent conditionnels. Les deux photos portant le même code vendeur ne sont pas des vues calibrées d’un exemplaire ou d’un moule certifié commun. Le diamètre17in d’une jante ne fournit pas le diamètre extérieur d’un pneu.

Repère isolé : X gauche pilote, Y vers l’arrière, Z haut ; origine au milieu de la plage haute. Aucun raccord installé. Bavette JV181410, brace PF181410, visserie, éclairage/plaque, selle et rack sont séparés et absents de cette source.

## Reconstruction

Depuis la racine du dépôt, avec les versions de `requirements.txt` et un seul thread Blender :

1. `python assets-src/moto-components/rear-mudguard-shell/prepare_features_v1.py` prépare les limites contraintes originales et les échantillons locaux des détails.
2. Blender4.3.2 `--background --threads 1 --python-exit-code 1 --python assets-src/moto-components/rear-mudguard-shell/triangulate_features_v1.py` triangule le domaine contraint. Les limites de chaque bouche doivent être conservées et l’aire comparée.
3. `python assets-src/moto-components/rear-mudguard-shell/generate_features_v1.py` fabrique les peaux, les détails extérieurs et les chants arrondis continus. `shell_surface_v1.py` décrit les sections, normales et champs originaux ; les cartes UV utilisent des longueurs de section/ligne centrale approximatives, pas une isométrie certifiée.
4. Blender, mêmes options, `build_features_v1.py` crée le maillage Blender éditable et l’export évalué. `make_feature_probes_v1.py` puis `node .../check_features_v1.mjs` lisent les vrais buffers et passages. `inspect_features_self_v1.py` contrôle aussi les dépendances d’ouverture et les croisements non adjacents détectables par BVH.
5. `render_features_v1.py` conserve les vues grises et rasantes avec configuration/caméra et empreintes. Les vues finales et la matière sont interdites dans ce script d’étude : elles demandent la lecture de ces preuves et une étape distincte.

La BVH détecte son témoin de croisement non coplanaire ; elle ne certifie pas les contacts coplanaires ou les recouvrements de triangles adjacents. La fermeture, le volume et l’absence de triangles nuls sont des contrôles techniques, pas une réception des formes ou des cotes. Aucun montage, dégagement pneu/selle, LOD mobile, iPhone physique ou réception artistique n’est acquis.

Le préflight final utilise une copie locale inchangée du helper projet `camera_preflight_v1.py`, empreinte d’origine dans provenance.json. Les premiers rendus d’étude/détails emploient la même empreinte sous tools/blender_component_camera_preflight.py ; pour leur reproduction historique dans un autre checkout, conserver cette version ou restaurer la copie épinglée à ce chemin dans une copie isolée. Aucun outil commun ni ancien gel n’a été modifié.

## Matière et contrôle séparés

Après lecture des gris/reflets (`gray-review.json`), `material_v1.py` ouvre la baseline `rear-mudguard-shell-features-v1.blend` et écrit un autre source, `rear-mudguard-shell-v1.blend`, et son GLB. La baseline grise reste intacte. Deux cartes originales512px, référence UV10mm approximative, graine15142 : normal map et canaux metallic/roughness ; couleur linéaire(.008,.0095,.012), métal0, roughness de base.31, coat.06/.24 et hauteurRMS.3µm sont des propositions optiques non mesurées. Pas de photo/usure copiée.

`check_export_v1.mjs`, `check_material_preservation_v1.mjs`, `inspect_material_v1.py` et `inspect_source_v1.py` contrôlent les vrais buffers, tous attributs/indices/matrices G3→PBR, pixels PNG et dépendances relatives/embarquées. Les quatre previews natives ont été réellement lues ; six finales96 sont la prochaine preuve, via `render_v1.py -- --final`, avec un checkpoint après chaque image. `record_v1.py --freeze` ferme les entrées explicitement énumérées, y compris les JSON de gates nécessaires au lancement des scripts ; aucune collecte récursive de preuves indépendantes ROOT.

La lecture indépendante locale retient une réserve sur la hauteur de bouche latérale (Matriz paraît plus haut que le profil courant). Les champs/caméras/moules non appariés ne permettent pas une correction métrique imposée ; cette position reste estimée et non reçue. Aucun autre détail certain manquant n’a été retenu dans cette comparaison bornée.
