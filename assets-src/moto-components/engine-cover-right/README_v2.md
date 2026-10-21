# Carter droit v2 — correction des normales héritées

Même composant MOTO-ENGINE-COVER-RIGHT-001 et mêmes dimensions estimées. La v1 et ses manifestes restent intacts. `build_v2.py` ouvre la source185274, retire explicitement les normales personnalisées conservées après évaluation du modificateur WeightedNormal et enregistre une source/export v2 séparés. Les357132triangles de la coque, positions, faces, volume, trous et matériaux sont inchangés.

L’audit des images96 a révélé deux ruptures apparentes sur le chant arrière et des oreilles dentelées. Les deux mêmes caméras ont été rendues8avec cette seule correction en mémoire : ces défauts de reflets disparaissent. Les normales héritées différaient de plus5° sur20615coins, percentile99=21.8°, maximum92.7°. Ce diagnostic n’est pas présenté comme un rendu de la nouvelle source. `normal-state-equivalence.json` vérifie directement que le fichier v2 conserve exactement les normales ordinaires de cet état de diagnostic, les positions, les paramètres PBR et les lumières.

Le contrôle des vrais buffers GLB compare les triangles orientés Float32 de v1 et v2 par une signature canonique : la géométrie reste identique, malgré les éventuels splits de sommets liés aux normales. Zéro aire0, valeur non finie ou erreur glTF. La fermeture et le volume positifs sont recontrôlés dans la source.

Le raccord sombre entre les deux bosses reste visible après correction. Il est lié au relief construit et à l’éclairage ; sa conformité OEM n’est pas établie à partir des photos obliques/partiellement masquées. Sa profondeur, les sections supérieures, le dos et les attaches restent estimés. Aucun remodelage n’est déduit de ce seul changement de reflets.

Collection `WEWA_ENGINE_COVER_RIGHT`, parent `Engine RH cover provisional datum`, repère et limites identiques à v1. `render_v2.py` prévoit deux vraies vues96/OIDN et vérifie les sommets évalués contre le cadrage et near/farclip avant chaque image. Checkpoints locaux révisés liant aussi le SHA du script et le clipping. Les images96, le navigateur et la réception artistique restent des preuves distinctes. Aucune qualification matérielle iPhone.
