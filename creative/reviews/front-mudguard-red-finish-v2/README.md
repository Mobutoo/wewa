# Garde-boue avant — finition rouge v2, matériau seul

La coque grise d’étude reçoit une peinture rouge unie dans le schéma original WEWA. Aucun changement de forme, transformation, normale, UV ou index. La géométrie reste une étude historique avec attaches cachées et montage non réceptionnés. Pas de G8.

## Intégration main

Le fragment `main-fragment.json` identifie collection, selected_objects, source et GLB avec SHA exacts. Collection sélectionnable : `WEWA_FRONT_MUDGUARD_RED_FINISH_V2`. Source : `assets-src/moto-components/front-mudguard-red-finish-v2/front-mudguard-red-finish-v2.blend`. GLB : `front-mudguard-red-finish-v2.glb` dans ce même dossier assets.

Un seul objet local conserve **le même datablock mesh lié** à `../front-mudguard/front-mudguard-shell-v1.blend`, collection d’origine `WEWA_FRONT_MUDGUARD_SHELL_ISOLATED`. Ses material_slots sont en mode OBJECT avec matériau local ; aucun changement du matériau partagé ou de l’ancien maillage. La bibliothèque relative doit rester disponible. Pas de packing, copie de texture, nouveau UV, logo ni image WEWA du réservoir. `save_version=0`, aucune .blend1. Export limité à la sélection et `use_active_scene=True`.

## Références et choix matière

Les photos physiques RDC00/04 privées ont été réellement ouvertes : le garde-boue avant est rouge brillant dans les deux profils. Elles ne mesurent ni colorimétrie ni rugosité, ne déterminent pas si le support est métal ou plastique et ne deviennent pas une texture. Le registre source public ne contient que URL/SHA/observations.

Le matériau uni reprend les valeurs du matériau sans texture `WEWA original red paint - estimated` réellement relu dans le réservoir : baseColor linéaire `[0.4178850651,0.0060488330,0.0122864880,1]`, roughness0.22, coat0.35, coat roughness0.12, IOR1.5, metallic0. Ces valeurs sont **authored/estimated**, non une teinte OEM ou une mesure photographique. Metallic0 décrit la couche peinte diélectrique ; il ne certifie pas le substrat. Aucun vieillissement, micrograin ou épaisseur inventé.

## Contrôles exécutés

`export-invariance-validator.json` lit les accessors des deux GLB, y compris byteStride et offsets : **POSITION/NORMAL/TEXCOORD_0/TANGENT/INDICES bit pour bit identiques**, même type, count, normalized, mode de primitive et nodes. 52811sommets exportés,102912triangles. Le validateur complet donne0erreur/0avertissement. Aucun seuil de normale/tangente ni réparation de buffers.

`reopen-raw-check.json` rouvre la nouvelle source, vérifie bibliothèque liée, override local et empreintes anciennes. Aperçu PBR12 réellement ouvert avant les finales. Trois vues Cycles CPU2threads à96échantillons,800×650 : neutral-quarter, neutral-reverse, raking. Cadre entier et clipping vérifiés sur les sommets évalués avant chaque rendu. Trois PNG ouverts et trois EXR lus en pixels ; en-têtes EXR vérifiés FLOAT32 pour tous les canaux, valeurs finies. Source/caméras/lumières/exposition/look sont enregistrés par le protocole et les rapports ; pas de rendu moto entière.

Lecture visuelle : rouge continu et brillant, larges reflets clairs sous les deux éclairages neutres ; le rasant fait apparaître les courbes et l’intérieur plus sombre. Ces reflets peuvent éclaircir le rouge vers le rose, comme dans l’étude de réservoir ; aucune correspondance calibrée ou changement de forme n’en est déduit. Les chants et interfaces restent ceux de la coque historique.

Babylon réel : `babylon-report.json`, captures quarter/reverse ouvertes. Un mesh chargé, mêmes52811vertices/102912triangles et bornes, albedo/roughness/coat importés avec leurs valeurs ;0erreur page/HTTP. Chromium software WebGL, pas qualification iPhone. Le rendu ponctuel de Babylon reste plus sombre et avec des reflets plus petits que le studio Cycles ; cette différence d’éclairage n’est pas déclarée parité photométrique. GLB sans images ni textures ; la scène Babylon possède son unique ressource interne, pas une texture de garde-boue copiée.

## État

G0 périmètre matériau établi ; G1 références de couleur lues, paramètres estimés ; G2 repère hérité intact ; G3 géométrie héritée, non réévaluée comme forme reçue ; G4 finition authored relue, calibration inconnue ; G5 interfaces historiques ouvertes ; G6 export et Babylon exécutés, pas réception artistique ; G7 coût mobile non qualifié ; G8 pending.

Aucun ancien dossier gelé, outil de composition, catalogue, racine ou Git modifié. Nouveau serveur de revue arrêté avant gel ; cache reproductible dédié sous scratch, sans usage des caches guard/kick/p29. Les seules sorties de ce travail matière sont dans ses trois nouveaux dossiers. L’audit global demandé suit dans un dossier séparé après le gel.
