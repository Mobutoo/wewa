# Écrou de fixation guidon — v2, revue en cours

Un écrou isolé, avec corps métallique et insert séparés. Les catalogues voisins attestent Nyloc M10, référence 39042215, quantité 2. La famille DIN985 M10 basse choisie pour la reconstruction reste conditionnelle ; aucune identité, norme, tolérance, couleur ou classe matière de la pièce RDC n’est certifiée.

La v1 rejetée (6856/1b1) reste intacte, avec ses deux images et checkpoints. Cette v2 possède une nouvelle source : le maillage suit la phase de l’hélice et ses arêtes de profil, la couture angulaire est décalée de 48 rangs, et les frontières des chanfreins suivent explicitement les méplats. Les quatre classes d’arêtes hélicoïdales et les deux frontières chanfrein/méplat sont vérifiées dans les vrais buffers.

Les normales de l’insert sont calculées dans la source depuis les plans, cylindres et arrondis de son propre profil. Le contrôle avant/après conserve positions, triangles orientés, matrices et normales du métal. Deux vues diffuses entières et deux macros courts de reflets, liés au gel G3, ont été réellement examinés avant les matières. Ils ne constituent pas une réception utilisateur.

Les matières originales distinguent extérieur métallique, filet/face d’appui plus lisses et insert bleu de famille générique. Quatre cartes 512² sont produites sans pixels documentaires ; leur présence et leurs canaux exportés sont lus effectivement. Les propriétés optiques sont estimées. Le passage G4 conserve géométrie et normales ; les tangentes inutilisées de la primitive sans carte normale produisent deux informations glTF, sans erreur ni avertissement.

Les vues finales seront enregistrées séparément avec leur SHA source/export, configuration de caméra et SHA PNG. Les macros autorisent explicitement un recadrage ; toutes les vues passent le préflight des sommets évalués. Aucun mécanisme de serrage, verrouillage polymère ou test physique de montage n’est acquis. L’optimisation mobile, la qualification iPhone et la réception artistique restent ouvertes.
