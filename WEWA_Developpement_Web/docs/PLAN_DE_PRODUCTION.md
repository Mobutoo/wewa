# Mise à jour 1.2 du plan de production

## Priorité de la V0

Une cellule visible, une moto agréable, nitro et deux caméras, puis Rush 30 s et score local. Conserver ensuite livraison et courte poursuite narrative. Aucun paiement réel, aucune IA de profilage ni classement public. Les 15 pages de plan antérieur en annexe conservent l’architecture, les budgets, les sources et les phases générales ; ces deux pages prévalent sur le périmètre et le backlog.

## Chemin des tâches

W02-W03 : socle et import. W06-W08 avec audit routier W04 : conduite, collisions et entrées. W35-W37 puis W09 : nitro, vue au guidon, effets et validation. W38-W39 : Rush et score. W10-W13 et W40 : trafic, livraison, poursuite et récit. W14 ferme la V0 avec ces deux branches. W01 nécessite du matériel réel ; son indisponibilité ne bloque pas W02.

## Après la V0

W43 : panel qualitatif ; finition des assets P4. W41 : recommandations locales après W25. W42 : fantômes après la bêta ; W44 : catalogue de défis après W31 et W41. Les services d’achats restent W32-W34 et ne sont pas avancés. Le backlog compte 45 tâches : une tâche terminée d’audit et 44 tâches en attente.

## Fichiers et démarrage

Lire d’abord docs/CADRAGE_R9.md et config/product.json dans WEWA_Developpement_Web. Lire config/rush.json, nitro_camera.json, personalization.json et narrative.json ; exécuter backlog/tasks.json en respectant ses dépendances. Le dossier racine et son prompt indiquent le chemin de reprise. Les 351 GLB sont provisoires, non texturés.

## Rush et état de jeu

Tests de chrono à 30 et 60 images/s, fin unique à 30 s, collision unique par contact, dépôt atomique, absence de récompense après la fin. Rejouer réinitialise inventaire, nitro, score, trafic et chrono. Sauvegarder uniquement le record terminé ; versionner les règles et la graine. Les scores locaux ne constituent pas un classement anti-triche.

## Conduite et confort

Collision balayée à vitesse nitro maximale, bascule de caméra sans changement de position physique, aucune touche persistante après pause ou perte de focus. Tester accélération, direction et nitro simultanément en tactile. Contrôler lisibilité des obstacles en mode Confort et avec effets. Les budgets CPU/GPU existants restent des objectifs à mesurer sur les mêmes appareils et parcours.

## Récit et économie

Prototype avec une amie et une personnalité fictive ; Didi Stone n’est pas représentée sans cadrage ultérieur. Reprises narratives gratuites, pas de piège de paiement ; aucune offre déclenchée par des échecs. Les décisions de monétisation des pages actuelles prévalent sur toute interprétation des anciennes notes. Aucun compte obligatoire ni télémétrie distante cachée.

## Preuves de sortie

Build reproductible, capture du moteur, course terminable, contrôles clavier/tactile et rapport des tests réellement exécutés. Petit panel de 20-30 participants proposé, sans promesse de succès commercial. La V0 fournit une base pour mesurer retours et relances ; les cohortes J1/J7 et les expérimentations commerciales viendront avec une audience suffisante.

---

# WEWA - Plan de développement web


## 01. Le mandat : une Kinshasa jouable sur le web

WEWA - Plan de production 1.0, 20 octobre 2026 (Europe/Paris). Base narrative : concept R8. Décisions de production et budgets initiaux, à éprouver sur matériel réel.

| Engagement | Traduction concrète |
|---|---|
| Promesse du jeu | Une petite moto, la connaissance des rues et les contacts du quartier permettent de retrouver un taxi et de sauver un proche. |
| Cible de diffusion | Un lien HTTPS, aucun téléchargement d’application obligatoire. PC au clavier et téléphone en paysage avec commandes tactiles. |
| Ambition visuelle | Réalisme photographique sur les premiers plans du parcours de démonstration ; densité crédible et cohérence des sons, gestes et matériaux. Qualité adaptée au matériel. |
| Ambition de performance | 60 images/s sur le PC de référence ; 30 images/s stables sur le mobile de référence. Mesures prolongées, résolution et qualité documentées. |
| Ambition « meilleurs 10 % » | Objectif de comparaison future sur un panel déclaré de jeux web comparables. Aucun classement acquis ni promesse de battre les jeux natifs AAA. |
| Livré dans ce kit | Plan, backlog, budgets, consignes de reprise, scripts et secteur pilote découpé en GLB. Ce kit prépare le développement ; il ne contient pas encore de jeu jouable. |

Le rendement de production vient de la génération reproductible, de composants réutilisables et de tests précoces. Ajouter toute la ville avant de valider un carrefour augmenterait fortement le travail à reprendre.


L’autonomie désigne la capacité d’un agent à reprendre une tâche documentée pendant une session. Aucune équipe humaine engagée ni exécution permanente en arrière-plan n’est annoncée.


## 02. Définir la première version et son extension

Deux livraisons distinctes : une V0 qui prouve le plaisir de conduire, puis une V1 qui démontre la qualité artistique. La carte complète vient après ces validations.

| Version | Contenu à réaliser | Critère de sortie |
|---|---|---|
| V0 - boucle jouable | Secteur de travail Gombe, emprise d’environ 1,66 × 1,66 km, mais parcours limité à quelques rues validées. Moto, taxi cible, minibus, colis, deux itinéraires, freinage, élan, pause et reprise. | Une livraison et une poursuite de 5 à 8 minutes terminables au clavier et au tactile ; contrôle sans blocage ni collision inévitable. |
| V1 - démonstration | Parcours de 15 minutes : quado, concert, roulage, convoi, recherche de cible, cour relationnelle et halte au fleuve. Modèles et lumière finalisés sur le corridor visible. | Qualité visuelle validée en mouvement, objectif de performance atteint sur les appareils retenus et envie de rejouer observée. |
| V2 - extension urbaine | Réseau étendu vers port et autres quartiers ; neuf zones narratives, nouveaux repères et types de missions. Chaque secteur passe les mêmes contrôles. | Continuité des parcours, mémoire et téléchargement maîtrisés ; zones ajoutées sans dégrader les cellules existantes. |
| Après validation | Combat à pied, gangs plus développés, météo et cycles d’éclairage additionnels, nouvelles missions et boutique réelle. | Chaque fonctionnalité a une valeur démontrée, un coût de production et une marge technique disponibles. |

Le périmètre actuel de Gombe n’est pas une liaison port-fleuve validée. L’accès au quai et le trajet des quinze minutes seront choisis sur les données et les images ; aucune rue fictive ne sera présentée comme relevée.


V0 : solo, heure fixe de fin d’après-midi, publicités fictives, boutique de démonstration éventuelle. Pas de compte obligatoire, paiement réel, foule complexe, intérieur généralisé ou multijoueur.


## 03. Architecture choisie et décisions à éprouver

Choix de départ : TypeScript + Babylon.js + export statique web. La sélection repose sur l’adéquation au projet ; elle ne constitue pas un benchmark comparatif des moteurs.

| Bloc | Choix proposé | Pourquoi / condition |
|---|---|---|
| Rendu | Babylon.js complet, WebGL 2 en base ; variante WebGPU optionnelle [S01-S02]. | Un même moteur pour les deux chemins. Détection et reprise WebGL en cas d’échec ; aucune logique de mission dépendante de WebGPU. |
| Structure | TypeScript, modules séparés, bundler et lockfile ; UI HTML/CSS au-dessus du canvas. | Séparer world, vehicle, traffic, missions, audio, input, streaming et telemetry ; limiter les dépendances et geler leurs versions lors du premier build. |
| Conduite | Contrôleur arcade spécifique, simulation fixe à 60 Hz et interpolation du rendu. | Accélération, frein, braquage, inclinaison visuelle, suspensions par rayons et balayage anticollision. Assistance basse vitesse réglable. |
| Collisions | Évaluer Rapier WASM pour les requêtes et corps cinématiques [S07]. | Le contrôleur générique n’est pas une physique de moto prête à jouer. Une seule solution de collision après le test ; éviter deux moteurs concurrents. |
| Assets | Blender pour la finition ; GLB/glTF 2, KTX2 et compression de géométrie testée [S05-S06]. | Sources modifiables séparées des exports. Vérifier visuellement normales, UV, animations et temps de décodage après chaque compression. |
| Alternatives | PlayCanvas si le test Babylon révèle un blocage ; Three.js demanderait davantage de systèmes maison. | Changer uniquement sur preuve : temps CPU, compatibilité, workflow ou taille. Ne pas développer trois prototypes complets. |

WebGPU ne dispense pas d’optimiser et sa disponibilité doit être testée appareil par appareil. L’API reste signalée comme à disponibilité limitée par MDN lors de cette consultation [S02].


Le jeu tourne sur le client. L’hébergement fournit les fichiers et, ultérieurement, les services d’achats ; il ne diffuse pas une vidéo de jeu calculée sur un serveur distant.


## 04. Transformer les données en environnement

Le socle existant comprend 608 094 objets bâtis, 44 640 tronçons, 8 804 POI et 33 repères sélectionnés. Ce sont des données de préproduction, pas des modèles finalisés.

| Étape | Travail automatisable | Contrôle nécessaire |
|---|---|---|
| Normaliser | Identifiants stables, validation des géométries, reprojection EPSG:32733, origine locale et empreintes des sources. | Bâtiment complet / partie, doublons, objets superposés et coordonnées de points qui ne désignent pas une entrée. |
| Bâtir | Emprises extrudées, toits et façades par famille, variantes déterministes, niveaux de détail et collisions simples. | 99,4 % des objets n’ont ni hauteur ni étages : conserver le statut estimé ; relever les silhouettes importantes. |
| Créer la voirie | Largeurs documentées ou estimées, rubans, raccords, trottoirs et surfaces. Graphe de voies séparé. | Sens uniques, virages autorisés, ponts, passages dénivelés, gabarit moto et entrées réelles ; ne pas connecter deux voies sur une simple intersection 2D. |
| Adapter le relief | Relief régional puis terrain local nettoyé ; profils de chaussée édités. | Le Copernicus 30 m est un modèle de surface. Il ne décrit ni un nid-de-poule, ni un trottoir, ni le sol sous un toit. |
| Habiller | Kits de boutiques, panneaux, mobilier, végétation, véhicules et personnes selon règles de placement. | Rues praticables, circulation piétonne, proportions et variation locale ; aucun distributeur aléatoire d’objets sur le parcours. |
| Découper | Cellules de 128 m au départ ; géométrie, collisions, navigation, sons et liste d’assets séparées. | Les neuf zones LIGA sont narratives. Les cellules techniques suivent le budget et la visibilité, pas les frontières de zones. |

Conserver deux couches : référence géographique à l’échelle 1:1 et modifications du jeu. Chaque raccourci inventé et chaque distance comprimée ont un identifiant et une justification.


Générer les bâtiments ordinaires à partir de familles réutilisables ; traiter les monuments à la main avec des vues vérifiées. Une génération par IA peut proposer des variantes, mais ne fournit pas une preuve de la forme réelle.


## 05. Construire le réalisme à hauteur de moto

L’effort artistique suit ce que le joueur voit longtemps et de près. La cohérence des proportions, de la lumière et des matériaux prime sur l’accumulation de polygones.

| Couche | Production prévue | Contrôle artistique |
|---|---|---|
| Premier plan : 0-40 m | Moto et pilote, bordures, chaussée, bas de façades, enseignes, étals et véhicules proches. Matériaux PBR, normales et rugosité, salissures localisées. | Échelle réelle, roues au sol, raccords, densité de textures cohérente, absence de flottement et lisibilité des ouvertures. |
| Quartier : 40-180 m | Modules de façade, silhouettes de personnes, trafic simplifié, toitures et végétation en groupes. | Variantes structurées : couleurs et réparations cohérentes ; ne pas répéter le même commerce tous les vingt mètres. |
| Horizon | Volumes simplifiés, repères majeurs, fleuve et Brazzaville lointaine selon le site et l’orientation. | Silhouette, hauteur apparente et brume ; le ciel ne doit pas servir à cacher une géographie erronée. |
| Lumière | Heure fixe V0/V1, éclairage indirect précalculé et sondes, ombre dynamique proche pour moto et trafic. | Concordance des ombres fixes et mobiles ; exposition maîtrisée. Pas de cycle continu plaqué sur une lumière précalculée à une seule heure. |
| Son et animation | Moteur selon régime et charge, klaxons directionnels, voix localisées, gestes de roulage et musiciens. | Transitions et distances crédibles ; audio déclenché après interaction utilisateur ; mixage qui laisse entendre le danger. |
| Effets mesurés | Reflets approximés et poussière localisée, eau simple ; effets coûteux réservés au profil haut. | Désactiver avant tout les effets qui nuisent au temps de trame ou à la lecture. Le flou de mouvement reste optionnel. |

Première bibliothèque proposée : 6 familles de bâtiments, 12 modules de façade, 4 familles de chaussée, 20 accessoires, 4 véhicules (moto, taxi, Mercedes, Hilux/Prado selon mission). Quantités à ajuster après relevés.


Un lieu phare et une rue de 150 à 250 m servent d’étalon artistique. Les autres cellules sont produites uniquement après validation de cet étalon en mouvement, avec la caméra réelle du jeu.


## 06. Budgets graphiques : des cibles mesurables

Budgets de départ proposés, non mesurés et non garantis. Choisir des appareils physiques avant de figer le minimum. Les nombres de triangles et de draw calls ne suffisent pas à prédire les FPS.

| Indicateur | Mobile accessible | PC de référence / qualité haute |
|---|---|---|
| Appareil candidat à qualifier | Android 6 Go, classe Snapdragon 695, Chrome ; test séparé Safari sur iPhone 12 ou équivalent. | PC 16 Go, classe RTX 3060 ; Chrome et Firefox. Un portable à GPU intégré sert de profil intermédiaire. |
| Cible de cadence | 30 FPS ; p95 de trame ≤ 35 ms ; p99 ≤ 50 ms. | 60 FPS ; p95 ≤ 18 ms ; p99 ≤ 25 ms. |
| Résolution interne | Plafond 1280 × 720, adaptation 0,7-1,0 ; UI à résolution de l’écran. | 1920 × 1080 initialement ; échelle dynamique documentée. |
| Géométrie visible / appels de rendu | ≈ 250 000 triangles ; ≤ 180 appels toutes passes incluses. | ≈ 1 million de triangles ; ≤ 450 appels toutes passes incluses. |
| Ressources suivies par le jeu | ≤ 180 Mo de ressources GPU estimées ; ≤ 200 Mo de heap JS lorsque mesurable. | ≤ 700 Mo de ressources GPU estimées ; ≤ 400 Mo de heap JS lorsque mesurable. |
| Population proche | 12 véhicules actifs ; 16 piétons détaillés au maximum au départ. | 32 véhicules actifs ; 40 piétons détaillés au maximum au départ. |
| Chargement cible | Premier jeu contrôlable : ≤ 6 Mo transférés, ≤ 10 s à 10 Mbit/s, RTT 100 ms, cache froid. | Même premier accès léger ; pack visuel additionnel chargé après le début. |

V0 complète visée : ≤ 25 Mo transférés ; V1 : ≤ 80 Mo pour le secteur, avec pack haute qualité facultatif. À 10 Mbit/s, 25 Mo exigent au moins environ 20 secondes de transfert idéal : le démarrage doit donc être progressif.


Les plafonds mémoire sont des estimations du moteur, pas une mesure universelle de la mémoire du navigateur. Tester 20 minutes et les allers-retours de cellules ; relever chauffe, croissance mémoire et pertes de contexte.


## 07. Phases 0 à 3 : prouver le cœur du jeu

Chaque phase se ferme sur une preuve livrable. L’agent exécute les tâches dont les dépendances sont satisfaites et garde une seule tranche fonctionnelle en cours.

| Phase / rôle responsable | Travail | Livrable et passage |
|---|---|---|
| P0 - cadrage et audit / production | Verrouiller boucle, versions V0/V1, données sources et risques. Préparer un blockout et les critères. | Ce plan et le secteur pilote existent. Restent choix des appareils réels et validation du trajet. |
| P1 - fondation web / technique | Créer dépôt et build reproductible, dépendances gelées, écran de chargement, rendu WebGL 2, import d’une cellule, commandes et instruments. | URL privée qui ouvre une scène, journal de build, compteur de trame et fiche appareil. L’import du GLB doit être testé réellement. |
| P2 - conduite / gameplay | Moto arcade, caméra, freinage, élan, collisions, pente simple et réapparition. Tester clavier et tactile sur un circuit court. | Tour complet reproductible ; aucun passage à travers un mur ; pause, changement d’onglet et reprise sans bond physique. |
| P3 - boucle de mission / gameplay + level design | Livraison, taxi cible, trafic sur voies, perte de vue avec recherche, raccourcis et fin de mission. | V0 jouable de 5 à 8 minutes. Observer des joueurs sans explication ; enregistrer les incompréhensions et blocages. |

Chemin critique : voie praticable → contrôleur et collision → poursuite → mesure sur appareil → étalon artistique. La boutique, les grands monuments et les autres quartiers ne doivent pas bloquer cette chaîne.


La création des kits de décor peut commencer sur des emprises validées pendant P2/P3. Leur intégration reste conditionnée à la conduite et au budget de la scène. Ne pas multiplier les intégrations simultanées.


## 08. Phases 4 à 7 : atteindre puis étendre la qualité

L’enrichissement artistique est progressif. Un jalon qui ne tient pas son budget retourne en optimisation avant l’ajout du secteur suivant.

| Phase / rôle responsable | Travail | Livrable et passage |
|---|---|---|
| P4 - étalon artistique / direction artistique + technical art | Finir une rue, la moto, un Mercedes et un lieu de vie ; lumière, sons et matériaux. Fabriquer LOD, collisions et textures compressées. | Même parcours avant/après, captures du moteur et comparaison en mouvement. La qualité choisie tient le profil matériel prévu. |
| P5 - démonstration / production de contenu | Assembler les quinze minutes : concert, agent, convoi, contact, cour et berge. Streaming anticipé et sauvegarde locale. | V1 terminable, cohérente et compréhensible ; pas de trous visuels ou de géométrie manquante au changement de cellule. |
| P6 - bêta web / QA et performance | Tests de trois navigateurs, froid/chaud, réseau lent, session prolongée, déconnexion, restauration et accessibilité. Comparaison avec panel. | Rapport réel de cadence et de qualité ; aucune régression bloquante ; modèle de configuration adapté au matériel. |
| P7 - extension et exploitation / production + services | Ouvrir les autres zones par ensembles de parcours. Introduire cosmétiques et contenus payants uniquement après validation des achats et du support. | Revenus et coûts mesurés séparément ; nouvelle zone acceptée sans dégrader les précédentes ; retour possible à la version stable. |

Ne pas annoncer un délai de photoréalisme avant P1/P4. Estimer ensuite chaque lot à partir du temps réellement constaté pour une rue, un véhicule et une mission ; inclure les reprises et la vérification.


Le planning est piloté par dépendances et critères. Les délais de prises de vue, validation locale, voix, licences et comptes de paiement restent des dépendances externes que l’automatisation ne supprime pas.


## 09. Organisation experte et exécution autonome

Les fonctions ci-dessous sont des responsabilités à couvrir. Elles ne signifient pas que des spécialistes ont déjà été recrutés ou que plusieurs agents travaillent actuellement.

| Responsabilité | Décision / preuve attendue |
|---|---|
| Direction du jeu / production | Arbitre périmètre, plaisir, coût et ordre des tâches ; refuse l’ajout de fonctionnalités sans bénéfice démontré pour la boucle moto. |
| Technique moteur et performance | Mesure CPU/GPU, streaming, mémoire et compatibilité ; conserve un protocole reproductible et explique chaque régression. |
| SIG et génération procédurale | Préserve coordonnées, provenance et niveaux de confiance ; produit les cellules et résout les connexions routières. |
| Level design et gameplay | Choisit rues et raccourcis, équilibre trafic et recherche ; assure plusieurs réponses lisibles à un événement. |
| Direction artistique / technical art | Fixe l’étalon, les matériaux, la silhouette et les budgets ; valide les exports et les transitions de détail. |
| Animation, son et regard kinois | Contrôle motos, gestes, uniformes, dialogues, musique et scènes de vie. Les informations non confirmées restent étiquetées. |
| QA, accessibilité et services | Vérifie parcours, entrées tactiles, état sauvegardé, incidents, achats et support ; produit une preuve au lieu d’un simple statut « testé ». |

Boucle de travail : lire le contexte → choisir un ticket prêt → implémenter le minimum complet → tester le risque concret → archiver les preuves → mettre à jour le statut et la prochaine tâche. Un échec doit laisser un point de reprise clair.


Le fichier AGENTS.md formalise cette méthode. Une revue indépendante pourra être confiée à un expert ou un autre agent si mandaté ; aucune expertise humaine ni indépendance de revue ne sera simulée dans les comptes rendus.


## 10. Collecte complémentaire : quoi relever et pourquoi

Ne collecter que ce qui débloque un asset ou une décision du pilote. Conserver date, orientation, auteur, droits, lieu, échelle et degré de confiance.

| Lot prioritaire | Informations à obtenir | Sortie attendue |
|---|---|---|
| Parcours et carrefours | Vues dans les deux sens, largeur, trottoirs, obstacles fixes, passages, niveaux et accès aux cours. | Plan de voies annoté ; entrée/sortie de chaque raccourci ; liste des écarts avec OSM. |
| Bâtiments proches | Façade de face et oblique, étage de référence, toiture, matériaux, commerces et équipements. | 6 familles typologiques ; dimensions crédibles et 12 modules plutôt qu’un assemblage d’immeubles génériques. |
| Moto et minibus | Vues latérales et trois-quarts, empattement et dimensions documentées, intérieur visible, usure et variantes. | Modèle Wewa complet et Mercedes T1 de variante identifiée ; ne pas appeler 207 une photo dont le badge indique 208. |
| Repère majeur | Vues datées, plan accessible, silhouette, dimensions et environnement immédiat. | Fiche de validation et modèle spécifique ; éviter de mélanger plusieurs états d’un chantier. |
| Vie et son | Roulage, réparation, vendeur, orchestre, sape, uniformes ; ambiances et dialogues avec autorisations appropriées. | Gestes et timbres identifiables ; contexte culturel relu localement, fichiers audio utilisables. |
| Appareils et réseau | Modèles réellement utilisés, mémoire, navigateur, résolution, coût et débit des connexions. | Matrice de matériel et choix du profil par défaut, fondés sur observations plutôt que sur intuition. |

Le registre sources.json cite les documents techniques vérifiés et les bases existantes. Le registre asset_register.json sépare source, référence, droits de distribution, estimation et validation.


Les photos de reportage servent au relevé visuel ; elles ne deviennent pas automatiquement textures ou portraits de PNJ. Pour les matériaux, privilégier prises de vue autorisées, créations originales et bibliothèques aux droits établis.


## 11. Systèmes runtime et chargement du monde

La ville paraît continue, mais seuls les éléments utiles sont simulés et affichés en détail. Les systèmes restent isolés et communiquent par événements simples.

| Système | Règle d’implémentation |
|---|---|
| Streaming | Cellules proches chargées, couronne anticipée selon vitesse et direction ; cache borné et éviction après délai. Priorité au sol et aux collisions avant détails. À défaut de chargement, ralentir proprement plutôt que laisser tomber la moto. |
| Instances et visibilité | Grouper les objets répétitifs par matériau et petite zone. Les thin instances sont utiles pour le statique, mais leur visibilité se traite par groupe [S03] : aucun groupe unique à l’échelle de la ville. |
| Simulation | Pas fixe, nombre de rattrapages limité, pause sur onglet masqué et remise à zéro de l’accumulateur au retour. IA lointaine simplifiée et mise à jour moins fréquente. |
| Trafic | Graphe de voies et règles de priorité ; anticipation des changements, réservation de carrefour et déblocage des files. Pas de téléportation visible pour libérer un bouchon. |
| Poursuite | États : filature, poursuite visible, cible perdue, recherche, interception, succès ou reprise. Dernière direction et contacts fournissent des indices ; un arrêt imposé adapte le délai. |
| Entrées et confort | Clavier ZQSD/WASD, frein et élan ; tactile gauche/droite et accélération/frein distincts ; zones tactiles adaptées. Pause, sensibilité, réduction des secousses et informations non dépendantes de la couleur. |
| Données locales | Progression et réglages versionnés, sauvegarde automatique et export facultatif. Jouer sans compte ; les droits d’achats futurs restent gérés côté serveur. |

Les LOD visuels ne changent pas les collisions ni la logique de mission. Une cible de poursuite reste simulée indépendamment de son niveau de détail.


Éviter le gel global des objets actifs dans un monde en streaming ; optimiser seulement les matrices et matériaux réellement statiques [S04]. Un Worker ne sera introduit que si un profilage montre un calcul déplaçable.


## 12. Prouver la qualité et encadrer le « top 10 % »

Un classement exige un périmètre et des mesures comparables. On peut viser l’excellence du jeu web sur matériel défini ; on ne peut pas certifier aujourd’hui les meilleurs 10 % de tous les jeux.

| Évaluation | Protocole proposé |
|---|---|
| Cadence | Même build, scène et trajet rejoué ; 30 s de chauffe puis 180 s de capture, trois répétitions. Noter appareil, OS, navigateur, alimentation, température, renderer et résolution réelle. |
| Mesures | Temps de trame médian/p95/p99, moyenne de FPS sur la capture, 1 % low avec définition explicite, incidents > 50/100 ms, CPU/GPU lorsque disponible et mémoire suivie par le moteur. |
| Stabilité | Session de 20 min, tours répétés, changement d’onglet, perte de réseau, reprise et pression mémoire. Les mesures à chaud sont distinctes du chargement initial. |
| Réalisme et lisibilité | Évaluer les mêmes vues en déplacement, sans nom de moteur, avec un petit panel de joueurs et de relecteurs kinois. Grille : proportions, matériaux, lumière, animation, ambiance et lecture du trafic. |
| Panel comparatif | Constituer et dater un panel d’au moins 10 jeux web 3D comparables en interaction et densité. Rendre visibles les différences de qualité et de contenu ; ne pas comparer une rue vide à une ville animée. |
| Conclusion autorisée | Présenter séparément qualité visuelle, fluidité et accessibilité. Une première place sur 10 références sélectionnées ne prouve pas le décile supérieur de tout le marché. |

Les tests automatisés couvrent les régressions mesurables ; les tests de conduite et la relecture locale restent nécessaires. Aucune image générée ou vidéo précalculée ne sera utilisée comme preuve de performance.


Le script summarize_benchmark.py calcule les indicateurs à partir d’une capture réelle. Le kit ne contient aucune capture de FPS : les performances du jeu sont encore inconnues.


## 13. Distribution, publicité et achats

La cible initiale est désormais le navigateur autonome. Les contraintes des boutiques mobiles du concept R8 ne s’appliquent pas automatiquement à cette distribution web.

| Étape | Décision |
|---|---|
| V0 privée | URL HTTPS, build statique, assets servis depuis la même origine ou avec CORS explicite. Fichiers versionnés et compressés ; aucune dépendance obligatoire à un CDN tiers pour exécuter le jeu. |
| Cache et mises à jour | Manifest hashé et remplacement atomique ; ne pas mélanger ancienne géométrie et nouvelles collisions. Service worker après validation du premier chargement ; cache facultatif et limites explicites. |
| Publicité | Emplacements identifiés et habillages fictifs. Campagne réelle activée après contrat et validation des scènes ; secours local si le réseau tombe. |
| Boutique de démonstration | Prix et contenu prévus dans R8, sans paiement ni promesse d’achat réel. Vérifier l’ergonomie hors des poursuites. |
| Paiement web futur | Choisir prestataire compatible avec l’entité éditrice et les pays ; chiffrer frais fixes, mobile money, reversements et fiscalité. Recalculer la marge : ne pas appliquer automatiquement une commission App Store au web. |
| Sécurité d’achat | Le serveur vérifie le paiement et attribue le droit une seule fois. Aucun secret dans le navigateur ; webhook vérifié, anti-rejeu, rapprochement, remboursement et restauration. |
| Évolution app store | Si une application mobile est publiée ensuite, revérifier les règles de cette boutique et sa facturation à ce moment-là. |

Les achats restent facultatifs et transparents. Le paiement ne répare pas une difficulté volontairement dégradée ; boosts et progression mécanique restent dans l’économie gagnée en jouant.


Le budget d’exploitation doit intégrer le trafic de données : par exemple 80 Mo téléchargés par 10 000 utilisateurs représentent environ 800 Go, hors répétitions et mises à jour. C’est un volume théorique, pas un tarif d’hébergement.


## 14. État livré, limites et prochaine tâche

Le lot technique préparé dans cette session est un blockout géographique. Il est utile pour démarrer l’import et le streaming ; il n’a pas encore été ouvert dans un moteur de jeu.

| Livré / constaté | Portée réelle |
|---|---|
| 1 747 objets bâtis / 1 748 parties | Extrusions issues du secteur pilote ; 23 anneaux intérieurs conservés. 130 hauteurs déduites des étages × 3 m ; 1 617 à 6 m provisoires. Aucun toit ou façade photoréaliste. |
| 248 tronçons routiers | Axes projetés et surfaces planes provisoires ; 3 tronçons à niveau distinct écartés du maillage routier pour examen. Pas de graphe de voies validé. |
| 191 cellules / 351 fichiers GLB | 34 435 triangles au total, environ 2,79 Mo de GLB non compressés. Un bâtiment appartient à une cellule, mais peut dépasser ses limites ; utiliser ses bornes réelles. |
| Contrôles structurels réussis | En-têtes, tailles de buffers, nombres de sommets, valeurs finies, normales unitaires et bornes contrôlés. Pas de validation complète Khronos ni de test navigateur à ce stade. |
| Conflit géométrique détecté | Environ 2 061 m² de recouvrement cumulé entre emprises bâties et routes à largeur estimée ; ce chiffre n’est pas une surface unique. À examiner avant collisions et tracé jouable. |
| Prochaine tranche | Ticket W01 : choisir appareils et trajet ; W02 : créer build web et instrumentation ; W03 : importer une cellule et parcourir une rue. Corriger le niveau avant d’étendre la carte. |

Aucun objectif de FPS n’est déclaré atteint. La V0 jouable est la prochaine production à réaliser, distincte de ce kit d’organisation et de génération.


Risques prioritaires : hauteur/voirie manquantes, coût artistique des façades proches, commandes tactiles, surchauffe mobile, téléchargements lourds et validation locale. Chacun possède une tâche de réduction du risque dans le backlog.


## 15. Références et traçabilité

Documentation consultée les 19-20 octobre 2026. Les choix de budgets et de production sont des propositions du projet, distinctes des capacités décrites par les éditeurs.

| ID / source | Portée |
|---|---|
| S01 - Babylon.js - WebGPU Support | Support des deux chemins de rendu ; pas de gain de FPS démontré pour WEWA. |
| S02 - MDN - WebGPU API | Disponibilité et contexte HTTPS ; vérifier matériel et navigateur. |
| S03 - Babylon.js - Thin Instances | Coût des instances et visibilité par groupe. |
| S04 - Babylon.js - Optimizing Your Scene | Matrices, matériaux, appels de rendu et limites du gel global. |
| S05 - glTF Transform - CLI | Inspection, validation, compression de géométrie et textures KTX2. |
| S06 - Blender - glTF 2.0 | PBR glTF : extrait officiel indexé consulté ; accès direct indisponible pendant la recherche. |
| S07 - Rapier - Character controller | Requêtes et contrôleur générique ; aucun modèle de conduite moto fourni. |
| S08 - PlayCanvas - Batching | Alternative examinée ; compromis matériaux, groupes et visibilité. |
| S09 - Babylon.js - Planning Real-Time Assets | Organisation des assets pour le temps réel. |
| S10 - OpenStreetMap - Copyright | Attribution et licence de la base ; conserver les obligations des dérivés. |
| D01 - Kit_Kinshasa_3D - audit local | Snapshot OSM 18/10/2026 ; manifest et géodonnées locaux examinés. |
| D02 - WEWA concept R8, version 7 | 31 pages, direction créative et monétisation ; relu avant rédaction. |
| D03 - Dossier géographique - 15 pages | Périmètre et limites du socle géographique. |

Les URL complètes figurent dans docs/sources.json et dans le plan Markdown du kit. Les photos et crédits antérieurs restent dans le dossier conceptuel et le kit géographique.


Ne pas confondre documentation disponible, dépendance installée et fonctionnalité implémentée. Le moteur du jeu, ses versions gelées et son hébergement restent à créer dans la phase P1.


## URL des sources

- S01 : [Babylon.js - WebGPU Support](https://doc.babylonjs.com/setup/support/webGPU/) — Support des deux chemins de rendu ; pas de gain de FPS démontré pour WEWA.
- S02 : [MDN - WebGPU API](https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API) — Disponibilité et contexte HTTPS ; vérifier matériel et navigateur.
- S03 : [Babylon.js - Thin Instances](https://doc.babylonjs.com/features/featuresDeepDive/mesh/copies/thinInstances/) — Coût des instances et visibilité par groupe.
- S04 : [Babylon.js - Optimizing Your Scene](https://doc.babylonjs.com/features/featuresDeepDive/scene/optimize_your_scene) — Matrices, matériaux, appels de rendu et limites du gel global.
- S05 : [glTF Transform - CLI](https://gltf-transform.dev/cli) — Inspection, validation, compression de géométrie et textures KTX2.
- S06 : [Blender - glTF 2.0](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html) — PBR glTF : extrait officiel indexé consulté ; accès direct indisponible pendant la recherche.
- S07 : [Rapier - Character controller](https://rapier.rs/docs/user_guides/javascript/character_controller/) — Requêtes et contrôleur générique ; aucun modèle de conduite moto fourni.
- S08 : [PlayCanvas - Batching](https://developer.playcanvas.com/user-manual/graphics/advanced-rendering/batching/) — Alternative examinée ; compromis matériaux, groupes et visibilité.
- S09 : [Babylon.js - Planning Real-Time Assets](https://doc.babylonjs.com/preparingArtForBabylon/planningRealTimeAssets/) — Organisation des assets pour le temps réel.
- S10 : [OpenStreetMap - Copyright](https://www.openstreetmap.org/copyright) — Attribution et licence de la base ; conserver les obligations des dérivés.
- D01 : [Kit_Kinshasa_3D - audit local](library:libfile_a31a8ed3edec81918d435087dc2390b5) — Snapshot OSM 18/10/2026 ; manifest et géodonnées locaux examinés.
- D02 : [WEWA concept R8, version 7](library:libfile_57065fa3dc0081919ba44686af3ec800) — 31 pages, direction créative et monétisation ; relu avant rédaction.
- D03 : [Dossier géographique - 15 pages](library:libfile_121b5e93fd2c8191a5ab7671c9606e07) — Périmètre et limites du socle géographique.

## Ajout du 20 octobre 2026 : nitro et vue au guidon
Lire docs/NITRO_ET_CAMERAS.md et config/nitro_camera.json dans ce sous-dossier. Ils ajoutent le nitro avec effets réglables et les deux caméras dès P2/V0. Le backlog comprend désormais 38 tâches ; W35-W37 sont en attente. Les PDF de base restent la référence générale, complétés par docs/WEWA_Addendum_Nitro_Cameras.pdf.
