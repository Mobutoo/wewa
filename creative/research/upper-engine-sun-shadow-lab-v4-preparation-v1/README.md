# Soleil et ombres v4 — code préparé, aucune capture exécutée

Le [lab v4](../../../tools/motorcycle-material-camera-lab-v4/index.html) importe le [v2 gelé](../../../tools/motorcycle-material-camera-lab-v2/review.js), qui importe le v1. Il n’importe pas v3/SSAO. Le [rapport de conservation](conservation.json) rattache les cinq nouveaux fichiers, les 22 entrées protégées inchangées et les huit fichiers API Babylon 9.31.0 réellement lus. Les contrôles de syntaxe JavaScript et Python passent ; aucun navigateur, Blender, rendu ou contrôle runtime n’a été exécuté pour cette préparation.

Le [protocole retenu](../upper-engine-sun-shadow-protocol-v1.md) fournit les deux caméras communes, le GLB `d0b1a121…`, la source `7c62b0c1…` et le HDR `206c67e3…`. Le lab garde le HDR à +π/2, intensité 0,3, exposition EV 1,91008748 et ACES. Les vues chaudes Blender existantes et leurs checkpoints restent des références liées, avec leurs pixels intacts.

W0 et W1 emploient une seule DirectionalLight : direction glTF `(0,638240 ; −0,397131 ; −0,659497)`, couleur RGB linéaire `(1 ; 0,72 ; 0,48)`, intensité Babylon **1,5 expérimentale**. Seul son `shadowEnabled` change entre ces deux états. Aucun sol, fill, autre lampe, AO ni pipeline supplémentaire n’est ajouté. La PCF est fixée à 2048² et `QUALITY_MEDIUM` ; le repli silencieux vers un autre filtre est refusé.

Les extents et la profondeur sont calculés à partir de chaque sommet réellement importé, transformé par sa matrice monde puis par la vue de lumière. Le padding par axe vaut `max(2 × span / 2048 ; 4 × normalBias)`, sans ajustement manuel. **Le bias API n’est pas en mètres** : les 20 µm demandés deviennent `2e-5 × abs(projection[10]) / BIASFACTOR`, où le shader 9.31 utilise `BIASFACTOR=0,5` en NDC demi-profondeur et `1` sinon. Le `normalBias` de 0,1 mm agit directement en espace monde. Les valeurs API, NDC, matrices prévues et matrices réelles du générateur sont rapportées.

La [capture v4](../../../tools/capture_material_camera_comparison_v4.py) traite systématiquement **les deux caméras**. Pour chacune :

1. Relancer le v2 intact et sauver son vrai canvas neutre ; sauver ensuite le vrai canvas v4 neutre, avec le soleil désactivé. Exiger l’égalité exacte des PNG décodés et des hashes `readPixels`, ainsi que la conservation des buffers/matrices/assignations, de la configuration caméra/HDR et des matériaux sérialisés (seuls les `uniqueId` sont omis pour comparer deux pages fraîches).
2. Capturer W0 puis W1. Exiger des pixels non vides, les huit témoins de projection à moins de 0,05 px — seuil logiciel, pas photographique — et la conservation exacte G/N/tous UV/T/indices/matrices/assignations et de la sérialisation PBR complète entre W0/W1.
3. Consigner les 14 meshes runtime, leurs sources de géométrie partagées éventuelles, les casters et receivers complets, le soleil et ses paramètres. Les instances reçoivent l’ombre via leur mesh source Babylon ; les deux bouchons physiques ne sont pas oubliés. Le frustum dérivé doit être celui réellement utilisé par le générateur.
4. Vérifier une différence effective W0/W1, puis conserver les quatre PNG entiers et les rapports JSON. Aucun PNG composite, aucune compensation des matériaux ni choix de paramètres selon le résultat.

Pour exécution **par root**, sur le serveur Vite du dépôt déjà disponible au port 4143 et vers un dossier neuf :

```bash
python tools/capture_material_camera_comparison_v4.py \
  creative/reviews/upper-engine-sun-shadow-v4 --port 4143
```

Le script ne démarre pas de serveur et refuse d’écraser une revue. Il conserve les preuves partielles et un rapport `failed-no-adoption` en cas d’échec ; un témoin neutre différent interrompt les captures chaudes. Les entrées et les outils v1/v2/v3 sont recontrôlés en fin de parcours. Les paramètres de lumière/ombre n’ont aucun argument CLI.

Les huit PNG attendus sont des captures réelles séparées : avant et opposée, chacune en neutre v2, neutre v4, W0 et W1. La réussite des contrôles mènera à `checks-passed-pending-human-review`, jamais à une adoption. La comparaison aux creux des ailettes et au vrai warm Blender reste visuelle : PCF n’établit ni pénombre 2°, ni parité AgX/ACES/BRDF, ni occlusion du HDR diffus. Aucun test de clone déplacé, aucune qualification iPhone ni réception artistique n’est revendiqué. L’AO des hauts maillages reste suspendue jusqu’aux vrais atlas de LOD. Aucun fichier de Source14, gel, registre ou jeu n’a été modifié.
