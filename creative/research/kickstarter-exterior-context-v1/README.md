# Kick extérieur P20 — composition de l’existant

Dispatch du coordinateur dans l’objectif utilisateur de terminer la moto. Aucun nouveau composant physique ni forme créée : identité MOTO-KICKSTARTER-001 conservée. Le parent historique était routé P14 ; ce fragment est routé P20 sur demande du coordinateur.

Quatre objets du natif kickstarter-v2 sont réemployés, avec leurs vrais datablocks liés et matériaux historiques : collier/chape, bras/œil, caoutchouc strié, embout chromé. Trois objets historiques estimés (vis, écrou, axe de pliage) restent exclus sans remplacement. L’ensemble garde la pose repliée réellement enregistrée, et non une valeur initiale de contrôle catalogue.

## Repère et montage

`native-links-and-transforms.json` contient les matrices sources réellement évaluées en ouvrant le natif. Une translation commune place le datum moteur à zéro ; aucune pièce n’est recalée individuellement. `coord-plan.json` donne l’inverse pour restituer le repère historique et le contexte RH uniquement conditionnel. Aucun ajustement sur le moteur actuel, amplitude mécanique ni certification de variante RDC n’est acquis. Les lacunes G1/G2/G5 de la source restent ouvertes.

Le wrapper direct est `assets-src/moto-components/kickstarter-exterior-context-v1/integration-wrapper.blend`, collection KICKSTARTER_EXTERIOR_INTEGRATION_V1, root KICKSTARTER_EXTERIOR_CONTEXT_ROOT. L’exemplar coord-exemplar.blend a été réellement rouvert par le vérificateur whole v3. Le GLB utilise les quatre maillages et matériaux du GLB historique, puis est comparé au natif réimporté triangle par triangle.

## Correction de préparation

Une première préparation lisait des matrices identitaires d’objets liés hors scène. La parité réelle a détecté cette erreur avant passage matière. Ses octets ont été archivés dans creative/reviews/kickstarter-exterior-context-diagnostic-v1 : ce diagnostic n’est pas livrable pour intégration. La préparation corrigée lit le natif ouvert et évalué ; le natif historique reste inchangé. Les seuls gris admis sont gray-preview-v2, relus avant les deux material-preview-v2.

## Limites

Le réemploi ne reçoit pas artistiquement le modèle historique. Les rendus et Babylon contrôlent transport et composition. Les captures paysage ont une superposition de l’interface de laboratoire sur la projection ; aucun test matériel iPhone ni montage qualifié n’en découle. Les originaux documentaires restent privés ; le registre ne publie que chemins, URL, empreintes et observations.
