# Préparation de montage cockpit v1

Les14sources courantes demandées sont déjà placées dans **le même repère de travail**. Leurs exports concordent avec les bornes évaluées Blender, après conversion `(x,z,−y)`, à8,32×10⁻⁹m près au maximum. Il est donc possible de les relire ensemble en conservant leurs matrices, sans placement supplémentaire. Cela ne reçoit aucun montage OEM. [Rapport court et empreintes](report.json).

Un conflit actuel est établi : le petit faisceau libre du contact traverse le cache central des compteurs. Dans l’assemblage existant du coordinateur,32paires de triangles se croisent près de l’extrémité libre, dans la zone Blender **X6,80–7,86mm, Y−109,94–−108,54mm, Z26,47–28,71mm**. L’intersection est confirmée par segments/triangles, au-delà d’une simple boîte englobante. La montrer dans la revue ; ne pas déplacer une pièce ou percer un trou dans la copie pour la masquer. [Localisation](pigtail-crossing-localization.json).

| Groupe | Placement déjà présent | Ce qui reste ouvert |
| --- | --- | --- |
| Guidon, pontets, poignéesv3, manchon, commodos et leviersv2 | Repère guidon ; poignées/commandes aux bouts±(.340,.085,.105)m et pontetsX±.045m. | Le jeu radial de travail ne certifie ni serrage ni tolérances. Les vis de bridage des supports restent manquantes. |
| MiroirsLHv2/RHv3 | Axes de fixation repris des supportsv2 actuels, hashes liés concordants. | Filetage/contact physique et montage actuelRDC estimés. |
| Contact, compteursv3 et visière | Datums de travail existants ; aucune nouvelle translation à appliquer. | Structure de support/fixations non reçue, et conflit du petit faisceau ci-dessus. |
| Support des compteurs, tés, Nyloc et rondelle isolés | Leurs matrices/origines sont celles de présentation locale, **pas une pose cockpit**. | Origine/angle/empilement manquants ; ne pas les déposer à l’origine commune ni copier aveuglément la pose des compteurs. |
| Gaines partielles | Trois volumes déjà dans le repère commun. | Deux gaines commencent àZ−.319m et finissent versZ−.731/−.749m ; aucun trajet continu depuis les commandes. Affectations, raccords et terminaux restent inconnus. |

Les sorties fixes de gaine des leviers, versZ+.109m, sont distinguées de leur siège mobile de câble dans le JSON. Les extrémités réelles des anneaux de coupe sont extraites dans les sources ; elles concordent avec le relevé de fabrication. Elles ne représentent pas des bouchons ou prises d’usine.

Le contrôle renouvelé sur les sources courantes compte177tests ciblés :176sans croisement, un conflit du petit faisceau. Sont notamment relus commodos/leviers actuels au repos et en course partielle, poignéeLH/commandes, poignéeRH attachée de0à50° et guide fixe, petit faisceau/parties physiques des compteurs/visière. Il ne s’agit pas d’un calcul de jeu minimal, de contenant solide ou de toutes les paires cockpit. Les anciens scores commodo/levier portent des hashesv1 ou v2 périmés ; ils ne sont pas réétiquetés comme tests de toute la moto. [Contrôles détaillés](current-contact-checks.json).

L’assemblage de revue existant du coordinateur attache déjà **seulement la copie de poignéeRH au rotor**, matrices conservées ; gauche et guide restent fixes. Cette liaison n’a pas été ajoutée par l’auditeur. Les identifiants `yaw/pitch` des deux miroirs et `pull` des deux leviers se répètent : tout contrôleur commun doit les qualifier par asset, sans concaténation directe des clés. Le README ancien du guidon inverse aussi les noms des axes entrantsG/D ; conserver les matrices et la convention physique+Xgauche/−Xdroite.

Extraction19sources en lecture seule,1thread surCPU0, puis14GLB relus sans réécriture ; aucun rendu, nouveau modèle, placement, fichier propriétaire ou registre partagé modifié. Les poses de contrôle ont changé seulement en mémoire dans la copie existante, sans sauvegarde. Les [matrices et bornes évaluées](evaluated-source-frames.json), [bornes exports](export-frames.json) et [instantané des paramètres/sources](input-snapshot.json) permettent la revue reproductible. Aucun résultat de matière/optique, tolérance OEM, réception artistique ou iPhone physique n’est accordé.

SHA256 du rapport : `b62f7526ab67596222e45dfea32025acff257469b7b1ccff48ad3daf43c7161d`.
