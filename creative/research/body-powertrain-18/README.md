# Recherche des lots 15, 17 et 18 — structure, moteur extérieur et habillage

Recherche documentaire du 20 octobre 2026. **Aucun modèle fabriqué et aucun passage artistique reçu.** Le [rapport par pièce](report.json) décompose 20 composants avec vues réellement examinées, références conditionnelles, inconnues et prochaine capture utile. Les originaux restent hors dépôt public, dans `/workspace/wewa-assets/references/body-powertrain-18/` ; [archives.json](archives.json) conserve leurs URL, empreintes et état d’inspection.

La cible reste la Boxer 125 HD présentée pour la RDC, millésime inconnu. WEWA sera le marquage original du jeu. Les photographies constructeur/vendeur et leurs inscriptions ne deviennent ni textures ni décalques réutilisables.

## Ce qui est maintenant exploitable

| Lot | Pièces | Base observable pour le fabricant | Ce qui empêche encore une restitution métrique fidèle |
|---|---|---|---|
| 15 | Garde-boue avant | Coque rouge bombée, descente arrière, bavette noire, fixations et guide de câble séparés | Dessus/dessous, section à la couronne, épaisseur et entraxes |
| 15 | Garde-boue arrière | Coque arquée sous selle, descente de plaque, bavette et petit réflecteur distincts | Raccord sous selle, forme intérieure et attaches cachées |
| 15 | Cadre et bras oscillant | Colonne, liaison supérieure, berceau, sous-cadre triangulé ; bras à faces larges et tendeurs gauche/droit | Sections réelles, coordonnées des pivots, entre-bras, soudures et lumières d’axe |
| 17 | Moteur extérieur | Ailettes noires, **carters droit et gauche différents**, joints, bossages, bouchons et interfaces mécaniques | Profils perpendiculaires, largeur des pièces, contours et reliefs de fonderie |
| 17 | Échappement | Collecteur et silencieux à droite, corps noir, petit pare-chaleur clair, attaches et sortie séparés | Coudes, section du silencieux, diamètre de sortie et identification exacte |
| 17 | Repose-pieds, pédales, kick et béquilles | Patins conducteur striés, supports passager triangulés ; pièces de pivot/retour documentées par éclatés | Gros plans du montage RDC, dimensions et positions fonctionnelles |
| 18 | Réservoir et caches | Épaules du réservoir, retour inférieur et raccord selle ; caches latéraux avec lèvres/pions/vis | Dessus et dessous du réservoir, sections, position du bouchon, dos des caches |
| 18 | Selle et porte-bagages | Housse/embase/appuis dissociés ; plateau arrière avec branches triangulées et attaches | Variante exacte de housse, dimensions par station, diamètres/sections et entraxes |
| 18 | Ensemble arrière | Feu rouge large à bas arrondi, clignotants ronds, support, plaque et réflecteur distincts | Profondeur des lentilles, prismes, arrière des corps et fixations |

L’arceau noir devant le moteur est une **protection rapportée** : il ne doit pas être confondu avec le cadre. Le kick chromé devant le carter droit n’est pas une nervure de fonderie. La tige de frein et le tirant de réaction arrière ne sont pas la même pièce.

## Sources vues et portée

- [D01 — constructeur RDC](https://www.bajajauto.com/fr-cd/bikes/boxer-125hd) : les huit rotations sont examinées, du profil droit à l’arrière puis au profil gauche, ainsi que les gros plans moteur, selle et protection. Elles donnent des contours, **aucune caméra calibrée ni vue supérieure orthogonale**.
- [D04 — catalogue BM125 UG](https://motobro.ua/files/Boxer_BM_125_UG_Provisional_SPC_%282%29.pdf) : tables et éclatés ciblés ; le rapport utilise les **numéros de feuilles PDF à partir de 1**. Les variantes 4/5 vitesses restent distinctes.
- [D15 — catalogue BM150, mars 2012](https://reypiston.com/wp-content/uploads/2024/04/Boxer-BM150-SPC.pdf) : comparaison de références et d’assemblages. Ce BM150 ne certifie aucune pièce de la 125 HD RDC actuelle.
- [N01 — Crosland, JV191001](https://www.croslandrepuestos.pe/asiento-de-boxer-lineas-jv191001/p) : annonce BM125/BM150 et trois photos réellement examinées, dont **le dessous de selle complet** : nervures, agrafage, attaches et sept appuis caoutchouc visibles.
- [N02 — Bajaj Matriz, JV191001](https://bajajmatriz.com/producto/asiento-completo-moto-boxer-150-ug-bajaj) : annonce BM150 UG ; vue trois quarts de la housse et du grain. Pas une preuve de finition RDC.
- [N03 — silencieux 36PF0025](https://partonwheels.com/product/kit-silencer-without-shield-for-boxer-bm-150-bajaj/) : page et deux images vues, application annoncée BM150 2011–2013. Photos à aspects différents, sans plan coté ; leur montage actuel RDC n’est pas établi.

## Cotes utilisables, sans glissement de variante

La page RDC donne **2016 × 740 × 1134 mm**, un empattement de **1285 mm** et une capacité de **11 L**. Ce sont des propriétés de la moto ou de sa capacité ; elles ne donnent pas la largeur du réservoir, la longueur de selle ou les coordonnées du pivot de bras.

D04 donne notamment une durite `PF171803` désignée **L185**, une rondelle `39217924` **5,1 × 10 × 1 mm** et un joint de filtre UG de diamètre intérieur **59,6 mm**. Ces cotes concernent des pièces de **variante voisine**. Une autre ligne UG donne une rondelle de diamètre extérieur 9 mm. Aucune de ces valeurs ne permet de mettre arbitrairement tout le moteur ou le réservoir à l’échelle.

**Aucune nouvelle cote extérieure certifiée** de garde-boue, bras, cadre, carter, réservoir, selle ou rack n’a été trouvée. Les éclatés sont des indications d’assemblage, jamais des plans à mesurer à l’écran.

## Choix de variantes à conserver ouverts

1. D04 distingue `PF111103` et `PF111000` pour le cadre. Le second apparaît aussi en BM150 : numéro commun ne signifie pas millésime courant confirmé.
2. Garde-boue avant chrome, version ED peinte et bavettes ont des références différentes. La coque rouge RDC ne valide pas le groupe chrome.
3. D15 distingue des échappements avec/sans catalyseur et protection filaire. D04 donne `JV591009` ; la fiche BM150 ne remplace pas cette identification.
4. D04 cite la selle plate `JV191001`, D15 cite aussi la profilée `PF191000`. Les vues vendeur montrent des lignes embossées ; le visuel RDC paraît plus lisse. **Ne pas importer automatiquement ce motif de housse.**
5. Le feu complet D04 `PF401005` diffère de D15 `DF201138`. Une quantité de clignotant arrière droit imprimée « 2 » dans D04 reste inexpliquée ; les photos RDC montrent deux clignotants arrière au total.

## Captures suivantes, par ordre d’utilité

1. **Réservoir/bouchon** : dessus avec règle, face/dos et profils, puis dessous si accessible ; mesurer largeurs par station et raccord à la selle.
2. **Moteur** : profils gauche/droit à hauteur de carter, macros des ailettes, bouchons, vis et joints ; garder le repère d’échelle dans le plan observé.
3. **Cadre/bras** : vues moins occultées et mesures dans un même repère de la colonne, du pivot, des axes et des attaches moteur.
4. **Selle/rack** : dessus et dessous de la pièce exacte avec code, règle et points d’attache ; les nouvelles vues Crosland servent de comparaison conditionnelle.
5. **Feu arrière/garde-boue** : dos perpendiculaire et dessous, lentilles éteintes/allumées sans saturation, entraxes et raccords de support.
6. **Commandes basses/béquilles** : chaque côté et positions utiles, pivot/appui/ressort et jeux avec moteur/échappement.

Une seule pièce entre ensuite en fabrication détaillée après consolidation de G1/G2. Ce dossier prépare ce passage ; il ne clôt ni la calibration, ni la vérification moteur, ni la réception utilisateur.
