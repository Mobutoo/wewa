# WEWA : mandat de développement autonome

Lire README.md, docs/PLAN_DE_PRODUCTION.md, config/product.json, backlog/tasks.json et validation/STATUS.json avant une modification. Le dossier conceptuel R8 reste la référence narrative ; ce kit fixe la cible navigateur.

## Exécution
- Choisir la première tâche pending dont toutes les dépendances sont done. Marquer in_progress, réaliser une tranche verticale, vérifier ses critères puis enregistrer les preuves et le statut.
- Ne jamais marquer done une vérification non exécutée. blocked exige une cause et la prochaine action. Conserver les décisions dans docs/DECISIONS.md.
- Limiter les changements au périmètre de la tâche. Ne pas réécrire le moteur ou changer de stack sans preuve d'un blocage de performance ou de compatibilité.
- Continuer les actions réversibles déjà autorisées. Signaler un besoin de données, de droits, de compte ou de budget réel ; ne pas inventer l'accès.
- L'autonomie s'exerce pendant une session d'exécution. Ce kit ne lance aucun travail permanent ni service en arrière-plan.

## Géographie et assets
- Les coordonnées sources sont immuables. Stocker les adaptations de jeu séparément avec source_id, raison et version.
- Les hauteurs estimées doivent rester identifiables. Un GLB généré est un blockout jusqu'à validation artistique et géographique.
- Conserver les trous et les parties de bâtiments ; résoudre les superpositions avant production. Vérifier les ponts, niveaux et traversées avant de construire le graphe de voies.
- Aucun fichier géographique complet de centaines de Mo dans le bundle web. Exporter seulement les cellules nécessaires.
- Tous les assets livrés doivent avoir une provenance, une licence et un statut de validation. Une photo de référence n'est pas automatiquement une texture utilisable.

## Jeu et qualité
- PC clavier + mobile tactile, commandes remappables ; ZQSD et WASD, freiner, élan, pause, reprise. Simulation fixe, rendu interpolé.
- Tester conduite, collisions, recherche de cible, mission terminable et reprise après perte de focus avant d'embellir.
- Maintenir le rendu WebGL 2 ; WebGPU reste optionnel jusqu'au benchmark. Éviter toute dépendance de gameplay à un effet réservé à WebGPU.
- Respecter config/performance.json comme budgets initiaux révisables avec preuve. Une cible de FPS n'est jamais un résultat mesuré.
- Pas de déclaration top 10 %, photoréalisme atteint, livraison complète ou validation mobile sans preuves réelles.
- Aucun paiement réel en V0. Conserver les publicités fictives et les droits d'achat simulés clairement indiqués comme démonstration.
- À chaque jalon : build, contrôle du contenu, session jouable, journal des limites. Si le navigateur de test n'est pas disponible, ne pas présenter le jalon de jeu comme validé.

## Livraison
- Git et lockfile pour le code du jeu ; assets sources séparés des exports ; versionner manifests et empreintes.
- Publier par le workflow d'hébergement disponible, avec accès privé par défaut. Ne pas changer l'audience sans instruction.
- Rapport final : livré / testé / non testé / problèmes restants / prochaine tâche. Ne pas confondre maquette, démo jouable et version commercialisable.
