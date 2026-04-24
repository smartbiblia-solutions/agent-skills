---
name: generate-agent-scaffold
description: >
  Generates a Nanobot/OpenClaw-compatible agent workspace scaffold from a
  natural-language brief, with optional conversational elicitation when the
  brief is incomplete. Use this skill when the user asks for an "agent",
  "agent folder", "agent scaffold", "AGENTS.md", "SOUL.md", or wants to
  scaffold a new nanobot workspace. Supports internal skill references (bare
  kebab-case names) and external skill dependency references (full GitHub URLs,
  including repository subpaths). External skills are declared for AgentDesk to
  resolve at runtime, not copied into the generated agent repository. Returns a
  strict JSON scaffold plan ready to be materialized to disk by a downstream
  file-writing agent. Do not use this skill when the task is to create or update
  a skill package — use create-agent-skill instead.
metadata:
  {
    "version": "0.1.0",
    "author": "smartbiblia",
    "maturity": "experimental",
    "preferred_output": "json",
    "openclaw": { "requires": {} },
  }

selection:
  use_when:
    - The task is to scaffold a new agent workspace or repository.
    - The user needs starter contents for AGENTS.md and SOUL.md.
    - The desired output is a structured scaffold plan another agent can write to disk.
    - The user mentions internal skills or external skill dependency URLs to reference from the agent.
  avoid_when:
    - The task is to create or update a skill package — use create-agent-skill instead.
    - The user already has an agent repository and only needs one file edited.
    - The task is documentation-only and no scaffold output is needed.
    - The user only wants advice on agent design without generating a scaffold.

tags:
  - agent
  - scaffold
  - nanobot
  - openclaw
---

## Purpose

This skill turns an agent brief into a deterministic scaffold plan. It is useful
when an agent needs to create a new git-native agent workspace quickly without
guessing which files are mandatory, which directories are optional, or how much
structure belongs in a `minimal`, `standard`, or `full` template.

When the initial request is vague, the skill first guides the user through a
short conversational elicitation to capture the agent's purpose, scope,
persistence, constraints, and tone. The final output is a JSON plan with ordered
directories and files, including starter content, so a downstream agent can
materialize the folder tree directly from the result.

---

## When to use / When not to use

Use this skill when the user wants a real agent scaffold, not just advice.
Typical prompts include:

- "Create a nanobot agent"
- "Generate an agent folder"
- "Scaffold AGENTS.md and SOUL.md"
- "Give me a standard nanobot repo layout"
- "Build an agent that uses github.com/org/skill-rag"

Do not use it when:

- The task is to create a skill package — use `create-agent-skill` instead.
- The user already has an agent repository and only needs one file edited.
- The task is documentation-only and no scaffold output is needed.

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
- select `full` when the brief requires multiple internal skills plus
  `/knowledge`, `/raw`, `/memory`, deterministic workflows, or generated examples

### Step 4 — User honesty (MANDATORY)

The output MUST include, in `assumptions` or `summary`:

- a warning when an agent is likely unnecessary
- a note when a script or a single skill would suffice
- a justification of the chosen level of complexity

Example:

> "Assumption: This use case could be solved with a simple script.
> A workspace scaffold is generated because it was explicitly requested."

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
- Skill references: internal bare names (`review-summary`) or external GitHub
  URLs (`https://github.com/org/repo/tree/main/skills/skill-rag`)

---

## Elicitation flow

If the initial brief is incomplete, the skill conducts a short conversational
interview before generating the scaffold. Ask at most 4 to 6 questions, one at
a time, in plain language. Skip questions already answered by the brief. Do not
ask questions merely to be exhaustive.

Suggested sequence:

1. **Purpose** — "What do you want this agent to do for you?"
2. **Scope** — "Is this for one project or something you'll reuse across different tasks?"
3. **Memory** — "Should this agent remember context between sessions, or start fresh each time?"
4. **Capabilities** — "Will it need reusable skills, tools, workflows, or sub-agents?"
5. **Constraints** — "Are there things this agent should never do, or rules it should always follow?"
6. **Persona** — "Do you want a specific name, tone, or working style for it?"

If the user abandons the elicitation or answers vaguely, generate the smallest
reasonable scaffold anyway, record the inference in `assumptions`, and avoid
asking more questions than necessary.

---

## Workspace structure

```
workspace/
├── AGENTS.md
├── SOUL.md
├── USER.md
├── TOOLS.md
├── HEARTBEAT.md
├── memory/
│   └── MEMORY.md
├── skills/
│   └── <skill-name>/
│       └── SKILL.md
```

### File roles

| File | Role |
|---|---|
| `AGENTS.md` | Routing + reasoning rules, task → context → skills mapping |
| `SOUL.md` | Persona, tone, boundaries |
| `USER.md` | User profile |
| `TOOLS.md` | Tool usage conventions (not permissions) |
| `HEARTBEAT.md` | Short checklist for periodic tasks |
| `memory/MEMORY.md` | Long-term structured memory |

---

## Skill and Dependency Reference Handling

The skill extracts all internal skill names and external dependency URLs from
the brief before generating the scaffold.

### Reference formats

| Format | Example | Type |
|---|---|---|
| Bare kebab-case name | `review-summary` | Internal |
| GitHub URL | `https://github.com/owner/repo/tree/main/skills/skill-rag` | External |

### Handling Rules

- **Internal ref** (bare kebab-case, no `/`, no `github.com`): the generated
  agent owns this skill.
  - Create `skills/<name>/SKILL.md` in the scaffold.
- **External ref** (contains `github.com/`): shared dependency owned outside the
  generated agent repository.
  - Preserve the full URL exactly, including branch and subpath.
  - Do NOT download it.
  - Do NOT create a local `skills/<name>/` placeholder for it.
  - Declare it in `skill_refs`, `AGENTS.md`, and `TOOLS.md` so AgentDesk can
    resolve or install it when the agent launches.

### AGENTS.md Skill Blocks

In `AGENTS.md`, emit separate sections:

- `Internal skills:` for skills generated inside the agent repository.
- `External skills to install:` for full GitHub URLs that AgentDesk should
  resolve later.

Omit a section if it has no entries. Do not invent skill names or URLs not
present in the brief.

---

## Task reference

This is a single-task contract pack. There is no `--task` flag.

| Task | Output schema | Required input |
|---|---|---|
| `generate-agent-scaffold` | `schemas/output.schema.json` | A natural-language brief describing the intended agent |

---

## Rules

- Validate before proceeding.
- If the brief is underspecified, run the elicitation flow first.
- Ask one question at a time, with a maximum of 6 questions total.
- Return JSON only once you have enough context to generate the scaffold.
- Do not emit Markdown fences or prose outside the final JSON object.
- Always include `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`,
  and `memory/MEMORY.md`.
- Choose the smallest viable template that satisfies the brief.
- Do not invent compliance, sub-agents, tools, or workflows unless the brief
  implies them.
- If the brief is underspecified, make explicit assumptions in `assumptions`.
- Before generating, evaluate if an agent is necessary.
- If a simpler alternative exists (script or skill), record it in `assumptions`.
- Always justify structural choices (template, directories, files).
- External skill refs must be preserved as full URLs and declared for AgentDesk
  runtime resolution. They must not be downloaded or duplicated into `skills/`.

---

## CLI usage

```bash
uv run skills/generate-agent-scaffold/scripts/cli.py prompt
uv run skills/generate-agent-scaffold/scripts/cli.py schema
uv run skills/generate-agent-scaffold/scripts/cli.py validate \
  --json-file /path/to/output.json
```

---

## Output

The final output is a strict JSON scaffold plan. The elicitation itself is
conversational and does not alter the output schema.

The optional `skill_refs` field provides a structured breakdown of internal
skills and external skill dependencies extracted from the brief. External
dependencies preserve their full source URLs, including subpaths.

```jsonc
{
  "agent_name": "legal-research-agent",
  "template": "standard",
  "summary": "Standard scaffold for a legal research agent with internal and external skills.",
  "topology": "SINGLE",
  "decision_log": {
    "agent_needed": true,
    "simpler_alternative": null,
    "justification": "The brief requires persistent memory and multi-skill orchestration."
  },
  "skill_refs": [
    {
      "ref": "case-summarizer",
      "type": "internal",
      "source": "case-summarizer",
      "version": null,
      "install": "generate"
    },
    {
      "ref": "https://github.com/owner/agent-skills/tree/main/skills/skill-rag",
      "type": "github",
      "source": "https://github.com/owner/agent-skills/tree/main/skills/skill-rag",
      "version": null,
      "install": "declare_external"
    }
  ],
  "directories": [
    {
      "path": "skills/case-summarizer",
      "purpose": "Internal case-summarizer skill generated inside this agent repository.",
      "required": false
    }
  ],
  "files": [
    {
      "path": "AGENTS.md",
      "purpose": "Rules, priorities, and how to behave.",
      "required": true,
      "content": "# Agent Instructions\n..."
    },
    {
      "path": "SOUL.md",
      "purpose": "Persona, identity and communication style.",
      "required": true,
      "content": "# Soul\n..."
    },
    {
      "path": "USER.md",
      "purpose": "Information about the user to help personalize interactions.",
      "required": true,
      "content": "# User Profile\n..."
    },
    {
      "path": "HEARTBEAT.md",
      "purpose": "Tiny checklist for periodic tasks the agent must work on.",
      "required": true,
      "content": "# Heartbeat Tasks\n..."
    },
    {
      "path": "TOOLS.md",
      "purpose": "Notes about local tools and conventions.",
      "required": true,
      "content": "# Tool Usage Notes\n..."
    },
    {
      "path": "memory/MEMORY.md",
      "purpose": "Curated long-term memory with important information that persists across sessions.",
      "required": true,
      "content": "# Long-term Memory\n..."
    }
  ],
  "assumptions": [
    "External skill dependency https://github.com/owner/agent-skills/tree/main/skills/skill-rag is declared for AgentDesk runtime resolution and is not copied into this agent repository."
  ],
  "next_steps": [
    "Implement skills/case-summarizer/.",
    "Verify AgentDesk can resolve the declared external skill URL at launch time."
  ]
}
```

---

## Common workflows

```bash
# Print the prompt contract for the model step
uv run skills/generate-agent-scaffold/scripts/cli.py prompt

# Print the schema consumed by a validator or orchestrator
uv run skills/generate-agent-scaffold/scripts/cli.py schema

# Validate a generated scaffold plan
uv run skills/generate-agent-scaffold/scripts/cli.py validate \
  --json-file ./scaffold-plan.json
```

---

## Composition hints

```text
generate-agent-scaffold          output: elicited brief → JSON scaffold plan
  |
  v
file-writing agent or workflow   output: materialized folder tree on disk
```

Use this skill before any file-writing step that should create a full agent
workspace from a brief. The output is intentionally structured so a downstream
agent can create directories and files with no additional inference.
