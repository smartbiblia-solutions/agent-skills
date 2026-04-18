# Pipeline overview

## Séquence imposée

1. retrieve-knowledge
2. retrieve-memory
3. extract-metadata-json-thesis
4. validate-json-schema-thesis
5. search-records-sudoc
6. search-authorities-idref
7. enrich-with-idref
8. generate-unimarc-xml-thesis
9. validate-unimarc
10. convert-records-unimarc
11. self-improve-cataloging
12. update-wiki-cataloging

## Principes

- Toujours valider le JSON intermédiaire avant les recherches externes et avant la génération UNIMARC.
- La séparation `dataset/`, `knowledge/`, `memory/` est stricte.
- `knowledge/` contient des règles génériques réutilisables.
- `memory/` contient des cas, erreurs et corrections observés.

## Sorties attendues par étape

- extraction: JSON strict conforme au schéma
- enrichissement: personnes alignées avec forme retenue et identifiants
- génération: UNIMARC XML minimal mais cohérent
- validation: rapport bloquant / non bloquant
