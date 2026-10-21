# Compteurs v4 — carter central

Source `instruments-v4.blend`, export réel `instruments-v4-inspection.glb`, collection `WEWA_INSTRUMENTS_SEPARATE_PARTS`. Les deux commandes d’aiguilles, la pose et le contrat de démonstration du LCD restent identiques ; le chiffre5 ne certifie pas le nombre de rapports RDC.

Seul le champ de normales du carter central change. Les152faces latérales du contour C1 étaient toutes plates, et WeightedNormal ne les rendait pas lisses. Le nouveau champ raccorde ces côtés avant le bevel existant, en gardant les deux grandes faces planes et leurs limites franches. Les positions/topologie/UV/matière/matrice évaluées du carter restent identiques. Les177autres objets sources et174autres nœuds de maillage GLB gardent leurs buffers, matières, images et matrices ; les corrections optiques de v3 sont protégées.

Le contexte de contrôle reprend les géométries clé/pigtail gelées de cockpit-cablesv2 et exactement sa caméra/lumières enregistrées. La copie évaluée du seul carter v4 remplace son témoin v3 dans une scène RAM non sauvegardée. Ce montage est une preuve de correction visuelle, pas un nouvel assemblage du véhicule ni une certification de la monte réelle. Les autres photos/profils et leurs estimations restent inchangés.

Les cadrans, reliefs USB, angles, pivots et dimensions restent les candidats antérieurs ; aucune nouvelle mesure n’est déduite du lissage. Réception artistique, parité d’apparence source/moteur et test Safari physique restent ouverts. Le gel final et les vues effectivement lues sont dans `creative/reviews/instruments-v4/`.
