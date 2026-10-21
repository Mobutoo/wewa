# Capuchon de bougie — candidat apparenté DD111048

`MOTO-ENGINE-SPARK-CAP-001` représente l’enveloppe moulée et le petit contact métallique visible dans son port court. Le fil HT, son trajet, la bobine et la mécanique électrique cachée restent distincts et non fabriqués ici.

Le [plan de fabrication](../../../creative/research/engine-spark-cap/fabrication-plan-v1.json) attribue deux photographies physiques StockNuts. La quatrième vue, téléchargée mais non ouverte par l’auteur de la recherche partagée, a été effectivement ouverte par le fabricant : elle montre la pièce retournée, la bouche du gros fût et la ligne de moulage. Le rapport partagé figé n’a pas été réécrit. Aucune de ces vues n’apporte de cote ni une installation exacte RDC.

Formes retenues : fût large à lèvre annulaire, col rétréci avec transition raccordée, port transversal muni d’un rebord, deux cavités visibles ouvertes et petit relief métallique de contact. La ligne de moulage est un faible relief physique original dont la hauteur reste estimée. Le lettrage illisible n’est pas inventé. La matière sombre utilise un PBR constant original ; aucun pixel photographique, grain mesuré ou normal map automatique n’est ajouté.

Toutes les dimensions et les sections sont des hypothèses bornées dans `parameters.json`. La coque hérite de la matrice inchangée de la bougie candidate ; l’orientation du port vers +Ylocal est conditionnelle et ne décrit pas un trajet HT connu. Les profondeurs internes sont simplifiées et aucun mécanisme électrique complet n’est déduit du petit contact photographié. Son relief hélicoïdal est une estimation visuelle, sans filetage mécanique certifié.

Source `engine-spark-cap-v1.blend`, collection `WEWA_ENGINE_SPARK_CAP`, datum `Spark cap inherited unchanged provisional plug datum`. Objets : `Molded spark cap body - conditional candidate` et `Visible short-port metallic contact - section estimated`. Les sources liées de culasse et de bougie ne sont pas exportées. Le GLB comporte uniquement les deux volumes et le datum.

Reconstruction avec Blender4.3.2/un thread : `build.py`, `check_triangulation.py`, puis `check_export.mjs` depuis la racine et `check_interface.py` en lecture seule. Le volume des quads hélicoïdaux du contact diffère d’environ4,08×10⁻⁵ du calcul BMesh : la référence d’export est donc le volume des vraies loop-triangles du rendu, sans relâcher la tolérance ni modifier les buffers. Les deux diagnostics sont conservés. Le corps moulé triangulé n’a pas cette différence.

Les vues gris/reflets/PBR et le contexte précèdent le gel ; chaque finale96 garde un checkpoint source/configuration/PNG/EXR. Les distances échantillonnées et l’absence de croisement de surfaces candidates ne certifient ni étanchéité, ni portée de contact, ni montage réel. Aucun LOD mobile ou essai physique iPhone reçu.
