# Alignement IdRef

Pour chaque personne ou collectivité :

1. Rechercher des candidats via `search-authorities-idref`.
2. Comparer le nom normalisé, la discipline, le contexte institutionnel et les œuvres connues.
3. Assigner un PPN uniquement si la correspondance est forte.
4. Expliquer les candidats ambigus.
5. Retourner `aucune autorité IdRef pertinente trouvée` si aucun alignement fiable n’existe.

## Interdictions

- Ne jamais halluciner un PPN.
- Ne jamais forcer une correspondance.
- Ne jamais prendre le document en cours de catalogage comme preuve d’autorité existante.

## Injection UNIMARC

Insérer `$3{PPN}` dans `700`, `701`, `702` et `711` seulement en cas de correspondance forte.
