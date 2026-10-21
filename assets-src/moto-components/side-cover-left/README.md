# P01 — peau extérieure du cache latéral gauche

Source originale Blender/GLB, étude estimée de l’apparence Boxer125HD RDC.
La pièce n’est pas placée sur la moto. P01 n’est pas terminé.

- [Paramètres](parameters-study-v1.json) : profil relevé manuellement sur la vue officielle gauche ; unités et incertitude explicites.
- [Source grise](side-cover-left-study-v1.blend) et [export gris](side-cover-left-study-v1.glb).
- [Source matière](side-cover-left-candidate-v1.blend) et [export matière](side-cover-left-candidate-v1.glb).
- [Références et limites](../../../creative/research/side-cover-left-p01/G0-G2-plan-v1.json).
- [Images et contrôles](../../../creative/reviews/side-cover-left-study-v1/README.md).

Collection `WEWA_SIDE_COVER_LEFT_STUDY`, objet `LEFT_COVER_OUTER_SKIN`.
Repère local : +X vers l’arrière du profil gauche, +Y vers le haut, +Z vers l’extérieur.
Ce repère n’est pas un placement dans le cadre.

Taille de travail approximative 272 ×156mm, bombé18mm et retour4mm estimés ;
aucune cote OEM mesurée. Une boucle arrière demeure ouverte volontairement.
Pas de revers, de pions, de grommets, ni de fixation basse fabriqués ici.
Les graphismes du constructeur ne sont pas repris. Les couleurs et la texture
rouge/noir sont originales ; aucun pixel documentaire n’est utilisé.

Protocole depuis la racine, Blender4.3.2 officiel avec Cycles CPU/OIDN :

```sh
python tools/create_side_cover_left_paint_p01.py
blender --background --python-exit-code 1 --python tools/build_side_cover_left_p01.py -- geometry
blender --background --python-exit-code 1 --python tools/build_side_cover_left_p01.py -- gray
# Lire les images et consigner gray-review.json avant material.
blender --background --python-exit-code 1 --python tools/build_side_cover_left_p01.py -- material
blender --background --python-exit-code 1 --python tools/build_side_cover_left_p01.py -- preview
# Lire les aperçus et consigner preview-review.json avant final.
blender --background --python-exit-code 1 --python tools/build_side_cover_left_p01.py -- final
node tools/check_side_cover_left_p01.mjs
node tools/check_motorcycle18_exports.mjs side-cover-left-study
python tools/capture_motorcycle18_v3.py side-cover-left-study
```

Ces commandes produisent les sorties de la révision. Pour une nouvelle correction,
utiliser une nouvelle révision et de nouveaux chemins ; ne pas écraser les preuves
historiques publiées. Aucun rejeu propre complet n’est revendiqué.
