# Finalisation extérieure — suite exécutable

Objectif : achever la moto entière, en conservant sources Blender, exports et contrôles publics à chaque livraison. Le registre de candidats ne mesure pas le nombre de pièces physiques terminées. Aucun paquet n'est déclaré reçu par un simple contrôle technique.

| Ordre | Travail concret | Preuve / dépendance | Sortie attendue |
|---|---|---|---|
| 1 | Publier les dossiers coordonnés du repose-pied passager gauche, de la protection moteur et des deux gaines observées | Sources natives gelées ; trois pièces passager réutilisées ; tube moteur non doublé ; traces A/B distinctes mais sans fonction attribuée | Blender/GLB, vues96 isolées, EXR, Babylon, manifestes SHA, commit et push par dossier |
| 2 | Relire les vues globales gauche, droite et arrière avec leurs matériaux | Assemblage gris v14 de101 parents ; sources originales et poses conservées | Nouveau dossier matériaux v6, contrôles natifs et EXR, images accessibles GitHub |
| 3 | Réunir les exemplaires répétés pour une revue de moto entière | Décision explicite sur la [proposition déjà préparée](../motorcycle-provisional-repetition-proposal-v1/PLAN.md), exigée par la méthode originale ; aucune réponse présumée | Répétitions provisoires listées, chaque transform tracée ; pas de réception G8 automatique |
| 4 | Résoudre les raccords visibles passager et commandes | Le premier support passager est une référence apparentée, non une preuve du montage actuel. Le kick garde sa pose historique ; la pédale conserve une séparation de revue | Photos montées nettes ou mesure permettant les axes et sièges ; ajout de la seule géométrie effectivement justifiée |
| 5 | Compléter les entrées et terminaisons visibles des câbles | A/B basses sont deux observations actuelles ; leur bijection avec les anciennes études, leur fonction et leur trajet occulté restent inconnus. Les embouts embrayage/accélérateur sont documentés séparément | Une vue nette de chaque raccord et une vue opposée bornant la profondeur. Ne pas fabriquer de continuité sous le réservoir ou le saute-vent |
| 6 | Fermer le dossier optique avant | Les images attribuées DJ201051 montrent une optique vitrée ; elles ne prouvent pas le profil nu de cuve ou les facettes internes. Les circuits publics déjà épuisés et refus d'accès sont archivés | Réflecteur démonté vu de face et de biais, profil profondeur/col mesuré et lumière diffuse. Sans cela : blocage explicite, pas de cuve générique |
| 7 | Vérifier les autres enfants et raccords encore ouverts des trente paquets | Dessous de selle et supports partiels ; attache avant de carter de chaîne ; interfaces de bouchon/tube/platine ; visserie, axes et supports non observés restent distincts | Audit G1/G2 par enfant puis fabrication seulement lorsque la preuve ou une estimation bornée justifiée suffit |
| 8 | Contrôler l'ensemble avant réception | Deux côtés, face, arrière, éclairage neutre ; aucune collision critique masquée ; capteurs de terrain réels non remplacés par software WebGL | Revue visuelle et mécanique documentée, exports d'assemblage, puis réception artistique explicite G8 |

## Méthode pour chaque paquet

1. Relire la fiche canonique et les versions refusées ; identifier la variante et les inconnues.
2. Chercher d'abord dans les références et sources déjà conservées ; ne relancer une route épuisée qu'avec une piste réellement nouvelle.
3. Distinguer exact, apparenté, estimé et inconnu. G1 peut autoriser une estimation bornée et justifiée ; une interface critique cachée n'est pas inventée.
4. Vérifier cadrage/caméra/variante avant de modifier une forme. Ne jamais déformer une pièce source pour cacher une erreur de pose.
5. Produire un exemplaire, lire les aperçus gris puis matière, enregistrer les rendus détaillés96 et EXR FLOAT32, rouvrir Blender, contrôler l'export strict et lire les images réelles du moteur.
6. Geler source, rapports, scripts et manifestes ; conserver les défauts et versions refusées. Mettre à jour les suivis puis commit/push `HEAD:main` sans force avant le paquet suivant.
7. Ne pas transformer un contrôle technique en réception artistique ; ne pas répéter les exemplaires avant la décision requise par la méthode.

Le jalon v14 est une composition de revue avec placements estimés. Il ne résout ni les cotes montées, ni les variantes apparentées, ni la réception des matières. Les fichiers externes de référence restent privés ; URL, observations et empreintes restent publics.

[Les trente paquets et leurs questions de sortie](THIRTY_PACKAGES.md) · [Instantané machine](thirty-package-audit.json). Les questions héritées doivent être confrontées aux nouvelles livraisons avant de déclencher une fabrication.
