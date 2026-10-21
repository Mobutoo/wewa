# Tube d’échappement avant et bas — candidat v1

MOTO-EXHAUST-HEADER-001, groupe17. Une seule paroi tubulaire creuse, coude avant et trajet bas vers l’arrière droit du pilote (−X). La séparation avec le silencieux est une limite d’auteur dans l’ensemble apparenté JV591009 ; elle ne prouve pas un raccord démontable.

Les vraies vues RDC00/01/02/04/06/07 et moteur sont archivées en privé et identifiées dans la provenance. Elles documentent des fragments et des occlusions. Aucun diamètre extérieur, angle, rayon, épaisseur ou longueur développée n’a été mesuré. Toutes les cotes locales et portions cachées sont estimées ; aucune inversion de caméra ni mise à l’échelle locale par empattement n’a été employée.

La source géométrique est conservée séparément du matériau. Le trajet C1 est paramétré par longueurs de cordes, échantillonné adaptativement par bornes Bézier ; les sections utilisent des repères transportés. La vraie paroi possède deux lumières ouvertes et des arrondis de bouche de travail. Les normales sont construites dans la source analytique ; aucun buffer d’export n’est réparé. Le premier essai à rayon trop petit et le cadrage macro refusé restent documentés.

La finition sombre représentative comporte deux cartes originales512×8192, couleur et rugosité, sans photo, normal map, bump, déplacement, rouille, bleuissement ou soudure inventés. Les positions, indices, normales, UV et matrices réels sont inchangés depuis le témoin géométrique. Sa réponse optique et son échelle de variation ne sont pas mesurées.

`recipe.py` décrit la reconstruction dans une copie de travail neuve, avant gel. Blender4.3.2, un thread. `check_export.mjs` vérifie le vrai GLB, `check_protected_export.mjs` compare ses buffers au témoin géométrique ; `check_openings.py` contrôle les deux lumières et la paroi candidate ; `check_interface.py` contrôle les surfaces et inclusions échantillonnées contre les trois guides gelés. Les ambiguïtés BVH nécessitent une vérification directe float64 unanime. Ce sont des contrôles de candidats, pas une réception de montage.

La bride, le joint moteur, les fixations, le silencieux, le pare-chaleur et les supports sont des unités séparées non fabriquées par cette source. Aucun catalyseur, chicane ou intérieur caché n’est inféré. Les bibliothèques directes et les cartes sont relatives/embarquées ; la résolution courante est contrôlée, sans annoncer un test de checkout déplacé.

Source d’inspection dense, pas un LOD mobile qualifié. `render.py` produit les vues96 et `record_review.py` lie leurs PNG/EXR/checkpoints après lecture ; aucun test iPhone physique ni réception artistique/OEM n’est acquis.
