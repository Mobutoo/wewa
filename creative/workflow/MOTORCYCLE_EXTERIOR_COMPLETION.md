# Finalisation extérieure de la moto — plan d’exécution

Plan du 21 octobre 2026, autorisé par la demande utilisateur de planifier les pièces restantes et leurs sauvegardes GitHub. Base : commit `37eaaa52aadb147d29d13e367c35e283c572a402`, 101 candidats enregistrés. **Aucune nouvelle fabrication ni réception n’est déclarée par ce plan.**

Le [plan exécutable en JSON](motorcycle-exterior-completion-v1.json) complète le [plan des dix-huit ensembles](motorcycle-execution-18.json) sans remplacer son historique. Il reprend toutes ses obligations restantes. Les groupes2/4/8 disposent déjà de candidats : leurs interfaces seront relues dans les contrôles de montage et du cockpit. Les références sources et les anciennes études restent conservées.

## Ordre de fabrication

Les vagues indiquent une priorité, pas des journées ni des délais promis. Chaque ligne est un **paquet à décomposer en pièces observables**, pas un unique maillage ni un nombre garanti de pièces. Les critères détaillés figurent dans le JSON.

| Vague | ID | Paquet de travail | Dépendances de fabrication |
|---|---|---|---|
| 1 | P01 | Cache latéral gauche | Documentation et repères existants |
| 1 | P02 | Porte-bagages et poignée passager | Documentation et repères existants |
| 1 | P03 | Garde-boue avant | Documentation et repères existants |
| 2 | P04 | Cache latéral droit | P01 |
| 2 | P05 | Support du feu arrière | P02 |
| 2 | P06 | Optique principale du phare | Documentation et repères existants |
| 3 | P07 | Feu arrière | P05 |
| 3 | P08 | Support de plaque | P02, P05 |
| 3 | P09 | Clignotant avant : raccords et fixations | Documentation et repères existants |
| 4 | P10 | Clignotants arrière et supports | P02, P05 |
| 4 | P11 | Plaque et accessoires arrière observables | P08 |
| 4 | P12 | Bouchon et accessoires visibles du réservoir | P01, P04 |
| 5 | P13 | Supports et dessous de selle | P02 |
| 5 | P14 | Sélecteur de vitesses | Documentation et repères existants |
| 5 | P15 | Pédale et tringlerie de frein arrière | Documentation et repères existants |
| 6 | P16 | Repose-pieds et caoutchoucs | P14, P15 |
| 6 | P17 | Béquilles et ressorts visibles | Documentation et repères existants |
| 6 | P18 | Moteur : volumes centraux extérieurs manquants | Documentation et repères existants |
| 7 | P19 | Carburateur et raccords visibles | P18 |
| 7 | P20 | Admission, durites et attaches échappement | P19 |
| 7 | P21 | Moyeu arrière et porte-couronne | Documentation et repères existants |
| 8 | P22 | Couronne, pignon et chaîne | P18, P21 |
| 8 | P23 | Axes arrière, tendeurs et commande de frein | P15, P21 |
| 8 | P24 | Axe avant et détails roue/frein | P03 |
| 9 | P25 | Fourche et direction : finitions visibles | P24 |
| 9 | P26 | Cadre, bras oscillant et pare-moteur : liaisons restantes | P18, P23 |
| 9 | P27 | Pose et fixations des amortisseurs | P21, P23 |
| 10 | P28 | Fixations guidon et leviers | Documentation et repères existants |
| 10 | P29 | Câbles et faisceau visibles | P19, P24, P28 |
| 10 | P30 | Visière et cockpit : raccords finaux | P06, P09, P25, P29 |

## Démarrage et enchaînement

1. Commencer par **P01, cache latéral gauche** : retrouver les références, définir le contour et les attaches, relever les inconnues et créer les fiches enfants avant la forme détaillée.
2. Préparer indépendamment **P02, porte-bagages / poignée passager**, et **P03, garde-boue avant**. Un seul enfant détaillé par défaut ; trois au maximum globalement si des exécutants indépendants sont réellement disponibles. Les noms d’anciens agents ne prouvent pas qu’ils travaillent encore.
3. Attribuer un propriétaire unique par enfant et par interface commune. Avant de démarrer, vérifier le dépôt distant, les fiches actives et les sources déjà construites. Réutiliser ces sources ; ne pas recréer selle, réservoir, amortisseurs ou coque de clignotant.
4. Prendre ensuite le premier enfant prêt de la vague la plus basse. Une dépendance signifie qu’une source figée et ses interfaces sont disponibles pour la revue ; elle ne transmet aucune réception artistique. Les placements estimés restent bornés et signalés.
5. Si une référence manque, consigner le blocage, la recherche ciblée et le critère de résolution ; poursuivre un enfant indépendant prêt. Une inconnue cachée ne justifie ni une invention silencieuse ni l’arrêt de tout le programme.

## Méthode identique pour chaque enfant

Appliquer [G0 à G8](README.md) et la [recette véhicule](RECIPES.md). Avant G3 : identité/variante, sources et droits, vues utiles, paramètres, échelle, repères, interfaces et incertitudes. Conserver les originaux documentaires non redistribuables hors du dépôt public.

Fabriquer la source Blender éditable ; contrôler forme grise, reflets, normales, triangles, ouvertures et cadrage. Lire les images et corriger les défauts avant la matière. Produire ensuite les aperçus studio et ciel neutre, avec exposition documentée ; ne lancer les rendus détaillés qu’après cette lecture. Conserver PNG, EXR et protocoles originaux, y compris les états rejetés.

Contrôler les buffers du GLB réel et leur cohérence avec la source, puis réaliser des captures Babylon réelles, cadrées et non vides ; consigner les erreurs éventuelles. Tester les raccords et mouvements utiles en revue. Un contrôle automatique réussi ne réceptionne pas la forme ni la matière. Ne multiplier les motifs et exemplaires qu’après réception de leur exemplaire, conformément au workflow.

La plaque recevra un format et une implantation documentés pour la variante retenue ; une inscription de jeu fictive sera signalée. L’éclairage de plaque et le catadioptre sont des points de recherche explicites, pas des pièces présentes supposées. L’attache avant manquante du carter supérieur reste une obligation de P26.

## Revues d’assemblage

- **R01 — silhouette extérieure**, après les vagues1 à4 : face, arrière, gauche, droite, dessus et deux trois-quarts ; matrice visible « présent / incomplet / absent / non applicable justifié ». Présenter aussi les écarts aux références.
- **R02 — montage mécanique**, après les vagues5 à9 : contacts roues/sol, raccords selle/réservoir/caches, axes, transmission, amortisseurs, repose-pieds et béquilles ; braquage et mouvements utiles sans intersections inexpliquées.
- **R03 — ensemble final**, après le cockpit et R01/R02 : mêmes vues dans Blender et Babylon, révisions exactes et défauts résiduels. Produire ensuite une version optimisée séparée et ses comparaisons ; les mesures sur iPhone physique et la réception utilisateur restent des étapes distinctes.

Faire aussi des contrôles de placement dès que deux pièces voisines sont disponibles, sans attendre ces revues globales. La moto seule précède toujours le conducteur. Aucune modification du jeu public n’est incluse dans cette fabrication.

## Sauvegardes GitHub régulières

Un commit puis un push à chaque jalon exploitable : **dossier documentaire**, **forme grise contrôlée**, **matière et rendus**, **export et contrôle Babylon**, puis **revue d’assemblage**. Sauvegarder également avant toute interruption ; signaler clairement un travail incomplet au lieu de le déclarer livré.

Avant chaque push : récupérer l’état distant, résoudre les conflits sans écraser le travail d’une autre session, vérifier les fichiers réellement indexés, les liens et les empreintes des preuves nouvelles. Inclure sources, paramètres, scripts, exports et images générées, fiches, manifestes et limites ; mettre à jour [les livraisons publiques](../../LIVRAISONS_MOTO.md) et le statut à chaque livraison. Garder les protocoles historiques immuables. Après le push : vérifier le commit distant et l’accès public aux nouvelles preuves. Si main ne peut pas avancer, pousser une branche de sauvegarde et donner son nom et le blocage exact ; ne jamais forcer main.

À chaque fin de séance, consigner : dernier commit poussé et vérifié, enfant actif et passage G courant, preuves produites, défauts/blocages, prochaine action et prochain enfant prêt. Le statut des tâches du JSON passe de `planned` à `active`, `blocked` ou `candidate_delivered` selon les preuves ; la réception reste dans la fiche du composant. Un paquet ne peut être clos tant que ses enfants et ses interfaces restent incomplets.

Ce document est une file de travail persistante pour l’exécution successive ; il ne crée pas de tâche d’arrière-plan ni de calendrier automatique. La mise à jour du PRD Ewutelo, si l’outil est disponible à la reprise, doit refléter les résultats réellement obtenus ; aucune synchronisation n’est présumée ici.
