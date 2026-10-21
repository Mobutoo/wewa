# Filets cosmétiques des rétroviseurs — diagnostic en lecture seule

Les deux sources figées ont été réellement ouvertes dans Blender sans sauvegarde. Elles conservent la même grille : 72 secteurs et 270 niveaux axiaux uniformes pour le goujon estimé. Les valeurs radiales aux sommets respectent le profil voulu à environ 22 nm près, mais ses quatre courbes hélicoïdales de rupture de pente ne sont pas alignées sur les arêtes du maillage. Les faces traversent donc ces ruptures ; cette construction est une cause plausible de l’ondulation observée sous l’écrou du miroir droit v2. Elle n’est pas une propriété attestée de la pièce réelle.

Ce contrôle ne suffit pas à isoler l’effet des normales et de l’union finale. Le diagnostic éventuel de correction doit conserver rayon, profil et pas estimés, placer les ruptures hélicoïdales dans les arêtes, puis vérifier les surfaces après union et leur réponse sous lumière de reflets. Les autres corps et anciens gels doivent rester inchangés. Ni diamètre, ni pas, ni sens, ni compatibilité de filetage RDC ne sont établis.

`inspect_source.py` est reproductible avec Blender officiel 4.3.2 ; `source-audit.json` lie les empreintes des deux sources. Aucune nouvelle géométrie ni image n’a été produite par cette inspection.
