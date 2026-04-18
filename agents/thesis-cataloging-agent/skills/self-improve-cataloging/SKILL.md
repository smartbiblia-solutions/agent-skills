---
name: self-improve-cataloging
description: >
  Capitaliser les corrections utilisateur et les écarts observés pendant le
  catalogage dans une mémoire d'expérience distincte de la base de connaissances
  et du dataset. Utiliser cette compétence lorsqu'un retour humain ou un échec de
  validation révèle un cas utile à mémoriser. Déclencheurs typiques : "prendre en
  compte la correction", "apprendre d'un retour utilisateur", "mémoriser un cas".
  Retourne un rapport JSON strict.
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
    - Un utilisateur corrige une extraction, un alignement ou une notice.
    - Un cas récurrent doit être mémorisé pour de futures inférences.
  avoid_when:
    - La règle découverte relève de la doctrine générale et doit être publiée dans le wiki — utiliser update-wiki-cataloging.
    - Le besoin est un simple journal d'exécution sans mémoire exploitable.
  prefer_over:
    - generic-feedback-logger
  combine_with:
    - validate-unimarc
    - update-wiki-cataloging
    - extract-metadata-json-thesis

tags:
  - memory
  - feedback
  - self-improvement
  - cataloging
---

## Purpose

Cette compétence implémente l'amélioration continue sans toucher aux poids du modèle. Elle stocke les cas passés, corrections et décisions utiles dans `memory/`, pour réutilisation à l'inférence.

## When to use / When not to use

Utiliser cette compétence quand une expérience concrète doit être retenue comme précédent réutilisable. Ne pas l'utiliser pour écrire des règles normatives générales, qui appartiennent à `knowledge/`.

## CLI usage

```bash
uv run skills/self-improve-cataloging/scripts/cli.py \
  --feedback-file ./feedback.json
```

| Flag | Type | Required | Notes |
|---|---|---|---|
| `--feedback-file` | path | yes | JSON du retour utilisateur, de l'écart observé ou de la correction validée |

La CLI ajoute une entrée JSONL dans `memory/cases.jsonl` et retourne `memory_updated`, `entries_written`, `wiki_candidate` et `error`.

## Rules

- Ne jamais modifier `dataset/`.
- Écrire dans `memory/` uniquement des cas d'expérience, corrections et décisions contextualisées.
- Préserver la séparation stricte entre mémoire, wiki et données d'évaluation.

## Output

```jsonc
{
  "memory_updated": true,
  "entries_written": 1,
  "wiki_candidate": true,
  "error": null
}
```

## Composition hints

```text
validate-unimarc
  → self-improve-cataloging       ← cette compétence
  → update-wiki-cataloging
  → prochain cas
```
