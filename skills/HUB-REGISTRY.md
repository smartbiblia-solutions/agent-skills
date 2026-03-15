# Hub registry — smartbiblia skills

Complete reference for all packages, logical skills, and their relationships.

---

## Package inventory

| Package | Type | Maturity | Purpose |
|---|---|---|---|
| `generate-search-queries` | contract pack (single task) | stable | Build a bilingual search strategy from a research question |
| `search-works-openalex` | CLI tool | stable | Retrieve scholarly works from OpenAlex |
| `search-records-hal` | CLI tool | stable | Retrieve records from HAL (French open repository) |
| `search-records-sudoc` | CLI tool | stable | Search library catalog records via SRU/Sudoc (UNIMARC, holdings, theses) |
| `synthesize-literature` | contract pack (multi-task) | stable | Post-retrieval analysis: screen, summarize, appraise, synthesize |
| `orchestrate-literature-review` | orchestrator | beta | End-to-end pipeline from question to synthesis |
| `trace-agent-execution` | utility | stable | Produce readable audit traces from agentic run logs |
| `explore-dataset` | analytical CLI | experimental | EDA + interactive HTML dashboard on any tabular dataset |
| `create-hub-skill` | meta-skill | stable | Create or update hub-compliant skills of any type |

---

## Logical skill identifiers

Skills addressable independently in the hub registry.
All `synthesize-literature` tasks share the same CLI and contract pack.

| Logical skill ID | Task / subcommand | Package | Category | When to use |
|---|---|---|---|---|
| `generate-search-queries` | *(single task, no --task flag)* | `generate-search-queries` | generation | Translate a research question into 8–15 bilingual search queries |
| `explore-dataset` | *(single command)* | `explore-dataset` | analytical | EDA + dashboard on CSV/TSV/JSON/Excel/Parquet/Arrow |
| `create-hub-skill` | *(no CLI — prompt-driven)* | `create-hub-skill` | meta | Create or update any hub-compliant skill |
| `search-works-openalex` | `search` | `search-works-openalex` | retrieval | Keyword search across the OpenAlex corpus |
| `lookup-dois-openalex` | `batch-lookup-by-doi` | `search-works-openalex` | retrieval | Resolve one or more DOIs to full bibliographic metadata |
| `get-citing-works-openalex` | `get-citing-works` | `search-works-openalex` | retrieval | Find papers citing a specific work |
| `classify-text-openalex` | `classify-text` | `search-works-openalex` | classification | Classify a title or abstract by academic topic |
| `search-records-hal` | `search` | `search-records-hal` | retrieval | Search HAL collections and portals (Solr, collection-first) |
| `screen-studies-prisma` | `screen_study_prisma` | `synthesize-literature` | screening | Evaluate each title/abstract for PRISMA inclusion |
| `summarize-paper` | `summarize_paper` | `synthesize-literature` | extraction | Structured critical reading note from title + abstract |
| `extract-metadata-paper` | `extract_metadata` | `synthesize-literature` | extraction | Structured methodology and concept extraction |
| `appraise-study-quality` | `appraise_study_quality` | `synthesize-literature` | appraisal | Methodological quality assessment and risk of bias |
| `synthesize-papers-thematic` | `synthesize_papers_thematic` | `synthesize-literature` | synthesis | Cross-cutting theme identification across a corpus |
| `synthesize-papers-chronological` | `synthesize_papers_chronological` | `synthesize-literature` | synthesis | Evolution of a field over time |
| `synthesize-papers-methodological` | `synthesize_papers_methodological` | `synthesize-literature` | synthesis | Comparison of methodological approaches |
| `synthesize-papers-prisma` | `synthesize_papers_prisma` | `synthesize-literature` | synthesis | Formal PRISMA 2020 systematic synthesis |

---

## Invocation patterns

### generate-search-queries (single task — no --task flag)

```bash
uv run skills/generate-search-queries/scripts/cli.py prompt
uv run skills/generate-search-queries/scripts/cli.py schema
uv run skills/generate-search-queries/scripts/cli.py validate --json-file /tmp/queries.json
```

### synthesize-literature (multi-task — --task required)

```bash
uv run skills/synthesize-literature/scripts/cli.py prompt --task <task_name>
uv run skills/synthesize-literature/scripts/cli.py schema --task <task_name>
uv run skills/synthesize-literature/scripts/cli.py validate --task <task_name> --json-file /tmp/output.json
```

---

## Full hub skill map — annotated pipeline

```
generate-search-queries                    output: queries[].query strings (8–15, bilingual)
  │
  │  use queries[].query as --query / --q
  ▼
search-works-openalex                      output: results[] records with id, title, abstract, doi
  ├── lookup-dois-openalex                 output: same schema, from DOI input
  ├── get-citing-works-openalex           output: same schema, citing works
  └── classify-text-openalex             output: topics[], keywords[]
  │
search-records-hal                           output: results[] records (OpenAlex-compatible schema)
  │  (run in parallel with openalex when lang "fr" queries or HAL collection targeted)
  │
  │  also usable:
search-records-sudoc                       output: catalog records (UNIMARC / SRU)
  │
  │  merge results[] from all sources, deduplicate on doi field
  │
  │  optional: explore corpus before screening
explore-dataset                                output: .metrics.json + .summary.md + .dashboard.html
  │
  ▼
screen-studies-prisma                      output: decision (include/exclude/uncertain) per record
  │  keep "include" records only
  ▼
summarize-paper                            output: structured reading note per paper
  │  optional:
extract-metadata-paper                     output: methodology + concepts per paper
appraise-study-quality                     output: quality score + risk of bias per paper
  │
  ▼
synthesize-papers-thematic                 output: structured thematic synthesis
synthesize-papers-chronological            output: structured chronological synthesis
synthesize-papers-methodological           output: structured methodological synthesis
synthesize-papers-prisma                   output: formal PRISMA 2020 synthesis
  │
  ▼
orchestrate-literature-review              ← runs the full pipeline above end-to-end
  │
  ▼
trace-agent-execution                      ← audit trail for any run, any step

create-hub-skill                               ← meta-skill: create or update any skill in the hub
```

---