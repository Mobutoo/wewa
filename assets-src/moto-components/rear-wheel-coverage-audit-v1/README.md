# Audit court arrière / roues / transmission vs whole v15

V2 moteur terminé et laissé figé. Cet audit ne fabrique, ne pose, ne répète et n'exporte aucun nouveau composant. Il n'élargit pas le périmètre de fabrication. Aucun travail sur la source de réflecteur/phare.

`omissions-and-sources.json` est l'inventaire exploitable : sources et SHA actuels, objets exacts, fragments documentaires, repères natifs et ancres des parents v15. Les 19 sources candidates listées sont absentes des liens directs **et imbriqués** de v15 ; ce ne sont pas 19 nouvelles pièces physiques à empiler. Aucun de ces candidats ne possède une pose installée documentée : `global_matrix: null` est volontaire. Les matrices natives des objets sont des repères locaux, pas des poses véhicule.

| Groupe | Sources existantes recommandées | État et précaution |
|---|---|---|
| Porte-couronne arrière P21 | `front-completion-p21-front-material-front10-v5/carrier-material.blend` ; revers `front-completion-p21-reverse-front10-v8/carrier-reverse-material.blend` | Face et revers indépendants, pas un groupe assemblé validé. Éviter l'ancien matériau v3 tenu/rejeté pour revue. |
| Caoutchouc d'entraînement | `front-completion-p21-single-cush-front12-v2/cush-lobe-material.blend` | Un seul lobe prêt pour revue ; ce n'est pas une bague complète. Ne pas supposer le nombre ou les ponts. |
| Transmission P22 | `front-completion-p22-sprocket-v1/sprocket-gray.blend`, `front-completion-p22-pinion-rim-v1/pinion-rim-gray.blend`, `front-completion-p22-chain-motif-v1/motif-gray.blend` | Couronne 44T apparentée, bord 14T partiel, motif de chaîne unique ; pas de chaîne assemblée ni d'équivalence de variante. |
| Axe arrière | `front-completion-p23-rear-axle-v2/rear-axle-gray.blend` | Axe local +Z, ouverture latérale +X, coupe de revue ouverte. La variante `front-completion-p23-rear-axle-material-v2/material.blend` a une preuve de géométrie identique et seulement une préparation/aperçu matière ; ce n'est pas une seconde pièce. |
| Tendeurs LH/RH | `front-completion-p23-lh-adjuster-front10-v1/lh-adjuster-material.blend`, `front-completion-p23-rh-adjuster-front10-v2/rh-adjuster-material.blend` | Objets distincts indépendamment construits. Axe long local X, racine de tige ouverte et écart de revue de 2 mm : ne pas présenter ce jeu comme montage physique. |
| Plaque, tirant anti-couple, boulon, entretoise P23 | `front-completion-p23-endplate-front9-v1/endplate-material.blend`, `front-completion-p23-torque-arm-front10-v2/torque-arm-material.blend`, `front-completion-p23-torque-bolt-front10-v1/torque-bolt-material.blend`, `front-completion-p23-collar-outer-front12-v1/collar-material.blend` | Le tirant JW122004 n'est pas la tige d'actionnement de frein P15. L'entretoise est une peau extérieure à deux coupes ouvertes, pas un cylindre complet certifié. |
| Axe/colliers avant P24 | `front-completion-p24-axle-material-v1/material.blend`, `front-completion-p24-related-collar-front12-v1/front-collar-material.blend` | Absents également ; repères et variantes locaux, pas de pile montée certifiée. |
| Actionnement de frein P15 | `brake-actuation-rod-v1/child-candidate.blend` | Tige existante absente, différente du tirant anti-couple. Articulation, courbure terminale et course montées non résolues. La pédale de v15 ne la contient pas dans ses liens imbriqués. |
| Robinet, bouchon hexagonal | `fuel-tap-stepped-hex-cap-visible-v1/fuel-tap-stepped-hex-cap-visible-v1.blend` | Extérieur prêt pour revue locale. Donneur au titre Bajaj véritable distinct de l'autre robinet aftermarket : ne pas fusionner les identités. |
| Oreille avant de carter de chaîne | `chaincase-front-ear-root-v2/child-candidate.blend` | Candidat compact avec racine formée ; remplace l'interprétation d'oreille v1, ne s'ajoute pas comme seconde oreille. Coaxialité aux trous et fixation au parent non certifiées. |

Tous les chemins de la table sont relatifs à `assets-src/moto-components/`. Les chemins GLB existants et les noms d'objets sont dans le JSON ; aucun binaire n'est recopié ici.

## Déjà inclus : ne pas doubler

- Roues/pneus et jantes avant/arrière, flasque arrière DS151069, bras oscillant et deux demi-carters de chaîne sont des parents v15.
- Valve **avant** : `Valve rubber base - estimated`, `Valve stem - estimated`, `Valve dust cap - estimated` sont trois objets visibles (`hide_render=false`) de `WEWA_FRONT_RIM_EDITABLE`, déjà lié par v15. Même transformation globale que le parent `front-rim`.
- La valve arrière n'existe pas comme source distincte dans les catalogues/fragments et la jante arrière natifs inspectés. La valve avant ne prouve pas le montage arrière ; aucune valve arrière n'est inventée ici.
- Les objets de construction cachés dans les anciens fichiers ne deviennent pas des composants prêts du seul fait de leur nom.

## Poses documentées utiles à main

Les seules poses véhicule transmises sont les poses déjà déclarées par v15 dans `global_parent_anchors` : jante arrière T=(0 ; 0,8650000095 ; −0,7400000095), flasque arrière T=(−0,0520000011 ; 0,8650000095 ; −0,7400000095), rotation XYZ=(90 ; 0 ; −90) degrés ; carters de chaîne T=(0,1299999952 ; 0,8650000095 ; −0,7400000095). Ce sont des poses d'assemblage estimées, pas des mesures physiques. Le JSON conserve aussi jante avant, bras oscillant, pédale et réservoir, sans calculer une fixation absente de leurs sources.

Les candidats isolés nécessitent encore un calage sur ces parents, avec contrôle du côté, de l'axe, des coupes de revue et de la variante. Aucun groupe absent n'est déclaré « prêt à monter sans calage ». Les sources sont prêtes à être réutilisées pour ce travail ; aucun nouvel enfant détaillé n'est lancé.

## Lecture et gel

Lecture effective des catalogues/fragments, de 28 fichiers natifs ciblés, du tableau des parents v15 et de sa vue arrière trois-quarts. `native-source-read.json` conserve collections, objets, matrices locales et SHA. `catalog-candidates.json` conserve les fragments découverts, y compris les alternatives historiques exclues de la sélection finale. `frozen-audit.json` fige les résultats exacts. Pas de nouveaux tests géométriques, rendu lourd, changement de catalogue, racine ou Git.
