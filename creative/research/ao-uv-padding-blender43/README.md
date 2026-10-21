# Atlas AO — comportement documenté de Blender4.3.2

Lecture documentaire uniquement : aucun Blender, modèle, bake ou réparation exécuté ; le gros `uv-area-failure.json` n’a pas été ouvert.

Trois faits officiels expliquent pourquoi un opérateur terminé ne prouve pas un atlas valide :

- **Smart Project emballe déjà ses îlots.** Il projette par objet, puis appelle un packing commun sur les objets modifiés. Un second `pack_islands` est donc une seconde transformation, pas le premier rangement des UV. [Code3144–3320](https://github.com/blender/blender/blob/v4.3.2/source/blender/editors/uvedit/uvedit_unwrap_ops.cc#L3144).
- **Des petites faces sont explicitement mises à zéro.** Le seuil `smart_uv_project_area_ignore=1e-12f` porte sur l’aire locale BMesh ; les faces sélectionnées sous ce seuil reçoivent UV=(0,0). Ce n’est pas un test de taille en pixels ni une suppression de géométrie. [Constante3018 et traitement3209](https://github.com/blender/blender/blob/v4.3.2/source/blender/editors/uvedit/uvedit_unwrap_ops.cc#L3018).
- **FRACTION garde une marge dans l’espace UV final et cherche l’échelle des îlots.** Son solveur a25itérations et un plancher1e-5 ; s’il ne trouve pas de placement au plancher, le code conserve un placement de secours même imparfait. Ce mécanisme autorise une sortie sans garantir absence de triangles aplatis. [Solveur2003–2117](https://github.com/blender/blender/blob/v4.3.2/source/blender/geometry/intern/uv_pack.cc#L2003). La marge fractionnaire est plus coûteuse ; le code utilise aussi une voie rapide au-delà d’une petite sélection d’îlots. Cela ne prouve pas que cette branche a été atteinte dans ce dérivé.

[Documentation Pack Islands](https://docs.blender.org/manual/en/4.3/modeling/meshes/uv/editing.html#pack-islands) : FRACTION signifie fraction du carré UV, pas une division de la marge par le nombre d’îlots.16/1024=0,015625 reste une contrainte fixe à chaque îlot ;657316triangles ne disent pas combien d’îlots doivent tenir. Le bord8px appliqué après un pack valide est une homothétie positive de1008/1024 ; en arithmétique exacte, il ne peut pas transformer seul une aire positive en zéro. La précision float32 peut néanmoins devenir pertinente pour des UV déjà extrêmement petits.

**Multi-objet et carte active.** Le code rassemble les données de maillage uniques des objets en édition ; il ne travaille pas seulement sur l’objet actif. Pour chacun, `BM_uv_map_get_offsets` prend sa propre couche UV active. ActiverUV_AO sur un seul objet n’est donc pas suffisant. [Packingmulti1417](https://github.com/blender/blender/blob/v4.3.2/source/blender/editors/uvedit/uvedit_unwrap_ops.cc#L1417), [coucheactive45](https://github.com/blender/blender/blob/v4.3.2/source/blender/bmesh/intern/bmesh_query_uv.cc#L45). La sélection de faces et, selon le contexte UVEditor, la sélectionUV limitent les éléments traités. Un nombre d’objets sélectionnés sans12maillages réellement en édition ne suffit pas.

## Hypothèses à départager, sans correction présumée

1. Zéros produits dès Smart Project : comparer leur nombre aux faces d’aire locale≤1e-12, puis examiner au plus quelques exemples correspondants. Le seuil porte sur les faces, tandis que l’audit UV compte les triangles : ces comptes ne sont pas interchangeables pour des polygones non triangulaires.
2. UV positifs après Smart Project puis aplatis après le second pack : mesurer le nombre d’îlots, leur aire et l’échelle appliquée ; une pression du padding fractionnaire devient alors une hypothèse distincte.
3. Des objets/couches non traités ou une sélection partielle : relever nom/index UV actif, sélection effective et contexte à chaque étape, pas seulement le code demandé.
4. Triangles très étroits déjà positifs : conserver aire calculée enfloat64 depuis les vrais float32, plus bornes/quantiles ; ne pas confondre zéro exact, aire≤1e-18 et simple sous-pixel.

## Meilleure étape de mesure

Lire d’abord l’UV_AO actuel de la copie rejetée. Dans une opération séparée en mémoire, activerUV_AOindex1 sur les12copies, sélectionner réellement faces/UV enEDIT, exécuter seulement SmartProject66°/marge0, puis revenirOBJECT **avant** le second pack. Produire parmaillage : airelocale des faces et nombre≤1e-12 ; triangles UV à zéro exact et≤1e-18 ; UVfinis/bornes ; quantiles des aires ; éventuellement îlots par continuité exacte des arêtesUV. Limiter à trois exemples par objet. Protéger les empreintes de géométrie, normales, UV0 et sources avant/après ; ne rien sauvegarder enBLEND ni exporter/baker.

Cet essai localisera un échec avant ou après Smart Project ; il ne sépare pas à lui seul sa projection de son packing interne. Aucune réparation, changement de seuil ou validationAO/Babylon n’en découle avant lecture des données.

## Outil préparé, non exécuté

[`tools/measure_upper_engine_smart_uv_v1.py`](../../../tools/measure_upper_engine_smart_uv_v1.py) est prêt pour lecture root. Compilation statique passée ; aucun appel Blender exécuté. Il épingle le BLEND rejeté SHA `7017d79d…`, sélectionne les12copies locales du même spec, protège géométrie/normales/UVhorsAO et les SHA du BLEND/spec/sources gelées. Il sort enOBJECT avant les mesures finales, sans secondpack ni bord ni sauvegarde. Les aires et déterminants à1e-18 sont tous deux rapportés pour conserver la convention du contrôleur run005, avec croisement des zérosUV et des petites faces3D.

Exécution éventuelle par root uniquement :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python tools/measure_upper_engine_smart_uv_v1.py -- --count-islands
```

`--count-islands` est optionnel, potentiellement plus lent ; il utilise des arêtes physiques communes et des UV exactement égales, sans tolérance ou fusion. La sortie par défaut est un nouveau dossier privé `run-005/smart-only-measurement-v1/measurement.json`. Le script refuse de réutiliser un dossier existant. Aucune donnée n’a encore été produite par cet outil.
