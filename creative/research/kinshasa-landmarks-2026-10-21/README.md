# Collecte des lieux de Kinshasa pour Blender

Collecte du 21 octobre 2026, ajout documentaire pour Viva Wewa.

## Commencer ici

- [Dossier PDF de 33 pages](Viva_Wewa_Kinshasa_Collecte_Blender.pdf)
- [Catalogue local avec recherche](index.html) : ouvrir après téléchargement du dossier.
- [Registre des 51 lieux](registre_lieux.json), [CSV](registre_lieux.csv), [fiches individuelles](fiches/).
- [87 sources](sources.json), [97 médias sélectionnés](medias_selectionnes.json), [provenance](references/).
- [Huit matériaux génériques CC0 et 32 cartes 1K](textures_cc0/), [utilisation Blender](textures_cc0/UTILISATION_BLENDER.txt).
- [Géographie](geographie/) : 31 objets OSM, couvertures, métadonnées et aperçus de cinq jeux aériens.
- [Grille de collecte](grille_collecte.csv), [pistes d’archives](pistes_archives.csv), [critères de reconstruction](criteres_reconstruction.json).
- [Archive complète d’origine, découpée en 11 parties](archives/). Exécuter `python3 archives/reconstituer_zip.py` pour retrouver le ZIP original, avec contrôle SHA-256.

## Reprise dans Codex

Lire aussi `../../workflow/README.md` et la recette architecture dans `../../workflow/RECIPES.md`.
Ce dossier alimente la documentation G0/G1. Ses niveaux A/B/C mesurent la richesse documentaire, pas une réception artistique ni un passage G3 accordé.
La SOZACOM, le musée national et Zando sont les trois dossiers avec dessins et photographies complémentaires.
Les recommandations architecturales de ce dossier ne remplacent pas la priorité de fabrication courante de la moto dans le workflow.
Conserver les identifiants K001–K051. Décomposer bâtiment, façade, travée, toiture, statue, socle et place avant fabrication détaillée.
Ne pas réécrire les sources historiques du dépôt et ne pas modifier le jeu pour simplement importer cette collecte.

## Qualification et droits

Les documents sont des références de recherche. Les origines, licences et restrictions sont conservées dans les registres.
Une licence photographique n’établit pas automatiquement les droits sur l’œuvre représentée. `game_ready: false` reste appliqué aux médias de référence.
Les matériaux Poly Haven fournis sont génériques et CC0 ; ils ne constituent pas des relevés des matériaux kinois.
La mosaïque Maxar est annoncée non commerciale. Les cinq images aériennes locales sont des aperçus : les grands rasters ne sont pas inclus.
Aucune image Google Earth ou Street View n’est extraite. Les dessins et maquettes ne sont pas assimilés à l’état construit.
Aucun modèle Blender terminé, scan ou photogrammétrie validée n’est livré ni déclaré reçu.

## Intégrité

`manifest_fichiers.json` décrit les octets et empreintes du paquet d’origine.
`GITHUB_UPLOAD_MANIFEST.json` décrit l’ensemble de cet ajout, y compris les parties de l’archive, pour vérifier le transfert.
