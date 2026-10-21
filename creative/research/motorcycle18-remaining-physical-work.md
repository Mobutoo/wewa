# Pièces physiques restant à fabriquer —18lots

Le cadre, le bras oscillant, le groupe arrière et la carrosserie restent absents des sources de composants dédiées. Les détails déjà construits du cockpit et leurs correctifs ne doivent pas être comptés comme une moto achevée. Ce pointage distingue une pièce construite d’une preuve encore ouverte ou d’une interface inconnue.

[Registre détaillé, sources et états](motorcycle18-remaining-physical-work.json), pointage arrêté le 2026-10-21T02:08:45.233557+00:00. Lecture du board, de la production, des matrices châssis/cockpit/réservoir et du disque, recoupée directement avecA/B/C. Aucun modèle ou rendu exécuté ; seuls ce fichier et son JSON sont écrits. Le pointage est arrêté à cette heure : les évolutions ultérieures ne sont pas suivies indéfiniment.

| Lot | Propriétaire | Déjà construit / correctif | Physique restant | Dépendances et réserves |
| --- | --- | --- | --- | --- |
| 1 | A | Guidon, pontets ; Nylocv3 et rondellesup réellement fabriqués, preuves en cours. | Silentbloc supérieur DS181008, inférieur DS181009, rondelle inférieure DS181010. | Empilement pontets/té ; modèles unitaires ≠ deux montages qualifiés. |
| 2 | A (+C) | Supportv2 construit ; compteurs existants, correctionv3 déjà construite, finales en cours parC. | Pas de nouveau support ou compteur absent identifié. | Montage support/té/compteurs ; complément cockpit, aucun lot19. |
| 3 | B | Manchon/bobine/guide et poignéesv3 construits. | Câble sortant compté au10. | Raccords guidon et commandes6/7. |
| 4 | C | CommodoLH v3 et commandes construits. | Faisceau sortant au10. | Fixation au tube ; identité physique non reçue. |
| 5 | C | CommodoRH v1 et bouton rouge construits. | Faisceau sortant au10 ; inventaire RDC complet inconnu. | Fonction du bouton inconnue ≠ seconde pièce à inventer. |
| 6 | B | Levier/support/pivot/ajusteur embrayagev2 construits. | Vis+écrou de bridage ; câble au10. | Collier/tube, géométrie filetée réelle inconnue. |
| 7 | B | Levier/support/pivot/ajusteur freinv2 construits. | Vis+écrou de bridage ; câble au10. | Accélérateur3, commodo5, collier/tube et miroir8. |
| 8 | C | Deux miroirs construits ; LH v2 et RH v3 corrigés/gelés, finales en file. | Pas de miroir supplémentaire ; clôturer les preuves propres aux correctifs. | Supports6/7 ; filets, rotules et verre OEM inconnus. |
| 9 | B | Contacteur, rotor et clé construits. | Petit anneau ; connecteur compté au10. | Support2 ; position réelle et verrouillage inconnus. |
| 10 | B | Trois tronçons partiels de gaines/boucle déjà construits. | Segments embrayage/frein/accélérateur, faisceaux commodos, connecteur contact. | Sorties3–7/9, direction/visière ; trajets cachés exclus. |
| 11 | C | Étude de coqueG3 maintenant sauvée, brouillon non gelé ; placement refusé avec les compteurs. | Terminer coque/bord et résoudre implantation ; entourage/retours, supports et fixations restent à fabriquer. | Compteurs/support2, câbles10 et direction13 ; trous cachés non résolus. |
| 12 | C | Recherche seule. | Coque/réflecteur/optique phare ; clignotants avantG/D et supports/passages. | Visière11, direction13, faisceau10. |
| 13 | A | Tés, tube unitaire, soufflet et fourreauG fabriqués ; fourreauD sourceG3 active désormais sauvée. | Terminer fourreauD ; fabriquer tige centrale, pile roulements/cuvettes/joints, visserie et joints visibles absents. | Pontets1, axe14, cadre15 ; col48mm vs ouverture soufflet40,6mm estimés non compatibles. |
| 14 | A | Quatre sources historiques : pneu, jante+valve, flasquev2, levier de came. | Axe+écrou/rondelle, roulements, entretoises/joints, came, pince/indicateur, mâchoires/ressorts, entraînement compteur. | Fourreaux13 ; groupe variante et empilement à résoudre.15unités de matrice, dont10sans candidat. |
| 15 | A | Recherche seule ; aucun cadre/bras/garde-boue dédié construit. | Cadre et pattes ; bras, pivot/bagues, patin et tendeursG/D ; coques/bavettes avant/arrière et fixations. | Direction13, enveloppes14/16, appuis moteur17 et réservoir/selle18.14unités documentaires. |
| 16 | A | Recherche seule ; aucun groupe arrière dédié construit. | Pneu/jante/valve, axe/pile, couplage/caoutchouc, couronne/pignon/chaîne/carters, frein/tringlerie, deux amortisseurs et fixations. | Cadre/bras15 ; sortie/pédale17.26unités documentaires, pas26meshes certifiés. |
| 17 | B | RHv2, filtrev2, sortieLHv1 construits ; carterLHv2 figé/finales en cours ; kickv2 minimal désormais gelé, quatre finales en queue. | Cylindre/culasse et couvercles, centre extérieur/admission, collecteur/silencieux/pare-chaleur, repose-piedsG/D, sélecteur/pédale, béquilles et fixations. | Cadre15, transmission16 ; tige/rappel frein au16 uniquement. Béquille latérale encore mal identifiée. |
| 18 | B | Documentation seule : réservoir/rack/caches/selle/arrière ne sont pas des modèles. | Réservoir+col/bouchon/appuis/robinet/durite, cachesG/D, selle+embase, rack, feu/clignotantsAR, supportplaque et réflecteur. | Cadre15/moteur17 ; tunnel réservoir et dessous selle inconnus. Garde-boue/bavette comptés une seule fois15/A. |

Les lots14–16 ont été vérifiés contre la matrice détaillée : le15 et le16 n’ont encore aucun candidat dédié, tandis que le14 conserve ses candidats avant et sa valve déjà incluse dans la jante. La came/arbre ne doit pas être confondue avec le levier construit. Les unités documentaires et kits ne sont pas des comptes de pièces physiques ou de meshes reçus.

Les doublons ont été neutralisés dans ce suivi uniquement : coque/bavette arrière au15/A, éclairage/supportplaque au18/B ; pédale/pivot17/B, tige/tirant/rappel16/A ; cache sortie17 distinct du pignon16. Le connecteur contact et les câbles ne sont comptés qu’au10. Le guidon et les compteurs sont des compléments existants du cockpit, pas un19elot. L’attribution du câble compteur reste à coordonner10/2/14, sans prendre des mentions documentaires12/13 pour une fabrication prouvée.

Deux sources sont apparues pendant ce pointage : fourreauRH G3 et étude de visièreG3. Elles sont classées **fabrication active**, pas recherche seule. C signale un premier refus de placement de visière contre les deux coques de compteurs ; il ne s’agit pas d’un assemblage validé.

Le reliquat du boardlot1 est déjà périmé pour le Nyloc et la rondellesup : leurs sources existent. Inversement, les tés seuls ne contiennent pas la colonne. Les nouvelles révisions de carterLH, kick, compteurs et miroirs sont indiquées séparément des historiques ; source présente ne signifie pas correctif reçu. Le dernier pointage du coordinateur fige désormais le kickv2 minimal ; ses preuves sont en traitement. La fiche cylindre est ouverte, sans source dédiée observée dans ce dernier listing.

Après les pièces actives, A garde direction/pileavant puis cadre/pivot comme chemin de dépendances ; B garde les grands organes moteur/échappement puis carrosserie ; C garde visière puis optiques avant. Les petites sections DS illisibles ne doivent pas immobiliser tous les grands éléments.

Les inconnues de tunnel, montage, cotes, verre ou mécanismes cachés ne sont pas des pièces supplémentaires affirmées. Elles ne clôturent pas non plus G5 ; des candidats extérieurs explicitement estimés peuvent avancer dans les18lots autorisés. Aucun lot n’est déclaré complet ou reçu artistiquement, aucune qualification iPhone physique acquise. Les fichiers propriétaires et registres partagés n’ont pas été modifiés.

SHA256 du JSON : `17c5e8393c28c7d65bccf47d599c69488d116723280f2c44d357b5d016e82f29`.
