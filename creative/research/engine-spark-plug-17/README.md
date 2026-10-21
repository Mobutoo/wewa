# Lot 17 — bougie UG5 conditionnelle et capuchon

Photos isolées et fiche Champion obtenues, mais **montage exact RDC non identifié**. Le [JSON](reference-search-v1.json) conserve les vrais fichiers, URL, SHA256, observations et limites. Recherche coordonnée avec B ; aucune mesure n’est déduite du trou provisoire de sa culasse.

La branche documentaire reste celle de l’[audit extérieur](../engine17-exterior-coverage-v1/README.md) : D04 PDF35, planche23, **DD111018 « for Champion P‑RZ9HC » pour UG5**, cap **DD111048**, chacun quantité1. La ligne standard DG111008 et les variantes BM150/CT ne sont pas cumulées. Aucune conclusion twin-spark ou de nombre de bougies RDC n’est ajoutée.

## Dimensions réellement attribuées

La [fiche fabricant Champion](https://www.championpowersports.eu/ecat/code/motorcycle/spark-plugs/P-RZ9HC) donne le code de commande **P‑RZ9HC/T10**, code technique **P‑RZ9HC**, écartement **0,7 mm**, terminal **HC**, type résistif **K/R**. Son image technique6995 a été ouverte : les dimensions sont dans l’image, pas dans le texte HTML.

| Propriété | Champion, image6995 liée au produit | [Spareto, même référence commerciale](https://spareto.com/products/champion-spark-plug/p-rz9hc-t10) | Limite |
| --- | --- | --- | --- |
| Filetage | Diamètre **10** indiqué, pas absent | **M10×1,0** | Pas1,0 attribué au revendeur seulement |
| Longueur filetée | **12,5** indiqué entre flèches | **12,7 mm** | **Écart non résolu**, aucune moyenne ni conversion implicite |
| Clé | **16** indiqué | **16 mm** | Concordance sur ce produit, pas preuve de montage RDC |
| Siège | Bague/rondelle visible | « with gasket seat » | Pas d’épaisseur du joint écrasé mesurée |
| Saillie | Pas de valeur explicite | « Spark Position **2,4 mm** », « Projection **0,8 mm** » | Datums non définis ici ; ne pas additionner ni lire comme dépassement réel dans notre culasse |
| Borne | HC ; photo représentative avec borne SAE | M4/SAE | Vérifier borne filetée/écrou SAE et cap retenu |

L’unité des chiffres10/16/12,5 n’est pas répétée sur l’image ; leur lecture en millimètres est cohérente avec les valeurs du produit chez le revendeur. L’illustration ne donne ni tolérances ni certification métrologique d’un exemplaire. Le marquage photographié n’est pas PRZ9HC lisible ; elle reste une **image représentative liée par Champion à sa fiche**, sans autoriser la copie de tous ses détails. Aucun plan fabricant supplémentaire résolvant12,5/12,7 n’a été obtenu.

## Photos utiles et contradiction d’identité

- **Champion image6995**, `champion-P-RZ9HC-image-6995.jpg` : photo/illustration cotée, SHA256 `8d1c0dd26e044ec5c40ad028d2bbfdc94684518225f5efbe2cfd787efb90f694`.
- **Champion image62**, `champion-P-RZ9HC-image-62.jpg` : présentation couleur de bougie Champion POWER, céramique nervurée, borne, hexagone, bague et filet visibles. Code PRZ9HC non lisible ; pas de nouvelle cote.
- **[Maxy DD111018](https://maxygroup.co.ke/product/spark-plug-hc-bm150-bm125-bm100-dd111018/)**, `DD111018-maxy.png` : boîte lisible DD111018 « PLUG-SPARK (FOR CH…) », mais **bougie marquée BOSCH R6**. Céramique, hexagone, rondelle, filet et borne filetée nue visibles. Ce désaccord n’établit ni équivalence ni supersession officielle ; R6 ne suffit pas à identifier UR4AC. SHA256 `0ccc02a859f403af79354a44ccfc39973dced7b6287aebf8c17de1f9170b1c81`.
- **[Stock Nuts DD111048](https://www.stocknuts.in/product-page/dd111048-cap-spark-plug)**, `DD111048-stocknuts-1.jpg` : vrai capuchon isolé sombre, corps allongé avec élargissement et lèvre annulaire, port court coudé avec contact métallique fileté visible. SHA256 `8e54537df2d300f82160dce1491de10acb7226f3081b8859a25b6dcc1fb9d986`. Les vues2/3 ouvertes montrent seulement le sachet DD111048, daté10‑2021, **pas deux nouvelles faces de forme**.

Six images réellement inspectées au total, toutes privées dans `/workspace/wewa-assets/references/engine-spark-plug-17/`. Le JSON distingue une quatrième image Stock Nuts téléchargée mais non ouverte/utilisée. Aucun pixel constructeur ou vendeur n’entre au dépôt public ou aux textures.

Le cap n’a **aucune longueur, diamètre, angle ou résistance documentés** dans les sources lues. La vue opposée, son autre ouverture, la route du fil HT et le raccord installé restent à documenter. Ne pas reconstruire son intérieur depuis le petit contact visible. Pour la bougie montée, seule la portion extérieure effectivement découverte est à confronter ; les électrodes enfouies ne sont pas un détail visuel obligatoire.

Prochains verrous : identifier la bougie réellement montée RDC ; obtenir un dessin daté avec pas et référence de portée pour résoudre12,5/12,7 ; vérifier la borne et le même cap sur l’installation. Aucun achat, modèle, rendu, catalogue, registre ou inventaire complet ajouté.
