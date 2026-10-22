# Revue numérique indépendante des poses powertrain v6

**30 contrôles arithmétiques passent ; aucun défaut de matrice, d’axe ou de station nominale détecté dans les poses examinées.** Ce résultat ne certifie aucun emboîtement, fonction de carburateur, étanchéité, collision de matière ou montage reçu.

Dispatch du coordinateur dans l’objectif autonome autorisé par l’utilisateur. Les poses et valeurs v6 restent des hypothèses de coordination ; les cotes des candidats sont des estimations de leurs sources. L’ancienne hypothèse carbu d’origine `[0,.285,-.44]` et d’angle `[0,90,90]` n’est pas utilisée.

## Méthode et portée

Lecture du plan v6 et du script de construction par analyse Python, sans les exécuter. Vérification que leurs dictionnaires de rotations/translations concordent. Calcul indépendant des matrices Euler XYZ Blender `Rz·Ry·Rx`, des points/axes et des boîtes depuis les JSON natifs figés. Les transformations agissent sur les coordonnées world natives des parents, sans recentrage implicite.

Douze parents d’admission sont examinés. Les quatre collections historiques ont été ouvertes séparément pour lire leur `instance_offset` : tous quatre nuls. Les huit collections d’objets sélectionnés sont créées à offset nul par le script v6. Aucun chargement de whole72, rendu, changement de pose ou sauvegarde source. Aucun Git ni fichier partagé modifié.

Les grandes parois donneuses LH/RH ne figurent pas dans cette liste v6 de 72 parents : aucune pose ou paire de carters moteur n’est validée ici. La coque d’airbox, elle, est incluse dans l’audit.

## Axes et stations

`M = [0.024999996647, 0.217740789056, -0.395996332169] m` est la bouche du manifold natif conservé. `A = [0, cos20°, sin20°]` est l’axe idéal choisi pour la revue. L’axe natif diffère seulement par l’arrondi numérique stocké, consigné dans `report.json`.

- Carbu `[0,70,90]` et manchon/collier `[-70,0,0]` envoient leur +Z vers +A.
- Les trois corps carbu partagent exactement la même rotation et la même translation `M+71 mm·A`, préservant leurs relations natives.
- Le boot d’air envoie son +X vers −A, donc son bout évasé vers le carbu.
- La sortie +Y de la boîte est orientée vers −A, donc vers le boot/carbu. Le centre de sortie est coaxial dans ce repère nominal.
- Le manifold et l’isolant world natifs sont conservés à l’identité dans le plan : pas de seconde application du datum de culasse.

| Élément / plan nominal | Station sur A depuis M |
|---|---:|
| Bouche manifold | 0 mm |
| Bouche arrière du manchon, locale −Z | 2 mm |
| Bords de largeur du collier | 14,5 à 24,5 mm |
| Centre manchon/collier | 19,5 mm |
| Bouche avant du manchon, locale +Z | 37 mm |
| Col moteur du carbu, local z=−32 mm | 39 mm |
| Origine commune carbu | 71 mm |
| Lèvre nominale du pavillon carbu | 89,5 mm |
| Bout évasé du boot côté carbu | 91,5 mm |
| Bout de revue du boot côté boîte | 151,5 mm |
| Sortie ronde de la boîte | 153,5 mm |

Les quatre séparations nominales manifold→manchon, manchon→col carbu, pavillon→boot et boot→boîte valent **2 mm**, sans décalage transversal significatif. Ce sont des jeux entre centres/plans de construction, pas des spacers fabriqués ni des dégagements minimaux de toutes les surfaces.

Cap, entrée et coude : les centres des plans nominaux coïncident, avec axes correspondants. Le siège du cap rejoint la coupe de barillet `[-.048,0,-.017]`, le boot câble commence à la couronne du cap et le coude à la bouche du boot. Ces trois raccords nominaux sont **sans jeu de 2 mm** ; aucune profondeur de filetage/serrage n’est validée.

## Réserves numériques à conserver

1. **Cuve et gravité** : l’axe +X de la cuve est incliné de 20° par rapport à la gravité −Z. Niveau liquide, flotteur, roulis et attitude physique de ce modèle non qualifiés.
2. **Enveloppe complète du manchon** : ses appendices portent sa plage axiale à **M−5,5 … M+45,5 mm**. Ils dépassent donc les plans de bouche nominalement séparés de 2 mm. Cela ne prouve pas une collision, mais interdit de présenter ces jeux comme une absence générale de contact.
3. **Manchon/collier rigides** : ID collier 45 mm ; diamètre simple du manchon 45,6 mm, cordons jusqu’à 47,6 mm. Conflits diamétraux nominaux **0,6 mm et jusqu’à 2,6 mm** ; le cordon central se trouve dans la largeur du collier. Aucune déformation, compression, retouche de lèvre ou qualification de serrage.
4. **Rôles des bouts du manchon** : la pose place le bout local −Z/Garage vers le manifold et +Z/Matriz vers le carbu. C’est une sélection spatiale provisoire ; le sens physique et le même moule ne sont pas établis. La petite ouverture arrière et les lèvres ne sont pas ajustées pour forcer un montage.
5. **Relations carbu conservées, non reçues** : les 3 mm entre stations nominales bas/cuve et l’offset natif haut/bas restent inchangés. La séparation positive des boîtes natives bas/cuve est d’environ **0,3144 mm selon leur X commun**, distincte des 3 mm de stations de construction. Aucune de ces valeurs n’est une mesure de joint.
6. **Variantes et pièces restantes** : UG5/52JV0180/JV581404, JV581204/BM125 et PF581003/BM125–150 restent conditionnels entre eux et vis-à-vis du RDC125. Le petit connecteur carbu n’est pas le manifold. Les fittings, ajusteurs, câble, clips, fixations et routes de durites non placés restent explicites ; les centres cap/entrée/coude ne les remplacent pas.

## Boîtes et collisions

Les boîtes source transformées donnent **19 recouvrements AABB possibles**. Un test de séparation des boîtes orientées en écarte **9**, notamment plusieurs faux positifs dus à la rotation commune. Les **10 restants** comprennent des plans en contact et des boîtes qui se chevauchent ; ils ne prouvent pas une pénétration de triangles ou de matière dans les pièces creuses.

Les paires à garder pour la revue locale incluent haut/bas carbu, manchon avec carbu/manifold, boot avec coque de boîte et manchon/collier. Les contacts cap/entrée/coude sont également listés. Le conflit dimensionnel rigide collier/manchon est décrit séparément ; aucune conclusion générale « sans collision » n’est donnée.

## Fichiers

- `report.json` : matrices, 30 contrôles, axes, stations, jeux et réserves.
- `obb-refinement-and-full-envelope.json` : 19 paires AABB, séparation OBB et extensions réelles des boîtes du manchon.
- `native-bounds-input-snapshot.json` : limites et ports source exacts consommés.
- `collection-offsets.json` : lecture indépendante des quatre collections historiques.
- Snapshots du plan, du builder et de son inventaire : révision auditée préservée même si la coordination avance.
- `delivery-frozen.json` : empreintes de ce dossier uniquement ; aucun ledger vivant inclus comme fichier immuable.

Aucun nouveau modèle actif. Aucun ancien gel, source, métadonnée racine ou pose v6 modifié. Aucun G5/G8 ou lot terminé déclaré.
