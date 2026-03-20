---
name: dev-creating-subagents
description: Create and manage subagents in Kimi CLI and Codex. Use when users need to configure custom agents, define subagent workflows, set up agent inheritance (Kimi), or understand platform-specific subagent capabilities including Task tool usage, agent file formats (YAML/TOML), system prompts, and dynamic agent creation (Kimi).
---

# Creating Subagents

Guide for defining custom agents and subagents in Kimi CLI (YAML) and Codex (TOML).

## Platform Overview

| Platform | Config Format | User Config Path | Project Config Path | Key Features |
|----------|---------------|------------------|---------------------|--------------|
| **Kimi CLI** | YAML | `~/.kimi/agents/` | `.agents/` | Inheritance, dynamic creation, template variables |
| **Codex** | TOML | `~/.codex/agents/` | `.codex/agents/` | Batch processing, sandbox modes, nicknames |

## Core Concepts

### What are Subagents?

Subagents are specialized AI agents that:
- Handle specific task types (coding, review, exploration)
- Run in isolated contexts to avoid polluting main conversation
- Enable parallel execution for complex workflows
- Return results to the parent agent when complete

### Common Execution Model

Both platforms use similar subagent invocation via the **Task** tool:

```yaml
description: "Short task summary"
subagent_name: "agent-name"
prompt: |
  Detailed task description with context...
```

Key characteristics:
- **Isolated context**: No access to parent conversation history
- **Complete context required**: All necessary info must be in the prompt
- **Parallel capable**: Multiple subagents can run simultaneously
- **Result aggregation**: Parent collects and synthesizes results

---

## Kimi CLI

Kimi CLI uses YAML format with powerful inheritance and template support.

### Quick Start

**Create agent file** (`my-agent.yaml`):
```yaml
version: 1
agent:
  name: my-agent
  system_prompt_path: ./system.md
  tools:
    - "kimi_cli.tools.shell:Shell"
    - "kimi_cli.tools.file:ReadFile"
```

**Load it**:
```bash
kimi --agent-file /path/to/my-agent.yaml
```

### Full Configuration

```yaml
version: 1
agent:
  extend: default              # Inherit from built-in or custom agent
  name: my-agent               # Agent name
  system_prompt_path: ./system.md    # Path to system prompt (relative to agent file)
  system_prompt_args:          # Custom template variables
    ROLE: "security expert"
    FOCUS: "vulnerability detection"
  tools:                       # Enabled tools (module:ClassName format)
    - "kimi_cli.tools.shell:Shell"
    - "kimi_cli.tools.file:ReadFile"
    - "kimi_cli.tools.multiagent:Task"
  exclude_tools:               # Tools to exclude from inherited set
    - "kimi_cli.tools.web:SearchWeb"
  subagents:                   # Define subagents
    coder:
      path: ./coder-sub.yaml
      description: "Handle coding tasks"
    reviewer:
      path: ./reviewer-sub.yaml
      description: "Code review expert"
```

### Built-in Agents

| Agent | Purpose | Extra Tools |
|-------|---------|-------------|
| `default` | General use | Full tool set including Task, Shell, ReadFile, WriteFile |
| `okabe` | Experimental | default tools + SendDMail (delayed message) |

Select at startup:
```bash
kimi --agent okabe
```

### Inheritance System

Kimi supports powerful inheritance via `extend`:

```yaml
version: 1
agent:
  extend: default              # Inherit from built-in
  system_prompt_path: ./my-prompt.md   # Override specific fields
  exclude_tools:
    - "kimi_cli.tools.web:SearchWeb"
```

Extend from custom agent:
```yaml
version: 1
agent:
  extend: ./base-agent.yaml    # Relative path to another agent file
```

### System Prompt Templates

System prompt files support template variables with `${VAR}` syntax.

**Built-in variables**:

| Variable | Description |
|----------|-------------|
| `${KIMI_NOW}` | Current time (ISO format) |
| `${KIMI_WORK_DIR}` | Working directory path |
| `${KIMI_WORK_DIR_LS}` | Working directory file list |
| `${KIMI_AGENTS_MD}` | AGENTS.md content (if exists) |
| `${KIMI_SKILLS}` | Loaded skills list |
| `${KIMI_ADDITIONAL_DIRS_INFO}` | Additional directories info |

**Custom variables**:

```yaml
agent:
  system_prompt_args:
    ROLE: "security expert"
    FOCUS: "vulnerability detection"
```

Use in `system.md`:
```markdown
# Security Reviewer

You are a ${ROLE} focused on ${FOCUS}.
Current time: ${KIMI_NOW}
Working directory: ${KIMI_WORK_DIR}
```

### Defining Subagents

Subagents are defined in the main agent file:

```yaml
version: 1
agent:
  extend: default
  subagents:
    coder:
      path: ./coder-sub.yaml
      description: "Handle coding tasks"
    reviewer:
      path: ./reviewer-sub.yaml
      description: "Code review expert"
```

Subagent file (inherits from parent):

```yaml
# coder-sub.yaml
version: 1
agent:
  extend: ./agent.yaml         # Inherit from main agent
  system_prompt_args:
    ROLE_ADDITIONAL: |
      You are now running as a subagent specialized in coding.
      Focus on implementation details and code quality.
  exclude_tools:
    - "kimi_cli.tools.multiagent:Task"  # Exclude Task to prevent nesting
```

### Dynamic Subagent Creation

Create subagents at runtime with **CreateSubagent** tool (not enabled by default).

Enable in agent file:
```yaml
agent:
  tools:
    - "kimi_cli.tools.multiagent:CreateSubagent"
```

Usage:
```yaml
name: "analyzer"
system_prompt: |
  You are a code analyzer. Review the provided code for:
  1. Security issues
  2. Performance problems
  3. Maintainability concerns
```

Dynamic subagents:
- Persist with session state
- Automatically restored when resuming session
- Can be used with Task tool like predefined subagents

### Common Tool Paths

| Tool | Path |
|------|------|
| Task | `kimi_cli.tools.multiagent:Task` |
| CreateSubagent | `kimi_cli.tools.multiagent:CreateSubagent` |
| Shell | `kimi_cli.tools.shell:Shell` |
| ReadFile | `kimi_cli.tools.file:ReadFile` |
| WriteFile | `kimi_cli.tools.file:WriteFile` |
| StrReplaceFile | `kimi_cli.tools.file:StrReplaceFile` |
| Glob | `kimi_cli.tools.file:Glob` |
| Grep | `kimi_cli.tools.file:Grep` |
| SearchWeb | `kimi_cli.tools.web:SearchWeb` |
| FetchURL | `kimi_cli.tools.web:FetchURL` |
| AskUserQuestion | `kimi_cli.tools.ask_user:AskUserQuestion` |
| SetTodoList | `kimi_cli.tools.todo:SetTodoList` |
| EnterPlanMode | `kimi_cli.tools.plan.enter:EnterPlanMode` |
| ExitPlanMode | `kimi_cli.tools.plan:ExitPlanMode` |
| TaskList | `kimi_cli.tools.background:TaskList` |
| TaskOutput | `kimi_cli.tools.background:TaskOutput` |
| TaskStop | `kimi_cli.tools.background:TaskStop` |
| Think | `kimi_cli.tools.think:Think` |
| SendDMail | `kimi_cli.tools.dmail:SendDMail` |

---

## Codex

Codex uses TOML format with batch processing and sandbox controls.

### Quick Start

**Create agent file** (`reviewer.toml`):
```toml
name = "reviewer"
description = "Code review specialist"
developer_instructions = """
Review code for correctness, security, and maintainability.
Prioritize concrete findings over style comments.
"""
```

**Location**: Place in `~/.codex/agents/` (user) or `.codex/agents/` (project).

### Full Configuration

```toml
name = "pr-reviewer"
description = "PR reviewer focused on correctness, security, and missing tests"
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
Lead with concrete findings and include reproduction steps when possible.
"""

# Optional fields
nickname_candidates = ["Atlas", "Delta", "Echo"]  # Display names
model = "gpt-5.4"                                  # Model override
model_reasoning_effort = "high"                    # Reasoning level
sandbox_mode = "read-only"                         # Sandbox restriction

# MCP servers (platform-specific)
[mcp_servers.docs]
url = "https://developers.openai.com/mcp"

# Skills configuration
[[skills.config]]
path = "/path/to/skill/SKILL.md"
enabled = true
```

### Built-in Agents

| Agent | Purpose | Characteristics |
|-------|---------|-----------------|
| `default` | General-purpose | Fallback for all tasks |
| `worker` | Execution-focused | Implementation and fixes |
| `explorer` | Read-heavy | Codebase exploration |

Custom agents with matching names take precedence over built-ins.

### Global Settings

Configure in `.codex/config.toml` under `[agents]` section:

```toml
[agents]
max_threads = 6              # Concurrent agent threads (default: 6)
max_depth = 1                # Nesting depth (default: 1)
job_max_runtime_seconds = 1800  # Per-worker timeout for CSV jobs
```

**Important**:
- `max_depth = 1` allows direct child to spawn but prevents deeper nesting
- Raising `max_depth` increases token usage and latency risks
- `max_threads` caps concurrent threads but doesn't remove recursion costs

### Sandbox Modes

Control tool access via `sandbox_mode`:

| Mode | Description |
|------|-------------|
| `read-only` | File reads only, no modifications |
| `workspace-write` | Can write to workspace files |
| (default) | Full tool access based on parent session |

Example:
```toml
name = "explorer"
description = "Read-only codebase explorer"
sandbox_mode = "read-only"
developer_instructions = "Map code paths without making changes..."
```

### Subagent Definition

Unlike Kimi, Codex subagents are **standalone files** (no central registry):

**File**: `.codex/agents/reviewer.toml`
```toml
name = "reviewer"
description = "Code review expert"
developer_instructions = """
Review for correctness, security, and test coverage.
"""
sandbox_mode = "read-only"
```

**File**: `.codex/agents/explorer.toml`
```toml
name = "explorer"
description = "Codebase mapping specialist"
developer_instructions = """
Trace execution paths and identify relevant files.
"""
model = "gpt-5.4-mini"
sandbox_mode = "read-only"
```

### Batch Processing (CSV)

Codex supports `spawn_agents_on_csv` for parallel batch processing:

```
Create /tmp/components.csv with columns path,owner and one row per component.

Then call spawn_agents_on_csv with:
- csv_path: /tmp/components.csv
- id_column: path
- instruction: "Review {path} owned by {owner}. Return JSON with keys path, risk, summary."
- output_csv_path: /tmp/components-review.csv
- output_schema: object with required string fields path, risk, summary
```

Each worker must call `report_agent_job_result` exactly once.

---

## Platform Comparison

### Configuration Format

| Feature | Kimi CLI | Codex |
|---------|----------|-------|
| Format | YAML | TOML |
| Extension | `.yaml` | `.toml` |
| Inheritance | ✅ `extend` field | ❌ None (standalone) |
| System Prompt | External `.md` file | Inline `developer_instructions` |
| Template Variables | ✅ `${VAR}` syntax | ❌ Not supported |
| Dynamic Creation | ✅ `CreateSubagent` tool | ❌ Not supported |
| Batch Processing | ❌ Not available | ✅ `spawn_agents_on_csv` |
| Display Nicknames | ❌ Not supported | ✅ `nickname_candidates` |

### Subagent Definition

**Kimi**: Centralized registry in main agent file
```yaml
agent:
  subagents:
    coder:
      path: ./coder.yaml
      description: "Handle coding"
```

**Codex**: Distributed standalone files
```toml
# .codex/agents/coder.toml
name = "coder"
description = "Handle coding"
```

### Tool Control

**Kimi**: Explicit allowlist/denylist
```yaml
tools: [...]          # Only these
exclude_tools: [...]  # Remove from inherited
```

**Codex**: Sandbox mode + inheritance
```toml
sandbox_mode = "read-only"  # Control write access
```

### Migration: Kimi → Codex

1. Convert YAML to TOML format
2. Inline system prompt to `developer_instructions`
3. Add `description` field (required in Codex)
4. Replace `tools`/`exclude_tools` with `sandbox_mode`
5. Split subagents into separate files
6. Remove inheritance, copy parent settings

### Migration: Codex → Kimi

1. Convert TOML to YAML format
2. Extract `developer_instructions` to external `.md` file
3. Add `extend` for inheritance
4. Define subagents in `subagents` block
5. List explicit `tools` or use `exclude_tools`
6. Optional: Add `system_prompt_args` for templates

---

## Best Practices

### Subagent Design

1. **Single responsibility**: One focused task per subagent
2. **Complete context**: Include all necessary info in Task prompt
3. **Prevent nesting**: Exclude Task tool in subagents (if supported)
4. **Descriptive names**: 3-5 words in task description

### Workflow Patterns

**Parallel Review** (both platforms):
```
Spawn agents for:
1. Security review
2. Code quality check
3. Bug detection
4. Performance analysis

Wait for all, then summarize.
```

**Sequential Pipeline** (Kimi with inheritance):
```
main-agent → explorer (map code) → reviewer (find issues) → fixer (implement)
```

**Batch Processing** (Codex):
```
spawn_agents_on_csv with component list
→ Each worker reviews one component
→ Results aggregated in output CSV
```

### Security Considerations

- Use `sandbox_mode = "read-only"` (Codex) for exploration tasks
- Exclude dangerous tools via `exclude_tools` (Kimi) for untrusted subagents
- Validate inputs in Task prompts to prevent injection

---

## Complete Example: PR Review Workflow

### Kimi Implementation

**main-agent.yaml**:
```yaml
version: 1
agent:
  name: pr-reviewer
  extend: default
  system_prompt_path: ./system.md
  subagents:
    explorer:
      path: ./explorer-sub.yaml
      description: "Map codebase changes"
    reviewer:
      path: ./reviewer-sub.yaml
      description: "Review code for issues"
```

**system.md**:
```markdown
# PR Review Agent

You coordinate PR reviews. Current time: ${KIMI_NOW}.

## Workflow
1. Use 'explorer' to map affected code paths
2. Use 'reviewer' to identify issues
3. Summarize findings
```

**explorer-sub.yaml**:
```yaml
version: 1
agent:
  extend: ./main-agent.yaml
  system_prompt_args:
    ROLE: "codebase explorer"
  exclude_tools:
    - "kimi_cli.tools.multiagent:Task"
```

**reviewer-sub.yaml**:
```yaml
version: 1
agent:
  extend: ./main-agent.yaml
  system_prompt_args:
    ROLE: "code reviewer"
  exclude_tools:
    - "kimi_cli.tools.multiagent:Task"
```

### Codex Implementation

**.codex/agents/explorer.toml**:
```toml
name = "explorer"
description = "Read-only codebase explorer for gathering evidence"
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Stay in exploration mode.
Trace the real execution path, cite files and symbols.
Avoid proposing fixes unless the parent agent asks.
"""
```

**.codex/agents/reviewer.toml**:
```toml
name = "reviewer"
description = "PR reviewer focused on correctness and security"
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, and missing test coverage.
Lead with concrete findings.
"""
```

**.codex/config.toml**:
```toml
[agents]
max_threads = 6
max_depth = 1
```

---

## References

- [Kimi CLI Agents Documentation](https://moonshotai.github.io/kimi-cli/en/customization/agents.html)
- [Codex Subagents Documentation](https://developers.openai.com/codex/subagents)
- Detailed platform comparisons: [references/platform-comparison.md](references/platform-comparison.md)
