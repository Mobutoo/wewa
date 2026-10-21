# Soleil/ombres v5 — code additif prêt, non exécuté

Le [lab v5](../../../tools/motorcycle-material-camera-lab-v5/review.js) importe intégralement le v4 gelé et récupère son `ShadowGenerator` par l’API publique 9.31 `getShadowGenerator()`. Il ne construit aucune nouvelle scène, lampe, géométrie ou matière. La seule propriété de scène changée est **`ShadowGenerator.bias`**.

La valeur vient du **frustum réel au runtime**, sans constante tronquée :

```text
requested_m = max(orthoRight − orthoLeft, orthoTop − orthoBottom) / actualMap.width
API_bias = requested_m × abs(actualProjection[10]) / shader_BIASFACTOR
```

Le normalBias reste 0,1 mm ; mêmes caméras, source/GLB/HDR, soleil, frustum, PCF2048 MEDIUM, casters et receivers. Le [protocole retenu](../upper-engine-sun-shadow-acne-diagnostic-v1/README.md) reste la règle de lecture : v4 rejeté pour stries ; v5 est un seul essai, sans garantie de correction ni adoption.

La [capture v5](../../../tools/capture_material_camera_comparison_v5.py) importe les helpers du v4 protégé sans appeler son `main`. Elle exige deux caméras et **huit vrais PNG indépendants** : avant/opposée × neutre v2, neutre v5, W0 et W1. Elle vérifie :

- Témoins neutres v2/v5 égaux exactement en RGBA lu et PNG décodé.
- Nouveau W0 strictement égal au W0 v4 gelé, en pixels et buffers/matrices/PBR complets. Même lumière et réglages d’ombre, sauf les deux champs de bias attendus. Échec : arrêt avant W1.
- W0/W1 conservent G/N/tous UV/T/indices/matrices/PBR, caméra/HDR et casters/receivers ; la valeur du bias est recalculée depuis le frustum déclaré et sa projection réellement utilisée.
- Les **44 entrées v4**, toutes ses preuves publiques présentes et la nouvelle source API lue restent exactes avant/après. Les quatre nouveaux fichiers sont aussi hashés. Le [rapport de préparation](conservation.json) donne les chemins et empreintes.

Commande pour **une exécution root**, serveur Vite du dépôt déjà ouvert au port 4143, destination neuve :

```bash
python tools/capture_material_camera_comparison_v5.py \
  creative/reviews/upper-engine-sun-shadow-v5 --port 4143
```

Aucun serveur, navigateur, Blender ou rendu lancé ici. Syntaxe JavaScript/Python vérifiée ; aucun v4 modifié. La destination de capture n’est pas précréée. En cas d’échec, les preuves partielles restent avec un statut de refus ; aucune nouvelle valeur n’est choisie, aucun seuil assoupli et aucun nouvel essai automatique.

Même après réussite logicielle, root doit ouvrir les huit PNG et comparer W1 aux références v4/warm Blender à la taille native : refuser stries persistantes, nouveaux jours entre contacts et ombres, perte d’ombre sur bords fins, halos ou éclaircissement injustifié. Une ambiguïté reste non résolue. Aucun succès numérique ne constitue réception artistique, parité matière ou validation iPhone. Le jeu, les gels et les registres restent intacts.
