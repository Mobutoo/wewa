# Assemblage glTF statique sans copie de BIN — v1

Outil : `tools/compose_motorcycle_gltf_v1.mjs`. Exécuter depuis `/workspace/wewa`. Aucun Blender, Vite, rendu ou cache Vite utilisé. Les entrées et GLB restent en lecture seule.

## Probe sans écriture

```sh
node tools/compose_motorcycle_gltf_v1.mjs \
  --parents creative/reviews/whole-exterior-coverage-v15/linked-parents-check.json \
  --routes creative/research/authorized-repetition-layout-v1/export-routes-resolved.json \
  --out assets-src/moto-components/whole-motorcycle-runtime-v1/motorcycle.gltf \
  --probe
```

`--probe` compose, valide et calcule les bornes en mémoire ; stdout contient la preuve complète, aucun fichier de sortie créé. Retirer `--probe` pour écrire seulement `motorcycle.gltf` et `motorcycle.gltf.proof.json`, après réussite du validateur et du probe NodeIO. Les fichiers de sortie existants sont refusés. L’outil ne crée aucun BIN, aucune texture et aucun GLB. Le JSON est volontairement compact. Les sources doivent rester accessibles aux URI relatives ; cet assemblage est dépendant de leurs octets exacts, pas autonome.

Le dossier parents accepte `parents[]` avec `key`, `source`, `sha256` (empreinte native déclarée, non recertifiée), `selected_objects`, `translation_m`, `rotation_degrees`, `scale` et `placement_status`. Les routes acceptent `rows[]` avec `key`, `source_blend`, `glb`, `selected_objects`. Un parent manquant, une route dupliquée, un désaccord de source ou de sélection échoue. Des routes supplémentaires peuvent être présentes ; seuls les parents demandés sont instanciés. Main peut ajouter ses parents moteur/châssis et leurs routes sans modifier la composition.

## Réutilisation des octets

Chaque GLB2 original unique devient un buffer externe brut : URI relative encodée, `byteLength = taille entière du GLB`. Le parseur lit réellement les en-têtes et chunks ; `BIN payload offset` désigne le premier octet de données après l’en-tête de chunk BIN, jamais une constante supposée20/28. Chaque bufferView est remappée au buffer externe et reçoit `byteOffset_original + BIN_payload_offset`. Les bornes sont contrôlées contre le byteLength original du BIN déclaré. Aucune transformation des données de sommets, indices, normales, tangentes ou images.

Fusion explicite des tables bufferView/accessor/image/texture/sampler/material/mesh. Sparse accessors, attributs et indices de primitives, morph targets et inverseBindMatrices des skins sont remappés. Les textureInfo de matières et extensions de matières connues sont remappées, y compris leurs transformations KHR_texture_transform inchangées. Les références d’images de KHR_texture_basisu/EXT_texture_webp sont remappées. Une image externe locale conserve son fichier original par une URI recalculée depuis le dossier du GLB ; une data URI est conservée. Pas de copie d’image.

Chaque GLB est fusionné une fois, même si plusieurs parents l’emploient : buffers et mesh IDs partagés. Chaque instance possède ses propres nodes et skins remappés. Les noms et transformations des nodes originaux sont conservés. Un node parent unique par exemplaire porte `G * R_BlenderXYZ * S * G^-1` et la translation `G*T`, où `G(x,y,z)=(x,z,-y)` et `R_BlenderXYZ=Rz*Ry*Rx`. Les échelles de parents doivent être finies et strictement positives ; les échelles non uniformes, dont la profondeur moteur1,8, sont conservées. Miroir et échelle nulle refusés. Aucun correctif des transformations sources n’est appliqué.

## Sélection et scènes

Seule la scène par défaut (`scene`, sinon0 selon glTF2) est parcourue. Hiérarchie cyclique, référence hors scène active ou multiparent source refusée. `selected_objects` vide signifie tous les nodes mesh de cette scène. Une sélection doit correspondre exactement à un nom de node unique actif. Si ce node possède un mesh, seul celui-ci est sélectionné ; si c’est un groupe, les meshes descendants sont retenus. Les ancêtres nécessaires et les joints de skins restent comme hiérarchie, mais ne réintroduisent aucun mesh non sélectionné. Aucun autre node d’une scène inactive n’est instancié.

Un seul alias documenté : `Front brake panel - editable casting` → `Front brake panel - inspection export`. Aucun fuzzy matching, suffixe Blender ou fallback implicite vers un export entier. Un wrapper source peut rester dans la hiérarchie originale ; il n’autorise aucune correspondance approximative de nom. Tous les matchs sont consignés dans la preuve.

Animations et caméras sont omises. KHR_lights_punctual est explicitement supprimée des nodes et de l’union d’extensions, car la sortie est statique sans éclairage. Pour les autres extensions, l’union des déclarations sources est conservée. Toute extension inconnue, même seulement déclarée, échoue ; aucun index-bearing extension n’est deviné. Les extensions autorisées sont explicitement listées dans le code ; notamment Draco, meshopt, variants et instancing ne sont pas implémentés et sont refusés.

## Validation et preuve

`gltf-validator.validateString` charge chaque URI via `externalResourceFunction`, comme octets bruts du fichier référencé. `maxIssues:0` garde toutes les observations ; une liste tronquée ou une seule erreur arrête l’export. Aucun ignore de code, réparation normale/tangente ou seuil assoupli. Les avertissements et informations restent intégralement dans le rapport.

NodeIO avec ALL_EXTENSIONS recharge le JSON composé et ses ressources originales ; `getBounds` parcourt chaque sous-arbre parent réellement exporté. Nom/index du parent et finitude des bornes contrôlés. Les bornes sont en mètres glTF ; main devra les comparer aux native bbox correspondantes, après conversion des axes et en distinguant les surfaces réellement sélectionnées. Aucune comparaison native ou compatibilité mécanique n’est revendiquée ici. Les bornes de skin/morph restent celles de la méthode NodeIO, pas une animation évaluée.

Preuve : empreintes des deux entrées, SHA256 et taille de chaque GLB, offset/longueur du chunk BIN, index buffer, nombre d’exemplaires, scène active, sélection exacte, IDs mesh partagés, matrice de chaque parent, bornes NodeIO, rapport du validateur et SHA256 du JSON exact écrit. Les SHA256 des GLB sont recalculés après validation/lecture NodeIO pour détecter une modification pendant le probe. L’empreinte native `source_blend_manifest_sha256` reste une référence du manifeste fourni, pas une nouvelle ouverture Blender.

## Probe réel de cette livraison

Entrées : coverage-v15/linked-parents-check et authorized-repetition-layout-v1/export-routes-resolved. 114 parents,104 GLB uniques,592960384octets originaux référencés ; JSON516636octets avant ajout du champ de provenance transform_input (nouvelle ligne finale incluse), aucun octet BIN écrit. Six sources réutilisées : tube de fourche×2, amortisseur arrière×2, glace de clignotant×4, housing de clignotant×4, caoutchouc de repose-pied×2, bouchon de fourche×2. Le partage des mesh IDs des exemplaires non filtrés a été vérifié. Alias avant résolu exactement sur le node0.

Premier probe complet :0erreur,1avertissement,432informations ;114 bornes finies et104SHA GLB revérifiés. Le second probe utilise la version finale avec observations du validateur illimitées et extensions NodeIO enregistrées ; son résultat est consigné ci-dessous. Six rotations XYZ, dont des rotations composées24/0/180 et−90/−70/−90, ont aussi été comparées à un calcul indépendant point par point de `G*(R*p+T)`. Identité et rejet de miroir vérifiés. Aucun fichier d’assemblage généré dans cette livraison ; deux nouveaux fichiers permanents seulement, outil et ce protocole. Aucun Git, racine, catalogue, board ou rendu.

Résultat final :0erreur,1avertissement,432informations,114bornes finies et104SHA revérifiés ; six cas de matrice passés. Avertissement conservé : `MESH_PRIMITIVE_GENERATED_TANGENT_SPACE` à `/meshes/297/primitives/0/material` — la matière requiert un repère tangent absent du mesh, calcul runtime potentiellement non portable. Aucun ajout ni réparation de tangentes. La sortie reste un candidat technique à revoir par main, pas une réception visuelle ou G8.


## Transformations v16 — extension technique, sans gel d’assemblage

`row.scale` est appliquée dans le repère Blender, avant rotation : `T * Rz * Ry * Rx * S`. Exemple `[1,1.8,1]` en Blender donne des facteurs `[1,1,1.8]` en glTF pour rotation identité. Le facteur1,8 est ainsi porté par le bon axe, sans déformer les buffers partagés ni les autres exemplaires.

Une matrice Blender parent explicite peut être fournie dans un seul champ parmi `matrix_blender`, `matrix_world`, `matrix`. Format conseillé : tableau4×4 de lignes, comme `list(matrix_world)` en Blender ; translation dans la quatrième colonne. Une matrice plate16 requiert impérativement `matrix_layout: "row-major"` ou `"column-major"` pour éviter toute convention implicite. Ces matrices sont en axes Blender et deviennent `G * M_Blender * G^-1`.

La matrice explicite est prioritaire sur les champs translation/rotation/scale : elle décrit déjà la transformation parent complète ; les champs TRS ne sont pas appliqués une deuxième fois. Une éventuelle scale déclarée doit néanmoins rester positive. Deux champs matrices simultanés sont refusés. Matrice non affine, miroir, singularité et shear sont refusés ; la vérification d’orthogonalité utilise une précision numérique relative1e-10, sans altération ni réparation. Cette garde concerne la représentabilité TRS des matrices glTF, pas un assouplissement des contrôles de normales/tangentes.

`extras.transform_input` du parent indique la provenance utilisée. Les transformations des nodes de la source restent intégralement inchangées, sous ce parent. La comparaison aux native-evaluated-bounds reste à faire par main avec ses routes finales v16.

Parité de l’alias avant : seul le nom de sélection `Front brake panel - editable casting` est résolu en nom exact de node source `Front brake panel - inspection export`. Le mesh original de ce node est utilisé avec ses buffers, matériaux et transformations d’origine. L’alias n’ajoute aucun autre mesh et ne prouve pas à lui seul la parité géométrique avec le casting natif ; cette comparaison dépend des bornes évaluées de main.

Tests complémentaires exécutés : scale Blender `[1,1.8,1]`, translation et conversion d’axe ; équivalence matrice4×4 / plate row-major / plate column-major ; refus de scale nulle, négative ou infinie, matrice plate ambiguë, shear et miroir. Aucun fichier de sortie ni gel propre créé.

Probe114 après extension v16 :114parents,104GLB,0erreur validateur,1avertissement inchangé,114bornes NodeIO finies,104SHA revérifiés,0écriture de sortie. Trois tests indépendants supplémentaires de rotations composées avec scale non uniforme `[0.9,1.8,1.3]` passent également. Outil prêt pour routes/parents finaux ; aucun gel d’output.
