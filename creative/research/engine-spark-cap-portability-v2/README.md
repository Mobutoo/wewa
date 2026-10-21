# Capuchon2 — compagnon de portabilité et contexte

Le maître des rendus reste **engine-spark-cap-v2.blend bceb87f8…** et son GLB original **2a924e6e…**. Aucun gel, registre, catalogue ou index Git n’est changé. Les compagnons ci-dessous sont une livraison distincte, sans nouveau rendu ni export.

| Fichier nouveau | SHA256 | Fonction |
| --- | --- | --- |
| `engine-spark-cap-v2-portable.blend` | `c5e0756e79aab4d588634b7bceff7ea6cac12d00937d1224f0fa2ed67885db96` | Composant cap2 identique ; liens de contexte relatifs, bougie2 remplacée uniquement comme bibliothèque de contexte par le compagnon suivant |
| `engine-spark-plug-v2-context-portable.blend` | `130f06eed047b07c11b35ae7ac19cc885e62d99e89f8f0f90f3f11f211a13aa4` | Quatre corps/datum de bougie2 identiques ; lien imbriqué vers cap1 devenu relatif |

La collection propre du capuchon comporte deux maillages locaux et un datum. Ses guides bougie1/2 et culasse3 restent des bibliothèques dans les collections cachées de contexte, sans fusion dans le composant. Les deux images originales normal/roughness sont intégrées au BLEND et leurs octets restent identiques ; leurs `Image.filepath` absolus ne sont pas modifiés par cet outil limité aux `Library`.

La comparaison avant mutation, après remappage et après sauvegarde/réouverture est exacte pour positions brutes/évaluées, indices, UV, attributs, normales de coins, affectations et graphes de matériaux relevés, textures intégrées, parents et matrices. Le compagnon bougie2 dispose de la même preuve sur ses quatre corps. Voir `final-cap-invariance.json` et `plug-context-invariance.json`.

**La fermeture entière a été testée réellement dans un arbre déplacé :13 BLEND ouverts individuellement,18 liens directs vérifiés**, avec tous les liens directs/indirects effectivement chargés et objets liés non manquants. Chaque cible résolue par Blender est dans le nouvel arbre et porte le SHA du fichier copié : aucun repli vers `/workspace/wewa-github` accepté. Onze ancêtres publics sont copiés byte pour byte uniquement pour ce test ; seuls deux compagnons sont ajoutés au dépôt. Voir `full-context-tree-plan.json` et `full-context-open-check.json`.

L’essai initial « direct-only » ne couvrait que les trois liens visibles au chargement de cap2. Il reste diagnostic et ne vaut pas preuve transitive. Son BLEND a été déplacé hors dépôt, localisation/SHA consignés. L’erreur de reload de l’ancien test générique et son script sont conservés ; le script corrigé recharge la cible absolue de travail avant d’enregistrer le chemin relatif au nouveau compagnon.

## Rejouer les outils

Tous les chemins sont des arguments ; aucun binaire, checkout ou modèle n’est codé en dur dans les outils génériques. Les scripts de copie refusent une sortie déjà existante. `--original-root` désigne le préfixe historique ; `--checkout-root` permet un autre checkout de travail. `--library-target-map` est une substitution explicite de contexte, jamais un déplacement de composant.

```sh
blender --background --threads 1 --python-exit-code 1 --python portable_library_copy.py -- --source SOURCE.blend --output NOUVEAU_COMPAGNON.blend --original-root RACINE_HISTORIQUE --checkout-root CHECKOUT_ACTUEL --component-collection COLLECTION_PROPRE --report preuve.json
```

Pour cap2, ajouter `--library-target-map library-target-map.json` après avoir préparé le compagnon bougie2 ; la map consigne son chemin de dépôt exact. Le script inspecte les Library avant modification et compare les empreintes du composant avant/après. Les propriétaires indirects ne sont jamais édités dans le mauvais maître : fournir un compagnon de leur source.

La recette de fixture complète se rejoue avec des chemins quelconques et une **nouvelle** sortie :

```sh
python prepare_full_context_tree.py --repository-root CHECKOUT_ACTUEL --dependency-report CHEMIN_RAPPORT_DEPENDANCES.json --replacement-map context-replacement-map.json --test-root NOUVEL_ARBRE_TEST --report plan.json
blender --background --threads 1 --python-exit-code 1 --python verify_full_context_tree.py -- --tree-plan plan.json --report ouverture.json
```

Le rapport documentaire utilisé est `creative/research/motorcycle-source-dependencies-publication10-tyre-cap2-v1/report.json` ; les deux maps sont fournies dans ce dossier. `generic-final-tool-replay.json` démontre le script final sur un original de travail déplacé contenant encore l’ancien préfixe absolu. Aucune recette de génération de géométrie ni de rendu n’est rejouée.

L’audit ne reçoit ni moteur complet, ni jeux/OEM, ni apparence artistique ou performance iPhone. Les13 BLEND historiques et le GLB cap2 sont vérifiés inchangés dans `original-immutability-check.json`.
