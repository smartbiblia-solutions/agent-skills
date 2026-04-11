---
name: generate_agent_scaffold_gitagent
description: >
  Generate a gitagent-compliant agent scaffold from a natural-language brief.
  Use this skill when the user asks for a "gitagent agent", "agent folder",
  "agent scaffold", "agent.yaml + SOUL.md", or a repository structure that
  follows the open-gitagent standard. Prefer this skill when the goal is to
  produce a concrete folder tree and starter file contents, not just explain
  the spec. Guides the user through a short conversational elicitation when
  the brief is incomplete, then returns strict JSON describing directories,
  files, and starter content for a `minimal`, `standard`, or `full`
  gitagent scaffold.
metadata: {"version": "0.1.0", "author": "smartbiblia", "maturity": "experimental", "preferred_output": "json"}

selection:
  use_when:
    - The task is to scaffold a new agent repository that follows the gitagent standard.
    - The user needs starter contents for `agent.yaml`, `SOUL.md`, and optional gitagent files.
    - The desired output is a structured plan another agent can write to disk directly.
  avoid_when:
    - The task is to create or update a hub skill package rather than a gitagent repository scaffold — use create-hub-skill instead.
    - The user only wants an explanation of the gitagent specification without generating a scaffold plan.
  prefer_over:
    - generic-web-search
  combine_with:
    - create-hub-skill

tags:
  - gitagent
  - agent
  - scaffold
  - generation
---

## Purpose

This skill turns an agent brief into a deterministic scaffold plan for the
[`gitagent`](https://github.com/open-gitagent/gitagent) standard. It is useful
when an agent needs to create a new git-native agent repository quickly without
guessing which files are mandatory, which directories are optional, or how much
structure belongs in a `minimal`, `standard`, or `full` template.

When the initial request is vague, the skill first guides the user through a
short conversational elicitation to capture the agent's purpose, scope,
persistence, constraints, and tone. The final output remains a JSON plan with
ordered directories and files, including starter content, so a downstream agent
can materialize the folder tree directly from the result.

---

## Minimal-First Decision Framework

This skill does not blindly generate agent scaffolds.  
It first determines whether an agent is actually needed.

### Step 1 — Agent necessity check (MANDATORY)

Before generating a scaffold, evaluate:

- Can this be solved with a simple script? → DIRECT_CODE
- Can this be a reusable skill only?
- Does this require autonomy or persistence?

If a script or a skill is sufficient, the skill MUST:

- still produce a scaffold if explicitly requested
- but clearly warn the user that an agent may be overkill

### Step 2 — Topology reasoning (implicit)

The scaffold MUST reflect the simplest valid structure.

Internal topology patterns:

- DIRECT_CODE  — no agent needed
- SINGLE       — one agent
- PIPELINE     — sequential steps
- FORK_JOIN    — parallel branches
- CRITIC_LOOP  — generate + critique
- HIERARCHICAL — orchestrator

### Selection rules

- Always choose the SIMPLEST structure
- DIRECT_CODE > SINGLE > PIPELINE > others
- Avoid sub-agents unless strictly required
- Never introduce structure not justified by the brief

### Step 3 — Minimalism guarantee

The generated scaffold MUST:

- use the smallest viable template (`minimal` preferred)
- include only necessary files and directories
- avoid speculative features (skills, tools, workflows, agents)
- reflect real needs, not hypothetical extensions

### Step 4 — User honesty (MANDATORY)

The output MUST include, in `assumptions` or `summary`:

- a warning when an agent is likely unnecessary
- a note when a script or a single skill would suffice
- a justification of the chosen level of complexity

Example:

"Assumption: This use case could be solved with a simple script.  
A gitagent scaffold is generated because it was explicitly requested."

---

## When to use / When not to use

Use this skill when the user wants a real gitagent scaffold, not just advice.
Typical prompts include:

- "Create a gitagent agent"
- "Generate an agent folder following gitagent"
- "Scaffold `agent.yaml` and `SOUL.md`"
- "Give me a standard gitagent repo layout"

Do not use it when:

- The task is to create a skill package for the smartbiblia hub. Use `create-hub-skill`.
- The user already has a gitagent repository and only needs one file edited.
- The task is documentation-only and no scaffold output is needed.

---

## Input

The skill accepts either:

- A sufficiently detailed natural-language brief, or
- A partial brief that can be clarified through a short elicitation

Useful inputs to capture before generation:

- Agent purpose
- Scope: single project or cross-project
- Memory expectations: persistent or fresh each run
- Constraints and non-negotiable rules
- Persona or communication style
- Optional complexity signals: tools, workflows, sub-agents, compliance

---

## Elicitation flow

If the initial brief is incomplete, the skill conducts a short conversational
interview before generating the scaffold. Ask at most 4 to 6 questions, one at
a time, in plain language. Skip questions that are already answered by the
brief. Do not ask questions merely to be exhaustive.

Suggested sequence:

1. **Purpose** — "What do you want this agent to do for you?"
2. **Scope** — "Is this for one project or something you'll reuse across different tasks?"
3. **Memory** — "Should this agent remember context between sessions, or start fresh each time?"
4. **Capabilities** — "Will it need reusable skills, tools, workflows, or sub-agents?"
5. **Constraints** — "Are there things this agent should never do, or rules it should always follow?"
6. **Persona** — "Do you want a specific name, tone, or working style for it?"

Mapping guidance:

- Persistent memory usually implies `memory/`
- Reusable capabilities imply `skills/` and/or `tools/`
- Deterministic procedures imply `workflows/`
- Delegated roles imply `agents/`
- Regulated or auditable work may justify `DUTIES.md` and `compliance/`
- Strong safety or scope constraints often justify `RULES.md`

If the user abandons the elicitation or answers vaguely, generate the smallest
reasonable scaffold anyway, record the inference in `assumptions`, and avoid
asking more questions than necessary.

---

## Task reference

This is a single-task contract pack. There is no `--task` flag.

| Task | Output schema | Required input |
|---|---|---|
| `generate_agent_scaffold_gitagent` | `schemas/output.schema.json` | A natural-language brief describing the intended agent |

---

## Rules

- Validate before proceeding.
- If the brief is underspecified, run the elicitation flow first.
- Ask one question at a time, with a maximum of 6 questions total.
- Return JSON only once you have enough context to generate the scaffold.
- Do not emit Markdown fences or prose outside the final JSON object.
- Always include `agent.yaml` and `SOUL.md`.
- Choose the smallest viable template that satisfies the brief.
- Do not invent compliance, sub-agents, tools, or workflows unless the brief
  implies them.
- If the brief is underspecified, make explicit assumptions in `assumptions`.
- Before generating, evaluate if an agent is necessary.
- Prefer the smallest viable template (`minimal` by default).
- Do not generate sub-agents, workflows, or skills unless clearly required.
- Do not over-interpret vague briefs into complex architectures.
- If a simpler alternative exists (script or skill), record it in `assumptions`.
- Always justify structural choices (template, directories, files).

---

## CLI usage

```bash
UV_CACHE_DIR=/root/.cache/uv uv run skills/generate-agent-scaffold-gitagent/scripts/cli.py prompt
UV_CACHE_DIR=/root/.cache/uv uv run skills/generate-agent-scaffold-gitagent/scripts/cli.py schema
UV_CACHE_DIR=/root/.cache/uv uv run skills/generate-agent-scaffold-gitagent/scripts/cli.py validate \
  --json-file /path/to/output.json
```
---

## Output

The final output is a strict JSON scaffold plan. The elicitation itself is
conversational and does not alter the output schema.

```jsonc
{
  "agent_name": "legal-research-agent",
  "template": "standard",
  "gitagent_spec_version": "0.1.0",
  "summary": "Standard gitagent scaffold for a legal research agent with reusable skills and a workflow layer.",
  "directories": [
    {
      "path": "skills",
      "purpose": "Reusable capability modules for this agent.",
      "required": false
    },
    {
      "path": "workflows",
      "purpose": "Deterministic multi-step procedures.",
      "required": false
    }
  ],
  "files": [
    {
      "path": "agent.yaml",
      "purpose": "Primary gitagent manifest.",
      "required": true,
      "content": "spec_version: \"0.1.0\"\\nname: legal-research-agent\\nversion: 0.1.0\\ndescription: Legal research assistant\\n"
    },
    {
      "path": "SOUL.md",
      "purpose": "Identity and communication style.",
      "required": true,
      "content": "# Identity\\n..."
    }
  ],
  "assumptions": [
    "No regulatory compliance layer was requested, so DUTIES.md and compliance/ are omitted."
  ],
  "next_steps": [
    "Review the starter prompts and tighten domain-specific rules."
  ]
}
```

---

## Common workflows

```bash
# Print the prompt contract for the model step
UV_CACHE_DIR=/root/.cache/uv uv run skills/generate-agent-scaffold-gitagent/scripts/cli.py prompt

# Print the schema consumed by a validator or orchestrator
UV_CACHE_DIR=/root/.cache/uv uv run skills/generate-agent-scaffold-gitagent/scripts/cli.py schema

# Validate a generated scaffold plan
UV_CACHE_DIR=/root/.cache/uv uv run skills/generate-agent-scaffold-gitagent/scripts/cli.py validate \
  --json-file ./scaffold-plan.json
```

---

## Composition hints

```text
create-hub-skill                         output: hub-compliant skill package
  |
  v
generate-agent-scaffold-gitagent        output: elicited brief -> JSON scaffold plan for a gitagent repository
  |
  v
file-writing agent or workflow          output: materialized folder tree on disk
```

Use this skill before any file-writing step that should create a full gitagent
repository from a brief. The output is intentionally structured so a downstream
agent can create directories and files with no additional inference.
