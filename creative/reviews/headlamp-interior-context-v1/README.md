# Contexte P06 v1 — regroupement provisoire, optique bloquée

Livraison d’étude seulement, G8 pending. Aucun `headlamp-interior-completion-v1` : la cuve DJ201051 et ses facettes restent inconnues. L’audit nouveau est dans `../../research/headlamp-interior-evidence-audit-v1/README.md`.

## Inventaire et périmètre

Six sources natives effectivement ouvertes et sept GLB lus par leurs buffers POSITION : housing-v2 apparenté, cage-front16-v2, cap-front12-v1, base-front16-v1, flange-front15-v4, capsule-front15-v1, puis export nouveau. Quatre rendus antérieurs matière (base, flange, capsule et cage) réellement ouverts. La vue housing-v2 citée dans la fiche historique est absente du workspace ; elle n’est pas prétendue relue. `native-inputs.json` inclut les objets de construction pour inventaire ; seuls les objets non hide_render sont copiés dans les scènes d’étude.

`assets-src/moto-components/headlamp-interior-context-v1/headlamp-context.blend` contient l’ampoule principale et trois scènes isolées HOUSING, CAGE et CAP. Ces trois scènes ne constituent aucun montage commun ; elles préservent les repères natifs. La source contient aussi une sauvegarde Blender `.blend1` de la préparation avant correction de périmètre d’export, conservée comme historique, pas livrable actif.

`bulb-provisional.glb` contient seulement base, flange et les deux régions de capsule : quatre maillages, aucune cage, aucun capuchon ni housing. Le premier export incluait à tort d’autres scènes ; `use_active_scene=True` a corrigé ce point avant les rendus finaux et le gel. Le contrôle de buffers a été refait après correction.

## Poses et bornes

Les deux photographies opposées du même CL201023 justifient l’ordre flange/base/capsule et leur axe commun, pas un foyer optique. Base et flange conservent les repères auteur. La capsule est translatée de +6,2mm sur Z pour rejoindre la coupe de bouche de la base. La plage de travail3,2–6,2mm représente0–3mm de recouvrement exploratoire sur cette bouche native ; elle n’est ni une mesure photo ni une tolérance de montage validée. Le choix reste provisoire et G1/G5 ne sont pas déclarés passés pour les interfaces.

Les bornes héritées restent estimées : base rayon12–16mm / longueur10–17mm ; capsule rayon7,5–9mm / longueur36–45mm ; flange rayon20–23mm et tôle0,3–1mm ; cage rayon21–28mm / hauteur4–10mm. Elles décrivent des études isolées, pas leur compatibilité. Le raccord annulaire flange/base, les sertissages, soudures, contacts, filament, paroi interne et support caché ne sont pas ajoutés. La silhouette du capuchon opaque reste claire sous cet éclairage ; composition/couleur réelle non calibrées.

Aucune source commune ne borne un recul ou une rotation de cette ampoule/cage dans le housing YDY02002 apparenté. Pas de placement monté, de répétition, de cote de foyer ou de montage physique revendiqué. Aucun G8.

## Vérification réellement exécutée

Aperçu12 échantillons puis paire720×720 source native / GLB réimporté à96 échantillons, Cycles CPU,2threads, séquentiels. Aucun rendu moto entière. PNG et EXR des deux vues lus ; EXR finis et réouverture native contrôlés dans `reopen-raw-check.json`. Préflight cadre/clipping dans `build-report.json`.

Observations : contour entier lisible, base étagée et trois oreilles visibles ; capsule transparente vide conforme au périmètre incomplet hérité, pas une ampoule achevée. Fond et réponse diffèrent entre source et réimport : `image-comparison.json` mesure cet écart sans réception artistique ni parité matière passée. Aucune émission sur les maillages ; les plages claires viennent de l’éclairage et des hypothèses matière héritées. Pas de contrôle Babylon.js, donc G6 reste ouvert ; aucune qualification mobile.

Sources documentaires privées : URL/SHA/observations dans le dossier d’audit ; aucun pixel documentaire distribué. Nouvelles écritures limitées aux trois dossiers du manifeste. Aucun Git, racine, catalogue ou board ; six sources natives vérifiées inchangées en fin d’exécution.

Terminé : audit nouveau borné, inventaire natif/export, regroupement d’ampoule et scènes isolées, préflight, rendus96 et gel exact. Manquant : cuve nue identifiée, profil/glace séparée, interface housing/cage/ampoule documentée, raccords et réponse matière/export. Prochaine preuve utile : dépose du même phare identifié avec échelle, pas de nouvelle primitive optique.
