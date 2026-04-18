---
name: update-wiki-cataloging
description: >
  Mettre à jour la base de connaissances `/knowledge/` avec de nouvelles règles,
  cas limites et heuristiques de catalogage en français, de manière atomique et
  sans duplication. Utiliser cette compétence quand une connaissance généralisable
  est confirmée par l'expérience ou le retour utilisateur. Déclencheurs typiques :
  "mettre à jour le wiki", "ajouter une règle de catalogage", "documenter un cas
  limite". Retourne un rapport JSON strict.
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
    - Une règle générale ou un cas limite récurrent doit être ajouté au wiki.
    - Le pipeline d'amélioration continue a identifié une connaissance réutilisable au-delà d'un cas isolé.
  avoid_when:
    - La correction ne vaut que pour un cas particulier — utiliser self-improve-cataloging.
    - La tâche consiste à éditer le dataset d'évaluation, ce qui est interdit.
  prefer_over:
    - generic-note-writer
  combine_with:
    - self-improve-cataloging
    - extract-metadata-json-thesis
    - generate-unimarc-xml-thesis

tags:
  - knowledge-base
  - wiki
  - cataloging
  - unimarc
---

## Purpose

Cette compétence matérialise le comportement de wiki LLM exigé par l'architecture. Elle transforme une connaissance validée en règle explicite, versionnable et lisible par l'humain dans `/knowledge/`.

## When to use / When not to use

Utiliser cette compétence lorsqu'une information dépasse le cas particulier et doit devenir une règle consultable au début des exécutions futures. Ne pas l'utiliser pour mémoriser une simple correction ponctuelle.

## CLI usage

```bash
uv run skills/update-wiki-cataloging/scripts/cli.py \
  --rule-file ./rule.json
```

| Flag | Type | Required | Notes |
|---|---|---|---|
| `--rule-file` | path | yes | JSON contenant au minimum `title` et `rule_markdown` |

La CLI crée ou remplace un fichier de règle dans `knowledge/` et retourne `updated_files`, `rules_added`, `rules_updated` et `error`.

## Rules

- Écrire en français.
- Garder les règles atomiques, explicites et sans doublons.
- Mettre à jour le fichier le plus pertinent plutôt que multiplier les notes redondantes.
- La base `/knowledge/` reste prioritaire sur les suppositions internes de l'agent.

## Output

```jsonc
{
  "updated_files": ["knowledge/unimarc-zones.md"],
  "rules_added": 1,
  "rules_updated": 0,
  "error": null
}
```

## Composition hints

```text
self-improve-cataloging
  → update-wiki-cataloging        ← cette compétence
  → retrieve-knowledge du prochain run
```
