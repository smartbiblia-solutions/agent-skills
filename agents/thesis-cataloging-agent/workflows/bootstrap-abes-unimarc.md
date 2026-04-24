# Bootstrap documentaire ABES UNIMARC(B)

Ce workflow sert uniquement à l’installation ou à la maintenance documentaire. Il ne doit jamais être exécuté pendant un catalogage normal.

## Objectif

Alimenter `/raw/abes-unimarc/` avec des pages ABES transposées en markdown via la compétence externe `scrape-web-pages`, puis préparer l’ingestion vers `/knowledge/` via `wiki-ingest`.

## Zones à collecter

`008, 029, 100, 101, 102, 104, 105, 106, 181, 182, 183, 200, 214, 215, 320, 328, 330, 608, 686, 700, 701, 702, 711`

## URL

```text
https://documentation.abes.fr/sudoc/formats/unmb/zones/{zone}.htm
```

## Étapes

1. Vérifier que la maintenance documentaire est demandée explicitement par un humain.
2. Utiliser `scrape-web-pages` pour chaque URL.
3. Écrire les transpositions markdown dans `/raw/abes-unimarc/{zone}.md`.
4. Ne pas modifier les fichiers existants sans revue.
5. Utiliser `wiki-ingest` pour proposer des règles françaises vers `/knowledge/`.
6. Faire valider les changements par un catalogueur.
7. Journaliser dans `knowledge/log.md`.

## Graphify facultatif

Après validation du wiki, générer des artefacts facultatifs :

```bash
uv tool install graphifyy
graphify install --platform claw
graphify run --input knowledge --output graphify-out
```
