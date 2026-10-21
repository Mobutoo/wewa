# Bord opposé de siège SNS — dépendances de reprise

BaseSource19 `a2aa4bc04d5c6fff242de160d806cd4fdc91313b`. [Rapport](report.json), [fermeture](source-closure-v1.json) et [entrées stables](stable-recipe-inputs-v1.json) : **62paires SHA/octets**, **43entrées** nommées. Source `69e326632770ee32c8703e96605e40d5dda40b66bbe9eb16be8ef29693874836`, GLB `11f2f5129fe8b9959e3f7419da38661b183cfd336e6419b6df94a522b6ef897d`. Aucun gel final encore actif n’est pinné.

## Construction

Profil annulaire fermé et arrondi, UV angulaires et normales analytiques, paramètres propres et plan G0–G2. La méthode de section est réutilisée de l’autre extrémité, pas son maillage : dimensions et position sont indépendantes. Aucun autre bord ou mécanisme n’est chargé.

## Materiau

Le constructeur matière vérifie chacun des19 fichiers gris avant d’ouvrir le maître fourni ; tous sont déjà dans43. Plan noir constant original, base linéaire(.009,.010,.012), métal0, rugosité0,27, coat0,15. Aucune texture, police, atlas ou photo.

## Reprise

Le maître gris relu permet la matière ; reconstruire ce gris peut changer ses octets et nécessite une nouvelle revue. Les libellés de console hérités ne constituent pas une dépendance à une ancienne pièce.

## Controle

check_rest_envelopes charge uniquement les GLB noir extérieur et orange intérieur, déjà publiés, plus le GLB gris propre. Les jeux axiaux actuels sont des preuves de disjonction de candidats au repos, pas des appuis reçus. Aucun de ces calculs n’est relancé ici.

## Rendu

Studio final : checkpoint privé d’aperçu imposé pour la vue, la source et la matrice caméra. Neutre final : spec et rapport public, HDR public et hash de la mire18% originale ; exposition réutilisée 1.476710338088647EV, sans décoder ou remesurer la mire. Les checkpoints/PNG/EXR finaux sont des sorties de reprise optionnelles.

## Limites

Bord aplati visible seulement ; circonférence complète, section, arrière, limite intérieure, position et échelle sont estimés. Support central, empilement, soudure et siège fonctionnel cachés ne sont pas fabriqués. Aucun montage, métrologie OEM, peinture physique, essai iPhone ou réception artistique n’est établi.

## Restauration des deux entrées imposées

[Plan exact](replay-inputs/restoration-map.json). Depuis une copie de travail isolée ; cette restauration n’a pas été exécutée :

```sh
mkdir -p /workspace/wewa-assets/work-in-progress/rear-sns-opposite-seat-rim-v1/previews
cp creative/research/motorcycle-source-dependencies-publication19-sns-opposite-rim-v1/replay-inputs/opposite-rim-preview-render-checkpoints.json /workspace/wewa-assets/work-in-progress/rear-sns-opposite-seat-rim-v1/previews/render-checkpoints.json
mkdir -p /workspace/wewa-assets/render-raw/material-lighting-review
cp creative/research/motorcycle-source-dependencies-publication19-sns-opposite-rim-v1/replay-inputs/opposite-rim-neutral-graycard-original.exr /workspace/wewa-assets/render-raw/material-lighting-review/rear-sns-opposite-seat-rim-v1-neutral-lighting-graycard.exr
```

| Copie exacte | Octets | SHA256 |

| --- | ---: | --- |

| [opposite-rim-preview-render-checkpoints.json](replay-inputs/opposite-rim-preview-render-checkpoints.json) | 7779 | `5db67e8118077c3d2049c293538fd6c06f96a300b25308a3f6c4a539d3efd41f` |

| [opposite-rim-neutral-graycard-original.exr](replay-inputs/opposite-rim-neutral-graycard-original.exr) | 38158 | `9b491fdf243d609c41b48d704b50a7bbaaf3c00eeba044a9edb7ce159f98f507` |

Aucun modèle, ancien gel, registre global ou Git modifié. Aucun constructeur, checker, rendu, export ou ouvertureBlender exécuté. Les29 fichiers des cinq auditsSource19 antérieurs restent byte-identiques. Cette lecture statique ne prouve pas une reprise complète sur un environnement vierge et ne vaut aucune réception artistique ou mécanique.
