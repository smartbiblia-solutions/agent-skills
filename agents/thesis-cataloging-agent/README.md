# thesis-cataloging-agent

Agent gitagent de catalogage de thèses UNIMARC en français.

## Pipeline imposé

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

## Séparation architecturale

- `dataset/` : données de vérité terrain, hors ligne, jamais modifiées par l'agent
- `knowledge/` : wiki LLM en Markdown, modifiable et versionné
- `memory/` : mémoire d'expérience et corrections, utilisable à l'inférence
