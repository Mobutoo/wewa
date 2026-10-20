# WEWA - Cadrage R9

## WEWA / LE CADRAGE ACTUEL

Révision 9 - 20 octobre 2026 - Document de départ pour Codex

### La promesse

Dans Kinshasa, ta meilleure arme, c’est de connaître le passage. Petite moto Wewa, trafic lisible, choix d’itinéraire et conduite précise constituent le cœur du jeu. La ville, les personnages et la musique donnent du sens à cette maîtrise.

### Ce qui est décidé

Ajouter Wewa Rush de 30 secondes ; conserver les livraisons et l’enquête narrative ; intégrer nitro, vue arrière et vue au guidon ; distinguer score, réputation et monnaie gagnée. Reprises narratives gratuites. Personnalisation fondée sur les préférences de jeu. Aucun paiement réel dans la V0.

### Autorité des documents

Ces huit premières pages constituent le cadrage R9 et prévalent sur les formulations antérieures concernant modes, récit, caméras et reprises. Les 31 pages R8 qui suivent conservent les références de Kinshasa, véhicules, lieux, personnages, sources et économie générale. Elles sont identifiées comme annexe antérieure. Le détail nitro du précédent addendum reste valable sauf contradiction explicite.

### État réel

Le pilote Gombe comporte des volumes de bâtiments et de voirie, des données et des scripts. Aucune application jouable, conduite, mission, boutique ou mesure de FPS n’est encore livrée. Les nouveaux réglages sont des hypothèses de conception à éprouver. Le rendu photoréaliste et le classement parmi les meilleurs jeux restent des ambitions.

## WEWA RUSH / 30 SECONDES

Une boucle courte : choisir, transporter, livrer, recommencer

### Règles de la première version

Après un compte à rebours 3-2-1, le joueur part déjà en mouvement et dispose de 30 secondes de simulation active. Ramasser un colis par passage dans une zone balisée ; capacité initiale de trois colis. Livrer dans une zone dédiée en roulant sous le seuil configurable de 15 km/h. Un dépôt consomme seulement les colis présents. Aucun arrêt obligatoire à un menu.

### Score de départ à équilibrer

Chaque colis livré vaut 100 points × multiplicateur. Le multiplicateur démarre à 1, augmente de 0,25 après un dépôt propre et plafonne à 3. Un dépôt groupé utilise le même multiplicateur pour tous ses colis, puis augmente le multiplicateur une seule fois. Un passage technique validé rapporte 10 points, au maximum une fois par balise et par course. Le score est entier, arrondi à la fin de chaque événement.

### Risque et fin de manche

Une collision remet le multiplicateur à 1 et ralentit physiquement la moto ; un contact continu compte comme un seul incident. Les colis restent à bord en V0. À 30 secondes, aucun colis non livré ne marque de point ; aucun nouvel événement de score n’est accepté. Afficher score, colis livrés, record personnel et Rejouer. Pas de bonus pour heurter des personnes. Aucun prolongement payant en V0.

### Équité et variété

Une seule route et un trafic à graine fixe pour le premier Rush ; deux branches pour choisir entre trajet sûr et collecte supplémentaire. Les identifiants de colis et dépôts empêchent les doubles récompenses. Réinitialiser tout l’état au redémarrage. Une pause fige le temps en solo non classé. Plus tard, les défis classés partagent graine, règles et assistance ; aucune reprise ni adaptation cachée ne modifie un score classé.

## NITRO / DEUX CAMÉRAS

Sensation de vitesse forte, obstacles toujours lisibles

### Nitro arcade

Maintenir Maj ou le bouton tactile NITRO. Jauge de 100 unités ; consommation 33,3 unités/s, soit environ trois secondes pleines. Accélération × 1,5 et vitesse maximale × 1,25 comme valeurs de départ. Recharge passive 5 unités/s après deux secondes sans activation ; jeton dédié +20 dans la limite de 100. Pas de nitro à l’arrêt ou en marche arrière. Freinage, pause, perte de focus et chute l’interrompent.

### Effets de vitesse

Flou radial surtout périphérique, vent, régime moteur renforcé et légère ouverture du champ de vision. Garder le centre et le HUD lisibles. Champ vertical proposé : 60° à 68° en vue arrière, 65° à 71° au guidon. Transitions de 0,2 s à l’entrée et 0,35 s au retour. Les effets n’augmentent pas la vitesse physique au-delà des paramètres du contrôleur.

### Vue au guidon

Touche C ou bouton caméra : bascule à tout moment entre poursuite et première personne, y compris sous nitro. Mains, guidon, compteur et réservoir visibles, horizon stabilisé. Même physique, mêmes récompenses et mêmes collisions dans les deux vues. Choix mémorisé ; aucune bascule forcée pendant une manœuvre. Modèles provisoires acceptés pour la V0.

### Confort et performance

Flou, secousses et variation du champ de vision réglables séparément. Mode Confort sans flou ni secousse. Flou désactivé par défaut sur le profil mobile modeste. Aucune exigence de miroirs temps réel. Collisions balayées et chargement anticipé testés à la vitesse nitro maximale. Les paramètres détaillés restent dans config/nitro_camera.json.

## LE RÉCIT / UNE DISPARITION

Le lien personnel motive le héros ; la célébrité amplifie l’enjeu

### Déclencheur fictif

Une personnalité attendue à Kinshasa doit participer à un événement. Une amie proche du héros travaille dans son équipe. Après un changement de véhicule, les deux femmes disparaissent. Le héros reçoit de son amie un message vocal interrompu ; un détail du taxi et sa connaissance des rues lui donnent une première piste. Il peut admirer la célébrité, mais cherche avant tout son amie.

### Personnages et participation

Pour le prototype, utiliser une personnalité entièrement fictive, sans visage, voix ou biographie identifiables de Didi Stone. Didi Stone est conservée dans les notes comme proposition de collaboration à lui présenter, sans accord ni participation annoncés. Tout usage futur de son identité demanderait un cadrage de collaboration et un récit explicitement fictionnel. Aucun enlèvement réel n’est allégué.

### Progression en chapitres

1. Une livraison présente l’amie avant la disparition. 2. Le message déclenche une courte poursuite. 3. Le taxi disparaît ; un témoin ouvre l’enquête. 4. Une course utile permet d’obtenir un contact ou un accès. 5. Un indice mène vers un relais puis le port. 6. Le sauvetage résout le premier arc, avec une suite possible. Les lieux et distances restent soumis à validation du parcours.

### Rythme et initiative des victimes

L’amie laisse des indices et contribue à l’évasion ; la personnalité a aussi des décisions et une voix. Alterner tension, recherche, rencontre et respiration. Les livraisons annexes se placent pendant une attente ou servent directement l’enquête. Pas de cinquante courses sans rapport pendant une urgence immédiate. La V0 ne développe que l’introduction, une poursuite et un indice ; pas toute la campagne.

## REJOUER / PROGRESSER / ACHETER

Une économie compréhensible et une histoire accessible

### Trois compteurs distincts

Score de manche : performance et record, jamais dépensé. Réputation : contacts et missions, jamais vendue. Monnaie gagnée : personnalisation et équipements équilibrés. Les petits bonus récurrents doivent correspondre à une action ou un objectif clair ; éviter une multiplication de monnaies et des récompenses sans utilité.

### Règles de reprise retenues

Campagne : checkpoints gratuits, reprise proche de l’erreur. Rush V0 : tentatives gratuites illimitées, redémarrage immédiat, aucune seconde chance au-delà des 30 secondes. Après la V0, des événements peuvent utiliser des tickets gagnés en jeu et une reprise par jeton hors classement. Les reprises payantes obligatoires et les prix qui augmentent après un échec ne sont pas retenus.

### Revenus envisagés

Cosmétiques, collections, épisodes annexes, packs de nouveaux défis et sponsoring naturel du décor. Les effets visuels de nitro peuvent être personnalisables, sans avantage mécanique. Les prix indicatifs de l’annexe R8 sont en USD, restent des hypothèses et doivent être validés avant vente. Pas de contrat de marque présumé. Toute boutique V0 est une démonstration sans encaissement.

### Offres et options non engagées

Présenter contenu exact, aperçu et prix explicite ; proposer des articles correspondant aux goûts du joueur. Pas d’offre pendant la conduite ni après chaque échec. Les tentatives payantes facultatives restent une piste à réexaminer, pas une tâche de développement autorisée pour la V0. Pas de récompense aléatoire payante. Le revenu doit être suivi avec la satisfaction, les retours et les remboursements.

## PERSONNALISATION / PRÉFÉRENCES

Adapter les propositions sans modifier l’équité

### Profils de jeu modifiables

Chronomètre : records et parcours techniques. Exploration : repères et raccourcis. Histoire : chapitres et dialogues. Personnalisation : livrées et accessoires. Temps disponible court : Rush. Ces catégories décrivent une préférence récente, pas la psychologie, la richesse ou la vulnérabilité de la personne. Le joueur peut choisir son mode sans recommandation.

### Premières règles simples

V0 : choix explicite entre Rush, livraison et histoire ; progression locale seulement. Plus tard : après au moins cinq sessions valides, proposer en priorité le mode le plus souvent choisi. Après trois échecs consécutifs, proposer entraînement ou assistance, sans achat associé. La proposition reste refusable et ne modifie pas silencieusement la difficulté d’une course classée.

### Données et contrôle

Prévoir des événements locaux minimaux : début et fin de course, mode, durée active, colis livrés, score, collisions, caméra et activation d’une aide. Ne pas enregistrer les touches brutes, les contacts ou les données privées du téléphone. Préférences réinitialisables. Un suivi distant éventuel fera l’objet d’un chantier séparé avec information et choix utilisateur ; aucune connexion analytique cachée en V0.

### Essais et limites des références

Comparer des variantes clairement définies sur des groupes distincts lorsque l’audience le permet. Le support Tetris Mobile décrit des essais sur récompenses et prix ; cela ne prouve pas un profilage psychologique individuel. La recherche sur l’ajustement de difficulté ne garantit aucun gain pour WEWA. Nos premières règles sont des hypothèses produit à mesurer, pas un algorithme de monétisation déjà validé.

## RYTHME / REJOUABILITÉ / PREUVES

Valider la qualité d’une course avant d’étendre les neuf zones

### Trois durées complémentaires

Rush : 30 s pour la maîtrise et la revanche immédiate. Livraison express : cible de 2 à 4 min pour un trajet complet. Chapitre narratif : cible de 8 à 15 min plus tard, avec sauvegarde intermédiaire. La première V0 reste un petit ensemble de courses et une poursuite de 5 à 8 min, complété du Rush.

### La rue devient un terrain de maîtrise

Deux ou trois itinéraires ont des risques et avantages compréhensibles. Un carrefour doit donner une décision, pas une collision inévitable. Alterner densité, ouverture et climax. Trafic annoncé par gestes, roues, feux et sons. Garder l’humour, la musique et l’entraide ; Kinshasa ne se résume pas aux crimes. Prioriser moto, premier plan, signalétique et ambiance sonore.

### Extension après validation

Fantôme personnel d’abord, puis fantômes d’amis avec conditions comparables, uniquement après le socle. Défis de quartier, variations de parcours et collections peuvent renouveler l’intérêt. Ne pas démarrer par un multijoueur temps réel, une ville complète ou une boutique complexe. Les classements publics exigent une validation des scores et des mesures contre la triche, absentes du prototype local.

### Ce que l’on mesurera

Petit panel qualitatif de 20 à 30 personnes, incluant des joueurs kinois : compréhension, incidents injustes, choix de trajet et relance spontanée. Puis, sur une audience suffisante : retour J1/J7, taux de fin de course, nombre de relances, stabilité et satisfaction. Définir les cohortes et distinguer retour volontaire et relance suggérée. Les essais ne démontrent pas à eux seuls un futur best-seller.

## DÉMARRER DANS CODEX

Priorité : une course agréable, reproductible et réellement jouable

### Ordre opérationnel

Lire 00_LIRE_AVANT_DE_CODER.md puis PROMPT_REPRISE_CODEX.txt. Initialiser app/ et importer une cellule de Gombe ; réaliser le contrôleur et les collisions ; ajouter nitro et deux caméras ; réaliser Rush et le score ; ajouter livraison et courte poursuite. Mesurer la performance. Affiner ensuite art, personnages, musique et recommandations. Aucun paiement réel avant les tâches dédiées post-bêta.

### Contrats vérifiables

À 30 s, le Rush termine exactement une fois et ne compte plus de dépôt. Un colis ne rapporte qu’une fois. Rejouer réinitialise timer, jauge, trafic, inventaire et multiplicateur. La simulation produit les mêmes règles à 30 et 60 images/s. Pause et perte de focus ne laissent pas l’accélérateur bloqué. Les deux caméras partagent le même état du véhicule. Les dépendances du backlog doivent rester sans cycle.

### Fichiers faisant autorité

WEWA_Developpement_Web/docs/CADRAGE_R9.md ; config/rush.json ; config/nitro_camera.json ; config/personalization.json ; config/narrative.json ; backlog/tasks.json. Les fichiers context/ conservent les textes et exports ; la version R9 prévaut sur les descriptions historiques. Le plan de production est actualisé en version 1.2. Les fonctionnalités indiquées pending ne sont pas réalisées.

### Références et annexes

La suite conserve le dossier R8 complet, avec ses crédits et ses références locales. Sources complémentaires relues le 20 octobre 2026 : support Tetris Mobile, « My rewards are different from someone else » ; Ascarza, Netzer et Runge, « Personalized game design for improved user retention and monetization in freemium games », DOI 10.1016/j.ijresmar.2025.01.006. Ces sources éclairent les tests ; elles ne prouvent pas la performance de WEWA.
