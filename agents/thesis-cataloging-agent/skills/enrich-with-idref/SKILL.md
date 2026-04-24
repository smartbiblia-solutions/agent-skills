# enrich-with-idref

## But

Enrichir les personnes et collectivités avec les candidats IdRef fiables.

## Règles

- Utiliser les résultats de `search-authorities-idref`.
- Comparer nom normalisé, contexte disciplinaire, institutionnel et œuvres connues.
- Ajouter un PPN seulement pour une correspondance forte.
- Pour ambiguïté : expliquer les candidats, ne pas choisir.
- Si aucun candidat fiable : `aucune autorité IdRef pertinente trouvée`.

## Sortie

JSON enrichi avec PPNs et rapport d’incertitude.
