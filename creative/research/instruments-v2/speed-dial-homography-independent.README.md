# Cadran vitesse — étude indépendante d’homographie

21 octobre 2026. **Une homographie aide la comparaison photographique ; ces données ne permettent pas de calibrer le cadran.** Aucun angle, pivot, dessin ou modèle source n’a été changé. Pas de Blender ni de rendu.

La photo privée native 1000 × 600 a été ouverte. Aucun nouveau relevé n’est prétendu : nous réutilisons les 16 points du bord imprimé et les six ancres 40–140 de `speed-dial-calage.json`, avec leur incertitude approximative de ±3 px par coordonnée. Les boîtes de `dial-artwork-plan.json` ne constituent pas de nouveaux points indépendants. Le 0 masqué et le 20 incertain restent exclus. L’ambiguïté page RDC 125HD / nom de fichier BM150 demeure.

L’essai préféré suppose un bord circulaire plan et des **directions radiales régulièrement espacées**. Il laisse libre la position radiale de chaque ancre : un même rayon extérieur n’est pas établi. Le premier essai à rayon commun ajoutait cette contrainte sans preuve ; il n’est pas retenu comme calibration.

| Modèle de comparaison | Incrément / 20 km/h | Écart ancre→direction max, ajustement | Max après retrait d’une ancre |
| --- | ---: | ---: | ---: |
| Affine, contrat v1 conservé | 38,5714° | 6,71 px | 9,80 px |
| Affine, hypothèse 40° | 40° | 3,77 px | 5,36 px |
| Projectif, contrat v1 conservé | 38,5714° | 1,62 px | 5,00 px |
| Projectif, hypothèse 40° | 40° | 2,00 px | 7,02 px |
| Projectif, incrément libre | 35,7619° ajustés | 0,98 px | 7,12 px |

Ce sont des distances perpendiculaires aux directions projetées, **pas des erreurs de position complètes**, ni une précision de 2 px. Le modèle libre améliore l’ajustement mais généralise moins bien au point retiré. Les quatre groupes de points de bord retirés donnent des maxima approximatifs de 1,66 px avec l’incrément v1 et 1,47 px avec l’incrément libre ; ils contraignent la conique, sans lever son ambiguïté de rectification. Les points retirés proviennent de la même photo : aucune vue indépendante n’a été validée.

Sous 120 perturbations uniformes de ±3 px par coordonnée, l’incrément libre varie de 23,17° à 41,10°. Ce résultat est un test de sensibilité, **pas un intervalle de confiance**. Dans une grille de profils de 0,5°, les incréments 27–43° admettent ici des résidus normaux et radiaux maximaux inférieurs à 3 px. Ce critère de distance approximative n’est pas une preuve de faisabilité exacte des coordonnées ±3 px. Les bornes et les minima locaux sont documentés ; aucune recherche globale exhaustive n’est revendiquée.

Le fichier [rapport JSON](speed-dial-homography-independent.json) fournit une homographie de travail **conditionnelle**, avec deux conventions explicites : repère local où θ40 = 0, et repère v1 où θ(s) = 225 − s × 270/140 degrés. La conversion a été vérifiée numériquement. Sa projection du centre du cercle est un résultat de l’ajustement ; elle n’est pas un relevé du moyeu d’aiguille et ne doit pas déplacer le pivot source. Le cercle unité ne porte aucune cote en millimètres. Une hypothèse de plan/cercle ne certifie ni l’optique de la vitre ni la géométrie imprimée réelle.

Pour lever l’ambiguïté, il faut notamment un relevé indépendant du moyeu/pivot visible, les deux extrémités ou axes de plusieurs graduations radiales clairement identifiées, puis une autre vue de la même variante. Ne pas utiliser le pivot du modèle comme une observation de la photo. En attendant, conserver le contrat v1 et employer la matrice uniquement comme aide de comparaison étiquetée.

Reproduction légère, Python + NumPy + SciPy :

```sh
OPENBLAS_NUM_THREADS=1 python creative/research/instruments-v2/study_dial_homography_independent.py
```

Le script, son auxiliaire `independent_homography_common.py` et [les résultats détaillés](speed-dial-homography-independent-results.json) conservent les résidus, les retraits, les profils, les hypothèses et les empreintes des entrées. Les originaux photographiques restent hors dépôt. Ce travail ne vaut ni calibration métrique, ni conformité constructeur, ni réception artistique.
