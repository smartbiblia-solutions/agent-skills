---
name: agent-trace
description: >
  Generates a readable execution trace from the raw log of an agentic run,
  regardless of the framework used (Claude Code, LangChain, AgentMD, etc.).
  Use this skill whenever a user mentions an execution log, an agentic run,
  an automated task history, or asks to "understand what the agent did",
  "get a run summary", "document the execution", or "produce an audit report".
  Also applies upstream: if the user asks how to trace or document their agentic
  workflows, propose this format.
metadata:
  version: 0.1.0
  author: smartbiblia
---

# Agent Trace

Transforms a raw agentic execution log into a readable, auditable, and
committable `.run.md` document — regardless of the source framework.

The goal is the same as a saved Jupyter notebook: someone who wasn't present
during the run should be able to understand what happened, why, and with what result.

---

## 1. Identify the output mode

Before generating the trace, determine who will read it:

| Mode | Target reader | Level of detail |
|------|---------------|-----------------|
| `audit` | Developer, ops | All steps, commands, exit codes, durations |
| `narrative` | Project manager, non-coder | Decisions and results in plain language, no commands |
| `compact` | CI/CD, archiving | Summary table only |

If no mode is specified, use `audit` by default and suggest the others at the end of the document.

---

## 2. Extract information from the raw log

Regardless of the source format (JSON, free text, terminal output, XML), extract:

- **Run identity**: workflow name, start timestamp, total duration
- **Global status**: success / failure / partial
- **Step sequence**: in execution order
- **For each step**: name or id, status, duration if available, significant output
- **Agent decisions**: evaluated conditions, chosen branches, retries
- **Rollbacks if any**: which ones were triggered and why
- **Captured variables**: important values produced during the run
- **Errors**: error messages, non-zero exit codes, timeouts

If information is missing from the log (duration, exit code…), leave the field
empty rather than inventing a value.

---

## 3. Structure of the `.run.md` file

ALWAYS use this exact template:

```markdown
# Trace: <workflow-name> — <ISO 8601 timestamp>

## Overall result

**Status**: ✓ success | ✗ failure | ⚠ partial  
**Duration**: <total duration>  
**Framework**: <Claude Code | LangChain | AgentMD | unknown>  

<One sentence summarising what the run accomplished or why it failed.>

---

## Steps

| # | Step | Status | Duration |
|---|------|--------|----------|
| 1 | <name> | ✓ | <duration> |
| 2 | <name> | ✗ | <duration> |

---

## Step details

### 1. <step name>

**Status**: ✓ success  
**Duration**: 14.2s  

<What this step did, in one or two sentences.>

**Significant output** (if relevant):
\```
<output excerpt, truncated to ~10 lines>
\```

---

### 2. <step name>

...

---

## Captured variables

| Variable | Value |
|----------|-------|
| VERSION | v1.4.2 |
| SERVICE_URL | http://... |

*(Section omitted if no variables were captured)*

---

## Errors and warnings

*(Section omitted if the run is a complete success)*

### <name of the failed step>

**Cause**: <error message or description>  
**Action taken**: stopped | continued | rollback triggered  

---

## Executed rollbacks

*(Section omitted if no rollbacks)*

| Rollback | For step | Status |
|----------|----------|--------|
| <name> | <compensated step> | ✓ |

---

## Notes

<Important observations that don't fit the sections above:
unexpected behaviours, retries, notable conditional decisions.>
```

---

## 4. Writing rules by mode

### Mode `audit`
- Include all template sections, even if some are empty (mark as "none")
- Keep significant output excerpts (errors, key values)
- Specify exit codes for failed steps
- Do not paraphrase error messages — transcribe them verbatim

### Mode `narrative`
- Replace the "Steps" table with a flowing narrative paragraph
- In step details, describe the action in plain language without technical terms
- Omit exit codes, shell commands, and stack traces
- Frame errors as plain statements ("The upload failed because the server was unavailable")
- Omit the "Captured variables" and "Rollbacks" sections unless critical for understanding

### Mode `compact`
- A single section: the summary table + overall result
- No per-step detail
- Suitable for embedding in an email or a ticket

---

## 5. Filename and location

Always suggest the filename:

```
<workflow-name>.<YYYYMMDD-HHMM>.run.md
```

Example: `deploy-staging.20241115-1432.run.md`

If multiple runs of the same workflow exist, they accumulate naturally
in chronological order within the same directory.

---

## 6. What this skill does not do

- It does not re-execute the workflow
- It does not interpret the agent's intent beyond what the log contains
- It does not fix run errors — it documents them
- If the log is too fragmentary to reconstruct a coherent sequence,
  it says so explicitly rather than filling the gaps by inference

---

## Example

**Input (raw terminal log):**
```
[14:32:01] check-workspace: OK
[14:32:01] ecr-login: running...
[14:32:08] ecr-login: done (exit 0, 7.2s)
[14:32:08] build: running...
[14:32:22] build: done (exit 0, 14.1s)
[14:32:22] push-image: running...
[14:32:31] push-image: FAILED (exit 1, 8.9s)
[14:32:31] stderr: denied: User: arn:aws:iam::123 is not authorized
[14:32:31] rollback: delete-ecr-tag running...
[14:32:33] rollback: delete-ecr-tag done (exit 0)
[14:32:33] workflow FAILED — rollback complete
```

**Generated output (mode `audit`):**

```markdown
# Trace: deploy-staging — 2024-11-15T14:32:01Z

## Overall result

**Status**: ✗ failure  
**Duration**: 32s  
**Framework**: unknown  

The deployment failed during the ECR image push due to missing IAM permissions.
A rollback was executed successfully.

---

## Steps

| # | Step | Status | Duration |
|---|------|--------|----------|
| 1 | check-workspace | ✓ | — |
| 2 | ecr-login | ✓ | 7.2s |
| 3 | build | ✓ | 14.1s |
| 4 | push-image | ✗ | 8.9s |

---

## Step details

### 1. check-workspace
**Status**: ✓ success

Preliminary workspace check.

### 2. ecr-login
**Status**: ✓ success  
**Duration**: 7.2s

Authentication against Amazon ECR.

### 3. build
**Status**: ✓ success  
**Duration**: 14.1s

Docker image build.

### 4. push-image
**Status**: ✗ failure  
**Duration**: 8.9s  
**Exit code**: 1

Attempted to push the image to ECR.

**Error**:
\```
denied: User: arn:aws:iam::123 is not authorized
\```

---

## Errors and warnings

### push-image

**Cause**: `denied: User: arn:aws:iam::123 is not authorized`  
**Action taken**: rollback triggered

---

## Executed rollbacks

| Rollback | For step | Status |
|----------|----------|--------|
| delete-ecr-tag | push-image | ✓ |
```