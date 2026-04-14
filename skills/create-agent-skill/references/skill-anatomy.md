# Skill anatomy — patterns and real examples

> Concrete patterns drawn from existing skills.
> Use this as a template library when drafting a new SKILL.md.

---

## Skill types

| Type | Examples | CLI pattern |
|---|---|---|
| **Retrieval CLI** | `search-works-openalex`, `search-records-hal`, `search-records-sudoc` | subcommands, JSON stdout, retry/backoff |
| **Contract pack (single task)** | `generate-search-queries` | `prompt`, `schema`, `validate` — no `--task` |
| **Contract pack (multi-task)** | `synthesize-literature` | `prompt --task <t>`, `schema --task <t>`, `validate --task <t>` |
| **Orchestrator** | `orchestrate-literature-review` | helper CLI lists steps; logic lives in SKILL.md |
| **Utility** | `trace-agent-execution` | no CLI; pure prompt-driven output |

---

## Frontmatter patterns

### Retrieval CLI skill

```yaml
---
name: search-records-hal
description: >
  Search and retrieve bibliographic records from HAL (Hyper Articles en Ligne),
  the French open repository, powered by Apache Solr. Use this skill whenever
  the user asks to search HAL, query a specific HAL collection or portal,
  retrieve bibliographic metadata, export BibTeX/TEI, or compute facets and
  trends from HAL. Prefer this skill over search-works-openalex when the task
  targets French institutional or lab deposits, francophone open-access
  preprints, or when generate-search-queries produced queries with lang "fr".
  Trigger on keywords like "HAL", "archives-ouvertes", "collection HAL",
  "portail HAL", "dépôt HAL".
metadata:
  {
    "version": "0.1.0",
    "author": "agent-skills",
    "maturity": "stable",
    "preferred_output": "json",
    "openclaw": { "requires": { "bins": ["uv"] } },
  }

selection:
  use_when:
    - The task targets a specific HAL collection or institutional portal.
    - The user asks for French open-access deposits or francophone preprints.
    - generate-search-queries produced queries with lang "fr" and HAL is a target source.
  avoid_when:
    - The task requires broad international scholarly coverage — use search-works-openalex instead.
    - DOI resolution is the primary goal — use lookup-dois-openalex instead.
  prefer_over:
    - generic-web-search
  combine_with:
    - generate-search-queries
    - search-works-openalex
    - screen-studies-prisma

tags:
  - hal
  - scholarly
  - open-access
  - france
---
```

### Contract pack (single task)

```yaml
---
name: generate-search-queries
description: >
  Build a structured documentary search strategy from a natural-language research
  question. Decomposes concepts, expands terminology (synonyms, broader/narrower
  terms, related terms), and produces 8–15 validated bilingual (EN/FR) search
  queries as strict JSON. Use this skill at the very start of any literature
  review or retrieval task, before calling any retrieval skill. Always use this
  skill before search-works-openalex, search-records-sudoc, or any other retrieval
  skill.
metadata:
  {
    "version": "0.1.0",
    "author": "agent-skills",
    "maturity": "stable",
    "preferred_output": "json",
    "openclaw": { "requires": {} },
  }

selection:
  use_when:
    - The task starts from a research question and needs searchable query expressions.
    - A bilingual (EN/FR) or multi-database search strategy is required.
  avoid_when:
    - Search queries have already been produced and the next step is retrieval.
    - The user provides keywords directly and only needs to run a search.
  prefer_over:
    - generic-keyword-generator
  combine_with:
    - search-works-openalex
    - search-records-sudoc
    - search-records-hal
---
```

### Multi-task contract pack

```yaml
---
name: synthesize-literature
description: >
  Contract pack for the post-retrieval stages of an academic literature review:
  screening, summarization, metadata extraction, quality appraisal, and synthesis
  (thematic, chronological, methodological, PRISMA). Use this skill whenever the
  task involves evaluating, summarizing, or synthesizing a set of already-retrieved
  academic papers. Each task is addressable independently.
metadata:
  {
    "version": "1.2.0",
    "author": "agent-skills",
    "maturity": "stable",
    "preferred_output": "json",
    "openclaw": { "requires": {} },
  }

selection:
  use_when:
    - The task is to screen, summarize, appraise, or synthesize retrieved papers.
    - A single atomic task (e.g. summarize one paper) is needed independently.
  avoid_when:
    - Papers have not yet been retrieved — use search-works-openalex first.
  combine_with:
    - generate-search-queries
    - search-works-openalex
    - orchestrate-literature-review
---
```

---

## Body section patterns

### Purpose section

```markdown
## Purpose

`scripts/cli.py` is a self-contained CLI (runs with `uv run`) that wraps the
[OpenAlex REST API](https://docs.openalex.org). It exposes four subcommands and
emits **strict JSON on stdout**, making it easy to pipe into further processing.

This skill exposes four logical operations, each addressable independently:

| Logical skill | Subcommand | Purpose |
|---|---|---|
| `search-works-openalex` | `search` | Keyword search across the OpenAlex corpus |
| `lookup-dois-openalex` | `batch-lookup-by-doi` | Resolve DOIs to full metadata |
| `get-citing-works-openalex` | `get-citing-works` | Find papers citing a specific work |
| `classify-text-openalex` | `classify-text` | Classify a title or abstract by topic |
```

### When to use / When not to use section

Always mirror the `selection` block but add prose nuance:

```markdown
## When to use / When not to use

Use this skill for any task involving discovery or retrieval of scholarly works,
DOI resolution, citation graph exploration, or topic classification of academic text.

Do not use it when:
- The task concerns a library catalog or institutional holdings — use `search-records-sudoc` instead.
- The task targets French institutional deposits — use `search-records-hal` instead.
- Papers have already been retrieved and the next step is synthesis —
  use `synthesize-literature` instead.
```

### Subcommands section (retrieval CLI)

```markdown
### `search` — keyword search for works

```bash
uv run skills/search-works-openalex/scripts/cli.py search \
  --query "transformer language models" \
  --max-results 15 \
  --date-from 2022-01-01 \
  --oa \
  --sort-by cited_by_count:desc
```

| Flag | Type | Default | Notes |
|---|---|---|---|
| `--query` | string | **required** | Free-text search query |
| `--max-results` | int | `15` | Max 200 per call |
| `--date-from` | `YYYY-MM-DD` | — | Inclusive lower bound |
| `--oa` | flag | off | Open-access works only |
```

### CLI usage section (contract pack — single task)

Note the absence of `--task`:

```markdown
## CLI usage

This skill exposes a single task. There is no `--task` flag.

```bash
uv run skills/generate-search-queries/scripts/cli.py prompt
uv run skills/generate-search-queries/scripts/cli.py schema
uv run skills/generate-search-queries/scripts/cli.py validate \
  --json-file ./queries.json
```
```

### CLI usage section (contract pack — multi-task)

```markdown
## CLI usage

```bash
uv run skills/synthesize-literature/scripts/cli.py list
uv run skills/synthesize-literature/scripts/cli.py prompt --task screen_study_prisma
uv run skills/synthesize-literature/scripts/cli.py schema --task summarize_paper
uv run skills/synthesize-literature/scripts/cli.py validate \
  --task screen_study_prisma --json-file ./screening.json
```

Returns `{"valid": true, "errors": []}` or `{"valid": false, "errors": [...]}`.
Exit code is `0` on success, `1` on validation failure.
```

### Output section

Always include a jsonc example. For retrieval skills, show the common record schema:

```markdown
## Output

```jsonc
{
  "total_found": 1523,
  "returned": 15,
  "results": [
    {
      "source": "openalex",           // always present — identifies the source
      "id": "W2741809807",
      "title": "Attention Is All You Need",
      "authors": ["Ashish Vaswani"],
      "abstract": "string or null",
      "doi": "10.48550/arXiv.1706.03762",
      "pdf_url": "https://… or null",
      "url": "https://openalex.org/W2741809807",
      "year": 2017,
      "date": "2017-06-12",
      "doc_type": "preprint",
      "journal": "arXiv"
    }
  ],
  "error": null                       // always check this field — exit code is always 0
}
```

Always check the `error` field — the CLI never raises a non-zero exit code on API errors.
```

### Composition hints section

Always show a pipeline diagram with this skill's position:

```markdown
## Composition hints

```
generate-search-queries
  → search-works-openalex        ← this skill
  → screen-studies-prisma
  → summarize-paper
  → synthesize-papers-thematic
```

For citation analysis, start here directly:
```
lookup-dois-openalex             ← resolve seed papers
  → get-citing-works-openalex   ← expand the citation graph
  → screen-studies-prisma
```
```

### Environment variables section

```markdown
## Environment variables

Set in `skills/<n>/.env` or export in the shell.

| Variable | Default | Purpose |
|---|---|---|
| `OPENALEX_API_KEY` | *(empty)* | Optional — higher rate limits |
| `OPENALEX_HTTP_TIMEOUT` | `15.0` | Seconds before timeout |
| `OPENALEX_MAX_RETRIES` | `2` | Total attempts per request |
| `OPENALEX_BACKOFF_BASE` | `1.0` | Base seconds for backoff |
| `OPENALEX_BACKOFF_FACTOR` | `2.0` | Backoff multiplier |
| `OPENALEX_JITTER_MAX` | `0.25` | Max random jitter (seconds) |
| `OPENALEX_TRACE` | `0` | Set to `1` for HTTP trace logging |

Retried status codes: 429, 500, 502, 503, 504. Timeouts are also retried.
```

### Failure modes section

```markdown
## Failure modes

- **Exit code always 0**: check the `error` field — the CLI never raises non-zero on API errors.
- **Author/institution not found**: returns zero results with an `error` key.
- **Rate limiting**: handled automatically via retry with exponential backoff.
  If persistent, set the API key environment variable.
- **Abstract unavailable**: `abstract` is `null` for some records — screen on title only.
```

### Task reference section (multi-task contract pack)

```markdown
## Task reference

| Step | Task | Schema | Input required |
|---|---|---|---|
| 1 | `screen_study_prisma` | `screen_study_prisma.schema.json` | research_question, title, abstract |
| 2 | `summarize_paper` | `summarize_paper.schema.json` | research_question, title, abstract |
| 3 | `extract_metadata` | `extract_metadata.schema.json` | title, abstract |
| 4 | `appraise_study_quality` | `appraise_study_quality.schema.json` | summary from step 2 |
| 5a | `synthesize_papers_thematic` | `synthesize_papers_thematic.schema.json` | research_question, summaries[] |
| 5b | `synthesize_papers_prisma` | `synthesize_papers_prisma.schema.json` | research_question, summaries[], screening_log[] |
```

### Rules section (contract pack)

```markdown
## Rules

- Execute one task at a time.
- Return JSON only — no prose, no markdown outside the JSON object.
- Validate each output before moving to the next step.
- Retry at most 2 times on schema validation failure, then stop and report.
- If information is absent from the input, use `null` — never invent values.
```

---

## CLI implementation patterns

### Self-contained uv script header

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ['requests']   # or urllib3, or nothing if stdlib only
# ///
```

### Retry with exponential backoff (standard pattern)

```python
import os, random, time

RETRIED_STATUS = {429, 500, 502, 503, 504}

def _env_float(name, default):
    try: return float(os.environ.get(name, default))
    except: return default

TIMEOUT      = _env_float("MYSOURCE_HTTP_TIMEOUT", 15.0)
MAX_RETRIES  = int(os.environ.get("MYSOURCE_MAX_RETRIES", "2"))
BACKOFF_BASE = _env_float("MYSOURCE_BACKOFF_BASE", 1.0)
BACKOFF_FACTOR = _env_float("MYSOURCE_BACKOFF_FACTOR", 2.0)
JITTER_MAX   = _env_float("MYSOURCE_JITTER_MAX", 0.25)

def _backoff(attempt):
    t = BACKOFF_BASE * (BACKOFF_FACTOR ** max(0, attempt - 1))
    time.sleep(t + random.random() * JITTER_MAX)
```

### Error output pattern (exit code always 0)

```python
import json, sys

def emit(obj):
    json.dump(obj, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")

# On error:
emit({"total_found": 0, "returned": 0, "results": [], "error": str(e)})
# On success:
emit({"total_found": n, "returned": len(results), "results": results, "error": None})
```

### Record normalization to common schema

```python
def normalize(raw: dict) -> dict:
    return {
        "source": "mysource",
        "id": raw.get("id"),
        "title": raw.get("title"),
        "authors": raw.get("authors", []),
        "abstract": raw.get("abstract"),       # null if unavailable
        "doi": raw.get("doi"),                 # null if none
        "pdf_url": raw.get("pdf_url"),         # null if not OA
        "url": raw.get("url"),
        "year": raw.get("year"),
        "date": raw.get("date"),
        "doc_type": raw.get("type"),
        "journal": raw.get("journal"),
        # source-specific fields below:
        "mysource_id": raw.get("native_id"),
    }
```

---

## Logical skills pattern

When a package exposes multiple distinct operations (like `search-works-openalex`),
document them as a table at the top of `## Purpose` and register them in
registry documentation as separate logical skill identifiers pointing to the same package:

```markdown
This skill exposes four logical operations, each addressable independently:

| Logical skill | Subcommand | Purpose |
|---|---|---|
| `search-works-openalex` | `search` | Keyword search |
| `lookup-dois-openalex` | `batch-lookup-by-doi` | DOI resolution |
```

Rule of thumb: expose separate logical skill identifiers when the subcommands
have **meaningfully different** `use_when` conditions. If they share the same
trigger profile, keep them as subcommands without separate identifiers.