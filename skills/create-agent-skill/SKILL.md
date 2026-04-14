---
name: create_agent_skill
description: >
  Meta-skill for creating new agent skills that conform to the skill
  specification standards. Use this skill whenever the task is to create a new skill,
  update an existing skill to match conventions, or review a skill for
  compliance. Guides the agent through three phases: researching the data source
  and producing a llm.md reference document, drafting a compliant SKILL.md, and
  reviewing coherence with existing skills. Always use this skill before writing
  any new SKILL.md — it ensures naming, frontmatter, selection block,
  CLI patterns, and output schemas are consistent with existing skills.
metadata:
  {
    "version": "0.2.0",
    "author": "agent-skills",
    "maturity": "stable",
    "preferred_output": "markdown",
    "openclaw": { "requires": {} },
  }

selection:
  use_when:
    - A new skill needs to be created.
    - An existing skill needs to be reviewed or updated for compliance.
    - A llm.md reference document needs to be produced for a data source API.
  avoid_when:
    - The task is to scaffold a gitagent repository — that is a different kind of task.

tags:
  - meta-skill
  - skill-creator
  - skill-standards
---

# create-agent-skill

## Purpose

This meta-skill guides the creation of spec-compliant skills. It enforces the
conventions established across all existing skills so that new contributions
are immediately consistent in naming, structure, routing signals, CLI patterns,
and output schemas.

---

## When to use / When not to use

Use this skill when creating a new skill from scratch, updating an
existing skill to match current conventions, or producing a `references/llm.md`
API reference document for a data source (only when the skill wraps an API
that lacks an LLM-optimized documentation page).

Do not use it when:
- The task is to create a new gitagent repository scaffold (`agent.yaml`, `SOUL.md`, etc.) — that is a different kind of task.
- Only a single file in an existing skill needs a minor edit — edit it directly.

---

## Reference documents

These files are the authoritative sources for skill conventions.
Fetch them at the start of each phase that requires them.

| Document | Path | When to fetch |
|---|---|---|
| Spec skills | `skills/SPEC_SKILLS_en.md` | Phase 2 — naming rules, manifest structure |
| Skill anatomy | `references/skill-anatomy.md` | Phase 2 — detailed patterns with real examples |
| llm.md guide | `references/llm-md-guide.md` | Phase 1 — how to document a data source API |

`skill-anatomy.md` and `llm-md-guide.md` are local to this skill and describe
stable patterns for skill creation.

---

## Workflow

### PHASE 1 — Research the data source (conditional)

**Only for skills that wrap an external API** — skip to Phase 2 otherwise.

**Goal**: produce a `references/llm.md` when the API lacks an LLM-optimized
documentation page (e.g., no `/llm.txt` file).

1. Read `references/llm-md-guide.md`.
2. Check if the API provides an LLM-optimized reference (e.g., OpenAlex's `/llm.txt`).
   - If yes: skip Phase 1 — the LLM can reference the official document directly.
   - If no: proceed to produce a condensed `references/llm.md` for this skill.
3. Produce `skills/<new-skill>/references/llm.md` capturing non-obvious behaviors:
   - Authentication, encoding rules, pagination quirks
   - Field mappings to the common record schema
   - Rate limits and retry guidance

`references/llm.md` stays in the repo as a maintenance document. It is not
required at agent runtime — agents use the `SKILL.md` directly.

Skip this phase entirely if the skill does not wrap an external API
(e.g., contract packs, pure analytical tools, orchestrators).

---

### PHASE 2 — Draft the SKILL.md

**Goal**: produce a spec-compliant `SKILL.md` for the new skill.

Fetch before starting:
- `SPEC_SKILLS_en.md` — for naming rules and manifest conventions

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
  (e.g. Sudoc SRU, HAL Solr)
- Use `queries` when the output is search query expressions
- Use `papers` for generic scholarly papers when no typed entity model exists

Check existing skills in the `skills/` folder to verify the name does not conflict.

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
  {
    "version": "0.1.0",
    "author": "agent-skills",
    "maturity": "experimental",
    "preferred_output": "json",
    "openclaw": { "requires": {} },
  }

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
- Every skill that has a sibling needs at least one `avoid_when` entry.

Rules for `selection.combine_with`:
- Review existing skills in the `skills/` folder to find the pipeline position of this skill.
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
- normalize output to the common record schema (see below)
- support a `--trace` flag for HTTP debug logging
- be self-contained (`uv run`, inline dependencies declared in the script header)

**Common record schema** — retrieval skills should normalize to this shape so
that downstream steps can process records from any source without transformation:

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

**Goal**: verify coherence with existing skills.

#### Coherence checklist

- [ ] Skill name follows `<verb>-<object>-<source>` and does not conflict with existing skills
- [ ] `object` token is semantically correct for this source's data model
- [ ] `selection.avoid_when` names at least one alternative skill explicitly
- [ ] `selection.combine_with` reflects the actual pipeline position
- [ ] Output schema is compatible with the common record schema
- [ ] `## Composition hints` shows where this skill sits in the annotated pipeline
- [ ] `maturity` is set to `experimental` for a new, untested skill
- [ ] No optional metadata fields filled with placeholder or default values
- [ ] `references/llm.md` produced only if: (a) skill wraps an external API, and (b) the API lacks an LLM-optimized reference like `/llm.txt`

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

No packaging step needed — agents access skills directly from the repo
by path (`skills/<n>/SKILL.md`).

---

## Output

This skill produces one or more of the following artifacts, depending on which
phases are executed:

| Phase | Artifact | Description |
|---|---|---|
| 1 | `skills/<n>/references/llm.md` | Condensed API reference (only for API-wrapping skills when API lacks `llm.txt`) |
| 2 | `skills/<n>/SKILL.md` | Spec-compliant skill manifest and body |

Phase 2 is always required. Phase 1 is only for skills wrapping an external API
that lacks an LLM-optimized documentation page.

---

## Composition hints

This skill has no upstream dependency — it is a standalone authoring tool.