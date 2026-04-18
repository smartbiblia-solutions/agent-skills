---
name: validate-json-schema-thesis
description: >
  Valider le JSON intermédiaire de thèse contre le schéma imposé par le pipeline.
  Utiliser cette compétence immédiatement après l'extraction de métadonnées et
  avant toute recherche Sudoc, alignement IdRef ou génération UNIMARC. Déclencheurs
  typiques : "valider le schéma JSON", "contrôler les champs obligatoires",
  "vérifier la structure du JSON de thèse". Retourne un rapport JSON strict.
metadata:
  {
    "version": "0.1.0",
    "author": "agent-skills",
    "maturity": "experimental",
    "preferred_output": "json",
    "openclaw": { "requires": {} },
  }

selection:
  use_when:
    - Le JSON intermédiaire vient d'être extrait et doit être contrôlé.
    - Le pipeline exige une validation bloquante avant les étapes externes et UNIMARC.
  avoid_when:
    - La tâche consiste à extraire les données depuis une couverture — utiliser extract-metadata-json-thesis.
    - La tâche consiste à valider une notice UNIMARC — utiliser validate-unimarc.
  prefer_over:
    - generic-json-checker
  combine_with:
    - extract-metadata-json-thesis
    - search-records-sudoc
    - generate-unimarc-xml-thesis

tags:
  - thesis
  - validation
  - json-schema
  - cataloging
---

## Purpose

Cette compétence impose un point de contrôle dur entre l'extraction et la suite du pipeline. Elle vérifie la conformité structurelle, la présence des champs requis et peut signaler des incohérences à corriger avant toute production de notice.

## When to use / When not to use

Utiliser cette compétence dès qu'un JSON de thèse doit être fiabilisé avant les étapes de recherche, d'enrichissement ou de conversion. Ne pas l'utiliser pour la validation logique d'une notice UNIMARC XML.

## CLI usage

```bash
uv run skills/validate-json-schema-thesis/scripts/cli.py \
  --json-file ./metadata.json
```

| Flag | Type | Required | Notes |
|---|---|---|---|
| `--json-file` | path | yes | JSON de thèse à valider ; la CLI accepte soit un objet racine, soit un objet contenant la clé `metadata` |

La CLI retourne un JSON strict avec `valid`, `errors` et `warnings`.

## Output

```jsonc
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

## Composition hints

```text
extract-metadata-json-thesis
  → validate-json-schema-thesis   ← cette compétence
  → search-records-sudoc
  → search-authorities-idref (subcommand `search`)
```
