# AgentDesk Agent Specification

> Companion to `SPEC_SKILLS_en.md`.
> Covers naming, manifest structure (`AGENT.md`), directory layout, and
> integration guidelines for pipeline agents running inside AgentDesk.

---

## 1. What is a pipeline agent?

A **skill** encodes one atomic capability.
A **pipeline agent** encodes a complete workflow — an ordered sequence of stages
that consumes skills and MCP servers to accomplish a compound, domain-specific
task.

The relationship is strictly layered:

```
Pipeline agent   ←  orchestrates
  Skills         ←  atomic capabilities
  MCP servers    ←  external integrations
  Agent CLI      ←  LLM backbone (selected in Discovery)
```

A pipeline agent does **not** embed a specific LLM. It delegates all LLM calls
to the active AgentDesk adapter (Codex, Claude Code, Mistral Vibe, …), received
via the AgentDesk execution protocol over `stdout`/`stdin`.

---

## 2. Naming convention

### Pattern

```
<verb>-<domain>[-<scope>]
```

* **verb** — the primary action performed by the full pipeline
* **domain** — the field or document type this agent specialises in
* **scope** — optional qualifier when multiple agents share a domain

### Character rules

Same rules as skills:
* Lowercase ASCII only
* Hyphens as separators, no underscores
* No version suffixes in the name
* No architectural terms: avoid `engine`, `bot`, `runner`, `service`, `tool`

The word `agent` is permitted **only** as a last-resort disambiguator when
the domain alone would be ambiguous — prefer a more specific verb or scope
instead. Example: `review-shs` is better than `agent-shs`.

### Recommended verbs

| Verb | Use when |
|---|---|
| `review` | Producing a structured literature review |
| `audit` | Evaluating compliance or quality of a corpus |
| `survey` | Broad landscape mapping, less formal than a review |
| `monitor` | Continuous tracking of a topic over time |
| `extract` | Bulk extraction from a large document set |
| `classify` | Large-scale categorisation pipeline |
| `curate` | Selection and organisation of a corpus |
| `produce` | Generic multi-stage document production |

### Good names

```
review-shs
review-biomedical-cochrane
audit-catalogue-unimarc
survey-ai-policy
extract-metadata-corpus
curate-reading-list
```

### Names to avoid

```
research-agent-shs       → "agent" in name, "research" is vague
literature-review-agent  → "agent" redundant
shs-pipeline             → no verb, "pipeline" is architectural
smart-review             → opaque brand-like label
```

---

## 3. Manifest — AGENT.md

The manifest is a single `AGENT.md` file at the root of the agent directory.
It follows the same frontmatter + Markdown body convention as `SKILL.md`.

AgentDesk reads the frontmatter as the machine-readable manifest.
The Markdown body is read by coding agents bootstrapping the project
(compatible with the [AGENTS.md standard](https://agents.md/)).

### 3.1 Frontmatter — required fields

```yaml
---
name: review-shs
description: >
  Autonomous 14-stage literature review pipeline for humanities and social
  sciences. Use this agent when the task is to produce a full systematic review
  from a research question: scope definition, multi-source retrieval (HAL,
  SUDOC, OpenAlex), PRISMA 2020 screening, thematic synthesis, and BibTeX
  export. Returns synthesis_report.md, references.bib, prisma_flow.md, and a
  full run trace. Requires human gate approval at source selection and PRISMA
  screening stages.

runtime: python
entry: researchagentshs.cli
config_schema: research_agent_shs.config.yaml
---
```

**Writing the description well is the most important field.**
It must answer in 3–5 sentences:
- What workflow does this agent execute?
- When should it be selected over a simpler skill or a different agent?
- What does it return (outputs)?
- What notable constraints exist (gates, network, runtime)?

### 3.2 Frontmatter — recommended fields

```yaml
metadata:
  version: 0.1.0
  author: smartbiblia
  maturity: experimental | beta | stable | deprecated

pipeline:
  stages: 14
  gates:
    - stage: 3
      name: SOURCE_SELECTION
      type: source_selection
      optional: false
    - stage: 5
      name: QUERY_VALIDATION
      type: query_validation
      optional: true
    - stage: 8
      name: PRISMA_SCREENING
      type: prisma_screening
      optional: false
    - stage: 10
      name: QUALITY_APPRAISAL
      type: quality_appraisal
      optional: true

dependencies:
  skills:
    - search-records-hal
    - search-records-sudoc
    - search-works-openalex
    - synthesize-literature
    - generate-search-queries
    - trace-agent-execution
  mcps: []

outputs:
  - synthesis_report.md
  - references.bib
  - prisma_flow.md
  - run_trace.md
  - knowledge_base/

selection:
  use_when:
    - The task is to produce a complete literature review from a research question.
    - The user needs PRISMA-compliant systematic screening with human oversight.
  avoid_when:
    - The task only requires searching or retrieving records (use skills directly).
    - The user needs a quick summary of a single paper.
  combine_with: []

tags:
  - literature-review
  - shs
  - prisma
  - systematic-review
  - french
```

### 3.3 Frontmatter — runtime values

| Value | Meaning |
|---|---|
| `python` | Entry is a Python module path (`python -m <entry>`) |
| `node` | Entry is a Node.js script path |
| `shell` | Entry is a shell command |

### 3.4 Gate types

Standard gate types understood by AgentDesk UI:

| Type | UI widget shown |
|---|---|
| `source_selection` | Checkbox list of available sources |
| `query_validation` | Editable query list with timeout |
| `prisma_screening` | Inclusion/exclusion review table |
| `quality_appraisal` | Score threshold review |
| `custom` | Generic approve/reject banner |

### 3.5 What to omit

Do not add fields that carry no information for your specific agent.
Stale or placeholder metadata is worse than absent metadata.
Never add: `llm_model`, `api_key`, `max_tokens` — LLM configuration
belongs in the per-run config YAML, not the manifest.

---

## 4. AGENT.md body structure

The body is Markdown read by coding agents (AGENTS.md-compatible).
Use it for everything a developer or a coding agent needs to
understand, run, and modify the agent.

```markdown
# Agent name

## What this agent does

One paragraph. The workflow, the outputs, the domain.

## Pipeline stages

| Stage | Name | Gate |
|---|---|---|
| 1 | QUESTION_INTAKE | — |
| … | … | … |

## Dependencies

Skills consumed, MCP servers required, Python/Node packages.

## Setup

```bash
# Install
pip install -e .

# Config
cp research_agent_shs.config.example.yaml research_agent_shs.config.yaml
```

## Running standalone (without AgentDesk)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
researchshs run --question "..." --skills /path/to/agent-skills
```

## Running via AgentDesk

Launched automatically by AgentDesk when the user clicks Run.
LLM calls are routed to the active adapter. No API key needed.

## Config reference

Document the config YAML keys that users typically adjust.

## Outputs

What files are produced and where.

## Resume an interrupted run

```bash
researchshs sessions
researchshs run --resume <session-id>
```
```

---

## 5. Directory layout

```
<agent-name>/
├── AGENT.md                    ← manifest + bootstrap doc (required)
├── <runtime-package>/          ← Python package, Node module, or scripts
│   ├── __init__.py
│   ├── pipeline.py
│   ├── agentProtocol.py        ← AgentDesk execution protocol adapter
│   ├── models.py
│   ├── session.py
│   └── stages/
│       ├── a_framing.py
│       └── …
├── <config_schema>.yaml        ← config template (name matches config_schema)
├── pyproject.toml / package.json
└── README.md                   ← human-facing quick start
```

### What belongs where

| File | Purpose |
|---|---|
| `AGENT.md` | Machine manifest + coding agent bootstrap doc |
| `agentProtocol.py` | Required for Python agents. Replaces direct LLM + gate calls |
| `<config_schema>.yaml` | Template config. Name must match `config_schema` in frontmatter |
| `README.md` | Human quick start. Can be brief if AGENT.md body is thorough |

---

## 6. AgentDesk execution protocol

Python (and other runtime) agents communicate with AgentDesk via
line-delimited JSON on `stdout`/`stdin`. The `AGENTDESK_PROTOCOL=1`
environment variable signals that the agent is running inside AgentDesk.

When not set, agents fall back to direct API calls and CLI prompts
(standalone mode for testing).

### stdout events (agent → AgentDesk)

```json
{ "type": "progress",    "stage": 3, "label": "QUERY_GENERATION", "message": "…" }
{ "type": "llm.request", "id": "<uuid>", "system": "…", "user": "…", "max_tokens": 4096, "json_mode": false }
{ "type": "gate.request","id": "<uuid>", "gate": "source_selection", "payload": {…} }
{ "type": "artifact",    "name": "synthesis_report.md", "path": "/abs/path/…" }
{ "type": "done",        "session_id": "…" }
{ "type": "error",       "message": "…" }
```

### stdin events (AgentDesk → agent)

```json
{ "type": "llm.response",  "id": "<uuid>", "text": "…" }
{ "type": "gate.response", "id": "<uuid>", "decision": "approved", "approved_by": "human", "amendments": {…} }
```

---

## 7. Agent discovery and installation

AgentDesk discovers agents in two locations, scanned in this order:

1. **Bundled agents** — `<agentdesk-repo>/agents/<agent-name>/AGENT.md`
   Shipped with AgentDesk, always available, read-only.

2. **User-installed agents** — `~/.agentdesk/agents/<agent-name>/AGENT.md`
   Installed via UI (GitHub URL or ZIP upload) or manually placed.

If an agent exists in both locations, the user-installed version takes
precedence (allows overrides and local forks).

---

## 8. Rules summary

### Required

* Lowercase hyphenated name starting with a verb
* `AGENT.md` at the root with valid YAML frontmatter
* `name`, `description`, `runtime`, `entry`, `config_schema` in frontmatter
* `agentProtocol.py` (or equivalent) for agents making LLM calls

### Strongly recommended

* `pipeline.stages` and `pipeline.gates` for multi-stage agents
* `dependencies.skills` listing consumed skills by name
* `selection.use_when` and `selection.avoid_when`
* `metadata.maturity`
* Standalone run instructions in the AGENT.md body

### Avoid

* Architectural terms in agent names (`engine`, `bot`, `runner`)
* Hardcoded LLM model or API key in the manifest
* Duplicating config values between `AGENT.md` frontmatter and the config YAML
* Filling optional fields with placeholder values
