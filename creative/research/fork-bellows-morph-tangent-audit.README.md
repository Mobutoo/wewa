# Audit indépendant — tangentes de morph du soufflet

21 octobre 2026. [Données, empreintes et références de code](fork-bellows-morph-tangent-audit.json). Aucun rendu, changement de source/GLB, modification de Blender partagé ou réception artistique effectué par cet audit.

Le changement local **`n.rotation_difference(morph_n)` est mathématiquement justifié**. Dans le vrai `PrimitiveCreator.__calc_morph_tangents` de Blender 4.3.2, `morph_n = n + deltaNormal` reconstitue la normale cible ; les normales et la tangente sont déjà dans le même repère glTF. `Vector.rotation_difference(other)` produit la rotation active du premier vecteur vers le second. La ligne native inverse cette correspondance, puis applique cette rotation à la tangente avec `t.rotate(q)`.

Un test réel mathutils à 30°, CPU 1 sans scène/rendu, donne `N_cible·T_rot ≈ 0,866` avec le sens natif, contre `−8,94×10⁻⁸` dans le sens corrigé. La rotation corrigée est propre (déterminant +1) : elle conserve aussi le produit vectoriel et la latéralité du repère ; ce résultat ne repose donc pas uniquement sur l’orthogonalité.

Les vrais buffers natifs `50e82d54…` et corrigés `eeda9976…` ont été décodés indépendamment, y compris leurs accesseurs clairsemés. Les indices, positions, normales, UV, tangentes de base **avec w**, positions/normales de morph sont numériquement identiques. Seules les tangentes de morph changent.

| État | Max. `abs(N·T)` natif | Corrigé réel | Écart maximal de direction corrigée / dérivée UV-U |
|---|---:|---:|---:|
| Repos | 0,00012560 | 0,00012560 | 0,00723° |
| Compression | 0,00206942 | 0,00012565 | 0,06317° |
| Extension | 0,00178836 | 0,00012557 | 0,05281° |
| Demi-compression | 0,00107077 | 0,00012561 | 0,03378° |
| Demi-extension | 0,00089399 | 0,00012558 | 0,02662° |

La comparaison de direction utilise les dérivées UV réelles des triangles, pondérées par les angles aux sommets et projetées dans le plan normal. Elle ne montre aucun retournement de la direction U, mais **ce substitut n’est pas un recalcul exact MikkTSpace**. Le résidu d’arrondi de la base est conservé, pas artificiellement annulé. Le helper local a été lu : garde de version/empreinte, remplacement temporaire de méthode et restauration dans `finally`. L’installation reste à l’empreinte `af539328…`.

Le signe V demande une distinction : `w × cross(N,T)` est opposé à notre dérivée `dP/dV` sur les 154 010 sommets, déjà au repos et dans les deux exports. L’exporteur convertit explicitement `V → 1−V` en conservant le signe Blender. Ce constat **ne justifie aucun changement global de w** : le correctif de morph conserve la base et sa convention, tandis que la lecture d’une carte normale dépend aussi de son orientation et de son espace tangent d’origine.

Le chargement réel Babylon **9.31.0** a été lu : le viewer utilise un repère droit ; le loader définit `invertNormalMapX=false`, `invertNormalMapY=true` lorsqu’une `normalTexture` existe et charge les textures avec `invertY=false`. Avec tangentes fournies, le shader construit directement `B=cross(N,T)*w` ; les inversions de la branche dérivée UV ne constituent pas une correction supplémentaire automatique de ce TBN. Sans tangentes fournies, la branche dérivée emploie les paramètres (+1, −1). Retournement de l’image à l’upload, canal vert et signe du bitangent sont trois opérations distinctes.

Le G3 neutre `eeda9976…` examiné initialement était **sans image ni normal map**. Le G4 `42cb7a7e…` est arrivé ensuite : ses attributs et deltas ont été indépendamment comparés au G3, sans aucune différence. L’auteur des cartes et leurs pixels embarqués ont été lus ; aucun rendu supplémentaire n’a été exécuté.

La régénération indépendante du champ déterministe montre que le PNG lu de haut en bas correspond aux lignes renversées de l’image auteur Blender de bas en haut : 786 431 composantes sur 786 432 sont identiques, la dernière diffère d’un octet de quantification. Le vert n’a pas été inversé ; les pixels embarqués sont identiques au PNG auteur. Avec `V_glTF=1−V_source` et `texture.invertY=false`, les mêmes texels restent donc associés aux mêmes points de surface. Garder le TBN fourni et w conserve la base source ; forcer son bitangent vers `dP/dV_glTF` la changerait.

Cette lecture et ces données soutiennent la cohérence de la chaîne image/UV/base tangente. Elles ne démontrent pas une parité photométrique exacte des shaders, de `NormalMap Strength`/`normalTexture.scale`, ou de tous les poids de morph. Les cinq états exclusifs examinés ne prouvent pas le mélange simultané compression/extension ni une déformation physique du caoutchouc. Aucun patch de buffers ou de signe global n’est proposé.
