# Engine exterior completion v2 — correction de la joue inférieure

Correction exécutée du manque inférieur LH observé en v1. V1 reste inchangé. Pas G8 : le donneur BM150 JE541038 reste conditionnel, non certifié apparié au RH ni interchangeable OEM RDC125.

## Entrées rapides pour main

- `main-integration-fragment.json` : **remplacer** `conditional-lh`, **mettre à jour la pose seulement** de `conditional-service-port`. Les cinq parents moteur historiques et RH sont conservés chacun une fois. Aucun parent supplémentaire à superposer.
- `lh-donor-lower-apron-v2.blend` : enfant LH modifié, collection `WEWA_LH_DONOR_LOWER_APRON_COMPLETION_V2`, objet `LH_JE541038_DONOR_PERIPHERY_AND_OBSERVED_LOWER_CAST_APRON`.
- `lh-donor-lower-apron-v2.glb` et `new-child-data-report.json` : seul nouveau buffer géométrique nécessaire, métadonnées JSON effectivement lues dans ce GLB et SHA exacts. Aucun GLB moteur complet nouveau.
- `engine-exterior-completion-v2-linked.blend` : contexte moteur lié aux vraies sources, collection `WEWA_ENGINE_EXTERIOR_COMPLETION_V2_CONDITIONAL`. Ne pas superposer ce wrapper complet aux cinq parents historiques déjà dans le global.
- `poses-and-sources.json` : matrices monde v14 en mètres, incertitudes et provenance. Le recalage LH/col est une translation de Y = −0,0002874533 m et Z = +0,0084993287 m par rapport à v1, sans nouvelle rotation ni nouvelle déformation. Ces décimales sont des paramètres reproductibles, pas une précision physique mesurée.

## Diagnostic : caméra, pose, forme et variante

La caméra ne crée pas le défaut : l'ouverture inférieure est présente dans les triangles natifs et exportés. La source LH v1 représente principalement une paroi périphérique. La photographie du même exemplaire montre une joue extérieure sous la cavité du magnéto, jusqu'au passage de service. Son absence faisait lire le bas comme un anneau détaché. Le contour inférieur lui-même est photographié : il n'a pas été remonté artificiellement pour aligner toutes les silhouettes.

Le premier essai de rotation globale à 20° est **rejeté**, conservé dans `rejected-rigid20/`. L'inclinaison du cylindre est native, mais l'axe Y de coupe du donneur est une construction estimée : les confondre comme repères physiques produit un débord supérieur. La correspondance du centre du magnéto photographié avec le centre approché du capot natif justifie seulement le petit recalage retenu, avec incertitude ±8 mm. Le parent RH indépendant reste inchangé.

Le facteur axial estimé déjà utilisé en v1 est conservé pour cette comparaison ; v2 n'en fait pas une cote réelle. Les identités de donneur, profondeur assemblée, plans supérieurs et interfaces au cadre ne sont pas certifiées par cette correction. Main contrôle leur visibilité dans son assemblage global.

## Construction bornée et photographies

`G0-G2-apron-plan.json` conserve trois URL/SHA/observations de photos réellement lues (65219, 65221 et 65222), sans pixels documentaires redistribués. La joue s'arrête sous la cavité photographiée et au contour périphérique source. L'épaisseur est estimée à 7 mm (plage 4–12 mm), le bombé large à 1,5 mm (plage 0–4 mm), avec bord avant de revue conservateur. La bouche de service réutilise la station et le rayon de travail de la source précédente.

La joue et la paroi sont unies comme régions du **même moulage observé**, pas comme une soudure ou une plaque rapportée supposée. Aucun cube central, fond arbitraire dans la cavité, galerie, rouage, bouchon, fixation cachée ni marquage privé n'est ajouté. Les versions à contour croisé/union vide et l'essai plat sont conservés séparément. La solution finale utilise Manifold 3.5.4 ; le changement de solveur est lié à des défauts numériques détectés, pas à un changement de forme cible.

## Contrôles exécutés

- Enfant : 162 148 triangles, maillage fermé, zéro arête ouverte/branchée, volume positif. +2 818 triangles par rapport au parent LH initial.
- Les 51 906 sommets de la zone supérieure non modifiée sont conservés exactement (écart maximal nul).
- Six sondes BVH : cavité magnéto, zone arrière non fermée et bouche de service ouvertes ; matière réellement présente sur les deux stations de joue.
- Parité native/GLB réimporté : 162 148 triangles, aucun triangle ajouté/perdu, écart maximal de sommet nul. Le validateur glTF ne rapporte ni erreur ni avertissement ; normales effectives valides.
- Wrapper réouvert : huit instances évaluées, 1 462 720 triangles. Les anciennes sources sont liées, sans copies de leurs textures ou géométries.
- Trois vues natives 96 échantillons CPU, deux threads, 540×480, EXR float32 + PNG, cadrage/clipping contrôlés. Profil isolé complémentaire à 12 échantillons, réellement relu sans les capots.
- Babylon : référence au contexte v1 avec retrait effectif du LH et du col anciens, réimport des deux sources appropriées ; compte final 1 462 720 triangles, dix maillages de rendu après séparation des matériaux, textures prêtes, canevas non vide et aucune erreur de page. Ce contrôle logiciel ne qualifie pas un iPhone physique.

## Comparaison à lire

[Avant LH v1](../engine-exterior-completion-v1/native-left.png), [après LH v2](native-left.png), [source LH sans les couvercles](child-source-profile.png), [Babylon LH](runtime-left.png). Les photos sont référencées exclusivement par URL dans le plan ; leur caméra n'est pas calibrée. Ces comparaisons montrent la correction de la joue et du faux anneau, sans prétendre mesurer un écart photographique en pixels.

`frozen-outputs.json` définit la révision exacte livrée. Aucun ancien fichier, catalogue, board, racine ou historique Git n'a été modifié par cette reprise. Aucun rendu whole lancé. La correction locale est exécutée ; réception artistique et assemblage OEM complet ne sont pas déclarés acquis.
