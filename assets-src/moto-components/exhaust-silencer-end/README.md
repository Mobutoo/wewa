# Fond arrière et petit orifice de silencieux — candidat v1

MOTO-EXHAUST-SILENCER-END-001, groupe17. Un fond annulaire extérieur à petit passage ouvert, distinct de la coque principale. Les vues RDC06/07 montrent une face sombre délimitée et un petit orifice, sans grande bouche conique ; elles ne mesurent ni section, épaisseur, profondeur, circularité réelle ou mode d’assemblage.

Le repère est dérivé de la frontière candidate de la coque figée. La section extérieure retire une marge radiale de travail0,3mm à sa lumière interne ; la face avant est placée3mm avant son bord arrière. Ces valeurs, l’orificeR8,5mm, la paroi1,2mm et la petite lèvre0,8mm sont des hypothèses déclarées avant forme. Elles ne prouvent ni emboîtement, ni soudure, ni cotes OEM. Aucun déplacement de la coque ou décalage après collision ne les valide.

La source possède un vrai volume fermé de paroi, un passage central ouvert, des bords arrondis construits et des normales/UV analytiques. La face intérieure non photographiée reste un support technique estimé ; aucun long tube caché, catalyseur, chicane ou mécanisme intérieur n’est ajouté. Le fond ne contient ni pare-chaleur, supports ni fixations des autres unités.

Deux cartes originales1024×2048 de couleur/rugosité proposent une finition sombre discrète. Aucun pixel photographique, normal map, bump, déplacement ou grain mesuré n’est revendiqué. Les vrais buffers de positions, indices, normales et UV ainsi que les matrices sont conservés depuis le témoin géométrique. La vue PBR de sortie élargit uniquement le cadrage par rapport au reflet macro pour lire la lèvre entière.

`recipe.py` reconstruit avant gel dans une copie de travail non figée. Contrôles : vrais buffers glTF et cartes décodées, cinq rayons dans l’ouverture, quatre rayons dans la paroi plate, traversées et inclusions échantillonnées contre la coque inchangée, chemins relatifs et cartes embarquées. Le contrôle BVH ne certifie pas les coïncidences strictement coplanaires ; son témoin non coplanaire et cette limite sont enregistrés.

Les bibliothèques et cartes sont résolues à l’emplacement courant ; aucun test universel de checkout déplacé n’est annoncé. Source dense d’inspection, aucun LOD/coût iPhone physique qualifié. `render.py` génère les PNG/EXR96 et leurs checkpoints, puis `record_review.py` les lie après lecture. Aucune preuve technique ou image ne vaut réception artistique, dimensionnelle ou OEM.
