# Publication10 — dépendances du pneu arrière1 et du capuchon HT2

**Aucun maître gris ni générateur de cartes nécessaire n’a été trouvé seulement en privé.** Deux points de publication restent à traiter : la revue grise lue par le pneu se trouve hors de son gel22, et deux liens de bibliothèques de contexte du capuchon sont absolus. Les fichiers visés existent ; ce n’est pas une absence de géométrie propre du composant.

Le [rapport](report.json) conserve48 dépendances avec chemins/SHA, présence dans les gels22/57, couverture antérieure et état Git lu sans mutation. Audit statique : lecture des scripts et blocs de bibliothèques Blender compressés, **aucun processus Blender, reconstruction, rendu, strict/UV/Babylon ou nouvelle boucle de vérification des79 fichiers**. Root avait déjà effectué ces contrôles. Aucun gel, index, modèle, ancien rapport ou registre modifié.

| Gel audité | Source | GLB |
| --- | --- | --- |
| [Pneu arrière1,22 fichiers](../../reviews/rear-tyre-v1/source-freeze.json) |612388ce…|5a257315…|
| [Capuchon HT2,57 fichiers](../../../assets-src/moto-components/engine-spark-cap/preflight-manifest-v2.json) |bceb87f8…|2a924e6e…|

## Pneu : maître et cartes présents, entrée de contrôle extérieure au gel

`g3-master-v1/` fournit le BLEND gris **a8c7479d…**, son GLB **16ff10eb…**, le rapport de géométrie et la procédure de restauration. Les quatre fichiers figurent dans le gel22. `build.py` reconstruit le volume depuis `parameters.json` sans charger d’asset extérieur.

`material.py` génère lui-même les cartes périodiques512² par NumPy/FFT avec **seed16003**, tuile10mm. Les deux PNG originaux sont fournis dans22 et empaquetés par le code ; aucun PNG maître ou pixel photographique extérieur n’est lu.

En revanche, sa ligne4 lit et vérifie les SHA de **`creative/reviews/rear-tyre-v1/gray-review.json`**, SHA256 **`cf08f89547c9623bd7a658a97540cc7973d9f0a77defec72fefa642cf684b432`**. Le fichier existe dans le dépôt de travail, mais reste hors du gel22 et hors de l’index au pointage. `record.py` prévoit déjà son inclusion dans le manifeste de revue finale : il faut conserver cette entrée lors de la publication coordonnée, sans fermer cette revue ici.

Pour rejouer G4 depuis le maître fourni, restaurer les deux fichiers gris et leur rapport comme indiqué dans son README. Une reconstruction fraîche peut changer le SHA du conteneur Blender ; elle ne doit pas hériter automatiquement d’une ancienne relecture G3. Ce garde est une entrée de contrôle, pas une texture ni un maître privé manquant.

Le rendu du pneu importe aussi `tools/blender_component_camera_preflight.py`, SHA **e33ebdf2…**, présent et déjà suivi dans Git mais hors22. Il concerne la régénération des vues, pas la géométrie ou les cartes.

## Capuchon : géométrie propre distincte du contexte

La recette57 contient `build_v2.py`, les paramètres, le profil d’épaule, le sampler extrait de `build.py`, les trois helpers partagés, la base v1, les stades gris géométrie/topologie et leurs rapports. Le sampler v1 est extrait par AST : son programme principal n’est pas exécuté. Le code importe les guides bougie2/culasse3 pour ses **assertions d’interfaces**, puis exporte seulement **datum, coque locale et contact local**.

`material_v2.py` cuit les cartes2048² depuis le bruit4D local **W17,391** et les paramètres publics : aucun maître image privé. Les deux cartes et les deux maîtres intermédiaires figurent dans57. Le GLB isolé et ses volumes propres ne comprennent pas les guides liés.

Les liens absolus réellement lus dans les blocs Blender sont :

1. Dans capuchon2 **bceb87f8…** → `/workspace/wewa-github/assets-src/moto-components/engine-spark-plug/engine-spark-plug-v2.blend` (**35648efb…**).
2. Dans cette bougie2 → `/workspace/wewa-github/assets-src/moto-components/engine-spark-cap/engine-spark-cap-v1.blend` (**69dc2767…**).

**Portabilité à corriger dans une copie additive de travail**, ou à gérer par une relocalisation documentée ; aucune édition des témoins gelés ici. Un clone placé ailleurs peut perdre ces guides. Cela ne signifie pas que la coque ou le contact exportés sont manquants.

`installed-context` active bougie2 et culasse3 ; les guides hérités bougie1/culasse3 restent aussi liés dans la base. La lecture statique a suivi **13 BLEND/18 liens**, tous présents, y compris cylindre1, couvercles OHC/visite1, culasse2 et carters antérieurs. Les ancêtres hors57 ont une couverture de gels antérieurs/source09 consignée aux SHA correspondants. Ces liens ne sont pas fusionnés dans le capuchon ; ils restent utiles à l’ouverture complète du contexte et à ses vues. La recette telle qu’écrite les exige également pour ses assertions avant l’export isolé.

`recipe_v2.py` utilise enfin un chemin local absolu vers Blender4.3.2. Le téléchargement et son checksum sont documentés publiquement ; les dépendances CSG `manifold3d==3.3.2` et `numpy==2.3.5` sont dans `tools/requirements-assets.txt`. Le chemin d’exécutable doit être adapté dans la copie de travail. Ce n’est pas une ressource propriétaire manquante ; ces pins système ne certifient pas non plus la version NumPy embarquée de Blender pour le générateur FFT du pneu.

Les finales A/B sont en cours selon le parent. **Aucun manifeste de revue globale n’est clos ici**, aucun clone propre complet n’a été rejoué et aucune reproductibilité binaire/pixel, réception artistique ou validation iPhone n’est déclarée. Les photographies documentaires privées restent hors des dépendances de construction et ne sont pas copiées.
