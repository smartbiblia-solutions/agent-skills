---
name: generate-unimarc-xml-thesis
description: >
  Générer une notice UNIMARC XML conforme à partir d'un JSON de thèse validé et,
  si disponible, enrichi avec les PPN IdRef. Utiliser cette compétence après les
  validations et l'enrichissement d'autorité, avant la validation finale et les
  conversions de sérialisation. Déclencheurs typiques : "générer l'UNIMARC XML",
  "produire la notice UNIMARC", "sérialiser la notice de thèse". Retourne un XML
  UNIMARC et un résumé JSON de contrôle.
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
    - Le JSON intermédiaire est validé et prêt à être transformé en UNIMARC.
    - Les alignements IdRef doivent être injectés dans les zones d'autorité.
  avoid_when:
    - La tâche consiste encore à contrôler le JSON intermédiaire — utiliser validate-json-schema-thesis.
    - La tâche consiste à vérifier la notice produite — utiliser validate-unimarc.
  prefer_over:
    - generic-xml-generator
  combine_with:
    - enrich-with-idref
    - validate-unimarc
    - convert-records-unimarc

tags:
  - unimarc
  - xml
  - thesis
  - cataloging
---

## Purpose

Cette compétence transforme la structure métier intermédiaire en notice UNIMARC XML en appliquant les règles issues de `/knowledge/`. Elle doit rester traçable, explicite et compatible avec une validation aval.

## When to use / When not to use

Utiliser cette compétence lorsque toutes les informations utiles sont stabilisées et qu'il faut produire la notice XML bibliographique. Ne pas l'utiliser pour la conversion entre sérialisations UNIMARC ni pour les recherches externes.

## CLI usage

```bash
uv run skills/generate-unimarc-xml-thesis/scripts/cli.py \
  --json-file ./metadata.json \
  --persons-file ./persons.json
```

| Flag | Type | Required | Notes |
|---|---|---|---|
| `--json-file` | path | yes | JSON de métadonnées ; la CLI accepte soit un objet racine, soit un objet contenant la clé `metadata` |
| `--persons-file` | path | no | JSON d'enrichissement IdRef contenant la clé `persons` |

La CLI retourne un JSON strict avec `xml`, `fields_written` et `error`.

## Output

```jsonc
{
  "xml": "<record>...</record>",
  "fields_written": ["200", "328", "700", "701", "702"],
  "error": null
}
```

## Composition hints

```text
validate-json-schema-thesis
  → search-records-sudoc
  → search-authorities-idref (subcommand `search`)
  → enrich-with-idref
  → generate-unimarc-xml-thesis   ← cette compétence
  → validate-unimarc
```
