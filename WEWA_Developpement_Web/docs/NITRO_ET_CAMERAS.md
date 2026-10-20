# WEWA - Nitro et vue au guidon

Statut : spécification validée par la demande utilisateur ; réalisation à venir.

## Décision et périmètre

Ajout demandé le 20 octobre 2026 : boost nitro arcade et caméra à la première personne, en complément de la caméra de poursuite. Référence de sensation : les jeux de course évoqués par le porteur du projet, sans copier leur interface. Le nom affiché sera NITRO. Ces fonctionnalités sont spécifiées, pas encore implémentées. Cet addendum prévaut sur les descriptions antérieures du bonus d’élan et des caméras.

## Boost : accélération réellement jouable

Maintenir Maj au clavier ou le bouton NITRO sur écran tactile. Relâcher ou freiner interrompt le boost ; il est indisponible à l’arrêt, en marche arrière, à pied ou pendant une chute. Une jauge pleine permet au maximum 3 secondes continues. Valeurs de départ à tester : accélération × 1,5 et vitesse maximale × 1,25, sans saut instantané de vitesse. Délai de réactivation de 1 seconde. Physique et collisions restent identiques dans les deux vues.

## Jauge et récompense

Capacité 100 unités ; consommation de 33,3 unités par seconde, recharge passive de 5 unités par seconde après 2 secondes sans boost. Un jeton dédié peut rendre 20 unités, dans la limite de 100 ; pas de recharge par collision ni d’achat de puissance. Les valeurs restent configurables après essais. Pause et perte de focus interrompent l’activation, sans recharger en arrière-plan.

## Sensation de très grande vitesse

Combiner légère ouverture du champ de vision, flou radial périphérique, filets de vitesse discrets, souffle du vent et montée du régime moteur. Garder le centre, les véhicules et le HUD lisibles. Transition progressive d’environ 0,2 seconde à l’activation et 0,35 seconde au retour. Valeurs initiales : champ vertical de 60° à 68° en vue externe et de 65° à 71° au guidon. Pas de flash blanc ni de flou plein écran.

## Deux caméras, librement choisies

Vue de poursuite par défaut ; touche C ou bouton caméra pour basculer au guidon, y compris pendant un boost. En vue subjective : mains, guidon, compteur et haut du réservoir visibles, horizon stabilisé, inclinaison et vibrations atténuées. Le modèle du pilote ne doit pas obstruer la caméra. La sélection est mémorisée. Aucun passage automatique en première personne au milieu d’un virage ou d’une poursuite.

## Confort et profils graphiques

Réglages indépendants : intensité du flou 0-100 %, variation du champ de vision et secousses désactivables. Préréglage Confort : horizon stable, zéro secousse et zéro flou. Sur mobile modeste : flou désactivé par défaut ; effet conservé par le son, la jauge et de légers filets. Aucune dépendance à WebGPU. Aucun miroir temps réel exigé pour la V0.

## Implémentation et ordre de travail

P2 : W35, contrôleur nitro et jauge ; W36, caméra au guidon et bascule ; W37, effets, confort et intégration. W09 doit attendre ces trois fonctions pour valider le tour jouable. W07 vérifie les collisions à la vitesse maximale avec nitro. W17 prévoit les mains et le guidon détaillés pour la finition P4 ; la V0 peut utiliser des modèles provisoires. La vue ne modifie ni la vitesse ni les récompenses.

## Vérification avant livraison

Comparer l’accélération et la consommation à 30 et 60 images/s. Vérifier activation, relâchement, freinage, jauge vide, pause, perte de focus et reprise sans touche bloquée. Tester un mur et le trafic à vitesse nitro maximale, sans traversée de collision. Vérifier bascule de caméra sans déplacement physique, sans double HUD et sans caméra dans la tête du pilote. En tactile : accélérer, diriger et activer le nitro simultanément.

## Performance et critères de sortie

Mesurer le même parcours avec et sans effets sur les appareils cibles ; conserver les budgets existants de 30 images/s mobile et 60 PC comme objectifs non mesurés. Si les effets dépassent le budget, réduire ou désactiver le flou avant de réduire la lisibilité du trafic. Les collisions et le chargement anticipé doivent suivre la vitesse nitro. Livrer une course terminable dans les deux vues, avec effet réglable et paramètres documentés.
