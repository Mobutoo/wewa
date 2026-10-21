# Source18 — recette de la coque de garde-boue arrière

Base Source17 `a78a6e52c38cf794f0d3733b6c08f0960abe09e1`. Audit séparé de la [coque arrière](../../../assets-src/moto-components/rear-mudguard-shell/README.md), source `d3d8bb96…` / GLB `b92fe032…`, sans définir de coupe ou curateur18. Le [rapport](report.json), la [fermeture source](source-closure-v1.json) et les [entrées stables](stable-recipe-inputs-v1.json) vérifient **84paires SHA/octets** et nomment **44entrées stables** du pipeline courant. Les trois compléments hors84 sont le helper caméra partagé et les package/lockfile déjà publiés.

Aucun modèle, shader, ancien gel ou global modifié ; aucun générateur, CDT, checker, rendu, export ou Git de mutation exécuté. Les six finales96 et leurs futurs rapports/manifestes restent hors de cet audit.

## Chaîne autonome courante

Les paramètres `parameters-features-v1.json` et `shell_surface_v1.py` définissent les stations et champs de la coque courante. `prepare_features_v1.py` produit les limites/échantillons du domaine et leur NPZ ; `triangulate_features_v1.py` emploie le CDT natif Blender ; `generate_features_v1.py` fabrique positions, triangles, normales, UV et rôles dans le NPZ auteur. `build_features_v1.py` importe cette géométrie en source Blender éditable avec contrôles de SHA. **Tous les producteurs, intermédiaires NPZ/JSON et le maître gris sont fournis dans84.** Aucun maillage vendeur ni CSG extérieur caché.

La matière ouvre directement `rear-mudguard-shell-features-v1.blend`, vérifie la permission `gray-review.json` contre ses deux SHA et lit son plan de matière. Le source final utilise un autre nom : le maître gris reste disponible. Les cartes normal/ORM512 sont originales, générées par FFT NumPy seed15142 ; pas de photo, police ou atlas. Les exigences de versions host NumPy/SciPy/Pillow, Blender4.3.2 et Node sont fournies ; aucune régénération byte-identique depuis clone propre n’est revendiquée.

Le rendu final utilise le helper caméra local épinglé. Les anciens renderers d’étude/features utilisent le chemin partagé ; les deux copies ont effectivement le même SHA `e33ebdf203865de95f25bfcf73b1bf4cacd91528e5cbed849b7eaf70e84d0c6a`. La provenance et le README source décrivent la restauration éventuelle de la copie épinglée au chemin partagé, dans une copie de travail isolée, sans modifier un outil historique.

## Études antérieures et archive imposée

L’étude initiale et `diagnostics/features-before-tip-return` sont des membres explicitement gelés de84 : leur présence et leurs SHA doivent être conservés pour livrer ce gel inchangé. Ils ne sont pas des maîtres BLEND/NPZ lus par la chaîne features courante. Leurs scripts archivés représentent des états diagnostiques ; cet audit ne promet pas de rejouer ces anciennes tentatives avec toutes leurs données privées ou intermédiaires d’origine. Aucun dossier supplémentaire ni ancien PNG/EXR privé n’est aspiré par récursion.

La reprise matière peut partir du maître features gris fourni sans reconstruire l’étude initiale ou les diagnostics. Reconstruire les features peut changer les octets et demande une nouvelle revue attribuée. Les gros fichiers déjà listés dans84 sont des obligations d’archive précises, pas une collection indéfinie de tous les essais.

## Rendu et limites

`render_v1.py` lit le source actuel, les contrôles d’export/géométrie et la permission de preview matière déjà gelés84. Il utilise le studio sauvegardé et les vues définies dans le script. Un checkpoint/PNG antérieur n’est ouvert que si les deux existent, pour vérifier une reprise optionnelle ; sans eux un nouveau rendu démarre. **Aucun checkpoint privé d’aperçu, HDR ou EXR de mire n’est imposé.** Aucune copie privée supplémentaire réalisée.

L’arche, les bouches, reliefs, épaisseurs et repères restent des estimations. La réserve documentaire sur la hauteur d’une bouche latérale reste attribuée ; elle n’est pas effacée par des contrôles de fichiers. Bavette, brace, visserie et raccords pneu/selle/cadre ne sont pas inclus. Aucun assemblage arrière complet, variante OEM, montage, LOD mobile, essai iPhone ou réception artistique reçu par cet audit statique. Les audits précédents restent intacts et aucune finale active n’est pinnée.
