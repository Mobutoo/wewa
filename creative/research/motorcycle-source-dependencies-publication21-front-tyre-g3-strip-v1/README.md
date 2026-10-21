# Source21 — front-tyre-g3-strip

Base métadonnées45 `7741d73f54782dc5746b715b3c21f01279dbd9d1`. Aucune coupe ni sélection Source21. [Rapport](report.json), [fermeture](source-closure-v1.json), [entrées utiles](stable-recipe-inputs-v1.json) : **33 paires SHA/octets vérifiées**, **19 entrées stables**. Les tables historiques des rapports ne sont pas des manifestes vivants.

## construction reelle

build_local_strip_v1 lit le vrai BLENDv1 (42Mo, déjà existant), parameters/local-strip-parameters et junction_field, avec NumPy de Blender. Il append l’objet natif nommé et reconstruit localement sa grille autour des lèvres existantes. Il retire le grossier champ transversal seulement de la référence triangulaire, conserve l’interpolation de couronne/longitudinal, applique l’unionp4 et découpe les voisins sur leurs vrais bords. Aucun ancien BLEND junction/local-grid rejeté n’est consommé, aucun CSG ou texture/photo requis pour G3.

## empreinte et invariants

Le maître335788…/GLBb5eb… est une correction du mêmeID. Empreinte actuelle explicitement élargie aux deux anciennes cellules angulaires et aux rails de couronne |X|≤32,40494mm ; ne pas la rebaptiser ancienne bande limitée4,2–7,8mm. Le code protège les coordonnées anciennes hors chevauchement et tous lesX. Selon les preuves source/GLB fournies :560anciens triples radiaux changés dans le chevauchement,148540triples anciens conservés ; rayonmax Float64 et largeur exacts, AABBZéchantillonnée−1,298/+1,311µm distincte. Aucun aplatissement pour forcer l’ancien contrat6bornes, aucun recalcul de ces résultats ici.

## source normales et limites

MaîtreG3 1109920triangles, UV/normales propres et nouvelle étude de forme ; normale fraîche mélangée aux anciennes entrées dans la transition déclarée. La sérialisation des normales est quantifiée ; on ne prétend pas leurs bytes identiques aux anciennes entrées. Les anciens20µm échantillonnés restent non atteints/non reçus, pas une toléranceOEM corrigée en silence.

## omission numeric baseline

Le renderer gris courant lit obligatoirement diagnostic-gray-baseline.json, hors33. Ce JSON réel3338octets SHAff51f32a4078119b8b3facb78c82bb4f52cbc5cd8985ecfadfa37e04e186f50d fournit seulement le témoin numérique d’exposition/caméra ; son ancien PNG, EXR, BLEND4084268f et GLB286c990d cités ne sont pas chargés. Entrée explicitement listée, gel33 inchangé. Les autres trois vues utilisent le maître courant et sa lecture grise, pas ce vieux modèle.

## reprise depuis maitre

Les rendus courants ouvrent le maîtreG3 exact et les rapports/preflights fournis. Pas de mire, HDR ou CP privé initial ; checkpoints/report sont des sorties publiques. Rendre à nouveau ne demande pas de rebâtir la forme depuisv1. Une reconstruction peut changer les octets et demande une nouvelle revue ; aucun clean replay ou contrôle de sommet exécuté ici.

## diagnostics et hors perimetre

Les bornes refusées/local-strip-bounds-diagnostic et les lectures propres présentes dans33 sont conservées comme preuves du gel, pas toutes des inputs initiaux du builder. Les modèles de jonction/local-grid rejetés et leurs archives, v2atlas, matièrev3 f8d22e/7e75 non gelée, bake/comparaisons en cours et futurs96 sont hors de cet audit. Aucun trait de mouleOEM, matériau de caoutchouc, ajustement, réception artistique ou iPhone déduit.

Aucun builder/checker/rendu/export ou Blender lancé ; aucun modèle, ancien gel, audit antérieur, registre ou index modifié. Aucun replay propre, ajustement mécanique/OEM, iPhone ou réception artistique revendiqué. Aucun duplicata de modèle ni pixel documentaire privé ajouté.
