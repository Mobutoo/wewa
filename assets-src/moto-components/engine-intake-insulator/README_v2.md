# Isolant d’admission — finition originale v2

Révision de matière uniquement du candidat **MOTO-ENGINE-INTAKE-INSULATOR-001**. Les deux photographies physiques JV581404 montrent une surface sombre striée, plus variée que la finition constante de v1. Deux cartes originales2048² reproduisent une variation de couleur et de rugosité à partir de brins irréguliers allongés et d’un grain fin procédural. Aucun pixel photographique n’est utilisé.

La forme est protégée : positions, indices triangulaires, normales de coins et matrices sont identiques à la source v1ac925. Une comparaison indépendante vérifie également les242640coins des triangles réellement exportés : positions, normales, ordre et monde sont identiques. L’ajout d’UV peut modifier la numérotation des accesseurs GLB pour les coutures, sans changer les triangles rendus. V1 et ses preuves restent intacts.

Six triangles très fins donnent des tangentes Mikk natives nulles dans un diagnostic en mémoire. Cette révision n’utilise **ni normalmap, ni attribut de tangente, ni déplacement** : la couleur et la rugosité ne nécessitent pas ce repère. Aucun buffer GLB n’a été réparé et aucune retessellation n’est effectuée. Les photos ne mesurent pas une profondeur de relief ; aucun microrelief n’est prétendu.

La direction, l’échelle et le contraste des stries sont des choix représentatifs bornés, pas une mesure de formulation, de fibres ou d’usinage. La chimie demeure inconnue et le revers n’est pas photographié. Les cartes sont empaquetées et enregistrées sous chemins relatifs dans `textures-v2/`. La bibliothèque de contexte head3 reste liée relativement ; le contrôle vérifie sa résolution actuelle, pas un checkout déplacé.

`build_v2.py` charge la source v1 immuable, ajoute seulement les UV et le matériau, puis exporte le vrai GLB. Les contrôles lisent les charges utiles des images natives et les UV exportés. Les gros plans neutre et rasant montrent l’apport des deux cartes sans modifier la géométrie. Les rendus96 sont clos séparément après leur lecture.

Le collecteur est une unité distincte figée en candidat428eecbc. La marche d’alésage25/22mm, les écarts estimés, les deux O-rings non construits et les autres interfaces restent réservés. Aucun contrôle ne vaut réception artistique, cote OEM/RDC ou validation matérielle iPhone.
