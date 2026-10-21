# Diagnostic graphique des UV AO, V5

Le prepare V4 a terminé normalement avec une erreur Python : son atlas contient au moins un triangle dont le déterminant UV ne dépasse pas 1e-18. Aucun bake n’a été exécuté. Cette variante conserve les opérateurs et paramètres V4, mais ajoute les noms de maillages, indices de triangles et polygones, positions 3D, coordonnées UV, aires et compteurs de tous les triangles concernés. Elle s’arrête sur le même critère strict avant tout bake. Une copie nommée FAILED-UV-INSPECTION-ONLY.blend permet d’examiner l’atlas rejeté sans modifier les sources.

Aucune réparation de géométrie, suppression de triangle ou tolérance élargie. L’aire 3D et l’aire UV sont des observations numériques, sans précision physique ou réception artistique. Les preuves V1–4 restent distinctes. La création de ce script ne prouve aucune exécution.
