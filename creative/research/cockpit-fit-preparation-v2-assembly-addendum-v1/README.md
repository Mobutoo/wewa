# Addendum — assemblage cockpit v2 réellement livré

**Le contrôle zéro contact est relié au nouvel assemblage v2**, sans rejouer les 177 tests. Source assemblée `849f4121…`, GLB livré `f002b974…` ; les 14 sources concordent toujours aux SHA de la passe précédente.

Les trois sources ont été rouvertes et évaluées dans Blender, guides masqués activés **en mémoire** avant mise à jour du graphe. La nouvelle source assemblée a été ouverte séparément. Aucun déplacement, sauvegarde, export, rendu ni modification du manifeste v2 précédent.

| Corps réel | Source fraîche → copie assemblée | Vrais triangles GLB → source / copie |
|---|---|---|
| Boucle câbles v2 | Positions locales/monde, indices et matrices bit-identiques | Écart maximal 0 / 0 nm |
| Cache central compteurs v3 | Positions locales et indices bit-identiques ; coordonnées monde écart maximal 29,802 nm | Écart maximal de sommet de triangle 31,729 / 14,909 nm |
| Visière v1 | Positions locales/monde, indices et matrices bit-identiques | Écart maximal 0 / 0 nm |

Les **65 596 triangles réels** sélectionnés correspondent au même multiensemble orienté, après correspondance des sommets effectivement dédoublés par les coutures UV/normales du GLB. Chaque sommet de triangle correspondant est comparé ; les positions exportées sont transformées par leurs vraies matrices glTF. Aucune matrice navigateur n’a servi à reconstruire le témoin source.

Le petit écart de matrice du cache fraîchement évalué est explicitement conservé : jusqu’à 3,5763e−7 sur ses coefficients de rotation, pour 29,802 nm sur coordonnées monde. La première tentative trop stricte « tout bit-identique » a donc échoué ; outil et log sont conservés. Cela ne devient pas un défaut géométrique démontré.

Pour fermer le lien avec la passe de contact, l’ancien assemblage réellement utilisé par celle-ci a aussi été rouvert : **son cache central et sa visière sont bit-identiques aux deux nouvelles copies**, positions locales/monde, indices et matrices. La boucle v2 de la passe précédente était la vraie source ajoutée en mémoire ; la nouvelle copie lui est bit-identique. Cette correspondance exacte relie les anciens 177 tests / zéro croisement, les segments et points contenus à cette nouvelle source assemblée. Elle ne repose pas sur une approximation du jeu.

Les tableaux complets et SHA sont dans `report.json`, `world-geometry-parity-all-references.json` et `historical-contact-target-parity.json`. Les vrais buffers lus et tableaux évalués sont conservés ; `delivery-manifest.json` ferme uniquement cet addendum. Le manifeste précédent reste à SHA `77fcf4ada18c8bc3ed10d8d1a591dcf7a6f5f88f371eac41ba60b575ebc28a78`.

Parité de coordonnées/triangles seulement. Aucun nouveau jugement de matière, réception artistique, montage OEM ou qualification iPhone. Connecteur, câbles supérieurs, faisceau complet et braquage complet restent ouverts.
