# Jante arrière — entrées grises de construction conservées

Ces trois fichiers sont des copies binaires vérifiées du maître gris original, de son GLB et de son rapport de géométrie. Ils ne sont ni une nouvelle pièce ni une nouvelle version de la géométrie. La source grise est `83528bcc…` ; l'export gris est `e0a6b043…`. La source et l'export PBR courants `f97ddc5f…` / `68412d8e…` restent inchangés.

Le rapport historique conserve les chemins de travail utilisés à sa création : son champ d'empreinte identifie le gris, même si l'ancien chemin final désigne désormais le PBR. Le contrôle de préservation compare les vrais triangles orientés, positions, normales, UV et tangentes ; aucune image photographique n'est une entrée de ces maîtres.

Pour reprendre la matière, travailler dans une copie isolée du dépôt : restaurer le maître gris à l'emplacement de sortie attendu par `../material.py` avant de lancer ce script, qui écrase sa source de sortie. Le constructeur `../build.py` recrée également la géométrie grise depuis ses paramètres. Le vérificateur historique de préservation attend encore son GLB gris dans `/workspace/wewa-assets/work-in-progress/rear-rim/g3/` ; ce chemin peut être préparé à partir du GLB conservé ici. Ne pas écraser une livraison gelée pour tester cette recette.

Cette conservation ferme une dépendance de travail omise du gel initial de quatorze fichiers. Elle ne modifie pas ce gel et ne prouve pas qu'une régénération complète a été exécutée depuis une copie propre. Profil, largeur, enveloppe annulaire centrale et matériau demeurent estimés ; aucun moyeu complet ou raccord mécanique reçu.
