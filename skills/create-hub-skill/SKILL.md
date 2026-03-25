---
name: create_hub_skill
description: >
  Meta-skill for creating new agent skills that conform to the smartbiblia hub
  standards. Use this skill whenever the task is to create a new skill for the
  hub, update an existing skill to match hub conventions, or review a skill for
  compliance. Guides the agent through three phases: researching the data source
  and producing a llm.md reference document, drafting a compliant SKILL.md, and
  reviewing coherence with the hub registry. Always use this skill before writing
  any new SKILL.md for the hub — it ensures naming, frontmatter, selection block,
  CLI patterns, and output schemas are consistent with existing skills.
metadata: {"version": "0.2.0", "author": "smartbiblia", "maturity": "stable", "openclaw": {"emoji": "🛠️"}}

selection:
  use_when:
    - A new skill needs to be created for the hub.
    - An existing skill needs to be reviewed or updated for hub compliance.
    - A llm.md reference document needs to be produced for a data source API.

tags:
  - meta-skill
  - skill-creator
  - hub-standards
---

# create-hub-skill

## Purpose

This meta-skill guides the creation of hub-compliant skills. It enforces the
conventions established across all existing skills so that new contributions
are immediately consistent in naming, structure, routing signals, CLI patterns,
and output schemas.

---

## Hub reference documents

These files are the authoritative sources for hub conventions.
Fetch them at the start of each phase that requires them — they are always
up to date at these URLs.

| Document | URL | When to fetch |
|---|---|---|
| Hub registry | `https://raw.githubusercontent.com/smartbiblia-solutions/agent-skills/main/skills/HUB-REGISTRY.md` | Phases 2 and 3 — naming, combine_with, pipeline position |
| Spec skills | `https://raw.githubusercontent.com/smartbiblia-solutions/agent-skills/main/skills/SPEC_SKILLS_en.md` | Phase 2 — naming rules, manifest structure |
| Skill anatomy | `references/skill-anatomy.md` | Phase 2 — detailed patterns with real examples |
| llm.md guide | `references/llm-md-guide.md` | Phase 1 — how to document a data source API |

`skill-anatomy.md` and `llm-md-guide.md` are local to this skill and do not
change with the hub — they describe stable patterns, not the current state of
the registry.

---

## Workflow

### PHASE 1 — Research the data source

**Goal**: produce a `references/llm.md` in the new skill's folder that
captures everything an agent needs to use the API correctly.

1. Read `references/llm-md-guide.md`.
2. Fetch the API documentation (official docs, OpenAPI spec, or equivalent).
   If the source provides an LLM-optimized page (like OpenAlex's `/llm.txt`),
   use it as the primary input.
3. Produce `skills/<new-skill>/references/llm.md`.

`references/llm.md` stays in the repo as a maintenance document. It is not
required at agent runtime — agents use the `SKILL.md` directly.

Skip this phase if the API is already well-documented in an existing
`references/llm.md`, or if the source is simple enough to proceed directly
to Phase 2.

---

### PHASE 2 — Draft the SKILL.md

**Goal**: produce a hub-compliant `SKILL.md` for the new skill.

Fetch before starting:
- `HUB-REGISTRY.md` (URL above) — to check existing names and pipeline position
- `SPEC_SKILLS.md` (URL above) — for naming rules and manifest conventions

Then read `references/skill-anatomy.md` for detailed patterns and real examples.

#### Step 1 — Choose the canonical name

Apply the `<verb>-<object>-<source>` convention:

```
verb    = the primary action (search, lookup, fetch, extract, generate, …)
object  = what is returned — based on the source's data model, not just the output type
source  = the external system, when behavior depends on it
```

The `object` token must reflect the source's actual data model:
- Use `works` when the source exposes typed work entities (e.g. OpenAlex `/works`)
- Use `records` when the source exposes a bibliographic index without entity typing
  (Sudoc SRU, HAL Solr) — consistent with `search-records-sudoc` and `search-records-hal`
- Use `queries` when the output is search query expressions
- Use `papers` for generic scholarly papers when no typed entity model exists

Check the fetched `HUB-REGISTRY.md` to verify the name does not conflict with
an existing skill.

#### Step 2 — Write the frontmatter

Required fields only — resist adding optional fields without concrete values:

```yaml
---
name: <canonical-name>
description: >
  <2–4 sentences: what / when / what it returns.
   Include trigger phrases. End with output format.
   Name sibling skills explicitly when disambiguation matters.>
metadata:
  version: 0.1.0
  author: smartbiblia
  maturity: experimental | beta | stable
  preferred_output: json | markdown | text

selection:
  use_when:
    - <concrete task condition>
  avoid_when:
    - <name the alternative skill explicitly, not just the category>
  prefer_over:
    - generic-web-search
  combine_with:
    - <upstream skill — what runs before>
    - <downstream skill — what runs after>

tags:
  - <source name>
  - <domain>
  - <document type>
---
```

Rules for `description`:
- Must answer: what does it do / when should an agent pick it / what does it return.
- Must include trigger phrases (keywords the user might type).
- Must name sibling skills when disambiguation matters.
- Must be pushy enough to trigger without reading the body.
- Start with `experimental` for new skills — promote to `beta` or `stable` after validation.

Rules for `selection.avoid_when`:
- Always name the alternative skill explicitly, not just the category.
- Every skill that has a sibling in the hub needs at least one `avoid_when` entry.

Rules for `selection.combine_with`:
- Use the fetched `HUB-REGISTRY.md` to find the pipeline position of this skill.
- List skills that immediately precede and follow.

#### Step 3 — Write the body

Use the section structure from `references/skill-anatomy.md`.
Adapt sections to the skill type — not every skill needs every section.

Mandatory for all skills:
- `## Purpose` — one paragraph, what problem this solves and for whom
- `## When to use / When not to use` — prose expansion of the selection block
- `## CLI usage` or `## Subcommands` — how to invoke
- `## Output` — schema with a jsonc example
- `## Composition hints` — pipeline diagram showing this skill's position

Mandatory for CLI retrieval skills:
- `## Environment variables` — table of all env vars with defaults
- `## Failure modes` — exit code behavior, error field, known edge cases

Mandatory for contract pack skills (prompt + schema):
- `## Task reference` — table of tasks with schema names and required inputs
- `## Rules` — validate-before-proceed, retry limit, JSON-only output

Optional (add only when genuinely useful):
- `## Common workflows` — 3–5 concrete bash examples covering distinct use cases
- `## Index reference` / `## Query syntax` — for Solr/SRU skills with complex query languages
- `## Data coverage` — scope, format, authentication requirements

#### Step 4 — Write the CLI (if applicable)

For retrieval skills, the CLI must:
- emit strict JSON on stdout — exit code always 0, errors surfaced in `error` field
- implement retry with exponential backoff for transient HTTP errors
- normalize output to the hub common record schema (see below)
- support a `--trace` flag for HTTP debug logging
- be self-contained (`uv run`, inline dependencies declared in the script header)

**Hub common record schema** — all retrieval skills normalize to this shape so
that downstream skills (`screen-studies-prisma`, `summarize-paper`, etc.) can
process records from any source without transformation:

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

Source-specific fields (e.g. `hal_id`, `ppn`, `cited_by_count`) can be added
alongside the common fields. Do not rename or remove common fields.

For contract pack skills, the CLI exposes only:
`prompt [--task <t>]`, `schema [--task <t>]`, `validate --task <t> --json-file <f>`
Single-task contract packs have no `--task` flag.

---

### PHASE 3 — Review and integrate

**Goal**: verify coherence with the hub and update the registry.

Fetch `HUB-REGISTRY.md` (URL above) before starting this phase.

#### Coherence checklist

- [ ] Skill name follows `<verb>-<object>-<source>` and does not conflict with existing skills
- [ ] `object` token is semantically correct for this source's data model
- [ ] `selection.avoid_when` names at least one alternative hub skill explicitly
- [ ] `selection.combine_with` reflects the actual pipeline position
- [ ] Output schema is compatible with the hub common record schema
- [ ] `## Composition hints` shows where this skill sits in the annotated pipeline
- [ ] `maturity` is set to `experimental` for a new, untested skill
- [ ] No optional metadata fields filled with placeholder or default values
- [ ] `references/llm.md` produced and committed (if Phase 1 was executed)

#### Update HUB-REGISTRY.md

After the SKILL.md is validated, update `HUB-REGISTRY.md` in the repo:

1. Add the skill to the **Package inventory** table
2. Add logical skill identifiers to the **Logical skills** table if the package
   exposes multiple addressable operations
3. Insert the skill in the **Annotated pipeline** at the correct position,
   with its input and output types documented
4. Add a row to the **Renaming map** if this skill replaces an older one

Commit the updated `HUB-REGISTRY.md` together with the new skill folder.

#### Skill folder structure

```
skills/<new-skill>/
  SKILL.md              ← the skill itself
  scripts/              ← CLI (retrieval skills)
    cli.py
    .env.example
  prompts/              ← methodological prompts (contract pack skills)
  schemas/              ← JSON schemas (contract pack skills)
  references/           ← maintenance documents, not used at agent runtime
    llm.md              ← API reference produced in Phase 1
```

No packaging step needed — agents access skills directly from the repo,
either by path (`skills/<n>/SKILL.md`) or via GitHub raw URL:

```
https://raw.githubusercontent.com/smartbiblia-solutions/agent-skills/main/skills/<n>/SKILL.md
```