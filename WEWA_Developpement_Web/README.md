# WEWA - Kit de développement web 1.0

Ce dossier organise le développement autonome d'un jeu de moto à Kinshasa.
Il contient un blockout 3D, pas encore un jeu jouable ni un rendu photoréaliste.

## Commencer
1. Lire AGENTS.md puis docs/PLAN_DE_PRODUCTION.md.
2. Lire validation/STATUS.json et backlog/tasks.json.
3. Choisir W01 ou W02 selon les dépendances disponibles.
4. Créer le projet du jeu dans un dépôt distinct ; conserver ce kit comme référence versionnée.

## Données déjà préparées
- data/pilot/world_manifest.json : origine, axes, cellules et limitations.
- data/pilot/cells/ : 351 GLB, 191 cellules ; géométrie plane non texturée.
- data/pilot/road_centerlines.local.json : lignes et attributs, pas un graphe routable.
- data/pilot/building_footprints.local.json : géométrie locale en mètres, pas un GeoJSON RFC 7946.
- validation/glb_structural.json : contrôle binaire local, pas un test moteur.
- config/ : profil produit, budgets initiaux et registre des assets.
- docs/ : plan, décisions et sources. Le PDF de présentation est fourni séparément.

## Reproduire les cellules
Python 3.11+ ; dans un environnement dédié :

    python -m pip install -r tools/requirements.txt
    python tools/prepare_pilot.py --source /chemin/Kit_Kinshasa_3D --out generated
    python tools/check_glb.py generated/cells --out validation/new_glb_checks.json

Le kit géographique complet reste une entrée externe ; il n'est pas dupliqué ici.
Le script lit le GeoJSON des bâtiments en mémoire : prévoir plusieurs Go de RAM.
Pour la ville complète, créer un index spatial GeoPackage/Parquet et lire en flux avant de lancer une génération massive.
Ne pas élargir aveuglément la bbox : dédoublonnage, voies et terrain doivent être traités d'abord.

## Mesurer le futur jeu
Capturer des mesures réelles après chauffe, avec appareil, navigateur, renderer, résolution et build dans metadata.
Format : {"metadata":{...},"frames":[{"frame_ms":16.7,"cpu_ms":4.1,"gpu_ms":8.0}, ...]}.

    python tools/summarize_benchmark.py capture.json --out validation/performance.json

Aucune mesure FPS réelle n'est fournie. Les scripts ne démarrent pas un moteur ni un service web.
La version de référence est en mètres, X est / Y haut / Z sud pour les GLB.
Conserver les crédits OSM et le statut des hauteurs. Les limites sont détaillées dans chaque manifest.
