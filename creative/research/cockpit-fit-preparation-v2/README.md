# Câbles v2 — reprise indépendante des contacts cockpit

**177 tests, aucun croisement.** L’ancien départ de contact v1 reproduit toujours ses **32 paires de triangles** avec le cache central des compteurs ; le v2 n’en présente plus dans le même contexte. Les 13 autres sources, dont compteurs v3 et visière v1, sont identiques aux empreintes du contrôle précédent.

Le contrôle charge l’assemblage de revue historique en lecture seule, puis la vraie collection câbles v2 et ses guides parents. Les guides sont activés **en mémoire** avant évaluation des matrices. Aucun déplacement d’installation, nouvelle géométrie, export, sauvegarde source ou rendu. La liaison poignée droite/rotor existante est conservée ; les poses partielles sont temporaires puis restaurées.

| Vérification réelle | Résultat |
|---|---:|
| Paires/poses du protocole v1 | 177 / 0 non nulle |
| Ancien témoin v1 contre cache central | 32 paires |
| Nouveau v2 contre même cache | 0 paire |
| Segments de triangles testés dans les deux sens | 31 674 / 0 intersection |
| Boucle → cache : sommets + centroïdes, trois directions | 26 208 / 0 contenu, ambigu ou frontalier |
| Cache → boucle : sommets + centroïdes, trois directions | 5 468 / 0 contenu, ambigu ou frontalier |
| Autocroisement de triangles non adjacents de boucle | 0 |

La distance minimale **échantillonnée de sommet de boucle vers surface du cache** vaut **3.873598 mm**. Elle n’est pas le jeu exact entre les surfaces.

## Incident numérique conservé

Les deux premières tentatives employaient un redémarrage de rayon à 10 nm : le triangle de sortie 171 était parfois touché plusieurs fois à cause des coordonnées flottantes. Le diagnostic sur le vrai sommet 5959 conserve les positions/triangles de chaque impact, puis compare 10 nm, 100 nm et 1 µm. À 100 nm et 1 µm, le témoin produit bien deux intersections distinctes. La tentative finale à 100 nm conserve le seuil frontière de 10 nm et les mêmes sources ; les trois directions classent tous les points testés à l’extérieur. Les tentatives et leurs assertions échouées restent disponibles et ne sont pas présentées comme des preuves passées.

`current-contact-checks-attempt03.json` et `independent-spatial-checks.json` sont les résultats finaux. `input-snapshot.json` et `report.json` contiennent les SHA des vrais inputs ; `delivery-manifest.json` ferme les fichiers de cette livraison. Le rapport v1 reste intact à SHA `b62f7526ab67596222e45dfea32025acff257469b7b1ccff48ad3daf43c7161d`.

Les intersections de segments n’utilisent pas la liste BVH overlap comme filtre. L’inclusion échantillonne sommets et centroïdes par trois rayons ; ce n’est pas un booléen exact ni une tolérance physique. Le test des buffers inchangés des gaines basses reste attribué à B, distinct de cette passe indépendante.

La correction concerne le départ du contact. Connecteur, câbles supérieurs des commandes, faisceau des commodos, trajets masqués et braquage complet restent ouverts. Aucun montage OEM, réception artistique ou test iPhone physique déclaré.
