# Parité indépendante des réglages du miroir droit v2

**Contrôle technique réussi : quatre poses, erreur maximale4.3350757e-08m pour une tolérance numérique2e-7m.** Le témoin est un vrai sommet de la bande de bord, évalué dans Blender puis retrouvé dans les positions réellement chargées par Babylon. Ce résultat ne donne ni réception artistique, ni précisionOEM, ni qualification physique iPhone.

[Rapport navigateur/source](attempt-01/browser-source-motion-parity.json), [témoin Blender indépendant](attempt-01/Blender-source-witness.json), [contrat source figé](source-axis-spec.json), [journal court](attempt-01/Blender-source-extraction.log).

| Yaw / pitch (°) | Erreur à l’ordre attendu (m) | Erreur au contre-ordre inversé (m) |
| --- | ---: | ---: |
| +0 / +0 | 0 | 0 |
| +10 / +7 | 3.0061949e-08 | 0.0037771046 |
| -10 / +7 | 1.8656656e-08 | 0.0037098122 |
| +7 / -5 | 4.3350757e-08 | 0.001891048 |

Le contre-ordre est séparé de l’ordre attendu d’environ1,89 à3,78mm dans les trois poses combinées. Le contrôle distingue donc effectivement les compositions, au-delà du simple constat que le modèle bouge. Ces valeurs décrivent le candidat numérique ; elles ne mesurent aucune pièce physique.

Les axes du témoin source viennent du ZBlender et de `head_pitch_axis_world` des paramètresv2. Blender évalue `rest @ yaw @ pitch` sur son propre pivot ; aucun point attendu n’est reconstruit depuis une matrice navigateur. L’extraction utilise le vrai sommet évalué83 de `RH continuous mirror edge seal - estimated`. Babylon retrouve le même point au repos à son index169 et conserve cet index dans les quatre poses. Deux indices exportés coïncident à cet endroit, ce qui est consigné ; aucun marqueur ni attribut n’a été ajouté au modèle.

Source`af1bfd1155b02281eb549b428042728e55f7975f0fdc449806bb288d850e0a58`, GLB`a5765a2c2b2c9b5aaefc9a7cc2e95b587731269e05227394b8f84c5058944e70`. Les octets du GLB effectivement reçus par HTTP ont aussi cette empreinte ; catalogue chargé identique à l’entrée locale `mirror-right-v2`, aucune pose clampée, zéro erreurJavaScript/HTTP. Source, export, paramètres, entrée sélectionnée et inspecteur sont contrôlés inchangés après la session.

Deux outils neufs réutilisables, [documentation](../../../../tools/rotation-parity.README.md) : `tools/extract_blender_rotation_witness.py` et `tools/check_blender_browser_rotation_parity.py`. CompilationPython et aideCLI vérifiées, puis exécution complète réussie sur le port4143. Extraction Blender en lecture seule, threads1, sans rendu/export/sauvegarde ; processus et Chromium confinés au CPU3 après coordination avecA/B. Les inspecteurs, outils historiques, sources et registres partagés n’ont pas été modifiés.

Ce contrôle porte sur un témoin de bord et ces quatre poses. Il ne vérifie pas tous les sommets, les collisions mécaniques, les limites de réglage réelles, les matériaux, le verre ou la fidélité optique.

SHA256 du rapport : `d19c24b5baba5470f0ec512dd85ae7268da87754176636f434446ab70dd4caf2`.

SHA256 du témoin source : `11e0446d8eede3087485156a17010bb1f2870f260fd774149dfcef36f0956ab1`.
