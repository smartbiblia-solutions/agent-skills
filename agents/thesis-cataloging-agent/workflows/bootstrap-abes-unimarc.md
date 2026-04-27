# Rafraîchissement source ABES UNIMARC(B)

Ce workflow sert uniquement à mettre à jour `/raw/abes-unimarc/` quand la documentation ABES change.
Il n’est pas requis au lancement de l’agent si `/raw` est déjà pré-rempli.
Il ne doit jamais être exécuté pendant un catalogage normal.

## Deux niveaux de maintenance

### 1. Maintenance courante

Utiliser ce niveau quand `/raw/` est déjà pré-rempli.

Objectif :
- comparer `/raw/abes-unimarc/` avec `/knowledge/` ;
- proposer des règles opérationnelles françaises pour `/knowledge/` ;
- faire valider les changements par un catalogueur ;
- journaliser les changements dans `knowledge/log.md` ;
- régénérer `/graphify-out/` après validation.

Ne pas scraper ABES pendant une maintenance courante.
Ne pas modifier `/raw/`.

### 2. Rafraîchissement source

Utiliser ce niveau seulement quand la documentation ABES a changé, quand une zone manque dans `/raw/`, ou quand un humain demande explicitement une régénération source.

Alimenter `/raw/abes-unimarc/` avec des pages ABES transposées en markdown via la compétence externe `scrape-web-pages`, puis préparer l’ingestion vers `/knowledge/` via `wiki-ingest`.

## Zones à collecter

`008, 029, 100, 101, 102, 104, 105, 106, 181, 182, 183, 200, 214, 215, 320, 328, 330, 608, 686, 700, 701, 702, 711`

## URL

```text
https://documentation.abes.fr/sudoc/formats/unmb/zones/{zone}.htm
```

## Étapes de rafraîchissement source

1. Vérifier que le rafraîchissement source est demandé explicitement par un humain.
2. Utiliser `scrape-web-pages` pour chaque URL.
3. Écrire les transpositions markdown dans `/raw/abes-unimarc/{zone}.md`.
4. Ne pas modifier les fichiers existants sans revue.
5. Utiliser `wiki-ingest` pour proposer des règles françaises vers `/knowledge/`.
6. Faire valider les changements par un catalogueur.
7. Journaliser dans `knowledge/log.md`.

## Graphify facultatif

Après validation du wiki, générer des artefacts facultatifs :

```bash
UV_CACHE_DIR=/root/.cache/uv uv tool install graphifyy
graphify install --platform claw
graphify run --input agents/thesis-cataloging-agent/knowledge --output agents/thesis-cataloging-agent/graphify-out
```
