# SmartBibl.IA — Agent Skills Hub

Reusable skills and MCP servers for AI agents working on libraries, scholarly
information, and research workflows.

Compatible with Claude Code, Codex, Opencode, Nanobot, and any agent that can
read a `SKILL.md` and run `uv`.

---

## What's in this repo

```
skills/          Agent skills (prompt contracts + JSON schemas + CLI)
mcp/             MCP servers (streamable-HTTP, Docker-ready)
```

### Skills

| Skill | Type | Purpose |
|---|---|---|
| [`generate-search-queries`](#generate-search-queries) | contract pack | Build a bilingual search strategy from a research question |
| [`search-works-openalex`](#search-works-openalex) | CLI tool | Retrieve scholarly works from OpenAlex |
| [`search-records-hal`](#search-records-hal) | CLI tool | Retrieve records from HAL (French open repository) |
| [`search-records-sudoc`](#search-records-sudoc) | CLI tool | Search the French academic union catalogue (UNIMARC, holdings, theses) |
| [`synthesize-literature`](#synthesize-literature) | contract pack | Screen, summarize, appraise, and synthesize retrieved papers |
| [`orchestrate-literature-review`](#orchestrate-literature-review) | orchestrator | End-to-end pipeline from research question to synthesis |
| [`trace-agent-execution`](#trace-agent-execution) | utility | Produce readable audit traces from agentic run logs |

### MCP servers

| Server | Port | Purpose |
|---|---|---|
| [`mcp/openalex`](#openalex-mcp-server) | 8011 | OpenAlex REST API over MCP |
| [`mcp/sudoc-sru`](#sudoc-sru-mcp-server) | 8012 | Sudoc SRU catalog search over MCP |

---

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for local script execution
- Docker + Docker Compose for containerized MCP servers

---

## Skills

All skills follow the same contract pattern:

```bash
uv run skills/<name>/scripts/cli.py prompt [--task <task>]   # read the methodological prompt
uv run skills/<name>/scripts/cli.py schema [--task <task>]   # read the JSON output schema
uv run skills/<name>/scripts/cli.py validate --json-file /tmp/output.json [--task <task>]
```

Skills with a single task (`generate-search-queries`) do not take a `--task` flag.
Skills with multiple tasks (`synthesize-literature`) require `--task`.

To use a skill, mention its name in your prompt. The agent reads `skills/<name>/SKILL.md`
and follows the workflow.

> See [`HUB-REGISTRY.md`](./skills/HUB-REGISTRY.md) for the full skill map, logical skill
> identifiers, and the annotated pipeline showing how outputs chain into inputs.

---

### generate-search-queries

Translates a natural-language research question into 8–15 bilingual (EN/FR)
search queries, with concept decomposition and terminology expansion.
Always run this skill first, before any retrieval.

```bash
uv run skills/generate-search-queries/scripts/cli.py prompt
# → produce /tmp/queries.json, then:
uv run skills/generate-search-queries/scripts/cli.py validate \
  --json-file /tmp/queries.json
```

Output: `queries[].query` strings directly usable as `--query` in `search-works-openalex`.

---

### search-works-openalex

Retrieves scholarly works from OpenAlex. Four subcommands:

```bash
# Keyword search
uv run skills/search-works-openalex/scripts/cli.py search \
  --query "climate change adaptation" \
  --date-from 2023-01-01 \
  --max-results 15 \
  --sort-by cited_by_count:desc \
  --oa

# DOI resolution (single or batch)
uv run skills/search-works-openalex/scripts/cli.py batch-lookup-by-doi \
  --doi 10.1038/s41586-021-03819-2

# Citation graph
uv run skills/search-works-openalex/scripts/cli.py get-citing-works \
  --openalex-id W2741809807 --max-results 20

# Topic classification
uv run skills/search-works-openalex/scripts/cli.py classify-text \
  --text "We evaluate climate adaptation strategies in coastal wetlands..."
```

Environment variables (optional, set in `skills/search-works-openalex/.env`):

```bash
OPENALEX_API_KEY=        # optional, for higher rate limits
OPENALEX_HTTP_TIMEOUT=15.0
OPENALEX_MAX_RETRIES=2
OPENALEX_TRACE=0         # set to 1 to enable HTTP trace logging
```

---

### search-records-hal

Retrieves records from HAL (Hyper Articles en Ligne), the French open
repository. Collection-first by design — always provide `--collection` when
the user targets a specific institution or lab portal. Output schema is
aligned with `search-works-openalex` for seamless deduplication and
downstream processing.

```bash
# Collection-scoped search
uv run skills/search-records-hal/scripts/cli.py search \
  --collection "FRANCE-GRILLES" \
  --q 'text:intelligence artificielle' \
  --rows 20 \
  --fl 'halId_s,title_s,authFullName_s,publicationDateY_i,uri_s' \
  --wt json

# Publication trend by year (facets, no records)
uv run skills/search-records-hal/scripts/cli.py search \
  --collection "FRANCE-GRILLES" \
  --q 'text:machine learning' \
  --rows 0 --facet-field publicationDateY_i --wt json
```

Prefer this skill over `search-works-openalex` for French institutional
deposits and francophone preprints, or when `generate-search-queries`
produced queries with `lang: "fr"`. Run both in parallel and deduplicate
on `doi` for comprehensive coverage.

Environment variables (optional, set in `skills/search-records-hal/.env`):

```bash
HAL_HTTP_TIMEOUT=20.0
HAL_MAX_RETRIES=2
HAL_TRACE=0          # set to 1 to enable HTTP trace logging
```

---

### search-records-sudoc

Searches the Sudoc union catalogue — all French higher education and research
library holdings. Five subcommands covering the main use cases:

```bash
# Keyword search (uses Sudoc index syntax)
uv run skills/search-records-sudoc/scripts/cli.py search \
  --query "mti=intelligence artificielle and msu=apprentissage" \
  --doc-type b \
  --lang-major fre \
  --year-from 2018

# French theses on a topic
uv run skills/search-records-sudoc/scripts/cli.py search \
  --query "nth=toulouse and mti=machine learning" \
  --doc-type y

# Resolve a PPN or ISBN
uv run skills/search-records-sudoc/scripts/cli.py lookup-by-ppn --ppn 070685045
uv run skills/search-records-sudoc/scripts/cli.py lookup-by-isbn --isbn 978-2-07-036024-5

# Count records before fetching
uv run skills/search-records-sudoc/scripts/cli.py count --query "edi=gallimard"

# Browse an index to discover valid terms (useful to debug zero-result queries)
uv run skills/search-records-sudoc/scripts/cli.py scan --index vma --term abricot --max-terms 20
```

Use this skill for French academic library holdings, thesis lookup, UNIMARC
metadata, and RAMEAU subject headings. For French open-access preprints, use
`search-records-hal` instead. For international scholarly literature, use
`search-works-openalex`.

Environment variables (optional, set in `skills/search-records-sudoc/.env`):

```bash
SUDOC_HTTP_TIMEOUT=30.0
SUDOC_MAX_RETRIES=3
SUDOC_TRACE=0          # set to 1 to enable HTTP trace logging
```

---

### synthesize-literature

Contract pack for all post-retrieval stages of a literature review.
Eight tasks, each backed by a methodological prompt and a strict JSON schema.

```bash
# List available tasks
uv run skills/synthesize-literature/scripts/cli.py list

# Run a task (read prompt → produce JSON → validate)
uv run skills/synthesize-literature/scripts/cli.py prompt --task screen_study_prisma
uv run skills/synthesize-literature/scripts/cli.py validate \
  --task screen_study_prisma --json-file /tmp/screen_W123.json
```

Available tasks:

| Task | Purpose |
|---|---|
| `screen_study_prisma` | Title/abstract screening — include / exclude / uncertain |
| `summarize_paper` | Structured critical reading note |
| `extract_metadata` | Methodology and concept extraction |
| `appraise_study_quality` | Quality appraisal and risk of bias |
| `synthesize_papers_thematic` | Cross-cutting thematic synthesis |
| `synthesize_papers_chronological` | Evolution of a field over time |
| `synthesize_papers_methodological` | Comparison of methodological approaches |
| `synthesize_papers_prisma` | Formal PRISMA 2020 systematic synthesis |

---

### orchestrate-literature-review

End-to-end orchestrator. Sequences all the above skills into a governed pipeline:

```
generate-search-queries
  → search-works-openalex (≤ 3 queries)
  → deduplicate by DOI
  → screen-studies-prisma (per record)
  → summarize-paper (per included record)
  → [appraise-study-quality] (optional)
  → synthesize-papers-* (choose mode)
```

Use this skill when the task is a complete literature review from a research
question to a structured synthesis. For individual steps, use the relevant
skill directly.

The helper CLI documents the pipeline structure:

```bash
uv run skills/orchestrate-literature-review/scripts/cli.py steps
uv run skills/orchestrate-literature-review/scripts/cli.py step --id search_references
```

---

### trace-agent-execution

Transforms a raw execution log (any format, any framework) into a readable,
committable `.run.md` trace. Three output modes: `audit`, `narrative`, `compact`.

---

## Typical workflows

### A — Skill-only local workflow

```bash
# 1. Build search strategy
uv run skills/generate-search-queries/scripts/cli.py prompt
# → /tmp/queries.json (contains queries with lang "en" and "fr")

# 2. Retrieve papers — run both sources, deduplicate on doi
uv run skills/search-works-openalex/scripts/cli.py search \
  --query "$(jq -r '.queries[0].query' /tmp/queries.json)" \
  --max-results 15 > /tmp/results_openalex.json

uv run skills/search-records-hal/scripts/cli.py search \
  --collection "MY-COLLECTION" \
  --q "$(jq -r '.queries[] | select(.lang=="fr") | .query' /tmp/queries.json | head -1)" \
  --rows 15 > /tmp/results_hal.json

# 3. Screen, summarize, synthesize
uv run skills/synthesize-literature/scripts/cli.py prompt --task screen_study_prisma
uv run skills/synthesize-literature/scripts/cli.py prompt --task summarize_paper
uv run skills/synthesize-literature/scripts/cli.py prompt --task synthesize_papers_thematic
```

### B — Orchestrated review (one prompt)

Ask your agent:

> `Use orchestrate-literature-review to run a systematic review on GraphRAG`

The agent reads `skills/orchestrate-literature-review/SKILL.md` and drives
the full pipeline step by step.

### C — MCP-first workflow

1. Start the MCP servers (see below).
2. Connect your MCP client to both endpoints.
3. Ask your agent to search OpenAlex or query Sudoc — no CLI needed.

---

## MCP servers

### OpenAlex MCP server

```bash
# Local
uv run mcp/openalex/mcp_server.py \
  --api-key "$OPENALEX_API_KEY" \
  --host 0.0.0.0 --port 8011 \
  --transport streamable-http

# From GitHub (no clone needed)
uv run \
  https://raw.githubusercontent.com/smartbiblia-solutions/agent-skills/refs/heads/main/mcp/openalex/mcp_server.py \
  --api-key "$OPENALEX_API_KEY" --host 0.0.0.0 --port 8011 --transport streamable-http
```

### Sudoc SRU MCP server

```bash
# Local
uv run mcp/sudoc-sru/mcp_server.py \
  --host 0.0.0.0 --port 8012 \
  --transport streamable-http

# From GitHub
uv run \
  https://raw.githubusercontent.com/smartbiblia-solutions/agent-skills/refs/heads/main/mcp/sudoc-sru/mcp_server.py \
  --host 0.0.0.0 --port 8012 --transport streamable-http
```

### MCP client config (`mcpServers`)

```json
{
  "mcpServers": {
    "openalex": {
      "command": "uvx",
      "args": [
        "run",
        "/absolute/path/to/mcp/openalex/mcp_server.py",
        "--api-key", "YOUR_OPENALEX_API_KEY",
        "--host", "0.0.0.0",
        "--port", "8011",
        "--transport", "streamable-http"
      ],
      "env": { "UV_CACHE_DIR": "/root/.cache/uv" }
    },
    "sudoc-sru": {
      "command": "uvx",
      "args": [
        "run",
        "/absolute/path/to/mcp/sudoc-sru/mcp_server.py",
        "--host", "0.0.0.0",
        "--port", "8012",
        "--transport", "streamable-http"
      ],
      "env": { "UV_CACHE_DIR": "/root/.cache/uv" }
    }
  }
}
```

---

## Docker

### Build and run manually

```bash
docker build -t smartbiblia-mcp-openalex ./mcp/openalex
docker build -t smartbiblia-mcp-sudoc-sru ./mcp/sudoc-sru

docker run --rm -p 8011:8011 \
  -e OPENALEX_API_KEY="$OPENALEX_API_KEY" \
  -e MCP_HOST=0.0.0.0 -e MCP_PORT=8011 -e MCP_TRANSPORT=streamable-http \
  smartbiblia-mcp-openalex

docker run --rm -p 8012:8012 \
  -e MCP_HOST=0.0.0.0 -e MCP_PORT=8012 -e MCP_TRANSPORT=streamable-http \
  smartbiblia-mcp-sudoc-sru
```

### Docker Compose

```bash
cp .env.example .env          # then set OPENALEX_API_KEY
docker compose up --build
docker compose down
```

---

## Download a single skill or MCP server

Use [DownGit](https://downgit.github.io/) to download one folder without
cloning the full repository:

- `https://github.com/smartbiblia-solutions/agent-skills/tree/main/skills/search-works-openalex`
- `https://github.com/smartbiblia-solutions/agent-skills/tree/main/mcp/openalex`

---

## Notes

- `mcp/openalex/mcp_server.py` reads all parameters from CLI args.
- `mcp/sudoc-sru/mcp_server.py` requires no external API key.
- `SKILL.md` files are the authoritative source for task semantics, prompt contracts, and expected JSON output schemas.
- See [`HUB-REGISTRY.md`](./skills/HUB-REGISTRY.md) for the complete skill map and logical skill identifiers.