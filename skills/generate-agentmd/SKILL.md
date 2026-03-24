---
name: generate-agentmd
description: >
  Generate a ready-to-use agent.md file through a guided conversational
  elicitation. Use this skill whenever a user wants to create a new agent
  but does not know where to start, faces a blank page, or needs a
  structured starting point adapted to a specific backend (Claude Code,
  Codex, OpenClaw, NanoBot, etc.). Always invoke this skill before
  launching a new agent session when no agent.md exists in the target
  workspace. Returns a complete agent.md file and the recommended folder
  structure for the chosen backend.

metadata:
  version: 0.1.0
  author: smartbiblia
  maturity: beta
  preferred_output: markdown
  supports_validation: false

selection:
  use_when:
    - The user wants to create a new agent and has no existing agent.md.
    - The user selects a backend widget from the Agentdesk home and no
      workspace is configured yet.
    - The user explicitly asks to define, configure, or scaffold a new agent.
  avoid_when:
    - The user already has an agent.md and wants to run or modify it directly.
    - The task is to launch or monitor an existing agent session.
    - The user points Agentdesk to an existing workspace folder.
  prefer_over:
    - blank agent.md template
    - static template picker
  combine_with:
    - detect-local-backends
    - launch-agent-session

tags:
  - agentdesk
  - scaffolding
  - onboarding
  - agent-configuration
---

# generate-agentmd

## Purpose

Guides the user through a short conversational elicitation to produce a
complete, backend-adapted agent.md file and the recommended workspace folder
structure. Solves the blank-page problem for users new to agents and saves
time for experienced users who do not want to write boilerplate.

This skill is itself an agent — it uses the Anthropic API internally to
conduct the conversation and generate the output. It is the first agent a
user encounters in Agentdesk, and its job is to make the next agent possible.

## When to use / When not to use

Use this skill at workspace creation time, triggered either by the user
selecting a backend widget on the Agentdesk home page with no existing
workspace, or by an explicit "create agent" action.

Do not invoke this skill if the user already has a workspace with an
agent.md. In that case, offer to open or edit the existing file directly.
Do not use this skill as a mandatory onboarding gate — advanced users must
be able to bypass it entirely by pointing Agentdesk to an existing folder.

## Input

The skill takes a minimal bootstrap context:

- `backend` (optional) — the backend selected by the user on the home page
  (`claude-code`, `codex`, `openclaw`, `nanobot`, `gemini`, `opencode`).
  If not provided, the skill will ask during elicitation.
- `workspace_path` (optional) — target folder where agent.md will be written.
  Defaults to a new folder named after the agent.

## Elicitation flow

The skill conducts a short conversational interview — 4 to 6 questions
maximum. Questions are asked one at a time, in plain language, with no
jargon. The user can answer freely; the skill interprets and maps answers
to agent.md fields.

Suggested question sequence:

1. **Purpose** — "What do you want this agent to do for you?"
2. **Scope** — "Is this for a specific project, or something you'll use
   across different tasks?"
3. **Memory** — "Should this agent remember things between sessions, or
   start fresh each time?"
4. **Backend** (if not already selected) — "Do you have Claude Code, Codex,
   or another tool installed? I can check for you."
5. **Constraints** — "Are there things this agent should never do, or
   rules it should always follow?"
6. **Persona** (optional) — "Do you want to give this agent a name or a
   specific tone?"

The skill may skip questions if earlier answers already imply the answer.
It must never ask more than 6 questions total.

## Output

The skill produces two artifacts:

**1. agent.md** — the main agent definition file, structured as follows:

```markdown
# [Agent name or purpose]

## Identity
[Who this agent is, its tone, its persona if defined]

## Purpose
[What this agent is for, in 2–3 sentences]

## Scope
[What it covers and what is explicitly out of scope]

## Rules
[Constraints, things it must always or never do]

## Memory
[What it should retain between sessions, if applicable]

## Backend
[The recommended backend and why, if relevant to document]
```

**2. Recommended folder structure** — printed as a tree, adapted to the
chosen backend:

For Claude Code / Codex:
```
/[agent-name]/
  agent.md
  /memory/
    context.md
  /skills/
  /projects/
    current.md
```

For OpenClaw / NanoBot:
```
/[agent-name]/
  agent.md
  /skills/
```

The folder structure is a suggestion, not a requirement. The user can
accept it as-is or modify it before the workspace is created.

## Commands

Invoked internally by Agentdesk at workspace creation. Not a CLI skill.

From within Agentdesk the skill is triggered by:
- Clicking "Create agent" on any backend widget
- Selecting "New workspace" from the Kanban view with no existing agent.md

## Examples

**Example 1 — Claude Code, dev project**

User answers:
- Purpose: "Help me maintain a side project, review my PRs, keep track of
  decisions"
- Scope: "Just this one repo"
- Memory: "Yes, remember past decisions"
- Backend: Claude Code (already detected)
- Constraints: "Never push to main directly"

Generated agent.md:
```markdown
# Dev Assistant — [project name]

## Identity
A focused development assistant. Precise, concise, no filler.

## Purpose
Assist with code review, pull request analysis, and decision tracking
for this repository. Acts as a second pair of eyes on the codebase.

## Scope
This repository only. Does not touch infrastructure or deployment
unless explicitly asked.

## Rules
- Never push directly to main.
- Always explain the reasoning behind suggested changes.
- Flag breaking changes explicitly.

## Memory
Track architectural decisions and their rationale in /memory/context.md.
Update after each significant session.

## Backend
Claude Code — task-scoped, launched from the repository root.
```

**Example 2 — OpenClaw, personal assistant**

User answers:
- Purpose: "Manage my emails, remind me of things, help me stay organised"
- Scope: "My whole life, not just one project"
- Memory: "Yes, everything"
- Backend: OpenClaw (not yet installed — skill will suggest installing it)
- Constraints: "Don't send emails without asking me first"

Generated agent.md:
```markdown
# Personal Assistant

## Identity
A proactive personal assistant. Warm but efficient. Speaks plainly.

## Purpose
Manage daily organisation: emails, reminders, calendar, and general
life admin. Available across sessions and channels.

## Scope
Personal productivity across all contexts. Not scoped to any single
project.

## Rules
- Never send an email or message without explicit user confirmation.
- Always summarise what you did at the end of each session.
- Ask before deleting anything.

## Memory
Remember user preferences, ongoing tasks, and important context
persistently. Update proactively.

## Backend
OpenClaw — persistent agent, accessible via Telegram or WhatsApp.
```

## Composition hints

This skill sits at the very beginning of any agent creation pipeline:

```
generate-agentmd
  → detect-local-backends   (if backend not yet confirmed)
  → launch-agent-session    (once agent.md is validated by the user)
```

The user must explicitly validate or edit the generated agent.md before
the workspace is created. The skill never writes to disk without confirmation.

## Failure modes

**User gives very vague answers** — the skill should make a reasonable
assumption, state it explicitly in the generated agent.md, and invite the
user to correct it rather than asking more questions.

**Requested backend not installed** — the skill generates the agent.md
anyway and adds a note recommending the backend. Agentdesk will surface the
install button for that backend on the home page.

**User abandons mid-elicitation** — partial answers are enough. The skill
generates the best agent.md it can from what it has, marking incomplete
sections clearly with a `<!-- TODO -->` comment.
