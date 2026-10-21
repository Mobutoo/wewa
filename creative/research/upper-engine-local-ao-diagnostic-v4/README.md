# AO local V4 — sélection UV initiale redondante, non exécutée

**V3 n’a pas résolu le crash.** Ses barrières après libération et avant les UV passent, puis le SIGSEGV 139 survient encore à la mise à jour précédant la sélection des objets, après `UV.create_layers.end` (séquence 1240). Script, spec, journal et crash sont maintenant archivés dans `run-003`, sans réécriture ; les dix entrées sont vérifiées conformes aux SHA attendus. Aucun prepared blend ni bake. V1/V2/V3 et leurs preuves restent conservés.

La recherche dans le **code Blender v4.3.2** étaye une cause plus précise que la seule invalidation de caches :

- `rna_mesh.cc:943–950` fait parcourir à l’ancienne collection `MeshUVLoopLayer.data` les `corners_num` coordonnées UV.
- `rna_mesh.cc:1738–1758` retrouve l’indice du coin de face à partir du pointeur UV ; le commentaire décrit explicitement les risques liés aux réallocations de CustomData.
- `rna_mesh.cc:1773–1780` appelle `ED_mesh_uv_map_vert_select_layer_ensure`, puis écrit `select[loop_index]`.
- `mesh_data.cc:330–337`, dans `ensure_corner_boolean_attribute`, cherche une couche booléenne au domaine `corners_num`, mais **alloue une couche nouvelle avec `mesh.faces_num`**. `mesh_data.cc:341–346` est bien le chemin appelé par le setter précédent.
- La création d’une nouvelle UV en mode objet (`mesh_data.cc:256–282`) ajoute sa couche float2 ; elle n’assure pas cette couche de sélection. Une première écriture de sélection peut donc emprunter la branche d’allocation fautive. La nouvelle UV de notre dérivé passe par ce cas.

Pour un maillage de triangles, les indices de coins vont au-delà du nombre de faces. Ce chemin source permet donc une écriture hors de la taille allouée lorsque la couche booléenne était absente. C’est un **défaut documenté dans le source de cette version**, compatible avec une corruption mémoire dont le signal arrive lors d’une mise à jour ultérieure. Ce n’est pas encore une reproduction instrumentée de l’écriture hors limites dans le binaire exécuté, et V4 n’a pas été lancée. Les passages et SHA des quatre sources consultées sont dans `spec.json` ; les fichiers complets restent privés.

L’[outil V4](../../../tools/prepare_upper_engine_local_ao_v4.py) supprime seulement la boucle initiale :

```python
for loop in mesh.uv_layers[UV_AO].data:
    loop.select = True
```

Cette sélection en mode objet était redondante : les vrais `bpy.ops.mesh.select_all` en édition et `bpy.ops.uv.select_all` avant packing restent conservés. Elle n’est remplacée ni par un autre accès aux booléens CustomData, ni par un contournement des opérateurs. Aucun patch de Blender, aucune modification de maillage ou tolérance élargie.

Les marqueurs flushés et faulthandler sont conservés. Une mise à jour explicite est maintenant tracée après **chaque** création de couche, chaque changement d’`active_index`, chaque sélection d’objet et les deux vrais opérateurs de sélection en édition. Les barrières V3 restent présentes. Cela permettra de voir si une simple création/index déclenche encore le problème sans cette boucle, au lieu d’attendre la prochaine sélection globale. Aucun message par coin ni boucle de tentatives.

Les fonctions de témoins, de conservation exacte, d’export, de clipping UV et de bake restent identiques à V3 par comparaison AST. Les paramètres AO/unwrap/packing et les limites restent inchangés. Une réussite de préparation ne constituerait pas une réception du bake ou du rendu.

Après revue du code, root pourra décider d’un seul essai neuf :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python tools/prepare_upper_engine_local_ao_v4.py -- --phase prepare --spec creative/research/upper-engine-local-ao-diagnostic-v4/spec.json > /tmp/wewa-upper-engine-local-ao-prepare-004.log 2>&1
```

La racine privée `…/upper-engine-local-ao-diagnostic-v1/run-004` n’a pas été créée. Aucun Blender, `main`, copie de source, bake ou rendu exécuté ici. Les seuls contrôles exécutés concernent syntaxe/JSON et identité AST des fonctions protégées. Sources officielles : [RNA mesh v4.3.2](https://raw.githubusercontent.com/blender/blender/v4.3.2/source/blender/makesrna/intern/rna_mesh.cc), [ED mesh_data v4.3.2](https://raw.githubusercontent.com/blender/blender/v4.3.2/source/blender/editors/mesh/mesh_data.cc), [API MeshUVLoopLayer 4.3](https://docs.blender.org/api/4.3/bpy.types.MeshUVLoopLayer.html).
