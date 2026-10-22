# Repères natifs et relations d’assemblage — dossier v1

**38 entrées existantes : 38 natifs et 38 GLB lus**, dont quatre pièces historiques d’admission et cinq entrées de repose-pieds en annexe. Aucune nouvelle géométrie, pose montée, transformation source, sauvegarde Blender, mise à l’échelle ou fusion de variante. Des fichiers manquants ont uniquement été restaurés depuis les blobs Git épinglés ; aucun staging ni changement de références Git.

Les dispatchs précis sont ceux du coordinateur, dans l’objectif de finition autonome autorisé par l’utilisateur. Les codes de pièces, coordonnées et hypothèses de placement ne sont ni des mesures OEM ni des valeurs fournies par l’utilisateur. Voir `provenance-and-authority-note.json`.

## Lire les données

- `parent-native-inventory.json` : 34 parents/compléments de base, chemins canoniques, SHA256 natif/GLB, boîtes utiles, repères et points/axes sémantiques. Les valeurs exactes décrivent les fichiers ; les dimensions physiques restent estimées.
- `native-coordinate-read.json` et `export-coordinate-read.json` : matrices complètes par objet/nœud, origine objet, hiérarchie, géométrie évaluée et limites. Les constructions cachées et le plan de studio sont distingués des maillages utiles.
- `relative-relations.json` : relations documentées par photos, conventions d’auteur et inconnues restantes. Les matrices de montage entre ces parents restent nulles : elles n’ont pas été fabriquées à partir d’un simple voisinage de boîtes.
- `intake-native-coordinate-read.json`, `intake-export-coordinate-read.json`, `intake-mouths-world.json` : quatre collections dédiées d’admission, avec coordonnées des embouchures et axes en world natif et glTF.
- `intake-relative-chain-and-coordinator-hypothesis.json` : chaîne historique culasse–isolant–manifold et évaluation numérique séparée de l’hypothèse du coordinateur.
- `parameter-snapshots.json` : paramètres de construction conservés comme preuves de lecture ; aucun paramètre source modifié.

Les unités natives lues valent un mètre (`scale_length=1`). Pour les exports contrôlés, conversion **Blender(x,y,z) → glTF(x,z,−y)** ; ce changement de base ne constitue pas une pose sur la moto. Les boîtes évaluées correspondent à cette conversion, sous les réserves du kick signalées dans les rapports de comparaison s’il y a lieu.

## Origines et axes importants

Toutes les coordonnées ci-dessous sont en mètres dans le **repère natif de la pièce**, sauf mention world. Une origine objet nulle ne signifie pas que deux pièces sont déjà montées ensemble.

| Groupe | Repères natifs utiles | Relation effectivement étayée / limite |
|---|---|---|
| P19 carbu haut/bas/cuve | Haut : admission Z, col moteur z=−0,032 ; barillet X à y=0,z=−0,017. Bas : X autour de y=0,z=−0,014. Cuve : bouche x=0,040,y=0,z=−0,014. | Même photo JV581204/BM125 ; continuité et joint visibles. Conventions d’auteur proches, sans calage métrique. Stations bas/cuve séparées nominalement de 3 mm et centres haut/bas décalés de 3 mm en Z : ce ne sont pas des jeux mesurés. **Conserver leurs coordonnées relatives sous une transformation commune** lors d’une future revue, plutôt que recentrer chaque pièce indépendamment. |
| P19 cap/boot câble/coude | Cap et petit boot : Z. Coude : extrémité (0,0,0) tangent −X ; autre extrémité `[-0.023,0.030,0]` tangent +Y. | Topologie cap–boot–coude visible sur le même carbu ; aucun raccord rigide chiffré ni routage de câble reçu. Petit boot câble distinct du gros boot d’air P20. |
| P14 sélecteur | Bras : X toe−/heel+, Y projection, Z sortant ; clairance centrale axe Z à (0,0,0). Moyeu : axe Z, z=0…0,026, fente vers +Y. Oreilles : convention héritée ; tête axe X à y=0,018,z=0,0115. | Source opposée marquée JZ561415 ; racine, portée, caoutchoucs et clocking restent non calibrés. Aucun bras ou moyeu à refaire. |
| P14 kick | Pivot moteur world natif ≈`[-0.170,0.322,-0.674]`, axe world −X. Pivot de repli ≈`[-0.210,0.331,-0.667]`, axe world −Z à l’état natif lu. | Sept pièces et deux datums restaurés à l’identique. Les axes locaux et matrices exacts sont dans le JSON/contrat ; les amplitudes 90°/60° sont des plages d’inspection estimées, pas des butées physiques. Aucun ancrage au moteur courant certifié. |
| P15 pédale | Bras : pixel (178,159)→origine, échelle 0,00063 m/px ; ce point est une zone de coude, pas un pivot reçu. Tube de pivot axe Z ; œil de languette `[0,-0.005,0]`, axe Z ; pad normal Z. | Sources PF161002/PF161001 apparentées ; pièces séparées et non placées. Origines de revue différentes. |
| P15 tige/chape | Tige droite X : 0…0,490. Chape : entrée selon X à l’origine, œil selon Z à `[0.020,0,0]`. | Topologie visible mais terminaison de tige encore lisse ; filetage/cintrage et emboîtement non documentés. Œil chape Ø6 vs languette Ø9 nominaux : aucun coaxial imposé ni adaptateur inventé. |
| P17 latérale | Fût X ; pivot `[-0.024,0,0]`, axe Z. Pied courbe commence vers x=0,225 ; fût finit x=0,245. | Deux vues JA113202 apparentées ; recouvrement nominal d’auteur de 20 mm, pas une soudure ou une coupe ajustée. |
| P17 centrale | X latéral projeté, Y haut, Z profondeur ; pivot tube axe X passant par `[0,0.290,0]`. Arbre séparé axe Z, longueur 0,112. | Même source PF113224 pour cadre et bras opérateur ; projection commune estimée, pas de transformation de soudure reçue. Ø14/Ø14 arbre/alésage nominaux sans qualification de jeu. |
| P18 grandes parois | LH : origine photo (350,550), échelle 0,00044, profondeur −Z de 58 mm. RH : même choix numérique mais photo indépendante, profondeur −Z de 68 mm. | **LH JE541038 et RH PF54100? sont deux donneurs BM150 conditionnels, pas une paire prouvée ni un moteur RDC125.** Ne pas superposer leurs origines, les mirer ou les fusionner pour fabriquer un raccord. |
| P18 plages supérieures | Plages XY, normal Z ; origines/photos différentes des vues frontales des grandes parois. | Aucun datum commun calibré entre plages, parois, culasse et couvercles. L’égalité des axes numériques ne prouve pas la même direction physique. |
| P20 airbox/boot | Boîte : origine photo (365,500), bouche ronde `[0.018,0.160,-0.036]`, axe +Y. Boot séparé : axe X, coupes de revue x=±0,030. | Même galerie physique PF581003/BM125–150, donc sortie/boot documentés ; signe, roulis, recouvrement et rétention masquée non reçus. Diamètres estimés ne constituent pas un fit. G4 airbox antérieur reste ouvert. |
| Repose-pieds | Supports avant PF113000/PF113001 : +X vers extrémité, datums isolés. Caoutchouc : bouche x=0, axe +X. Supports passager PF113002/PF113003 indépendants. | **Ils existent déjà.** Ni miroir LH/RH ni insertion du caoutchouc à l’origine imposés. Importer les collections/maillages finaux, pas les cutters cachés ou le plan de studio. |

## Admission historique : raccord world natif existant

Le `build.py` de l’isolant calcule son datum depuis le datum de culasse existant. Le manifold utilise ensuite `datum_isolant @ T(0,0,0.0052)` : épaisseur 4 mm + jeu d’auteur 1,2 mm. C’est une relation **exacte entre candidats historiques**, dont les valeurs physiques et l’applicabilité restent conditionnelles. Chaque corps est parenté à son propre datum libre ; il n’est pas directement parenté à l’objet culasse. Ne pas réappliquer une deuxième fois le datum de culasse à ces géométries déjà positionnées en world natif.

Bouche du manifold **52JV0180**, transformée depuis son centre local `[0,0,0.040]` par sa matrice native réellement ouverte :

- Centre world Blender : **[0,024999996647 ; 0,217740789056 ; −0,395996332169] m**.
- Axe sortant unitaire world : **[−0,000000108613 ; 0,939692676067 ; 0,342019975185]**.
- Centre world glTF : **[0,024999996647 ; −0,395996332169 ; −0,217740789056] m**.
- Rayon nominal du passage 12,5 mm ; ces valeurs sont celles du candidat conditionnel, pas une mesure constructeur. Marche historique 25/22 mm avec la culasse toujours non reçue.

Le manchon PF581402 et la bande DP101198 restent **isolés**. Leurs embouchures/axes dans leur scène ne sont pas des ancrages sur la moto. Le sens manifold/carbu du manchon reste inconnu ; les lèvres nominales et l’interférence documentée de 0,6 mm entre bande et diamètre simple de manchon empêchent de certifier une emboîture sans preuve. Le petit connecteur carbu d’environ 5,5 mm n’est pas ce manifold.

L’hypothèse du coordinateur `X→−Z,Y→−X,Z→+Y`, origine `[0;0,285;−0,44]`, place le col carbu local `[0,0,-0.032]` en `[0;0,253;−0,44]`. Écart au centre manifold : **61,68 mm**, dont **58,97 mm transversalement** et 18,08 mm selon son axe ; angle des axes ≈20°. Ce n’est donc pas une connexion coaxiale validée. Aucune correction de pose n’est appliquée.

La seule contrainte proposée pour la prochaine intégration est paramétrique : `R_carbu·[0,0,−0,032]+t_carbu = bouche_manifold + λ·axe_manifold`, avec axe carbu correspondant, **λ et roulis non choisis**. Appliquer au préalable la même transformation d’assemblage que celle éventuellement ajoutée à la culasse par la scène actuelle ; ne pas confondre world natif historique et world final du véhicule.

## Restauration, intégrité et limites

`intake-exact-restoration.json` et `requested-parent-exact-restoration.json` enregistrent les fichiers exacts restaurés depuis le commit `7d93dfa5a248a21343cd9f2ee70f3abc4591c302`, avec SHA1 de blob Git et SHA256. Aucun fichier existant écrasé ; aucun rebuild, staging ou changement de référence. L’isolant v1 est une dépendance liée du manifold, conservée sans adaptation. Kick et deux exports de supports ont aussi été restaurés pour compléter le relevé initial ; leur absence locale temporaire n’était pas un manque de géométrie à fabriquer.

Les inconnues restantes concernent le calage entre familles, les variantes, l’insertion, les contacts et les amplitudes physiques. Elles ne justifient pas de refaire les gros parents. Aucun G8, fit OEM ou lot fini déclaré. Ce dossier privilégie leur intégration et leur confrontation aux sources avant tout autre micro-enfant.
