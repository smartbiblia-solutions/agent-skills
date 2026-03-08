---
name: literature-review-agent
description: >
  Specialized agent for systematic academic literature reviews.
  Queries OpenAlex (and optionally HAL, Zotero), deduplicates results,
  evaluates relevance, and produces structured syntheses following PRISMA standards.
  Orchestrates build-search-queries, openalex, and academic-review-engine skills.
version: 0.1.0
author: smartbiblia
tags:
  - agent
  - orchestrator
  - literature-review
  - prisma
  - openalex
  - build-search-queries
  - academic-review-engine
depends_on:
  - skills/openalex           (required)
  - skills/build-search-queries (required)
  - skills/academic-review-engine (required)
---

# Literature Review Agent

---

## ⚡ Quickstart Codex (read this first)

> This skill is an **orchestrator-first skill** with an optional helper CLI at `scripts/cli.py`.
> It tells the agent WHAT to do, IN WHAT ORDER, and WITH WHICH COMMANDS.

### Mandatory rules

1. **Execute one step at a time.** Do not plan the entire pipeline before acting.
2. **Return the JSON output of each step before moving to the next.**
3. **MAX 3 OpenAlex calls per session** (vary queries, do not repeat the same one).
4. **MAX 2 retries per failed validation**, then STOP and report the error.
5. **Do not read all prompts at once.** Read only the prompt for the current task.

---

## Workflow overview

```
[research_question]
        │
        ▼
┌─────────────────────────────────────────┐
│  STEP 1 — search_references()           │
│  • Build search queries                 │
│  • Call OpenAlex (≤ 3 queries)          │
│  • Deduplicate by DOI                   │
└─────────────┬───────────────────────────┘
              │  normalized records[]
              ▼
┌─────────────────────────────────────────┐
│  STEP 2 — analyze_papers()              │
│  • Screen each record (PRISMA)          │
│  • Summarize included papers            │
│  • Score relevance                      │
└─────────────┬───────────────────────────┘
              │  analyzed_records[]
              ▼
┌─────────────────────────────────────────┐
│  STEP 3 — synthesize_corpus()           │
│  • Choose synthesis mode                │
│  • Produce structured review            │
└─────────────┬───────────────────────────┘
              │  synthesis JSON
              ▼
┌─────────────────────────────────────────┐
│  STEP 4 — save_to_zotero() (optional)   │
│  • Archive retained references          │
└─────────────────────────────────────────┘
```

---

## STEP 1 — search_references()

### 1a. Build search queries

Read the `build_search_queries` prompt:
```bash
uv run skills/build-search-queries/scripts/cli.py prompt
```
Produce the search strategy JSON, then validate:
```bash
uv run skills/build-search-queries/scripts/cli.py validate \
  --json-file /tmp/queries.json
```

### 1b. Call OpenAlex (≤ 3 queries, ≤ 15 results each)

```bash
uv run skills/openalex/scripts/cli.py search \
  --query "<main query>" \
  --max-results 15 \
  --date-from 2023-01-01 \
  --sort-by cited_by_count:desc \
  --trace \
  > /tmp/results_q1.json
```

Repeat for secondary queries if needed (max 2 additional calls).

### 1c. Deduplicate by DOI

Merge result files and remove duplicates on the `doi` field.
Records without a DOI are deduplicated by title normalization (lowercase, strip punctuation).

Expected canonical record structure (one record per paper):
```json
{
  "id": "W2741809807",
  "title": "string",
  "abstract": "string or null",
  "authors": ["First Last"],
  "year": 2025,
  "doi": "10.xxxx/xxxxx or null",
  "source": "openalex",
  "url": "https://... or null"
}
```

---

## STEP 2 — analyze_papers()

### 2a. Screen each record

For each record in the deduplicated list:

```bash
uv run skills/academic-review-engine/scripts/cli.py prompt --task screen_study_prisma
```

Produce a screening JSON per record:
- `decision`: `"include"` | `"exclude"` | `"uncertain"`
- `reason`: string (required if exclude or uncertain)

Validate:
```bash
uv run skills/academic-review-engine/scripts/cli.py validate \
  --task screen_study_prisma --json-file /tmp/screen_<id>.json
```

Keep only `include` records. Log all `exclude` decisions with their reason (required for PRISMA flow).

### 2b. Summarize included papers

For each included record:

```bash
uv run skills/academic-review-engine/scripts/cli.py prompt --task summarize_paper
```

Validate each summary:
```bash
uv run skills/academic-review-engine/scripts/cli.py validate \
  --task summarize_paper --json-file /tmp/summary_<id>.json
```

### 2c. (Optional) Quality appraisal

If formal PRISMA rigor is required, add:
```bash
uv run skills/academic-review-engine/scripts/cli.py prompt --task appraise_study_quality
```

---

## STEP 3 — synthesize_corpus()

### Choose synthesis mode

| Mode | When to use | Task |
|---|---|---|
| `thematic` | Identify cross-cutting themes | `synthesize_papers_thematic` |
| `chronological` | Show evolution over time | `synthesize_papers_chronological` |
| `methodological` | Compare methodological approaches | `synthesize_papers_methodological` |
| `prisma` | Formal systematic review | `synthesize_papers_prisma` |

### Run synthesis

```bash
uv run skills/academic-review-engine/scripts/cli.py prompt --task synthesize_papers_thematic
```

Provide to the LLM:
- `research_question`: the original question
- `records`: the list of summaries from step 2b
- `screening_log`: include/exclude decisions (required for prisma mode)

Validate:
```bash
uv run skills/academic-review-engine/scripts/cli.py validate \
  --task synthesize_papers_thematic --json-file /tmp/synthesis.json
```

---

## STEP 4 — save_to_zotero() (optional)

> ⚠️ Requires the Zotero connector (not included in this version).
> Check availability: `uv run skills/zotero/zotero_cli.py --help`

If available, archive included records with their metadata and a link to the synthesis.

---

## Full example: GraphRAG 2025 review

```bash
# Step 1 — Search
uv run skills/openalex/scripts/cli.py search \
  --query "GraphRAG graph retrieval augmented generation" \
  --max-results 15 --date-from 2025-01-01 \
  > /tmp/graphrag_results.json

# Step 2a — Screening (repeat for each record)
uv run skills/academic-review-engine/scripts/cli.py prompt --task screen_study_prisma
# → produce /tmp/screen_W123.json, validate, keep "include" only

# Step 2b — Summaries (repeat for each included paper)
uv run skills/academic-review-engine/scripts/cli.py prompt --task summarize_paper
# → produce /tmp/summary_W123.json, validate

# Step 3 — Thematic synthesis
uv run skills/academic-review-engine/scripts/cli.py prompt --task synthesize_papers_thematic
# → produce /tmp/synthesis_graphrag.json, then validate:
uv run skills/academic-review-engine/scripts/cli.py validate \
  --task synthesize_papers_thematic --json-file /tmp/synthesis_graphrag.json
```

---

## Expected error handling

| Situation | Behavior |
|---|---|
| OpenAlex timeout | Retry once with `--trace`, then STOP and report the error |
| Validation failed | Re-prompt with schema error message, max 2 retries |
| 0 OpenAlex results | Broaden the query (remove `--date-from`), 1 attempt, then STOP |
| Record with no abstract | Screen on title only, log `"abstract": null` |
| 3rd validation retry | STOP — return `{"error": "validation_failed", "task": "...", "details": [...]}` |
