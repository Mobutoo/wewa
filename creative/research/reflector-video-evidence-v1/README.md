# Réflecteur DJ201051 — recherche vidéo v1

Gel documentaire autonome, sans fabrication ni Git. Les pixels restent hors dépôt dans `/workspace/wewa-assets/references/reflector-video-evidence-v1/`. Aucun ancien gel ni registre partagé modifié.

**La géométrie du réflecteur reste bloquée.** Aucune glace séparée, cuvette nue, coupe ou frame vidéo n’a été vue. Aucun timecode probant ni SHA256 vidéo ne peut être fourni : les octets vidéo n’ont pas été obtenus. Les champs correspondants sont vides/null, jamais remplacés par la durée du film.

## Pistes publiques nouvelles

| Piste | URL | Durée indexée | Résultat / limite |
|---|---|---|---|
| MOTORCYCLE HEAD LIGHT REPAIR(BAJAJ BOXER). Full easy steps. | https://www.youtube.com/watch?v=-0U0LMGz7HI | 02:09 | Extrait indexé : changement d’ampoule, pas preuve de glace déposée. |
| bajaj boxer ct150 - DIY parklight bulb | https://www.youtube.com/watch?v=AbEgEam7d30 | 04:09 | Piste bouche pilote ; non vue. |
| cambia el foco de tu moto en menos de 5 minutos — Boxer 150 — Rod Rider | https://www.youtube.com/watch?v=XICuB33jVh0 | 03:46 | Changement H4 ; verso éventuel non vérifié. |
| BAJAJ PULSAR HEADLIGHT DEEP CLEAN / REFLECTOR POLISH — Technical Masterji | https://www.youtube.com/watch?v=vbG7Z76y78k | 21:59 | Piste prioritaire seulement après confirmation génération ronde et origine ; non vue. |
| Pulsar 150 headlight restoration — Paint it | https://www.youtube.com/watch?v=IvfXYcB95cQ | 04:37 | Extrait indexé : ponçage/polissage ; cuvette nue non établie. |
| Bajaj Pulsar 125/150/180 headlight glass unboxing price | https://www.youtube.com/watch?v=tZhB7aoXIEU | 02:02 | Forme/génération inconnue ; non vue. |
| Bóxer ct100 cambio de farola parte1 Varroc | https://www.youtube.com/watch?v=6uopcXZieYE | 06:57 | Variante voisine, origine revendiquée dans description indexée seulement. |

Tous ces candidats restent `related` provisoires, sans preuve visuelle. Les autres résultats et exclusions explicites figurent dans `video-candidates.json` (Pulsar220/NS/AS, auto, miroirs, interrupteur, etc.). Aucun candidat vidéo `exact` validé.

## Images réellement examinées

Les quatre références privées de départ ont été ouvertes, y compris Prom-0 et Prom-1 : même pose, autre résolution, pas deux vues. La ligne continue devant les projections d’ampoules et les reflets n’isolent toujours pas les frontières physiques des facettes.

Nouvelle galerie fabricant : https://www.unomindakart.com/product/uno-minda-hl-51001-head-light-assembly-round-for-bajaj-pulsar . `minda-1.jpg` montre un phare rond **vitré et assemblé**, bouche principale centrale et pilote inférieur. `minda-2.jpg` montre réellement le **boîtier noir arrière complet**, avec deux fenêtres et câbles ; ce n’est pas le verso de la cuvette. `minda-3.jpg` est un montage de dimensions commercial, rejeté comme relevé physique. Les deux photos Parton Wheels sont des reprises apparentes des mêmes clichés fabricant (marques jaunes et câbles identiques au dos), dont la face porte un gros filigrane. Elles ne comptent pas comme vues indépendantes.

HL-51001 est une référence de remplacement pour Pulsar ROUND, pas une identification démontrée DJ201051/RDC. La page fabricant fournit «19 x 17 x 20» sans unité dans le tableau, tandis que le montage indique 20cm ; aucun transfert de cote au diamètre de glace ou à la profondeur du réflecteur n’est justifié. Les observations restent `documented_related_variant` / `photo_inferred`. Les fichiers, URL et SHA256 de toutes les images effectivement vues sont dans `images-viewed.json`.

## Accès et portée

YouTube direct et yt-dlp (version 2026.10.21) : tunnel proxy 403. Vignettes i.ytimg : même refus. Aucun extrait téléchargé, aucune frame décodée ; ffmpeg disponible mais sans entrée vidéo. Aucun contournement des refus, authentification, DRM ou captcha. Brave a permis la découverte par texte public ; ce texte n’est pas une inspection de vidéo. Bing a fourni des résultats manifestement hors sujet, Google une coquille JS, DuckDuckGo une réponse challenge 202, Yahoo une boucle de redirection, Dailymotion une coquille HTML. Le service web intégré a renvoyé deux erreurs vides. Chaque échec concerne ce canal et cette session, sans preuve d’inexistence.

Le circuit public Team-BHP (restauration Pulsar150Classic, pages1–2) répond403. Pas de tentative sur les anciennes pièces jointes AutomotiveIndia refusées. Motozilla/MercadoLibre/MotoMarket et les APIs épuisées ne sont pas relancés, conformément au retour main. La correspondance catalogue Pulsar180Clasica/DJ201051 vient du registre front16 lu ; sa page PDF n’est pas nouvelle preuve visuelle.

## Décision et suite

Aucune nouvelle face ni relief DJ201051 n’est identifié avec assez de certitude pour construire. Impossible de borner numériquement la profondeur, les normales ou le profil des bouches. Les zigzags et bandes lumineuses ne sont pas convertibles en profondeur. La référence voisine ne ferme pas G1.

La prochaine preuve utile reste une dépose de glace d’un original identifié, cuvette nue de face et oblique, profil/verso avec les deux bouches, lumière diffuse ou mobile et échelle. Les URL vidéo ci-dessus sont des pistes à inspecter lorsque leur accès public normal sera disponible ; aucune continuation permanente n’est supposée.

Terminé : découverte et classement, contrôle visuel des photos nouvelles, journal d’accès, limites et manifeste. Manquant : vidéo vue, timecodes probants, cuvette nue exacte et glace séparée. Aucune modélisation, texture, image synthétique, publication de pixels ou réception artistique.

Le manifeste couvre les JSON/Markdown du gel et les octets privés acquis ; il exclut sa propre empreinte pour éviter une dépendance circulaire. Fichiers du gel passés en lecture seule ; empreintes = contrôle d’intégrité local, pas stockage WORM.
