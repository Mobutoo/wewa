# Addendum technique — même LEGACY15-REAR-REFLECTOR

Le gel initial est conservé inchangé ; le **[manifeste finalv2](production-manifest-v2.json)** couvre aussi cet addendum et le contrôle supplémentaire [parité/tangentesv2](export-buffer-check-v2.json). Aucun second exemplaire, nouveau modèle ou changement de mesh/matériau/export.

Le vérificateurparitév1 a été étendu avec un test d’orthogonalité de tangentes. Ce test échoue sur le cadre sombre : sa projectionUV n’est pas un dépliage pour normale et sa tangente est inutilisée, car son matériau n’a pas de normale. Le gel initial a été écrit malgré cet échec de commande ; il est gardé pour traçabilité, pas présenté comme validation de ce nouveau test.

Le protocolev2 conserve la comparaison de **tous** les triangles/positions/normales/UV et contrôle les tangentes sur les seules primitives dont le matériau utilise une normale. Résultat :101tangentes de la face, toutes finies/unitaires, W±1 et produitN·T maximal0. Cadre sans normale exclu de ce test d’usage, pas de sa comparaison géométrique. Aucun attributni export corrigé silencieusement. Le validateurglTF reste0erreur/0avertissement. Le défaut d’orthogonalité des tangentes inutilisées du cadre est une limite technique conservée, pas un succès global de toutes les tangentes.

Les capturesBabylon et natifs96 correspondent au mêmeGLB SHA2567ae7a3c53ca4e8703a1671068b94a58352c39b1cb37da987994b91df18b44d0f. Le sourceBlender SHA256bd0084aa8cb8f0a5f465f2fc1f8dfbd41d20308c064fc4347e5795e0ad64a80c demeure identique. Source×géométrie inchangée, normaleexport arrondie, aucun fit ou optics certifiés.

**G4rework et G5blocked inchangés ; G8pending.** La face montre un motif original encore trop régulier par rapport à la source, et les chiffres80×50×6mm restent des hypothèses. [Revue visuelle principale](README.md), [fiche locale](../../research/rear-reflector-30201069-visible-v1/component-record-fragment.json). Aucun root, cataloguepartagé ou Git.
