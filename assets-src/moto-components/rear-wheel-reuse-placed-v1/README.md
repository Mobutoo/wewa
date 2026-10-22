# Rear wheel reuse placed v1 — ADD ONLY pour v17

Quatre parents existants, sept meshes réels, zéro nouvelle géométrie. L'audit `rear-wheel-coverage-audit-v1` reste gelé inchangé. Le kit réutilise exactement les sources historiques ; G1 et G5 restent non reçus, variantes et dimensions estimées.

**Entrée main : `add-only-fragment.json`.** Ajouter seulement ses quatre lignes `add_only`, ou lier la collection `REAR_WHEEL_REUSE_ADD_ONLY_V1` du petit `rear-wheel-add-only-v1.blend`. Ne pas faire les deux. Le fichier Blender contient uniquement les quatre nouveaux parents ; le contexte des rendus n'y est pas sauvegardé. Aucun nouveau GLB ni texture copiée : les quatre GLB originaux sont référencés avec leurs SHA.

| Parent ajouté | Source exacte, relative à `assets-src/moto-components/` | Calage borné |
|---|---|---|
| Porte-couronne LH | `front-completion-p21-front-material-front10-v5/carrier-material.blend` | Axe local Z vers X gauche. Dos source Z=−3 mm posé à X=42 mm, soit 1 mm de séparation de revue avec l'enveloppe gauche de la jante X=41 mm. Pas de roulement ni d'entretoise inventé. |
| Axe arrière | `front-completion-p23-rear-axle-v2/rear-axle-gray.blend` | Longueur native inchangée 280 mm, centrée sur X=0 : tête provisoirement LH à X=140 mm et pointe à −140 mm. Axe local Z vers −X. Le choix du côté et le calage angulaire de la bouche restent estimés. |
| Tendeur LH | `front-completion-p23-lh-adjuster-front10-v1/lh-adjuster-material.blend` | Œil natif à l'origine sur l'axe de roue, station X=123,5 mm. Les joues à ±7,6 mm encadrent l'enveloppe latérale native du bras X=122 mm. Tige source −X orientée vers l'arrière global +Y. |
| Tendeur RH | `front-completion-p23-rh-adjuster-front10-v2/rh-adjuster-material.blend` | Source RH indépendante, rotation propre sans miroir ; œil sur le même axe à X=−123,5 mm. Tige vers +Y. |

Toutes les matrices 4×4 sont dans le repère monde Blender demandé : avant `[0,−0.42,−0.74]`, arrière `[0,0.865,−0.74]`, empattement 1,285 m. Aucune mise à l'échelle. L'axe arrière et les deux yeux sont coaxiaux au repère de roue ; cela ne certifie pas la pile mécanique, les tolérances, la variante courante ou le contact avec les fixations absentes. Incertitudes de pose explicites : ±6 mm sur station latérale, ±3 mm sur centre de roue, roulis ±8° des supports ; orientation de bouche de l'axe non documentée. La petite précision décimale des matrices sert à reproduire la pose, pas à revendiquer une mesure.

Dimensions de travail historiques : axe 280 mm (plage 240–360), rayon de tige 7,5 mm (6,5–8,5) ; tendeur LH longueur de corps 78 mm (60–100), séparation des joues 12 mm (8–18), rayon d'œil 10 mm (8–12) ; tendeur RH corps 74 mm (50–95), rayon d'œil corrigé à 10 mm ; porte-couronne rayon extérieur 65 mm (55–80), hauteur 38 mm (28–50). Les racines de tige ouvertes et écarts de revue de 2 mm sont conservés, sans soudure ou lien caché ajouté.

## Exclusions justifiées

- Tige d'actionnement de frein : source prête, mais liaison au levier arrière et extrémités montées non documentées. Ne pas la poser comme raccord caché ni lui substituer le tirant anti-couple JW122004.
- Came/levier avant : pas de mesh source prêt trouvé. Axe avant DJ151041 : branche UG/Pulsar explicitement non confirmée pour cet assemblage, pile/côté de fixation inconnus ; exclu.
- Revers de porte-couronne v8, lobe de cush et motifs de chaîne : études indépendantes, pas un second corps à superposer ni des répétitions installées établies.
- Flasques avant/arrière, jantes, valves avant, carters de chaîne : déjà présents dans v16. Aucun doublon ajouté.

`duplicate-audit.json` constate que les quatre sources ajoutées sont absentes des liens directs et imbriqués des 128 parents v16, et que les carters et flasques existants restent uniques. Aucun ancien parent remplacé ni retiré.

## Deux lectures grises rapides

- `gray-lh-inspection.png` : vue de contrôle LH, **carters de chaîne masqués uniquement dans ce contexte d'inspection** pour lire le porte-couronne. Main les conserve dans l'assemblage final.
- `gray-rh-context.png` : vue RH avec les deux carters de contexte.

640×450, quatre échantillons CPU/deux threads, EXR float32 et PNG, sans nouveau 96 ni rendu whole. Le premier cadrage trop serré est conservé dans `rejected-gray-crop/`. Les sources et matrices ADD ONLY sont identiques après correction du seul cadrage. Les deux lectures sont des contrôles visuels de réutilisation, pas une réception G1/G5/G8.

`native-datums.json` et `placed-native-check.json` sont les lectures effectives des objets évalués, noms sélectionnés, enveloppes et repères. Les guides/studios ne sont pas sélectionnés. Une ancienne bibliothèque de pneu guide absente lors de la lecture historique du flasque avant n'est ni restaurée ni incluse ; ce flasque sert seulement à confirmer le parent déjà présent et aucun nouvel objet avant n'est ajouté.

`frozen-outputs.json` fixe les octets livrés. Aucun fichier source, catalogue, racine, board ou Git modifié.
