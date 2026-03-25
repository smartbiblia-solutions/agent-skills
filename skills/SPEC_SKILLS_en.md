# Skills Hub Specification — Scholarly & Library Workflows

> Lightweight reference for naming, manifest structure, and agent routing.
> Compatible with AgentSkills conventions and OpenClaw/ClawHub format.

---

## 0. Compatibility notes

This spec targets the **AgentSkills** format as implemented by **OpenClaw**.
Key constraints imposed by OpenClaw's parser:

- The `name` field in YAML frontmatter must be **snake_case**.
- The `metadata` field must be a **single-line JSON object** (no multi-line YAML nesting).
- The `selection` block is a **AgentDesk-only extension**: OpenClaw ignores it gracefully;
  AgentDesk uses it for its skill recommendation UI and pipeline builder.
- The folder name (used as ClawHub slug) stays **kebab-case** — it is independent from `name`.

**Folder name** (slug, kebab-case) → `search-works-openalex`  
**`name` field** (snake_case, runtime identifier) → `search_works_openalex`

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
- **Folder name and ClawHub slug**: hyphens as separators (kebab-case)
- **`name` field in YAML**: underscores as separators (snake_case) — OpenClaw requirement
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
Folder / slug (kebab)          →  name field (snake_case)
──────────────────────────────────────────────────────────
generate-search-queries        →  generate_search_queries
search-works-openalex          →  search_works_openalex
search-records-sudoc           →  search_records_sudoc
lookup-dois-crossref           →  lookup_dois_crossref
extract-metadata-pdf           →  extract_metadata_pdf
extract-metadata-unimarc       →  extract_metadata_unimarc
screen-studies-prisma          →  screen_studies_prisma
summarize-paper                →  summarize_paper
synthesize-papers-thematic     →  synthesize_papers_thematic
appraise-study-quality         →  appraise_study_quality
classify-text-openalex         →  classify_text_openalex
trace-agent-execution          →  trace_agent_execution
```

### Names to avoid

```
academic-review-engine   → describes architecture, not action
literature-review-agent  → avoid "agent"
openakes                 → opaque
sru-sudoc                → no verb
search-screen-summarize-papers-openalex  → overloaded
```

---

## 3. Manifest structure

The frontmatter must stay **minimal and single-line compatible**.
OpenClaw's parser does not support multi-line YAML values under `metadata`.

### Required fields

```yaml
name: search_works_openalex
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

The `metadata` field must be a **single-line JSON object** merging:
- Your hub metadata (`version`, `author`, `maturity`, `preferred_output`, etc.)
- The `openclaw` sub-object for gating and runtime behavior

```yaml
metadata: {"version": "0.1.0", "author": "smartbiblia", "maturity": "beta", "preferred_output": "json", "openclaw": {"emoji": "🔬", "requires": {"env": ["OPENALEX_API_KEY"]}}}
```

For skills requiring no external binaries or env vars, `openclaw` can be omitted:

```yaml
metadata: {"version": "0.1.0", "author": "smartbiblia", "maturity": "beta", "preferred_output": "json"}
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
metadata: {"openclaw": {"requires": {"bins": ["uv", "curl"]}}}
```

### `requires.env`

List of environment variable names that must be set (or provided via config).

```yaml
metadata: {"openclaw": {"requires": {"env": ["OPENALEX_API_KEY"]}}}
```

### `requires.anyBins`

At least one binary in the list must exist. Use for tools with alternative
implementations.

```yaml
metadata: {"openclaw": {"requires": {"anyBins": ["curl", "wget"]}}}
```

### `requires.config`

List of `openclaw.json` config paths that must be truthy.

```yaml
metadata: {"openclaw": {"requires": {"config": ["browser.enabled"]}}}
```

### `primaryEnv`

The canonical API key env var for this skill. Enables the `skills.entries.<n>.apiKey`
convenience in `openclaw.json`.

```yaml
metadata: {"openclaw": {"primaryEnv": "OPENALEX_API_KEY", "requires": {"env": ["OPENALEX_API_KEY"]}}}
```

### `os`

Restrict the skill to specific platforms.

```yaml
metadata: {"openclaw": {"os": ["darwin", "linux"]}}
```

### `install`

Optional installer spec for the macOS Skills UI and automated setup.
Supported kinds: `brew`, `node`, `go`, `uv`, `download`.

```yaml
metadata: {"openclaw": {"requires": {"bins": ["uv"]}, "install": [{"id": "uv-pip", "kind": "uv", "package": "scholarly", "bins": ["scholarly"], "label": "Install scholarly (uv)"}]}}
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
| `emoji` | string | Emoji for macOS Skills UI |

---

## 5. SKILL.md body structure

Keep the frontmatter concise. Detailed usage belongs in the body.
Adapt the sections to the skill type — not every skill needs every section.

```markdown
--- YAML FRONTMATTER ---

# Skill title

## Purpose
One paragraph. What problem this skill solves and for whom.

## When to use / When not to use
Mirrors the `selection` block, but in prose. Add nuance the YAML can't carry.

## Input
What the skill expects: format, required fields, constraints.

## Output
What the skill returns: format, schema, example.

## Commands
How to invoke the skill (CLI, prompt command, API call).

## Examples
1–2 concrete input/output pairs.

## Composition hints
What typically comes before and after this skill in a pipeline.

## Failure modes         ← only if non-obvious
Known failure conditions and how to handle them.

## Validation           ← only for contract-based skills
Schema command, validate command, retry policy.
```

---

## 6. Agent selection guidance

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

### Chaining guidance

Document what comes before and after each skill.
Example pipeline for a systematic review:

```
generate-search-queries
  → search-works-openalex
  → screen-studies-prisma
  → summarize-paper
  → appraise-study-quality
  → synthesize-papers-thematic
```

---

## 7. Complete manifest example

```yaml
name: generate_search_queries
description: >
  Generate structured scholarly search queries from a natural-language research
  question. Use this skill whenever the task involves building a search strategy,
  expanding a review question into searchable expressions, or designing bilingual
  queries for systematic reviews. Always use this skill before retrieving records
  from any corpus. Returns validated JSON.

metadata: {"version": "0.1.0", "author": "smartbiblia", "maturity": "beta", "preferred_output": "json", "domain": "scholarly-communication", "category": "generation", "openclaw": {"emoji": "🔎", "requires": {}}}

selection:
  use_when:
    - The task is to translate a research question into searchable expressions.
    - The user needs a bilingual or multi-database search strategy.
  avoid_when:
    - Records have already been retrieved.
    - The user only needs a single keyword, not a structured query.
  prefer_over:
    - generic-keyword-generator
  combine_with:
    - search-works-openalex
    - search-records-sudoc

tags:
  - systematic-review
  - search-strategy
  - scholarly
```

Folder name: `generate-search-queries/SKILL.md`

---

## 8. ClawHub publishing

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

## 9. AgentDesk import notes

When AgentDesk imports a skill from the Github registry:

1. **`metadata` transformation** — the human-readable multi-level YAML that
   contributors *may* write in the repo is normalized to the single-line JSON
   format required by OpenClaw at install time. Contributors can write either
   style; AgentDesk normalizes on import.
2. **`selection` block** — parsed and stored as AgentDesk metadata for the
   skill recommendation UI (`combine_with`, pipeline builder). Not forwarded
   to the agent runtime.
3. **Gating** — `metadata.openclaw.requires` is evaluated against the local
   environment at install time. Missing bins or env vars generate a warning
   in the AgentDesk UI.

---

## 10. Rules summary

### Required
- Folder name: lowercase kebab-case starting with a verb (`search-works-openalex`)
- `name` field: snake_case version of the folder name (`search_works_openalex`)
- `<verb>-<object>-<source>` pattern when source matters
- Rich `description` answering: what / when / what it returns
- `metadata` as a single-line JSON object

### Strongly recommended
- `metadata.openclaw.requires` for any skill needing binaries, env vars, or config keys
- `metadata.openclaw.primaryEnv` for skills with a canonical API key
- `selection` block with `use_when`, `avoid_when`, `combine_with`
- `metadata.maturity` and `metadata.preferred_output`
- Chaining documentation in SKILL.md body

### Avoid
- Architectural terms in skill IDs (`engine`, `agent`, `tool`, `runner`)
- Opaque or brand-like names
- Overloaded multi-action names
- Version suffixes in names
- Multi-line YAML nesting under `metadata` (breaks OpenClaw's parser)
- Filling optional metadata fields with placeholder values
