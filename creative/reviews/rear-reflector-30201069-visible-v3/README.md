# Réflecteur30201069 v3 — UV cadre uniquement

Identité unique `MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001` / `LEGACY15-REAR-REFLECTOR`.

**Correction technique vérifiée ; G4/G5/G8 non reçus, aucun fit.** [Fragment PLAT](component-fragment.json) : fichiers relatifs à `assets-src/moto-components`, revue basename. [Plan](../../research/rear-reflector-30201069-visible-v3/technical-plan.json).

## Source et contrôle strict

[Réouverture](source-reopen-check.json), [UV natifs](native-UV-rechart.json), [export/parité stricte](strict-export-parity.json). Le seul rechart touche les boucles des polygones cadre, depuis le source Blender. Face buffers P/N/UV/T + index, texture normale, matériaux et toutes positions/triangles orientés/normales sont identiques à v2. Aucun postrepair GLB, aucune normale ou tangente fabriquée artificiellement, aucun attribut supprimé.

Face101T dot0 ; cadre816T max|N·T|0.00009984513, limite0.001 sur TOUTES les primitives. NormeT erreurmax0.00006364431, W=+1 ; aireUVmin cadre0.00000425361, face0.00048225447. Le cadre a encore des tangentes/UV inutilisés par son matériau, mais ils sont valides. glTF0erreur/0avertissement, deux informations inutilisation conservées.

## Images effectivement relues

[Aperçu large](preview-source-broad.png), [aperçu ponctuel](preview-source-compact.png), [lecture](preview-review.json) : exactement les mêmes pixels natifs que v2, aucun effet visuel du rechart non texturé.

Trois vrais rendus natifs96 du sourcev3 : [large](whole-source-broad.png), [ponctuel](whole-source-compact.png), [neutre HDR](neutral-outdoor.png). [Rapport](render-report.json), [EXR32](raw-render-check.json), [lecture finale](final-review.json). Lumières large/ponctuelle et HDR restent les mêmes protocoles que v2 ; exposition0/gamma1, AgX MediumHighContrast,900×700. Aucune calibration couleur/source.

Babylon réel : [trois-quarts](inspection-boyle-v1/engine-quarter.png), [face](inspection-boyle-v1/engine-driver.png), [coupe revers](inspection-boyle-v1/engine-reverse.png), [paysage](inspection-boyle-v1/engine-landscape-844x390.png), [contrôle](inspection-boyle-v1/engine-check.json), [caméra](native-camera-parity.json). Exportv3 réellement chargé, texture prête, canvas non vide, sans erreurJS/HTTP. Le revers ouvert montre l'omission documentaire, pas une pièce pleine ou un montage. Projection/éclairage moteur différents du natif : aucune parité photométrique ni qualification mobile physique.

## Limites et conservation

Matièrev2 et géométriev1 héritées sans nouvelle réception. Dimensions estimées80×50×6mm, courant RDC conditionnel, les quatre interfaces M5/revers toujours inconnues ; ni goujon, ni siège/contacts, ni dos ajouté. Aucun transport rétro-optique certifié. Anciennes versions/manifestev1v2 intacts vérifiés par SHA. Nouveau manifeste auto-exclu, protocoles snapshotés, fichiers0444 (pasWORM), pasGit/root/cataloguepartagé modifié.
