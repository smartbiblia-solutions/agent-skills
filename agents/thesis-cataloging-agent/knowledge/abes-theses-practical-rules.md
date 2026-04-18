# ABES theses practical rules

## Règles pratiques pour ce dépôt

- Toujours distinguer les erreurs bloquantes des avertissements.
- Un champ requis du schéma JSON manquant est bloquant.
- Une valeur de discipline hors vocabulaire local est un avertissement, pas une erreur bloquante.
- L'année de soutenance doit idéalement être sur 4 chiffres.
- Le type de diplôme doit rester dans une liste fermée alignée sur les formes académiques françaises usuelles.
- Les collectivités de soutenance doivent être conservées textuellement si l'alignement autorité n'est pas encore disponible.

## Heuristiques admises dans le prototype

- Déduire `document-type = thesis` sauf si le document mentionne explicitement un mémoire ou une HDR.
- Déduire la langue à partir de mentions textuelles explicites; sinon défaut `fre`.
- Déduire une discipline contrôlée par mots-clés, avec priorité à la précision plutôt qu'à l'exhaustivité.

## Contrôle humain recommandé

- Vérifier l'ordre `Nom, Prénom` pour les accès auteur.
- Vérifier les cas de co-tutelle.
- Vérifier les collectivités et écoles doctorales complexes.
