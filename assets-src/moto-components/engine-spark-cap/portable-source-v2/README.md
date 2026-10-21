# Sources compagnons de portabilité — distinctes des maîtres de rendu

`engine-spark-cap-v2-portable.blend` (c5e0756e79aab4d588634b7bceff7ea6cac12d00937d1224f0fa2ed67885db96) conserve exactement le composant du maître **bceb87f8…**. Ses guides restent séparés. Son contexte bougie2 utilise `engine-spark-plug-v2-context-portable.blend` (130f06eed047b07c11b35ae7ac19cc885e62d99e89f8f0f90f3f11f211a13aa4), qui rend aussi relatif le lien vers le capuchon1 historique.

Le maître original, les rendus96 et le GLB **2a924e6e…** gardent leur identité ; aucune nouvelle réception ni export. Garder ces deux fichiers ensemble à cette place relative dans le dépôt, ainsi que les ancêtres publics existants. Les textures propres sont intégrées, les chemins Library sont relatifs.

Preuves, outils génériques et test réel13BLEND/18liens déplacés : [audit de portabilité](../../../../creative/research/engine-spark-cap-portability-v2/README.md).
