# Haut moteur — diagnostic d’occlusion, état refusé

Le même GLB a été affiché dans la même session, avec puis sans SSAO2. La [capture désactivée](front/actual-babylon-AO-disabled.png) est **identique pixel par pixel** à la vue avant de la comparaison HDR v2. La [capture activée](front/actual-babylon-AO-enabled.png) est également un véritable canvas, sans modification de source, matière, caméra, HDR ou exposition.

Les creux entre ailettes s’assombrissent, mais des points clairs, contours irréguliers et du bruit apparaissent. **Cet état est refusé pour adoption dans le jeu.** Il ne constitue pas un rendu réaliste reçu. La cause précise des défauts reste à isoler entre anticrénelage, profondeur, filtrage et composition du postprocess ; une lumière ou un albédo retouché ne les résoudrait pas.

Paramètres de diagnostic : rayon15mm, biais de profondeur0,2mm,16échantillons, textureSamples1, résolution1000×750. Ce sont des choix de test, pas une mesure de matière ni un réglage mobile qualifié. L’occlusion écran ne voit pas toute la géométrie cachée et ne remplace pas la visibilité de l’environnement tracée dans Cycles. AgX/ACES et BRDF restent différents.

La [lecture réelle](coordinator-reading-v1.json), les [paramètres et contrôles runtime](front/engine-check.json) et la [liste figée](manifest.json) conservent cette tentative. L’autre caméra n’est pas calculée après ce défaut visible ; corriger dans une nouvelle révision avant d’élargir le test. Aucun code du jeu public, fichier Blender ou GLB modifié, aucune réception artistique ou qualification iPhone.

Reproduction dans une nouvelle destination avec Vite local:4143 :

```sh
python tools/capture_material_camera_comparison_v3.py creative/reviews/upper-engine-common-camera-v1/front-camera.json creative/reviews/nouveau-test-occlusion/front --rotation-y 1.5707963267948966 --orientation-report creative/research/upper-engine-environment-diagnostic-v1/report.json
```
