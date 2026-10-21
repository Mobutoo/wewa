# Haut moteur — orientation HDR explicite v2

Nouvel inspecteur de revue : seule la rotation de sampling du HDR devient `+π/2`. Les sources, le GLB, les matières importées, l’exposition, l’intensité et les deux caméras restent inchangés. La [dérivation des conventions](../../research/upper-engine-environment-diagnostic-v1/README.md) explique ce quart de tour pour Cycles4.3.2 et Babylon9.31.0 ; six rayons CPU du vrai HDR l’étayent.

| Cadrage | Blender natif | Babylon v1, orientation initiale | Babylon v2, orientation explicite |
|---|---|---|---|
| Quart avant | [Natif](../upper-engine-material-lighting-v1/neutral-outdoor.png) | [Avant](../upper-engine-common-camera-v1/front/actual-babylon-same-camera.png) | [Après](front/actual-babylon-same-camera.png) |
| Côté opposé | [Natif](../upper-engine-material-lighting-opposite-v1/neutral-outdoor.png) | [Avant](../upper-engine-common-camera-v1/opposite/actual-babylon-same-camera.png) | [Après](opposite/actual-babylon-same-camera.png) |

Les deux nouvelles images sont de vrais canvas Chromium/SwiftShader. Les reflets changent de place ; le cadrage conserve son écart logiciel maximal de0,000330pixel sur huit témoins par vue. Ce contrôle de projection n’est pas une mesure sur photo. Les octets HTTP du GLB et du HDR ainsi que les sources liées ont été vérifiés.

**Le rendu reste à reprendre.** La rotation est réellement appliquée au runtime ; elle ne prouve pas à elle seule l’étalonnage GPU de la radiance ou du préfiltre. AgX/ACES, BRDF et occlusion demeurent différents. Le lab n’a pas d’occlusion de scène et les matières n’ont pas d’occlusionTexture ; les creux des ailettes ne reproduisent donc pas encore les ombres de Cycles. Aucun assombrissement d’albédo ne masque ce manque.

La [lecture réelle](coordinator-reading-v1.json), les [mesures avant](front/engine-check.json), les [mesures opposées](opposite/engine-check.json) et la [liste figée](manifest.json) distinguent ces résultats. Aucun rendu natif relancé, source enregistrée ou pièce modifiée, aucune réception artistique, qualification iPhone ou modification du jeu public.

Reproduction, dans une nouvelle destination et avec le serveur Vite local:4143 :

```sh
python tools/capture_material_camera_comparison_v2.py creative/reviews/upper-engine-common-camera-v1/front-camera.json creative/reviews/nouvelle-orientation/front --rotation-y 1.5707963267948966 --orientation-report creative/research/upper-engine-environment-diagnostic-v1/report.json
```

Refaire avec `opposite-camera.json` dans une autre destination. Les scripts v1 et leurs premières captures sont conservés intacts.
