---
name: build-search-queries
description: Build a systematic-review search strategy from a natural-language research question and optional source constraints (OpenAlex, HAL, PubMed, WoS, Scopus). Use when the task is to decompose concepts, expand terminology, and produce validated bilingual (EN/FR) search queries as strict JSON.
---

# Build Search Queries Skill

This skill is a contract pack for a single task: `build_search_queries`.

## Use this skill

1. Read the prompt contract:
```bash
uv run skills/build-search-queries/scripts/cli.py prompt
```

2. Produce JSON output (no prose), then validate:
```bash
uv run skills/build-search-queries/scripts/cli.py validate \
  --json-file /tmp/build_search_queries.json
```

3. If validation fails, fix the JSON and validate again.

## Available commands

```bash
uv run skills/build-search-queries/scripts/cli.py prompt
uv run skills/build-search-queries/scripts/cli.py schema
uv run skills/build-search-queries/scripts/cli.py validate --json-file /tmp/output.json
```
