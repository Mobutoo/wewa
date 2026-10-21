# Bougie extérieure v2 — jonction analytique du chanfrein

La macro finale96 de v1 a révélé une bordure en marches sur la jonction cône/hexagone. La v1 et ses36 fichiers de revue restent intacts comme diagnostic. Cette révision remplace uniquement le maillage du corps métallique ; elle garde la rondelle, la céramique, la borne, tous les matériaux et les matrices du datum dans leur état précédent.

Le contour arrondi à six pans reprend les222 points YZ du corps v1. Pour chaque rayonR(φ), les stations X des limites de chanfrein sont calculées sur l’équation du cône. La boucle de raccord suit ainsi l’intersection, au lieu de former de petits paliers sur une grille de plans X fixes. Les limites mécaniques réellement anguleuses conservent une séparation de normales native ; aucune image, tangente ou normale exportée n’est retouchée.

`build-report-v2.json` documente les résidus de l’équation sur les vrais sommets, les écarts échantillonnés entre les deux surfaces et les signatures des trois autres pièces. `protected-export-invariants.json` compare leurs vrais accessors positions/normales/indices et tous UV présents, ainsi que matières et matrices ; l’identité est exacte pour ces trois pièces. Le budget triangulaire change uniquement dans le corps métallique.

Le capuchon69dc et la culasse head3 restent des bibliothèques de contrôle dans leurs poses fixes. `check_interface_v2.py` produit une nouvelle preuve contre ces sources ; il ne remplace pas les11 contrôles historiques du cap contre plug1. Les contrôles de surfaces et d’inclusion échantillonnée n’établissent pas un montage industriel ou une tolérance réelle.

Source `engine-spark-plug-v2.blend`, GLB `engine-spark-plug-v2-inspection.glb`, collection `WEWA_ENGINE_SPARK_PLUG_EXTERIOR`, datum `Spark plug inherited estimated seat datum`. `render_v2.py -- --preview --native-preview` crée des diagnostics24échantillons à la taille finale1100×850 ; ils précèdent le gel et les trois finales96.

Le [périmètre v1](README.md) reste applicable : extérieur installé conditionnel, insertion cachée lisse, ni électrode enfouie ni filetage hélicoïdal fabriqués. Les valeurs liées10/16/12,5 restent attribuées au dessin Champion, distinctes du12,7 et du pas1,0 revendeur. Toutes les autres cotes, la céramique représentative, la finition et l’identité RDC demeurent ouvertes. Aucune réception artistique ou qualification iPhone.
