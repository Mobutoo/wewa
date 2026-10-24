# Derniers éléments — vérification des variantes et blocages

Reprise du 22 octobre 2026 après la correction des pontets. **La moto ne peut pas encore être déclarée finalisée.** Les contrôles CI du commit `424a83fbc5d5debddfe656b43d611ecf15a5d200` ont réussi, y compris le build, les preuves des assets et les essais navigateur : [exécution 39856542474](https://github.com/Mobutoo/wewa/actions/runs/39856542474). Cela valide la livraison technique, pas les interfaces encore inconnues.

## Transmission : précision obtenue

Le [catalogue constructeur BM125 UG, copie lisible en ligne](https://www.scribd.com/document/811934465/Boxer-BM-125-UG-Provisional-SPC-2), planche 33 / page imprimée 70, sépare **36JV0010 + DH151047** et **36PF0010 + DS151068** pour la version UG cinq vitesses. La table donne aussi une chaîne JV141004 pour cette dernière. Les six vis de la ligne commune ne suffisent pas à attribuer six perçages au porte-couronne UG photographié avec quatre trous. Il faut conserver les branches du catalogue séparément.

| Source constructeur consultée | Branche établie | Limite pour la référence retenue |
|---|---|---|
| [BM150, révision septembre 2011](https://www.safexbikes.com/parts_catalog/boxer%20BM%20150.pdf), liste des kits, page imprimée 97 | 36PF0010 contient DX151023, 42 dents ; JZ551004, 14 dents ; JV141004, 122 maillons. | Variante BM150 historique, pas une identification de la 125HD RDC actuelle. |
| [BM150, révision mars 2017, copie du document constructeur](https://www.slideshare.net/slideshow/boxer-bm150-spc-pdf-2017pdf/259967381), liste des kits | Le même code de kit est associé à DJ151086, décrit avec 43 dents et quatre amortisseurs. | Le code du kit seul ne permet pas de choisir la révision de la couronne. |
| [Page officielle Boxer 125HD RDC](https://www.bajajauto.com/fr-cd/bikes/boxer-125hd) | Confirme la cible cinq vitesses, les jantes alliage de 17 pouces et l'empattement de 1 285 mm. | Ne précise pas la couronne, le porte-couronne, leur déport, les fixations ou le chemin des câbles. |

Les études six trous / 44 dents ne sont donc pas à transformer automatiquement en une couronne quatre trous. Une branche quatre trous cohérente existe dans les références apparentées, mais son identité pour la moto actuelle, son nombre de dents et ses dimensions restent à déterminer. Choisir 42 ou 43 dents uniquement pour finir l'assemblage contredirait la procédure du dépôt, qui demande de conserver les variantes et les contradictions.

Le téléchargement du PDF D04 sur son hébergement historique `motobro.ua` a échoué : HTTP 429 par téléchargement direct, HTTP 502 par lecture web. La copie textuelle du document a permis de relire la table ; aucune nouvelle vue cotée n'a été obtenue. Les documents consultés ne sont pas redistribués dans le dépôt.

## Autres blocages confirmés

- **Béquille latérale** : la référence DF161102 est retrouvée avec un écrou M10 dans des catalogues apparentés. Cela ne fournit pas le diamètre ni la longueur mesurés de l'épaulement, ni un œil compatible avec l'estimation actuelle de 9 mm. Le [dossier existant](../powertrain-completion-p17-v1/side-pivot-physical-plan-v11.json) conserve précisément ces inconnues.
- **Commandes** : la vis M6 est documentée pour une variante apparentée, tandis que l'alésage de 4,3 mm et son axe proviennent du modèle auteur. Les [observations du support](../control-perch-clamp-bolt/observations-before-form.json) interdisent de présenter cette paire comme montée sans reprise conjointe justifiée.
- **Guidon** : le [passage latéral est corrigé](../../reviews/handlebar-registration-v2/README.md). L'épaisseur comprimée des silentblocs, la longueur engagée et les sièges restent inconnus ; installer la pile existante ne démontrerait pas son ajustement.
- **Câbles et durites** : les segments observés ne définissent pas leurs raccords complets ni la réserve de longueur aux butées de direction. Il manque des vues continues de la moto retenue.

## Donnée ou choix nécessaire pour poursuivre

Pour poursuivre la reconstruction fidèle, il faut une identification de la variante de transmission, des vues montées/déposées des raccords et les dimensions critiques de ces mêmes pièces. Un catalogue explicitement applicable à la 125HD RDC retenue ou des observations de cette moto permettraient de lever ces inconnues.

L'autre voie serait de faire de Wewa une adaptation visuelle assumée, avec des interfaces conçues pour être cohérentes entre elles et clairement marquées comme estimées. Cette décision de fidélité n'a pas été fournie en réponse à la question posée pendant la reprise ; elle n'est pas déduite du silence. Aucun changement de variante ni montage fictivement certifié n'est donc livré ici.

La réception artistique et les essais Safari physiques restent deux validations distinctes. Les [travaux et critères de finition](../../workflow/motorcycle-finishing-plan-2026-10-22.md) demeurent ouverts ; aucun travail autonome n'est annoncé continuer après l'arrêt de l'objectif sur ces données manquantes.
