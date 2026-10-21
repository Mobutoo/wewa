# Boîtier de phare v2 — normales des nervures

Source `headlamp-housing-v2.blend`, export `headlamp-housing-v2.glb`, collection `WEWA_HEADLAMP_HOUSING`, racine fixe `HEADLAMP_HOUSING_ISOLATED_FRAME_UNPLACED`. Aucun rig ni montage cockpit certifié.

Cette révision corrige uniquement le champ de normales des côtés de quatre nervures courbes : leur profil C1 utilisait des normales constantes par segment. Le nouveau champ interpole les côtés avant arrondi et mise en forme, avec les coins terminaux francs conservés. Les positions et UV de chaque triangle indexé, ordre et enroulement inclus, et le JSON de matière effectif sont identiques à v1. Les sommets exportés peuvent être regroupés autrement lorsque les normales sont raccordées ; aucune identité des indices bruts n’est prétendue.

Les quatre vues96 de v1 restent des diagnostics avec marches de reflets. Deux nouvelles vues96 (dos et macro) contrôlent la correction ; voir les rapports et checkpoints de `creative/reviews/headlamp-housing-v2/`. Le protocole d’exposition r2 est le même, sans nouvelle retouche de lumière ou matière. Les UV triangulaires sans texture ne constituent pas un dépliage de patine final.

Pièce apparentée YDY02002 seulement : cotes, sections, profondeurs et résine estimées. Clip central supérieur et vis séparées absents ; optique et tous les autres éléments du phare restent séparés. Identité RDC, interfaces/installations et réception artistique ouvertes. Aucun test iPhone ni parité visuelle source/moteur déduit.
