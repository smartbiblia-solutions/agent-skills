# Skills Hub Specification — Scholarly & Library Workflows

> Lightweight reference for naming, manifest structure, and agent routing.
> Compatible with AgentSkills conventions and OpenClaw/ClawHub format.

---

## 0. Compatibility notes

This spec targets the **AgentSkills** format as implemented by **OpenClaw**.
Key constraints imposed by OpenClaw's parser:

- The `name` field in YAML frontmatter uses **kebab-case** — identical to the folder name.
- The `metadata` field must contain valid **JSON** (single-line compact or multi-line pretty-printed).
- The `selection` block is a **AgentDesk-only extension**: OpenClaw ignores it gracefully;
  AgentDesk uses it for its skill recommendation UI and pipeline builder.

**Folder name** and **`name` field** both use kebab-case: `search-works-openalex`

---

## 1. Design principles

- A skill name is a **routing identifier**, not a marketing label.
- A skill expresses **one dominant capability**.
- The `description` field is the **primary triggering mechanism** — it must be rich enough
  for an agent to select the skill without reading the body.
- Everything else in the manifest supports disambiguation and chaining, not routing.

---

## 2. Naming convention

### Pattern

```
<verb>-<object>-<source>
```

- **verb** — the main action performed
- **object** — the primary entity manipulated or returned
- **source** — the external system or corpus, when the behavior depends on it

The `source` segment is optional for source-agnostic skills:

```
<verb>-<object>
```

### Character rules

- Lowercase ASCII only
- **Folder name, ClawHub slug, and `name` field**: all use kebab-case (hyphens as separators)
- No version suffixes in names
- No architectural terms: avoid `engine`, `agent`, `tool`, `runner`, `service`

### Recommended verbs

| Verb | Use when |
|------|----------|
| `search` | Discovering items from a corpus |
| `lookup` | Resolving a known identifier |
| `fetch` / `retrieve` | Pulling a known resource |
| `generate` | Creating a new output |
| `extract` | Pulling structured info from a document |
| `summarize` | Condensing a single document |
| `synthesize` | Integrating multiple documents analytically |
| `screen` | Filtering a set against criteria |
| `appraise` | Evaluating quality or relevance |
| `classify` | Assigning categories or topics |
| `trace` | Documenting an execution |
| `validate` | Checking conformance to a schema or rule |
| `convert` | Transforming format or structure |
| `annotate` | Adding structured metadata to existing content |
| `orchestrate` | Orchestrating a pipeline end-to-end |
| `run` | Alternative to `orchestrate` for simpler pipelines |

### Good names

```
generate-search-queries
search-works-openalex
search-records-sudoc
lookup-dois-crossref
extract-metadata-pdf
extract-metadata-unimarc
screen-studies-prisma
summarize-paper
synthesize-papers-thematic
appraise-study-quality
classify-text-openalex
trace-agent-execution
```

### Names to avoid

```
academic-review-engine   → describes architecture, not action
literature-review-agent  → avoid "agent"
openalex                 → opaque
sru-sudoc                → no verb
search-screen-summarize-papers-openalex  → overloaded
```

---

## 3. Manifest structure

The frontmatter must stay **minimal and single-line compatible**.
OpenClaw's parser does not support multi-line YAML values under `metadata`.

### Required fields

```yaml
name: search-works-openalex
description: >
  Search and retrieve scholarly works from OpenAlex. Use this skill when the
  task is to discover academic papers, resolve bibliographic entities, or
  retrieve structured metadata from the OpenAlex corpus. Prefer this skill
  over generic web search for any scholarly retrieval task. Returns JSON.
```

**Writing the description well is the most important thing in the manifest.**
It should answer three questions in 2–4 sentences:
- What does this skill do?
- When should an agent pick it?
- What does it return?

### Recommended fields

The `metadata` field contains hub metadata and the `openclaw` sub-object for gating and runtime behavior. It can be written as **multi-line YAML with embedded JSON** for readability (preferred), or as **single-line JSON** for compactness. AgentDesk normalizes either format on import.

**Multi-line format (preferred for readability):**

```yaml
metadata:
  {
    "version": "0.1.0",
    "author": "smartbiblia",
    "maturity": "beta",
    "preferred_output": "json",
    "openclaw":
      {
        "requires": { "bins": ["uv"], "env": ["OPENALEX_API_KEY"] },
        "primaryEnv": "OPENALEX_API_KEY",
      },
  }
```

**Single-line format (compact):**

```yaml
metadata: {"version": "0.1.0", "author": "smartbiblia", "maturity": "beta", "preferred_output": "json", "openclaw": {"requires": {"bins": ["uv"], "env": ["OPENALEX_API_KEY"]}, "primaryEnv": "OPENALEX_API_KEY"}}
```

For skills requiring no external binaries or env vars, `openclaw` can be omitted:

```yaml
metadata:
  {
    "version": "0.1.0",
    "author": "smartbiblia",
    "maturity": "beta",
    "preferred_output": "json",
  }
```

The `selection` block is a **multi-line YAML extension** for AgentDesk and human readers.
OpenClaw ignores it. Keep it when it adds routing or chaining value.

```yaml
selection:
  use_when:
    - The task is to retrieve scholarly works from OpenAlex.
  avoid_when:
    - The task is to synthesize already-retrieved papers.
    - The task concerns a library catalog rather than scholarly articles.
  prefer_over:
    - generic-web-search
  combine_with:
    - generate-search-queries
    - summarize-paper
    - synthesize-papers-thematic

tags:
  - openalex
  - scholarly
  - retrieval
```

---

## 4. Gating (OpenClaw load-time filters)

OpenClaw filters skills at load time using `metadata.openclaw`.
Declare gates so the agent never attempts to use a skill whose dependencies
are absent from the environment.

### `requires.bins`

List of binaries that must exist on `PATH`. The skill is silently excluded if
any binary is missing.

```yaml
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv", "curl"] },
      },
  }
```

### `requires.env`

List of environment variable names that must be set (or provided via config).

```yaml
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["OPENALEX_API_KEY"] },
      },
  }
```

### `requires.anyBins`

At least one binary in the list must exist. Use for tools with alternative
implementations.

```yaml
metadata:
  {
    "openclaw":
      {
        "requires": { "anyBins": ["curl", "wget"] },
      },
  }
```

### `requires.config`

List of `openclaw.json` config paths that must be truthy.

```yaml
metadata:
  {
    "openclaw":
      {
        "requires": { "config": ["browser.enabled"] },
      },
  }
```

### `primaryEnv`

The canonical API key env var for this skill. Enables the `skills.entries.<n>.apiKey`
convenience in `openclaw.json`.

```yaml
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["OPENALEX_API_KEY"] },
        "primaryEnv": "OPENALEX_API_KEY",
      },
  }
```

### `os`

Restrict the skill to specific platforms.

```yaml
metadata:
  {
    "openclaw":
      {
        "os": ["darwin", "linux"],
      },
  }
```

### `install`

Optional installer spec for automated setup. Supported kinds: `brew`, `node`, `go`, `uv`, `download`.

```yaml
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv"] },
        "install": [{ "id": "uv-pip", "kind": "uv", "package": "scholarly", "bins": ["scholarly"], "label": "Install scholarly (uv)" }],
      },
  }
```

### Gating reference table

| Field | Type | Purpose |
|-------|------|---------|
| `requires.bins` | string[] | All must exist on PATH |
| `requires.anyBins` | string[] | At least one must exist on PATH |
| `requires.env` | string[] | All must be set in environment or config |
| `requires.config` | string[] | All config paths must be truthy |
| `primaryEnv` | string | Canonical API key var name |
| `os` | string[] | `darwin`, `linux`, `win32` — restrict by platform |
| `install` | object[] | Installer specs for automated setup |
| `always` | boolean | Set `true` to bypass all other gates |
| `homepage` | string | Optional URL shown as 'Website' in the UI |

---

## 5. CLI Implementation

All CLI-based skills **must** use `uv` as the package manager and runtime. CLI scripts should be self-contained Python files with inline script metadata.

### Inline script header

Every CLI script must begin with:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ['httpx', 'python-dotenv']
# ///
```

Replace dependencies with the actual packages required. Keep dependencies minimal — prefer stdlib when sufficient.

### Why uv

- **Zero configuration**: No `requirements.txt`, `pyproject.toml`, or virtualenv needed
- **Single file**: The script carries its own dependency declaration
- **Fast**: `uv run` caches and executes without manual installation
- **Reproducible**: Locked dependency resolution on first run

### CLI conventions

- Emit **strict JSON on stdout** for machine-readable output
- Exit code always `0`; errors surfaced in an `error` field within the JSON
- Support `--help` for all subcommands
- Use environment variables for configuration (with `.env` support via `python-dotenv`)
- Include retry/backoff logic for external API calls
- Support `--trace` flag for HTTP debugging

### Skill folder structure

```
skills/<skill-name>/
  SKILL.md              ← the skill manifest and body
  scripts/              ← CLI scripts (retrieval skills)
    cli.py
    .env.example
  prompts/              ← methodological prompts (contract pack skills)
  schemas/              ← JSON schemas (contract pack skills)
  references/           ← maintenance documents, not used at agent runtime
    llm.md              ← API reference (only when API has no llm.txt)
```

No packaging step needed — agents access skills directly from the repo
by path (`skills/<n>/SKILL.md`).

### Common record schema

Retrieval skills must normalize their output to this shape so downstream steps
can process records from any source without transformation:

```jsonc
{
  "source": "openalex | hal | sudoc | …",
  "id": "<source-specific id>",
  "title": "string",
  "authors": ["First Last"],
  "abstract": "string or null",
  "doi": "10.xxx/… or null",
  "pdf_url": "https://… or null",
  "url": "https://…",
  "year": 2024,
  "date": "2024-03-15 or null",
  "doc_type": "string or null",
  "journal": "string or null"
}
```

Source-specific fields (e.g. `hal_id`, `ppn`, `cited_by_count`) may be added
alongside the common fields. Do not rename or remove common fields.

For contract pack skills, the CLI exposes only three subcommands:
`prompt`, `schema`, and `validate --json-file <f>`.
Single-task contract packs have no `--task` flag.

---

## 6. SKILL.md body structure

Keep the frontmatter concise. Detailed usage belongs in the body.
Adapt the sections to the skill type — not every skill needs every section.

### Mandatory for all skills

```markdown
--- YAML FRONTMATTER ---

# Skill title

## Purpose
One paragraph. What problem this skill solves and for whom.

## When to use / When not to use
Mirrors the `selection` block, but in prose. Add nuance the YAML can't carry.

## CLI usage            ← or ## Subcommands for multi-command skills
How to invoke the skill. Use `uv run skills/<n>/scripts/cli.py <subcommand>` form.

## Output
What the skill returns: format, schema, jsonc example.

## Composition hints
Pipeline diagram showing where this skill sits relative to upstream and downstream steps.
```

### Mandatory for CLI retrieval skills (additional)

```markdown
## Environment variables
Table of all env vars consumed by the CLI, with defaults and required/optional status.

## Failure modes
Exit code behavior, the `error` field contract, known edge cases.
```

### Mandatory for contract pack skills (additional)

```markdown
## Task reference
Table of tasks with schema names and required inputs.
Single-task packs have one row and no --task flag.

## Rules
Validate-before-proceed policy, retry limit, JSON-only output constraint.
```

### Optional (add only when genuinely useful)

```markdown
## Input
What the skill expects: format, required fields, constraints.
Only needed when input is non-obvious or structured.

## Common workflows
3–5 concrete bash examples covering distinct use cases.

## Index reference / ## Query syntax
For Solr/SRU skills with complex query languages.

## Data coverage
Scope, format, authentication requirements.
```

---

## 7. Agent selection guidance

### Disambiguation rule

When multiple skills could apply, prefer in this order:

1. Most **source-specific** compatible skill
2. Most **atomic** skill
3. Skill with **explicit validation**
4. More general fallback

**Example** — user asks: *"Find papers on multilingual subject indexing in libraries."*

```
1. generate-search-queries   ← translate the question first
2. search-works-openalex     ← retrieve from scholarly corpus
3. search-records-sudoc      ← only if catalog evidence is also needed
4. generic web search        ← last resort
```

---

## 8. Complete manifest example

```yaml
name: generate-search-queries
description: >
  Generate structured scholarly search queries from a natural-language research
  question. Use this skill whenever the task involves building a search strategy,
  expanding a review question into searchable expressions, or designing bilingual
  queries for systematic reviews. Always use this skill before retrieving records
  from any corpus. Returns validated JSON.

metadata:
  {
    "version": "0.1.0",
    "author": "smartbiblia",
    "maturity": "beta",
    "preferred_output": "json",
    "domain": "scholarly-communication",
    "category": "generation",
    "openclaw": { "requires": {} },
  }

selection:
  use_when:
    - The task is to translate a research question into searchable expressions.
    - The user needs a bilingual or multi-database search strategy.
  avoid_when:
    - Records have already been retrieved.
    - The user only needs a single keyword, not a structured query.

tags:
  - systematic-review
  - search-strategy
  - scholarly
```

Folder name: `generate-search-queries/SKILL.md`

---

## 9. ClawHub publishing

ClawHub is the public registry for OpenClaw skills. The folder name is the slug.

```bash
# Publish a single skill
clawhub publish ./generate-search-queries \
  --slug generate-search-queries \
  --name "Generate Search Queries" \
  --version 0.1.0 \
  --tags latest

# Sync all skills in the repo at once
clawhub sync --all --bump patch
```

The Github repository remains the source of truth.
`clawhub sync` is the publication automation step.

---

## 10. AgentDesk import notes

When AgentDesk imports a skill from the Github registry:

1. **`metadata` transformation** — the multi-line JSON-in-YAML format that
   contributors write in the repo is normalized to the single-line JSON
   format required by OpenClaw at install time. Both formats are valid;
   AgentDesk normalizes on import.
2. **`selection` block** — parsed and stored as AgentDesk metadata for the
   skill recommendation UI (`use_when`, `avoid_when`). Not forwarded
   to the agent runtime.
3. **Gating** — `metadata.openclaw.requires` is evaluated against the local
   environment at install time. Missing bins or env vars generate a warning
   in the AgentDesk UI.

---

## 11. Rules summary

### Required
- Folder name: lowercase kebab-case starting with a verb (`search-works-openalex`)
- `name` field: kebab-case, identical to the folder name (`search-works-openalex`)
- `<verb>-<object>-<source>` pattern when source matters
- Rich `description` answering: what / when / what it returns
- `metadata` with valid JSON structure (single-line or multi-line)

### Strongly recommended
- `metadata.openclaw.requires` for any skill needing binaries, env vars, or config keys
- `metadata.openclaw.primaryEnv` for skills with a canonical API key
- `selection` block with `use_when`, `avoid_when`
- `metadata.maturity` and `metadata.preferred_output`
- Chaining documentation in SKILL.md body

### Avoid
- Architectural terms in skill IDs (`engine`, `agent`, `tool`, `runner`)
- Opaque or brand-like names
- Overloaded multi-action names
- Version suffixes in names
- Filling optional metadata fields with placeholder values
