# extract-metadata-json

## But

Extraire les métadonnées dans le JSON canonique avant toute génération UNIMARC.

## Schéma attendu

Voir `/examples/example-metadata.json`. Les listes de diplômes sont fermées. La discipline doit être unique et venir de `/knowledge/vocabulaires/discipline-tef.md`.

## Incertitude

Remplir `uncertainties` et diminuer `confidence.metadata` si une information est déduite ou absente.
