# ÉTAT ACTUEL — VIVA WEWA, PREMIER PROTOTYPE PUBLIC

Jeu disponible : https://viva-wewa.chummyrose33.chatgpt.site ; relecture : https://viva-wewa.chummyrose33.chatgpt.site/relecture.html. Code dans app/, dépendances gelées à la racine. Lire validation/STATUS.json et backlog/tasks.json dans WEWA_Developpement_Web pour les résultats actuels : les descriptions de manque ci-dessous sont historiques. Ne pas réinitialiser le moteur ni recréer le projet. Safari iPhone 15/16 et la géographie restent à qualifier.

---

# À LIRE EN PREMIER - CADRAGE R9 / PLAN 1.2

Le concept PDF est actualisé : huit pages R9 suivies du dossier source R8 identifié en annexe. Le plan PDF comprend deux pages 1.2 puis son annexe antérieure. Cadrage R9, configurations et backlog actuel prévalent. 45 tâches : W00 réalisé ; les autres en attente.

Lire WEWA_Developpement_Web/docs/CADRAGE_R9.md avant tout développement. Les compteurs anciens et la mention R8 dans les textes historiques sont remplacés par ce cadrage.

# WEWA - Reprise de développement dans Codex

État au 20 octobre 2026. Idée Ewutelo : 27f8ffb12df14ff79c6e0f13cbd1cf91
Titre : WEWA — Kinshasa à moto : jeu web 3D et reprise Codex

## Ce qui existe
- Concept R8 : 31 pages, gameplay, ville, personnages et monétisation facultative.
- Plan web : 15 pages, huit phases, budgets et critères ; backlog de 35 tâches.
- Kit géographique : routes, bâtiments, POI, neuf zones, relief, références et crédits.
- Pilote Gombe : 1 747 objets bâtis, 1 748 parties, 23 anneaux intérieurs, 248 tronçons routiers, 191 cellules, 351 GLB.
- 130 hauteurs estimées depuis les étages ; 1 617 valeurs provisoires de 6 m. Sol plat, pas de façades texturées.
- Images produites directement à partir des triangles de ces GLB. Elles ne sont pas des captures d’un jeu.

## Ce qui manque
Aucun moteur web initialisé, contrôleur de moto, simulation de trafic, mission jouable, déploiement ni paiement actif. Les FPS n’ont pas été mesurés. Les recouvrements entre voiries estimées et bâtiments doivent être examinés avant le corridor jouable.

## Nom du secteur
L’utilisateur a confirmé « secteur Gombe ». Ignorer « Dragon Bay », erreur de transcription du message précédent.

## Reprendre
1. Décompresser cette archive dans un dossier local WEWA.
2. Ouvrir ce dossier comme projet principal dans Codex ; l’AGENTS.md racine indique les documents à lire.
3. Coller PROMPT_REPRISE_CODEX.txt dans une nouvelle conversation de ce projet.
4. Si le plugin Ewutelo est présent dans cette session, lire l’idée avec son identifiant ; sinon utiliser context/ et les documents locaux.
5. Commencer par le socle web et une cellule, puis moto/collisions, mission et tests. Ne pas recommencer la recherche et la rédaction du concept.

## Arborescence
- docs/ : PDF conceptuel, plan web et dossier géographique.
- context/ : textes intégraux extraits des PDF et export des informations de reprise.
- WEWA_Developpement_Web/ : tâches, configurations, scripts, modèles et validations.
- data_sources/Kit_Kinshasa_3D/ : géodonnées complètes nécessaires pour régénérer ou étendre.
- images/ : vues techniques de Gombe.
- tools/ : script de rendu original pour traçabilité (ses chemins sont ceux du workspace d’origine, à adapter).
- app/ : à créer pour le jeu ; aucun code de gameplay n’est fourni aujourd’hui.

## Commande de régénération, depuis la racine
Après installation des dépendances de WEWA_Developpement_Web/tools/requirements.txt dans un environnement Python dédié :

    python WEWA_Developpement_Web/tools/prepare_pilot.py --source data_sources/Kit_Kinshasa_3D --out generated

Les GLB existants suffisent pour le premier import. La source bâtiments est volumineuse ; ne jamais la placer telle quelle dans les assets web.

## Transmission et vérité des résultats
Work peut préparer et modifier du code ; Codex est recommandé ici pour organiser la production autour du dossier, de Git, des builds et des tests. Ce transfert ne crée pas automatiquement un projet Codex, une connexion Ewutelo dans une autre session ou une tâche d’arrière-plan.
L’historique Work et celui de Codex sont distincts ; les documents locaux et les artifacts Ewutelo évitent de dépendre d’une continuité implicite.
Les « meilleurs 10 % » restent une ambition à évaluer avec un panel comparable, pas un résultat acquis.

## Informations dans Ewutelo
L’idée contient le PRD de synthèse opérationnelle et les consignes, révision 5, vérifiés après enregistrement. Les documents intégraux, les références détaillées et les fichiers binaires sont dans cette archive. context/ewutelo_export.json est la copie de la réponse relue ; context/complete_project_context.json contient le contexte intégral local.


## Ajout du 20 octobre 2026 : nitro et vue au guidon
Lire WEWA_Developpement_Web/docs/NITRO_ET_CAMERAS.md et config/nitro_camera.json dans ce sous-dossier. Ils ajoutent le nitro avec effets réglables et les deux caméras dès P2/V0. Le backlog comprend désormais 38 tâches ; W35-W37 sont en attente. Les PDF de base restent la référence générale, complétés par docs/WEWA_Addendum_Nitro_Cameras.pdf.
