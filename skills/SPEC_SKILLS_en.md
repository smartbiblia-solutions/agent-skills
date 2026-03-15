# Skills Hub Specification — Scholarly & Library Workflows

> Lightweight reference for naming, manifest structure, and agent routing.
> Compatible with AgentSkills conventions.

---

## 1. Design principles

- A skill name is a **routing identifier**, not a marketing label.
- A skill expresses **one dominant capability**.
- The `description` field is the **primary triggering mechanism** — it must be rich enough for an agent to select the skill without reading the body.
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
- Hyphens as separators, no underscores
- No version suffixes in the name
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
| `synthetize` |  |
| `orchestrate` | Orchestrating pipeline end-to-end |
| `run` | `orchestrate` alternative |

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
openakes                 → opaque
sru-sudoc                → no verb
search-screen-summarize-papers-openalex  → overloaded
```

---

## 3. Manifest structure

The frontmatter must stay **minimal**. The agent reads `name` and `description` first —
everything else is secondary.

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

```yaml
metadata:
  version: 0.1.0
  author: smartbiblia
  maturity: experimental | beta | stable | deprecated
  preferred_output: json | markdown | text | csv | xml

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

### Optional fields

Add these only when they carry real information for your hub registry:

```yaml
metadata:
  domain: scholarly-communication | research-workflows | libraries | bibliometrics
  category: retrieval | generation | extraction | synthesis | screening | appraisal
  source: openalex | crossref | sudoc | pubmed
  interface: cli | api | mcp
  requires_network: true
  supports_validation: true
```

### What to omit

Fields to drop unless you have a concrete reason to fill them:
`deterministic`, `scope`, `subcategory`, `entrypoint`, `package_manager`,
`requires_auth`, `input_modes`, `output_modes`, `languages`.
Stale metadata is worse than no metadata.

---

## 4. SKILL.md body structure

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

## 5. Agent selection guidance

### Disambiguation rule

When multiple skills could apply, prefer in this order:

1. Most **source-specific** compatible skill
2. Most **atomic** skill
3. Skill with **explicit validation**
4. More general fallback

**Example** — user asks: *"Find papers on multilingual subject indexing in libraries."*

```
1. generate-search-queries          ← translate the question first
2. search-openalex            ← retrieve from scholarly corpus
3. search-sudoc-sru            ← only if catalog evidence is also needed
4. generic web search               ← last resort
```

### Chaining guidance

Document what comes before and after each skill.
Example pipeline for a systematic review:

```
generate-search-queries
  → search-openalex
  → screen-studies-prisma
  → summarize-paper
  → appraise-study-quality
  → synthesize-papers-thematic
```

## 6. Complete manifest example

```yaml
name: generate-search-queries
description: >
  Generate structured scholarly search queries from a natural-language research
  question. Use this skill whenever the task involves building a search strategy,
  expanding a review question into searchable expressions, or designing bilingual
  queries for systematic reviews. Always use this skill before retrieving records
  from any corpus. Returns validated JSON.

metadata:
  version: 0.1.0
  author: smartbiblia
  maturity: beta
  preferred_output: json
  supports_validation: true

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
    - search-openalex
    - search-sudoc-sru

tags:
  - systematic-review
  - search-strategy
  - scholarly
```

---

## 7. Rules summary

### Required
- Lowercase hyphenated name starting with a verb
- `<verb>-<object>-<source>` pattern when source matters
- Rich `description` answering: what / when / what it returns

### Strongly recommended
- `selection` block with `use_when`, `avoid_when`, `combine_with`
- `metadata.maturity` and `metadata.preferred_output`
- Chaining documentation in SKILL.md body

### Avoid
- Architectural terms in skill IDs (`engine`, `agent`, `tool`, `runner`)
- Opaque or brand-like names
- Overloaded multi-action names
- Version suffixes in names
- Filling optional metadata fields with placeholder values