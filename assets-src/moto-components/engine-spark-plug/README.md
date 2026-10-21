# Bougie — extérieur installé conditionnel

`MOTO-ENGINE-SPARK-PLUG-001` couvre l’extérieur observable d’une bougie apparentée à la branche UG5 de D04 : corps métallique avec hexagone, rondelle séparée, céramique nervurée et borne métallique. Le capuchon et le fil HT restent des unités distinctes. Aucune bougie exacte montée en RDC n’a été identifiée.

La [recherche attribuée](../../../creative/research/engine-spark-plug-17/README.md) conserve la contradiction de la photo DD111018 montrant une BoschR6 et les images représentatives Champion. L’image technique6995 liée par Champion à P-RZ9HC donne10,16 et12,5 ; le revendeur annonce M10×1,0 et12,7. Aucune moyenne ni équivalence Bosch/Champion n’est déduite. Le pas revendeur n’est pas fabriqué comme filetage exact.

Le diamètre nominal10mm, la clé16mm et la portée12,5mm sont utilisés comme guides attribués au dessin lié. Les longueurs de céramique, la distribution des cinq nervures de travail, la borne, les profils et le siège restent estimés. Le groupe de nervures suit l’image6995 choisie comme référence primaire ; l’autre photographie représentative62 ne fournit pas un deuxième motif à fusionner. Aucun marquage constructeur non confirmé n’est copié.

La portion cachée est une enveloppe d’insertion lisse au diamètre nominal. **Ni électrode enfouie, ni filetage hélicoïdal, ni mécanique électrique interne ne sont inclus.** L’export est destiné à l’observation de la pièce installée et ne constitue pas une reproduction complète de la bougie démontée. La rondelle est une section non comprimée estimée, sans précharge ni écrasement mécanique certifiés.

Le profil est original : volumes fermés, arrondis réels, six pans avec coins arrondis et chanfreins construits par section conique limitée par le contour hexagonal. Le premier essai de loft présentait un pincement visible des reflets ; il reste privé et refusé. Les anneaux circulaires internes sont aussi subdivisés sur les longs plats afin de ne pas remplacer un alésage circulaire par de grands cordons polygonaux.

Source `engine-spark-plug-v1.blend`, collection `WEWA_ENGINE_SPARK_PLUG_EXTERIOR`, quatre objets physiques nommés dans `build-report.json`, datum `Spark plug inherited estimated seat datum`. Xlocal suit l’axe sortant du siège provisoire du head3 ; les matrices sont conservées au montage. Le puits et son rayon provisoire ne sont jamais utilisés comme cote de bougie réelle. Le GLB ne contient pas la culasse liée de contrôle.

Blender4.3.2, un thread : `build.py`, contrôle des vrais buffers avec `check_export.mjs`, puis `check_interface.py` en lecture seule. Les aperçus gris/reflets/PBR et le contexte précèdent le gel ; les vues finales96 gardent chacune leur checkpoint source/configuration/PNG/EXR. Les métaux et la céramique utilisent des PBR constants originaux sans photographie ni normal map prétendument mesurée. Aucun LOD mobile ni test physique iPhone reçu.
