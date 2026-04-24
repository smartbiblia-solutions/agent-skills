# validate-json-schema

## But

Valider le JSON métier.

## Contrôles

- Profil dans les deux valeurs autorisées.
- Type documentaire compatible.
- Diplôme dans la liste fermée du profil.
- Année à quatre chiffres.
- Discipline unique avec code présent dans le vocabulaire TEF local.
- Confiances numériques entre 0 et 1.
- Champs obligatoires non vides : profil, document_type, title, author, defense_year, degree_type, discipline, granting_institution.

## Échec

Retourner une liste d’erreurs en français et ne pas générer UNIMARC.
