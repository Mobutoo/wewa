# Source09 — complément capuchon et jante arrière

Instantané : 2026-10-21T04:57:08.205495+00:00. Audit statique uniquement ; aucune génération, Blender, rendu, copie de master, modification de gel/records ou indexation. Aucun catalogue global vivant n’est figé dans ce rapport.

## Fermeture des entrées manquantes

| Entrée réelle | SHA-256 | Action de publication à préparer par root |
|---|---|---|
| `assets-src/moto-components/engine-spark-plug/build-report.json` | `0a348c461fabf16b1f26395a45efdc7c01058e175163330303854772f2656d40` | Ajouter aux dépendances du capuchon : ce JSON v1 choisit les noms des objets liés |
| `assets-src/moto-components/rear-rim/g3-master-v1/rear-rim-inspection.glb` | `e0a6b043429ac242ff93f0ea92e8628ef19bb7af998e472f0e924d7dba9f79eb` | Copie G3 exacte promue par root et vérifiée ; candidat final inchangé |
| `assets-src/moto-components/rear-rim/g3-master-v1/rear-rim-v1.blend` | `83528bcc3eba9e1766172af2549ea19aaf3b94fd4ae1580123462b9281fc98f4` | Copie G3 exacte promue par root et vérifiée ; candidat final inchangé |
| `assets-src/moto-components/rear-rim/g3-master-v1/source-geometry-check.json` | `3929a5802e468e6981ee8e9e41e485f68fc5acd007fb7b271754e1439da74a40` | Copie G3 exacte promue par root et vérifiée ; candidat final inchangé |

Root a ajouté ces trois copies dans `assets-src/moto-components/rear-rim/g3-master-v1/`, avec README et `construction-input-manifest-v1.json` à quatre fichiers hachés. Les trois actifs et les quatre pins sont vérifiés. Le gel14 et les scripts restent inchangés.

Le guide du capuchon reste la **bougie v1 diagnostique a797**, avec son rapport historique correspondant. Les huit entrées/scripts/helpers de fabrication du capuchon sont présents ; seul le rapport de bougie manque au préflight28. Le worker CSG et le nettoyage sont déjà couverts. **Aucune bougie v2 en construction n’a été inspectée ni substituée.**

## Frontière constructeur → gris → matière

1. `rear-rim/build.py` lit uniquement ses paramètres et crée le gris sous les mêmes noms de source/export/rapport que le futur candidat. Le constructeur et les paramètres WIP sont déjà identiques octet pour octet aux fichiers publics.
2. `material.py` doit ensuite ouvrir **ce gris**, et son rapport gris, à ces noms de travail. Il génère les deux cartes originales puis écrase source/export/rapport en place. Pour poursuivre depuis le master G3 exact, il faut donc restaurer sa copie dans un espace de travail distinct. Relancer le matériau sur le `.blend` final déjà matérialisé ajouterait une nouvelle matière intérieure ; ce n’est pas une recette répétable du gris.
3. `check_material_preservation.mjs` lit réellement le GLB gris **e0a6** au chemin WIP absolu. Ce fichier original est désormais conservé dans la copie publique G3 ; l’ancienne fixture documentée doit rester accessible ou un nouveau vérificateur paramétrable doit être versionné. L’audit ne retouche pas le script gelé.

Le master gris **83528bcc** et son rapport **3929a580** sont les entrées de reprise exacte G3 ; une reconstruction par le constructeur est une autre frontière, sans reproduction binaire démontrée. Le GLB gris est indispensable au vérificateur actuel. `gray-review.json` et `geometry-check.json` sont des preuves G3 utiles, non des entrées de génération : leurs chemins/SHA sont séparés dans le JSON.

Les deux PNG finaux de jante sont déjà couverts par le gel14 et générés dans `material.py` (graine16002, FFT NumPy). Aucun pixel de photo n’alimente ces recettes. Pillow sert seulement au contrôle des images exportées. La jante n’a pas de helper CSG externe.

Les gels28/14 et leurs fichiers correspondent aux SHA. Le cap est gelé69dc ; la jante f97ddc/68412d. Les finales96 restent une phase distincte, annoncée en file ; aucune image finale n’est ouverte ou reçue par cet audit. État de manifeste final du cap observé : `False`. Le gel jante porte encore `final_images_pending=true`.

Le JSON contient les chemins réels, les SHA et l’état Git, les trois anciennes entrées WIP et leurs copies publiques vérifiées. B confirme que le rapport de bougie v1 reste historique ; le futur rapport v2 utilisera un autre nom, sans substitution de guide. Aucune réception artistique ou vérification de montage complet.
