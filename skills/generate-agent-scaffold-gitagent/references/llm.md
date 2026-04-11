# gitagent — LLM reference

> Condensed specification reference for creating and maintaining a skill that
> generates gitagent-compliant agent folders.
> Generated: 2026-04-10
> Source docs:
> - https://github.com/open-gitagent/gitagent
> - https://github.com/open-gitagent/gitagent/blob/main/spec/SPECIFICATION.md

---

## Standard overview

- **Standard**: `gitagent`
- **Current referenced spec version**: `0.1.0`
- **Purpose**: define a portable, git-native agent as a repository folder tree
- **Protocol**: file-system specification, not a network API
- **Core promise**: cloning a repo gives a complete agent definition

---

## Required files

Only two files are required for a valid minimal gitagent agent:

| Path | Required | Purpose |
|---|---|---|
| `agent.yaml` | yes | Canonical manifest with strict schema |
| `SOUL.md` | yes | Identity, personality, values, and communication style |

Everything else is optional and should be added only when the user brief
requires that capability.

---

## Canonical directory structure

The spec and README describe this structure:

```text
<agent-root>/
├── agent.yaml
├── SOUL.md
├── RULES.md
├── DUTIES.md
├── AGENTS.md
├── README.md
├── skills/
├── tools/
├── knowledge/
├── memory/
├── workflows/
├── hooks/
├── examples/
├── agents/
├── compliance/
├── config/
└── .gitagent/
```

Interpretation for scaffold generation:

- `minimal` template: emit only required files plus a small `README.md`
- `standard` template: include the common operational files and empty top-level
  directories used by most agents
- `full` template: include compliance, hooks, workflows, config, and sub-agent
  placeholders

---

## Generation Philosophy

The scaffold generation follows a strict minimal-first approach:

- Only `agent.yaml` and `SOUL.md` are required by the spec
- Over-scaffolding is considered a failure mode
- Additional files and directories must be justified by the user brief

The generator must prefer:

- minimal structure
- explicit needs
- real constraints

over:

- completeness
- hypothetical extensibility
- architectural ambition

---

## agent.yaml rules

The manifest is the only file with a strict schema.

### Required fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | Lowercase kebab-case, pattern `^[a-z][a-z0-9-]*$` |
| `version` | string | Semantic version |
| `description` | string | One-line description |

### Recommended fields

| Field | Type | Notes |
|---|---|---|
| `spec_version` | string | Use `"0.1.0"` for this referenced spec |

### Common optional fields

- `author`
- `license`
- `model`
- `skills`
- `tools`
- `agents`
- `delegation`
- `runtime`
- `a2a`
- `compliance`
- `tags`
- `metadata`

### Naming conventions

- YAML keys: `snake_case`
- Agent, skill, and tool identifiers: `kebab-case`
- Paths and folder names should remain lowercase ASCII where possible

---

## Template tiers

The README exposes three scaffold tiers:

| Template | Intent | Typical output |
|---|---|---|
| `minimal` | Smallest valid gitagent agent | `agent.yaml`, `SOUL.md`, optional `README.md` |
| `standard` | General-purpose working agent | Minimal files plus `RULES.md`, `AGENTS.md`, `skills/`, `tools/`, `workflows/`, `.gitagent/` |
| `full` | Compliance-heavy or production agent | Standard template plus `DUTIES.md`, `knowledge/`, `memory/`, `hooks/`, `config/`, `agents/`, `compliance/`, `examples/` |

The generation skill should infer the template from the user brief, but allow
explicit override.

---

## Optional sections and when to include them

| Path | Include when |
|---|---|
| `RULES.md` | The agent has hard behavioral constraints or safety rules |
| `DUTIES.md` | Segregation of duties or role boundaries matter |
| `AGENTS.md` | A framework-agnostic fallback instruction layer is useful |
| `skills/` | The agent owns reusable capability modules |
| `tools/` | MCP-compatible tool schemas or wrappers are needed |
| `knowledge/` | The agent should consult maintained reference material |
| `memory/` | Persistent cross-session state is needed |
| `workflows/` | Deterministic multi-step playbooks are required |
| `hooks/` | Startup or teardown behavior matters |
| `agents/` | The design includes sub-agents |
| `compliance/` | Regulated workflows require auditable artifacts |
| `config/` | Environment-specific overrides are needed |
| `.gitagent/` | Runtime state directory; usually present and gitignored |

---

## Compliance model

gitagent gives special weight to regulated environments.

Key compliance concepts available in `agent.yaml`:

- `risk_tier`
- `frameworks`
- `supervision`
- `recordkeeping`
- `model_risk`
- `data_governance`
- `communications`
- `vendor_management`
- `segregation_of_duties`

Use these only when the brief clearly calls for regulated or auditable
operation. Do not emit them in a minimal scaffold by default.

---

## Output mapping for the generation skill

The skill should normalize its output as a scaffold plan rather than raw prose.

| Output field | Meaning |
|---|---|
| `agent_name` | Kebab-case gitagent identifier |
| `template` | `minimal`, `standard`, or `full` |
| `gitagent_spec_version` | Usually `0.1.0` |
| `directories[]` | Ordered directory creation plan |
| `files[]` | Ordered file creation plan with starter content |
| `assumptions[]` | Inferred decisions made from the brief |
| `next_steps[]` | Suggested follow-up work after scaffolding |

Each file entry should include:

- `path`
- `required`
- `purpose`
- `content`

This lets a downstream agent write the folder tree deterministically.

---

## Known quirks and gotchas

- `agent.yaml` is strict; other files are descriptive and can stay lightweight.
- Only `agent.yaml` and `SOUL.md` are required. Over-scaffolding is a common
  failure mode.
- `DUTIES.md` is optional and should not be added unless role separation is
  actually needed.
- `.gitagent/` is runtime state and should typically be represented as a
  placeholder directory plus `.gitignore` guidance, not prefilled state files.
- Skills and tools are first-class git-native assets. Leave placeholders rather
  than inventing capabilities the brief did not request.

---

## Useful source examples

- README standard tree: shows required vs optional directories and the
  `minimal` / `standard` / `full` mental model.
- Specification section `Directory Structure`: authoritative path list.
- Specification section `agent.yaml — The Manifest`: authoritative naming and
  field rules.
