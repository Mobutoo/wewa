# Préparation bornée de l’assemblage avant

[Plan détaillé](preparation.json), fondé sur les surfaces d’inspection existantes et leurs vrais rayons source/GLB. Les deux images du guide neutre ont été réellement ouvertes. Aucun Blender, rendu ou nouvelle géométrie n’est produit ici.

La famille **D04 BM125 UG5gear** est la première hypothèse artistique cohérente avec les candidats JA131605/JA131607 existants ; elle suggère DJ151041 pour l’axe. Elle ne confirme ni la variante RDC ni les dimensions. D04 standard et D15 alliage restent des groupes alternatifs distincts.

La prochaine pièce proposée est **l’axe avant comme candidat artistique séparé**, avec tête/embase, fût et filetage documentés ou estimés explicitement. La longueur, le diamètre et le sens de montage restent paramétriques. Cette proposition n’annonce pas une reproduction dimensionnelle fidèle : aucune cote fiable du vrai axe n’a été trouvée dans la recherche déjà archivée. Écrou, rondelle et colliers suivent comme pièces distinctes.

| Repère d’inspection | Valeur disponible | Portée |
|---|---|---|
| Jante, rayon axial Y=7,5 mm | X=−35,984 à +34,964 mm | Surfaces réelles de ce candidat et de ce rayon |
| Flasque, même rayon | X=+36,500 à +48,000 mm | Pas une dimension constructeur |
| Œil de chaque fourreau | X local=−17,700 à +17,700 mm | Épaisseur échantillonnée, pas axe installé |
| Intervalle jante/flasque | 1,536 mm dans le guide actuel | Ni jeu mécanique certifié ni entretoise à reproduire |
| Alésages de travail fourche/jante/flasque | Ø12,4 / 13 / 13,4 mm | Paramètres estimés ; pas le diamètre de l’axe |
| Ent­raxe de fourche du guide | 175 mm | Hypothèse seulement, variable S |

Le modèle symbolique conserve **S** (écartement), **T** (décalage axial de la roue) et **P** (décalage relatif du flasque) indépendants. Les espaces côté opposé au flasque et côté flasque valent respectivement `S/2+T−53,683767 mm` et `S/2−T−P−65,700065 mm`, avec S/T/P exprimés en millimètres. Ces espaces ne fournissent pas automatiquement des longueurs de colliers : ils doivent encore être reliés aux véritables portées, joints et appuis. Les 210,4 mm entre faces externes du guide ne donnent pas la longueur sous tête de l’axe.

Après axe/retention/colliers : caler le flasque sans forcer sa butée dans une poche de fourche mal identifiée ; ajouter la prise extérieure de compteur et sa liaison au câble ; puis came, levier et terminaison du frein. Les roulements et engrenages cachés restent un contexte d’interface distinct, sans inventer leurs détails internes.

Un manque concret supplémentaire est confirmé dans le générateur du **levier de came** existant : il perce le siège d’arbre, l’œil de câble et la fente, **pas un passage transversal de boulon de pince**. Ajouter un boulon M6 flottant ne ferme donc pas cette interface. Une éventuelle correction du levier exige une révision séparée. La désignation M6×1 de l’écrou UG est sourcée ; elle n’est pas une spécification du filetage d’axe.

Les références restent privées et documentaires. Le plan sépare cotes nominales publiées, indications de variantes voisines, paramètres artistiques et surfaces numériques réelles. Il ne réceptionne ni montage OEM, ni fonctionnement du frein, ni réalisme artistique final. Le pneu G3/G4 en cours suit sa nouvelle révision ; l’ancien manque matière décrit par le guide n’est pas repris comme un nouveau travail à refaire.
