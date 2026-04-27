# Outils et compétences

## Compétences internes

- `orchestrate-unimarc-generation`
- `retrieve-knowledge`
- `retrieve-memory`
- `classify-profile`
- `extract-metadata-json`
- `validate-json-schema`
- `enrich-with-idref`
- `generate-unimarc-xml`
- `validate-unimarc`
- `self-improve`
- `update-wiki`

## Compétences externes déclarées

- `search-authorities-idref` — recherche d’autorités IdRef.
- `search-records-sudoc` — vérification des doublons Sudoc.
- `convert-records-unimarc` — conversion d’export uniquement.
- `scrape-web-pages` — bootstrap documentaire uniquement.
- `wiki-ingest` — transformation de `/raw/` vers `/knowledge/`.

## Graphify

Installation en environnement AgentDesk/OpenClaw :

```bash
command -v graphify || UV_CACHE_DIR=/root/.cache/uv uv tool install graphifyy
graphify install --platform claw
```

Pendant une maintenance documentaire, si `graphify` est absent, installer d'abord `graphifyy` avec `uv tool install`. Ne pas arrêter après le seul constat que `graphify` est absent, sauf si `uv` est absent ou si l'environnement interdit explicitement l'installation.

Le paquet PyPI officiel est `graphifyy`; la commande CLI reste `graphify`.

Les artefacts Graphify sont écrits dans `/graphify-out/` et ne remplacent jamais `/knowledge/`.
