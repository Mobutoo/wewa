# Publication de travail 22 — sources, études et préparations

La demande « Pousse tout sur github » étend cette publication à tout le travail utile présent dans le dépôt : sources éditables, textures originales, recherches, études refusées, diagnostics, outils et préparations non exécutées. Le [pointage](publication-scope.json) distingue ces états. La base de préparation est `824c01d8116e2cf22f03a09479ae6d8591adc1af`.

Le registre conserve 95 identités physiques ; 104 fiches comprennent des travaux encore non fabriqués. Les 120 entrées du catalogue servent à l’inspection. Publier une fiche, une étude ou un script ne crée aucune nouvelle pièce reçue. Tous les 18 groupes restent ouverts ; aucune réception artistique, qualification iPhone ou reconstruction depuis un clone propre n’est revendiquée ici.

| Travail ajouté | État à cette observation |
|---|---|
| [Terminal B](../../reviews/engine-protection-terminal-b-v1/manifest.json) | Source 68 et cinq finales 96 closes, candidat auteur non inscrit comme nouveau physique. |
| [Guide des jonctions](../../reviews/engine-protection-junctions-guide-v1/guide-manifest.json) | 34 fichiers fermés, copies de quatre sources existantes ; zéro nouvelle pièce. |
| [Coque de connecteur2](../../../assets-src/moto-components/ignition-connector/preflight-manifest-v2.json) | Source 66 stable ; revue finale encore en calcul. Les vues finies sont liées individuellement par leurs checkpoints. |
| [Lentille ambre](../../reviews/indicator-front-lens-v1/freeze-manifest.json) | Source 31 et finale 40 closes ; études précédentes conservées avec leurs limites/refus. |
| [Corps de clignotant](../../../assets-src/moto-components/indicators-front/housing/parameters-study-v1.json) | Paramètres et code préparatoire ; aucun BLEND/GLB/PNG créé. |
| [Cockpit 4](../../../assets-src/moto-components/cockpit-updated-review-v4/README.md) | Recettes et vérificateur préparés, non exécutés ; aucun nouvel assemblage livré. |
| [Diagnostics AO](../ao-uv-padding-blender43/README.md) | Petits scripts/mesures/échecs conservés ; aucune validation de bake. Les gros fichiers échoués restent privés. |

Les photographies documentaires, environnements, secrets, sauvegardes Blender, logs bruts et buffers temporaires privés restent exclus. Trois petits logs d’échec du guide des jonctions sont admis nommément car le manifeste 34 les fige ; ils contiennent les erreurs Python historiques et chemins publics, sans environnement ni secret. Aucun nouveau fichier privé externe n’est copié par cette préparation. Les deux synthèses encore changeantes de la coque (`render-report.json` et `author-final-read-progress.json`) sont différées ; leur absence ne masque pas l’état actif de la série. Les scripts préparatoires et rapports historiques peuvent citer des chemins privés : ces citations ne prétendent pas livrer les fichiers correspondants. Les tables des rapports historiques restent des instantanés ; seules les véritables tables de manifestes et gels sont contrôlées comme dépendances figées.

Le curateur privé produit une liste explicite et vérifiée avant toute indexation par le coordinateur. Ce dossier ne revendique aucun commit, push ou résultat CI.

## Envoi et vérification

Les 1 285 fichiers de travail sont poussés dans [`a2c2aab7`](https://github.com/Mobutoo/wewa/commit/a2c2aab7c65dd12c5dcf320f8fcbdca1943f78b3). Le complément [`78bb12b3`](https://github.com/Mobutoo/wewa/commit/78bb12b388d25d62becf2a64126839ad38af5988) fournit les 11 dernières sorties et synthèses du connecteur : la série comporte désormais quatre vues finales, après sortie du worker et revue auteur. Tous les fichiers utiles présents à cet instant sont poussés ; le dossier de travail était propre et aucun calcul n’était actif.

Le contrôle local du commit final, arbre `22e027cb641f8d0355ce890d5d4ec93857aa8f4e`, relit 5 292 JSON, 424 manifestes, 13 389 empreintes, 69 empreintes PNG de checkpoints et 6 326 liens, sans erreur dans ce périmètre. [Le rapport](../../../WEWA_Developpement_Web/validation/motorcycle18-source23-integrity.json) distingue les 95 identités physiques des 104 fiches. Les trois nouveaux candidats auteur ne sont pas automatiquement inscrits comme pièces reçues.

Le PRD complet Ewutelo est sauvegardé et relu en révision 47 : tous ses champs sont égaux et ses 45 exigences sont conservées. GitHub Actions a réussi pour [Source21](https://github.com/Mobutoo/wewa/actions/runs/39616838008) ; les contrôles [Source22](https://github.com/Mobutoo/wewa/actions/runs/39619608578) et [Source23](https://github.com/Mobutoo/wewa/actions/runs/39619933110) sont encore en cours à cette observation. Aucune réussite distante non observée n’est annoncée. La fabrication des 18 ensembles reprend après cet envoi.
