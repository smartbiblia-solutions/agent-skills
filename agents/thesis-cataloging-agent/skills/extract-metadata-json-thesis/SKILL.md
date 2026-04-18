---
name: extract-metadata-json-thesis
description: >
  Extraire depuis une page de couverture de thèse ou un texte OCR un JSON
  structuré conforme au schéma intermédiaire imposé pour le catalogage. Utiliser
  cette compétence au début du pipeline de catalogage, après la récupération des
  règles depuis `/knowledge/` et avant toute validation, recherche Sudoc ou
  génération UNIMARC. Déclencheurs typiques : "extraire les métadonnées",
  "analyser une page de couverture", "produire le JSON de thèse". Retourne un
  objet JSON strict.
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
    - La tâche consiste à transformer une page de couverture ou un OCR en métadonnées structurées de thèse.
    - Le pipeline de catalogage exige le JSON intermédiaire avant l'UNIMARC.
  avoid_when:
    - Le JSON a déjà été extrait et l'étape suivante est la validation — utiliser validate-json-schema-thesis.
    - La tâche consiste à produire directement une notice UNIMARC à partir d'un JSON validé — utiliser generate-unimarc-xml-thesis.
  prefer_over:
    - generic-ocr-parser
  combine_with:
    - validate-json-schema-thesis
    - search-records-sudoc
    - generate-unimarc-xml-thesis

tags:
  - thesis
  - metadata
  - unimarc
  - cataloging
---

## Purpose

Cette compétence formalise l'étape d'extraction initiale des métadonnées d'une thèse ou d'un mémoire. Elle doit s'appuyer sur les règles présentes dans `/knowledge/` et produire exactement le schéma JSON intermédiaire attendu par le reste du pipeline.

## When to use / When not to use

Utiliser cette compétence lorsqu'une entrée est fournie sous forme d'image de couverture ou de texte OCR et qu'il faut en dériver les champs bibliographiques structurés.

Ne pas l'utiliser quand le JSON existe déjà et nécessite seulement une validation ou une transformation ultérieure.

## Task reference

| Task | Output schema | Required input |
|---|---|---|
| `extract_metadata_json_thesis` | `schemas/thesis-metadata.schema.json` | Image de couverture ou texte OCR, plus règles récupérées depuis `/knowledge/` |

## CLI usage

```bash
uv run skills/extract-metadata-json-thesis/scripts/cli.py \
  --input-file ./cover.txt
```

| Flag | Type | Required | Notes |
|---|---|---|---|
| `--input-file` | path | yes | Fichier texte OCR ou transcription de couverture |

La CLI retourne un JSON strict avec les clés `metadata`, `knowledge_summary` et `error`.

## Rules

- Lire d'abord les fichiers pertinents de `/knowledge/`.
- Préférer les règles explicites de la base de connaissances aux suppositions internes.
- Produire tous les champs requis, même si certains restent vides.
- Ne pas inventer d'information absente de la source.
- Retour JSON strict uniquement pour la sortie structurée.

## Output

```jsonc
{
  "document-type": "thesis",
  "title": "Titre de la thèse",
  "subtitle": "",
  "author": "Prénom Nom",
  "advisor": ["Directeur 1"],
  "jury_president": [],
  "reviewers": [],
  "committee_members": [],
  "defense_year": "2025",
  "language": "fre",
  "abstract_language": ["fre"],
  "degree_type": "Thèse de doctorat",
  "discipline": "004 Informatique",
  "granting_institution": "Université Exemple",
  "co_tutelle_institutions": [],
  "doctoral_school": [],
  "partner_institutions": [],
  "abstract": ""
}
```

## Composition hints

```text
retrieve-knowledge
  → retrieve-memory
  → extract-metadata-json-thesis   ← cette compétence
  → validate-json-schema-thesis
  → search-records-sudoc
```
