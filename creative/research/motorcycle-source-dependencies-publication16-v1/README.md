# Source16 — audit statique borné de trois sources

Base immuable `ff197f3084c92058bd4b2638813049ea497b107b`. Aucun stage ni cutoff fixé. Le [rapport](report.json), la [fermeture exacte](source-closure-v1.json) et les [entrées par phase](stable-recipe-inputs-v1.json) pointent uniquement les trois sources nommées, sans renderer ni modification de source/globaux.

| Unité | Gel vérifié | État réel |
|---|---|---|
| Patin JB122003 candidat 1 | source 40, 7e8f4603/cba76569 | Géométrie et matière partielles ; pointes sans bouches, face opposée/contact inconnus ; finales 96 actives au début de l’audit. |
| Support métal LH v1 | préflight 70, 4738deb0/86fe3105 | Métal seul, sans caoutchouc ni vis cadre ; matière 2 µm et essai 8 µm archivés, six finales 96 actives. |
| Embase grise 7 | étude 26, 6008367f/fe865b4b | Plaque/ajours/reliefs/nervures partielles ; trois vues 12 spp grises/reflets, aucun matériau final ni finale 96 ni nouveau type de production enregistré. |

**136 paires SHA/octets vérifiées, zéro écart.** Les trois gels ne référencent aucun autre manifeste. Les finales actives ne sont pas figées ici. Les surfaces connues ne terminent aucun groupe ; art et iPhone restent non reçus.

## Reprise matière et dépendances effectives

Le patin possède une baseline publique G3. Restaurer ses deux binaires et les quatre contrôles dans une copie isolée, conserver la lecture grise liée aux SHA et le plan matière, puis appliquer material.py. Il écrase les chemins actifs et n’est pas idempotent sur le PBR. Les cartes normal/ORM512² sont originales, sans photo, graine 15123, relief/rugosité estimés. Les petits contrôles actuels de rendu et de raccord hors source 40 sont explicitement listés.

Le support LH appelle réellement la CSG : helper control_geometry → front-brake-plate/csg.py → **manifold3d 3.3.2 dans le Python hôte**, avec NumPy. Les volumes et JSON temporaires proviennent de la construction courante. Depuis le maître géométrique fourni, la matière n’a plus besoin de refaire cette CSG ; elle lit la vraie revue grise, les trois PNG originaux et leur provenance de génération. Le générateur Gaussian/SciPy/Pillow, graine 113000, n’échantillonne pas de photographie. L’état 2 µm courant et l’état 8 µm historique restent distincts, avec leurs contrôles protégés ; aucun maillage n’a été recalculé par cet audit.

Aucune police, HDR ou photo privée n’est requise pour ces trois recettes. Les extractions UV/PNG WIP du support sont régénérées par son checker Node. Les checkpoints/rendus de revue historiques ne deviennent pas des textures ni une preuve de replay propre. Aucun pixel privé ou EXR n’a été copié.

## Embase 7 : pas de fermeture artificielle 1–6

Le gel 26 **ne contient aucun manifeste antérieur**. build_study_v7.py est autonome : paramètres 7 et existence du plan 7 seulement. Le renderer gris utilise le source courant, build-report et l’outil caméra commun. Il n’a pas de pipeline matière/final96. Les études 2/4/5/6 ne sont donc pas nécessaires à cette recette.

Les deux comparateurs livrés requièrent seulement GLB+rapports1 et3 et deux témoins de régions source. Les quatre baselines BLEND/GLB1/3 totalisent **4 646 020 octets**. Les scripts de lecture seule extract_outer_rim_v1.py et extract_apertures_v3.py régénèrent les témoins aux chemins WIP attendus, puis les comparateurs1→7 et3→7 peuvent être lancés. Ces commandes sont nommées dans le rapport ; aucune extraction n’a été exécutée et aucune identité byte à byte d’un témoin fraîchement régénéré n’est prétendue. Les deux témoins numériques existants ont été hachés, sans copie publique ; ils ne contiennent aucun pixel documentaire.

Les générateurs/paramètres/plans autonomes 1 et 3 sont aussi nommés comme reprise optionnelle des baselines. Cela ne demande ni publication des anciens manifestes ni aspiration des essais intermédiaires. Les invariants de comparaison gardent leur portée exacte : régions POSITION/UV et différences de normales stockées rapportées ; pas toute la triangulation, tous les caps ou une fidélité photographique.

Le [relais hors gel](../../reviews/seat-base-study-v7-handoff/README.md), son JSON et l’alias/README root sont listés séparément. Leurs10entrées d’admission sont vérifiées sans en faire un nouveau manifeste. Ils distinguent nettement visibles NONfabriqués (autres nervures/spine, piédestaux/tampons, montants, projection arrière, retour/agrafes, petites plages) et faces cachées inconnues. Le catalogue d’inspection n’active aucune pièce de production. Aucun rootproduction C générique ou vues 96 spp n’est attendu de cette étude.

Les href locaux des README nommés sont vérifiés sans dispense globale. Joint 2 et unités suivantes restent hors de cet audit ; les gels, modèles et registres antérieurs restent inchangés. Aucune réception artistique ou de montage n’est déduite de l’intégrité des fichiers.
