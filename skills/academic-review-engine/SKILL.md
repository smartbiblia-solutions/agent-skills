---
name: academic-review-engine
description: Contract-based orchestrator skill (Host-LLM) for the post-retrieval part of an academic literature review pipeline: screening, extraction, appraisal, and synthesis (PRISMA / thematic / chronological / methodological). Use with build-search-queries plus retrieval skills such as OpenAlex.
version: 1.1.0
author: smartbiblia
tags:
  - prisma
  - systematic-review
  - literature-review
  - host-llm
  - contract-skill
---

# Academic Review Engine Skill (Host-LLM Contract)

This skill is a contract pack for review stages after query design/retrieval.

## Scope

- Included tasks: `screen_study_prisma`, `summarize_paper`, `extract_metadata`, `appraise_study_quality`, `synthesize_papers_prisma`, `synthesize_papers_thematic`, `synthesize_papers_chronological`, `synthesize_papers_methodological`
- Excluded task: `build_search_queries` (moved to `skills/build-search-queries`)

## Directory structure

```text
skills/academic-review-engine/
├── scripts/
│   └── cli.py
├── prompts/
│   ├── screen_study_prisma.md
│   ├── summarize_paper.md
│   ├── extract_metadata.md
│   ├── appraise_study_quality.md
│   ├── synthesize_papers_prisma.md
│   ├── synthesize_papers_thematic.md
│   ├── synthesize_papers_chronological.md
│   └── synthesize_papers_methodological.md
├── schemas/
│   ├── screen_study_prisma.schema.json
│   ├── summarize_paper.schema.json
│   ├── extract_metadata.schema.json
│   ├── appraise_study_quality.schema.json
│   ├── synthesize_papers_prisma.schema.json
│   ├── synthesize_papers_thematic.schema.json
│   ├── synthesize_papers_chronological.schema.json
│   └── synthesize_papers_methodological.schema.json
└── references/
    └── ARCHITECTURE.md
```

## Usage pattern

1. List available tasks:
```bash
uv run skills/academic-review-engine/scripts/cli.py list
```

2. Read one task prompt:
```bash
uv run skills/academic-review-engine/scripts/cli.py prompt --task screen_study_prisma
```

3. Produce JSON output, then validate:
```bash
uv run skills/academic-review-engine/scripts/cli.py validate \
  --task screen_study_prisma \
  --json-file /tmp/screening.json
```

4. Repeat for next task.

## End-to-end sequencing

1. Build query strategy with `skills/build-search-queries`
2. Retrieve records with `skills/openalex` (or other retrieval skill)
3. Use this skill for screening/extraction/appraisal/synthesis

## Tasks & contracts

| Step | Task | Schema | Purpose |
|---|---|---|---|
| 1 | `screen_study_prisma` | `screen_study_prisma.schema.json` | Title/abstract screening (include / exclude / uncertain) |
| 2 | `summarize_paper` | `summarize_paper.schema.json` | Structured critical reading note |
| 3 | `extract_metadata` | `extract_metadata.schema.json` | Methodology & concept extraction |
| 4 | `appraise_study_quality` | `appraise_study_quality.schema.json` | Quality appraisal & risk of bias |
| 5a | `synthesize_papers_prisma` | `synthesize_papers_prisma.schema.json` | PRISMA 2020 systematic synthesis |
| 5b | `synthesize_papers_thematic` | `synthesize_papers_thematic.schema.json` | Thematic synthesis |
| 5c | `synthesize_papers_chronological` | `synthesize_papers_chronological.schema.json` | Chronological synthesis |
| 5d | `synthesize_papers_methodological` | `synthesize_papers_methodological.schema.json` | Methodological synthesis |

## Rules

- Execute one task at a time.
- Return JSON only for task outputs.
- Validate each output before moving on.
- Retry at most 2 times on schema validation failures.

See `references/ARCHITECTURE.md` for the pipeline overview.
