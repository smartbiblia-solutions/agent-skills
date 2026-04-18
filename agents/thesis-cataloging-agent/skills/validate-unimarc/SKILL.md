---
name: validate-unimarc
description: >
  Vérifier la conformité structurelle et logique d'une notice UNIMARC générée.
  Utiliser cette compétence juste après `generate-unimarc-xml-thesis` et avant
  toute conversion de sérialisation ou livraison finale. Déclencheurs typiques :
  "valider l'UNIMARC", "contrôler la notice XML", "vérifier les zones et sous-zones".
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
    - Une notice UNIMARC XML vient d'être générée et doit être contrôlée.
    - Le pipeline exige une validation avant conversion ou diffusion.
  avoid_when:
    - La tâche consiste à valider le JSON intermédiaire — utiliser validate-json-schema-thesis.
    - La tâche consiste à convertir une notice déjà valide — utiliser convert-records-unimarc.
  prefer_over:
    - generic-xml-validator
  combine_with:
    - generate-unimarc-xml-thesis
    - convert-records-unimarc
    - update-wiki-cataloging

tags:
  - unimarc
  - validation
  - xml
  - cataloging
---

## Purpose

Cette compétence fournit la barrière qualité finale sur la notice UNIMARC. Elle vise autant la validité de structure que la cohérence catalographique, notamment l'injection correcte des autorités et des zones attendues pour les thèses.

## When to use / When not to use

Utiliser cette compétence pour toute notice UNIMARC générée par le pipeline. Ne pas l'utiliser à la place des validations amont ni comme convertisseur de formats.

## CLI usage

Valider soit un JSON produit par `generate-unimarc-xml-thesis`, soit un fichier XML direct.

```bash
uv run skills/validate-unimarc/scripts/cli.py \
  --json-file ./unimarc.json
```

```bash
uv run skills/validate-unimarc/scripts/cli.py \
  --xml-file ./record.xml
```

| Flag | Type | Required | Notes |
|---|---|---|---|
| `--json-file` | path | conditionnel | JSON contenant une clé `xml` |
| `--xml-file` | path | conditionnel | Fichier XML direct à valider |

Au moins une des deux options doit être fournie. La CLI retourne `valid`, `errors`, `warnings` et `checked_fields`.

## Output

```jsonc
{
  "valid": true,
  "errors": [],
  "warnings": ["Zone 328 présente sans note complémentaire."],
  "checked_fields": ["200", "328", "700", "701", "702"]
}
```

## Composition hints

```text
generate-unimarc-xml-thesis
  → validate-unimarc              ← cette compétence
  → convert-records-unimarc
  → self-improve-cataloging
```
