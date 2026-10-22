# Correction minimale des coupes supérieures — v5 finale

Fragment canonique : integration-fragment-v5.json. Sur une scène v4, retirer exactement les deux parents de parents_to_remove puis ajouter additions. Pour une scène neuve, utiliser complete_candidate_inventory : huit instances, six retenues de v4 et deux appuis corrigés. Sources/SHA/matrices4×4 sont inclus. Toutes les matrices restent identiques ; les tubes sont construits en coordonnées natives globales, matrices identité.

Seule correction : premier contrôle X de chaque appui avant ±145→±120mm, soit25mm vers l’intérieur dans la borne estimée±30mm. Y/Z et autres contrôles, gardes arrière, pegs et rubbers inchangés. upper-cut-correction-v5.blend contient seulement les deux appuis ; les GLB upper-cuts-* ne contiennent que ce patch.

Trois vues natives96 1000×800 et leurs EXR FLOAT32 conservés et lus ; aperçus gris/matière et deux captures Babylon lus. Pointes visibles corrigées. Runtime combiné8 meshes/518484 triangles, sans erreurs. Export strict0 erreurs/0 avertissements ; buffers gris/matière et matrices égaux, bornes natives/export égales.

Audit rouvert :43 instances structure/cases/exhaust,28SNS,2 peaux ; zéro croisement structure/SNS et entre pièces même côté. Restent278/272 intersections de triangles avec les seules peaux de caches aux émergences occultées : limite G5 explicite, sans soudure ou connecteur caché fabriqué, sans certification mécanique. Tracés photo-inférés, section12–18mm, X±30mm, échelle±10% ; limites historiques peg5mm/rubber22mm/cut90° préservées.

Entrées épinglées v4/v5 vérifiées inchangées. Aucun nouveau rendu whole ; aucune nouvelle révision prévue. Gel de preuve, pas de réception G8.
