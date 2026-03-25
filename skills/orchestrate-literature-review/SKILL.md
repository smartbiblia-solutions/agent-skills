---
name: orchestrate_literature_review
description: >
  End-to-end orchestrator for systematic academic literature reviews. Sequences
  query design, OpenAlex retrieval, deduplication, PRISMA screening, summarization,
  optional quality appraisal, and synthesis into a single governed pipeline.
  Use this skill whenever the user wants to run a complete literature review from
  a research question to a structured synthesis. Trigger on phrases like "do a
  literature review on", "systematic review of", "find and synthesize papers on",
  "review the literature on", or any request that implies going from a question
  all the way to a written synthesis. Does not replace the individual task skills —
  it orchestrates them.
metadata: {"version": "0.2.0", "author": "smartbiblia", "maturity": "beta", "preferred_output": "json", "openclaw": {"emoji": "🔬", "requires": {"bins": ["uv"]}}}

selection:
  use_when:
    - The user wants a complete literature review from a research question to a synthesis.
    - The task requires chaining retrieval, screening, summarization, and synthesis.
  avoid_when:
    - Only one step is needed (e.g. summarize a single paper, screen a list) —
      use the relevant task from synthesize-literature directly instead.
    - The user already has retrieved papers and only needs synthesis —
      start at synthesize-literature directly.
  combine_with:
    - generate-search-queries
    - search-works-openalex
    - synthesize-literature

tags:
  - orchestrator
  - literature-review
  - prisma
  - systematic-review
---

# orchestrate-literature-review

## Purpose

This skill is the **pipeline orchestrator**. It answers: *what to do, in what
order, with what rules*. It does not contain the methodological contracts —
those live in `synthesize-literature`.

It sequences four stages:

```
[research_question]
        │
        ▼
STEP 1 — search_references()
  Build queries → retrieve from OpenAlex (≤ 3 calls) → deduplicate by DOI
        │
        ▼
STEP 2 — analyze_papers()
  Screen each record (PRISMA) → summarize included papers → optional appraisal
        │
        ▼
STEP 3 — synthesize_corpus()
  Choose synthesis mode → produce structured review
        │
        ▼
STEP 4 — save_to_zotero()  [optional]
  Archive included records
```

---

## When to use / When not to use

Use this skill when the task is a full literature review end-to-end: from a
research question to a structured synthesis.

Do not use it when only one step is needed. If the user already has retrieved
papers, skip to `synthesize-literature` directly. If only a search strategy
is needed, use `generate-search-queries`.

---

## Mandatory rules

1. **Execute one step at a time.** Do not plan the full pipeline before acting.
2. **Return the JSON output of each step before moving to the next.**
3. **MAX 3 OpenAlex calls per session** — vary queries, do not repeat the same one.
4. **MAX 2 retries per failed validation**, then STOP and report the error.
5. **Read only the prompt for the current task** — do not load all prompts at once.

---

## STEP 1 — search_references()

### 1a. Build search queries

`generate-search-queries` is a single-task skill — there is no `--task` flag.

```bash
uv run skills/generate-search-queries/scripts/cli.py prompt
```

Produce the search strategy JSON, then validate:

```bash
uv run skills/generate-search-queries/scripts/cli.py validate \
  --json-file $WORKSPACE/queries.json
```

The validated output contains a `queries[]` array. Each `queries[].query`
string is directly usable as `--query` in the next step.

### 1b. Call OpenAlex (≤ 3 queries, ≤ 15 results each)

Use the `queries[].query` strings from step 1a, prioritising `type: "core"`
queries first, then `type: "synonym"` if more coverage is needed.

```bash
uv run skills/search-works-openalex/scripts/cli.py search \
  --query "<queries[0].query>" \
  --max-results 15 \
  --date-from 2023-01-01 \
  --sort-by cited_by_count:desc \
  --trace \
  > $WORKSPACE/results_q1.json
```

Respect `suggested_filters` from the query output when relevant
(open access flag, date range, discipline filters).

Repeat for secondary queries if needed (max 2 additional calls).

### 1c. Deduplicate by DOI

Merge result files and remove duplicates on the `doi` field.
Records without a DOI are deduplicated by title normalization
(lowercase, strip punctuation).

Canonical record structure after deduplication:

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

```bash
uv run skills/synthesize-literature/scripts/cli.py prompt --task screen_study_prisma
```

Produce a screening JSON per record. Required fields:
- `decision`: `"include"` | `"exclude"` | `"uncertain"`
- `justification`: string (required for exclude and uncertain)

Validate:

```bash
uv run skills/synthesize-literature/scripts/cli.py validate \
  --task screen_study_prisma --json-file $WORKSPACE/screen_<id>.json
```

Keep only `include` records. Log all `exclude` decisions with their reason
(required for PRISMA flow).

### 2b. Summarize included papers

```bash
uv run skills/synthesize-literature/scripts/cli.py prompt --task summarize_paper
```

Validate each summary:

```bash
uv run skills/synthesize-literature/scripts/cli.py validate \
  --task summarize_paper --json-file $WORKSPACE/summary_<id>.json
```

### 2c. Quality appraisal (optional)

Required for formal PRISMA rigor:

```bash
uv run skills/synthesize-literature/scripts/cli.py prompt --task appraise_study_quality
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
uv run skills/synthesize-literature/scripts/cli.py prompt --task synthesize_papers_thematic
```

Provide to the LLM:
- `research_question`: the original question
- `records`: the list of summaries from step 2b
- `screening_log`: include/exclude decisions (required for `prisma` mode only)

Validate:

```bash
uv run skills/synthesize-literature/scripts/cli.py validate \
  --task synthesize_papers_thematic --json-file $WORKSPACE/synthesis.json
```

---

## STEP 4 — save_to_zotero() (optional)

> Requires the Zotero connector. Check availability:
> `uv run skills/zotero/zotero_cli.py --help`

If available, archive included records with their metadata and a link to the synthesis.

---

## Error handling

| Situation | Behavior |
|---|---|
| OpenAlex timeout | Retry once with `--trace`, then STOP and report |
| Validation failed | Re-prompt with schema error message, max 2 retries |
| 0 OpenAlex results | Broaden query (remove `--date-from`), 1 attempt, then STOP |
| Record with no abstract | Screen and summarize on title only — log `"abstract": null` |
| 3rd validation retry | STOP — return `{"error": "validation_failed", "task": "...", "details": [...]}` |

---

## Full example: GraphRAG 2025 review

```bash
# Step 1a — Build search strategy from the research question
uv run skills/generate-search-queries/scripts/cli.py prompt
# → produce $WORKSPACE/queries.json (contains queries[].query strings), then validate:
uv run skills/generate-search-queries/scripts/cli.py validate \
  --json-file $WORKSPACE/queries.json

# Step 1b — Retrieve with the core query from queries[0].query
uv run skills/search-works-openalex/scripts/cli.py search \
  --query "GraphRAG graph retrieval augmented generation" \
  --max-results 15 --date-from 2025-01-01 \
  > $WORKSPACE/graphrag_results.json
# Repeat with queries[1].query, queries[2].query if needed (max 3 calls total)

# Step 2a — Screening (repeat for each record)
uv run skills/synthesize-literature/scripts/cli.py prompt --task screen_study_prisma
# → produce $WORKSPACE/screen_W123.json, validate, keep "include" only

# Step 2b — Summaries (repeat for each included paper)
uv run skills/synthesize-literature/scripts/cli.py prompt --task summarize_paper
# → produce $WORKSPACE/summary_W123.json, validate

# Step 3 — Thematic synthesis
uv run skills/synthesize-literature/scripts/cli.py prompt --task synthesize_papers_thematic
# → produce $WORKSPACE/synthesis_graphrag.json, then validate:
uv run skills/synthesize-literature/scripts/cli.py validate \
  --task synthesize_papers_thematic --json-file $WORKSPACE/synthesis_graphrag.json
```

---

## Helper CLI

The optional `scripts/cli.py` exposes the pipeline structure as JSON,
useful for tooling and introspection:

```bash
# List the 4 pipeline stages
uv run skills/orchestrate-literature-review/scripts/cli.py steps

# Get the definition of one stage
uv run skills/orchestrate-literature-review/scripts/cli.py step --id search_references
```

This CLI does not execute the pipeline — it documents its structure.