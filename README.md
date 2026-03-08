# SmartBibl.IA Agent Skills Hub

Hub of ready-to-use skills and MCP servers for AI agents, focused on libraries, scholarly information, and research workflows.

This repository provides reusable agent skills and MCP servers designed for documentary tasks such as:

- bibliographic search
- metadata retrieval
- library catalog queries
- scholarly API access (OpenAlex, Crossref, etc.)
- document analysis and enrichment

Compatible with modern agents like Claude Code, Codex, Opencode, Nanobot, OpenClaw, etc.

Skills and MCP servers for academic literature workflows.

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for local script execution
- Docker + Docker Compose for containerized MCP with Dockerfiles for MCP servers and root `compose.yml`

## Skills: how to use

Skills are documented in each `SKILL.md`.

### Use in Codex (Linux or WSL)

**Important**: Optional but recommended:

```bash
export UV_CACHE_DIR=/root/.cache/uv
```

Ask explicitly for the skill by name in your prompt, for example:

- `$openalex Find recent papers about battery recycling`
- `$build-search-queries Build EN/FR search queries for a review question`
- `$academic-review-engine Validate this JSON against synthesize_papers_thematic`
- `$literature-review-agent Orchestrate a review about GraphRAG`

Codex can then read the corresponding `skills/<name>/SKILL.md` and execute the workflow/commands.

### Use in Claude Code (Linux or WSL)

Same principle: mention the skill name and the task, for example:

- `Use the openalex skill and search 10 papers on CRISPR from 2024 to 2026`
- `Use build-search-queries to design the search strategy for my question`
- `Use academic-review-engine to get the prompt for summarize_paper`

If needed, point Claude Code to the file directly:

- `skills/openalex/SKILL.md`
- `skills/build-search-queries/SKILL.md`
- `skills/academic-review-engine/SKILL.md`
- `skills/literature-review-agent/SKILL.md`

## Skill CLI usage (local)

### 1) OpenAlex skill CLI

Main commands:

```bash
uv run skills/openalex/scripts/cli.py search \
  --query "climate change adaptation" \
  --date-from 2026-01-01 \
  --date-to 2026-12-31 \
  --max-results 10 \
  --sort-by cited_by_count:desc

uv run skills/openalex/scripts/cli.py batch-lookup-by-doi \
  --doi 10.1038/s41586-021-03819-2

uv run skills/openalex/scripts/cli.py get-citing-works \
  --openalex-id W2741809807 --max-results 20

uv run skills/openalex/scripts/cli.py classify-text \
  --text "We evaluate climate adaptation strategies in coastal wetlands..."
```

OpenAlex env vars (CLI):

```bash
export OPENALEX_API_KEY="your_key"
export OPENALEX_HTTP_TIMEOUT="15.0"
export OPENALEX_MAX_RETRIES="2"
export OPENALEX_BACKOFF_BASE="1.0"
export OPENALEX_BACKOFF_FACTOR="2.0"
export OPENALEX_JITTER_MAX="0.25"
export OPENALEX_TRACE="0"
```

Or inline:

```bash
OPENALEX_API_KEY="your_key" OPENALEX_TRACE=1 \
uv run skills/openalex/scripts/cli.py search --query "fisheries climate vulnerability"
```

### 2) Build Search Queries skill CLI

```bash
uv run skills/build-search-queries/scripts/cli.py prompt

uv run skills/build-search-queries/scripts/cli.py schema

uv run skills/build-search-queries/scripts/cli.py validate \
  --json-file /tmp/queries.json
```

### 3) Academic Review Engine skill CLI

```bash
uv run skills/academic-review-engine/scripts/cli.py list

uv run skills/academic-review-engine/scripts/cli.py schema \
  --task synthesize_papers_thematic

uv run skills/academic-review-engine/scripts/cli.py validate \
  --task summarize_paper \
  --json-file /tmp/summary.json
```

### 4) Literature Review Agent skill CLI

```bash
uv run skills/literature-review-agent/cli.py name
uv run skills/literature-review-agent/cli.py steps
uv run skills/literature-review-agent/cli.py step --id search_references
```

Env vars:

```bash
export LITERATURE_REVIEW_AGENT_NAME="my-review-agent"
```

## MCP servers: 

### 1) Local usage with `uv run`

#### OpenAlex MCP (`mcp/openalex/mcp_server.py`)

`--api-key` is required.

```bash
uv run mcp/openalex/mcp_server.py \
  --api-key "$OPENALEX_API_KEY" \
  --host 0.0.0.0 \
  --port 8011 \
  --transport streamable-http \
  --http-timeout 15.0 \
  --max-retries 2 \
  --backoff-base 1.0 \
  --backoff-factor 2.0 \
  --jitter-max 0.25
```

### Sudoc SRU MCP (`mcp/sudoc-sru/mcp_server.py`)

```bash
uv run mcp/sudoc-sru/mcp_server.py \
  --host 0.0.0.0 \
  --port 8012 \
  --transport streamable-http
```

## MCP servers: remote one-file run from GitHub

You can run MCP servers directly from raw GitHub URLs.

```bash
uv run \
  https://raw.githubusercontent.com/smartbiblia-solutions/agent-skills/refs/heads/main/mcp/openalex/mcp_server.py \
  --api-key "$OPENALEX_API_KEY" --host 0.0.0.0 --port 8011 --transport streamable-http

uv run \
  https://raw.githubusercontent.com/smartbiblia-solutions/agent-skills/refs/heads/main/mcp/sudoc-sru/mcp_server.py \
  --host 0.0.0.0 --port 8012 --transport streamable-http
```

## Standard MCP client config (`mcpServers`)

Many MCP clients use a JSON config like this:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["..."],
      "env": {
        "KEY": "value"
      }
    }
  }
}
```

OpenAlex from local file:

```json
{
  "mcpServers": {
    "openalex": {
      "command": "uvx",
      "args": [
        "run",
        "/absolute/path/to/smartbiblia-marketplace/mcp/openalex/mcp_server.py",
        "--api-key",
        "YOUR_OPENALEX_API_KEY",
        "--host",
        "0.0.0.0",
        "--port",
        "8011",
        "--transport",
        "streamable-http"
      ],
      "env": {
        "UV_CACHE_DIR": "/root/.cache/uv"
      }
    }
  }
}
```

OpenAlex from GitHub raw URL:

```json
{
  "mcpServers": {
    "openalex-remote": {
      "command": "uvx",
      "args": [
        "run",
        "https://raw.githubusercontent.com/smartbiblia-solutions/agent-skills/refs/heads/main/mcp/openalex/mcp_server.py",
        "--api-key",
        "YOUR_OPENALEX_API_KEY",
        "--host",
        "0.0.0.0",
        "--port",
        "8011",
        "--transport",
        "streamable-http"
      ],
      "env": {
        "UV_CACHE_DIR": "/root/.cache/uv"
      }
    }
  }
}
```

## Download only part of the repo

If you only need one folder/file from GitHub, use DownGit:

- Tool: https://downgit.github.io/
- Paste a GitHub folder URL, for example:
  - `https://github.com/smartbiblia-solutions/agent-skills/tree/<ref>/skills/openalex`
  - `https://github.com/smartbiblia-solutions/agent-skills/tree/<ref>/mcp/openalex`

This is useful when you want only one skill or one MCP server without cloning the whole repository.

## Docker: run MCP servers in containers

### Build images manually

```bash
docker build -t smartbiblia-mcp-openalex ./mcp/openalex
docker build -t smartbiblia-mcp-sudoc-sru ./mcp/sudoc-sru
```

### Run OpenAlex MCP container

```bash
docker run --rm -p 8011:8011 \
  -e OPENALEX_API_KEY="$OPENALEX_API_KEY" \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8011 \
  -e MCP_TRANSPORT=streamable-http \
  smartbiblia-mcp-openalex
```

### Run Sudoc SRU MCP container

```bash
docker run --rm -p 8012:8012 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8012 \
  -e MCP_TRANSPORT=streamable-http \
  smartbiblia-mcp-sudoc-sru
```

## Docker Compose (root `compose.yml`)

### 1) Set environment

```bash
export OPENALEX_API_KEY="your_key"
```

Or create `.env` at repo root:

```dotenv
OPENALEX_API_KEY=your_key
```

From template:

```bash
cp .env.example .env
```

### 2) Start services

```bash
docker compose up --build
```

### 3) Stop services

```bash
docker compose down
```

## Typical integration patterns

### A) Skill-only local workflow (no MCP)

1. `skills/build-search-queries/scripts/cli.py` to design search queries.
2. `skills/openalex/cli.py` to retrieve papers.
3. `skills/academic-review-engine/scripts/cli.py prompt` to generate contract prompt.
4. Host LLM produces JSON.
5. `skills/academic-review-engine/scripts/cli.py validate` to enforce schema.

### B) MCP-first workflow

1. Run OpenAlex MCP on `:8011`.
2. Run Academic Review Engine MCP on `:8012`.
3. Connect your MCP client (Codex/Claude-compatible host) to both endpoints.
4. Orchestrate the review process in your host LLM.

## Notes

- `mcp/openalex/mcp_server.py` reads API/runtime parameters from CLI args.
- `mcp/academic-review-engine/mcp_server.py` is standalone (no external API key needed).
- Skill docs remain the source of truth for task semantics and expected JSON outputs.
