# Platform Comparison: Kimi CLI vs Codex Subagents

Detailed comparison of subagent capabilities between Kimi CLI and Codex.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Kimi CLI](#kimi-cli-details)
- [Codex](#codex-details)
- [Feature Matrix](#feature-matrix)
- [Migration Guides](#migration-guides)

---

## Quick Reference

### File Locations

| Platform | User Config | Project Config |
|----------|-------------|----------------|
| Kimi CLI | `~/.kimi/agents/` | `.agents/` |
| Codex | `~/.codex/agents/` | `.codex/agents/` |

### File Formats

| Platform | Format | Extension |
|----------|--------|-----------|
| Kimi CLI | YAML | `.yaml` |
| Codex | TOML | `.toml` |

### Loading Commands

| Platform | Command |
|----------|---------|
| Kimi CLI | `kimi --agent-file /path/to/agent.yaml` |
| Codex | Auto-discovered from config directories |

---

## Kimi CLI Details

### Strengths

1. **Powerful Inheritance**: `extend` field allows configuration reuse
2. **Template System**: `${VAR}` syntax with built-in and custom variables
3. **Dynamic Creation**: `CreateSubagent` tool for runtime agent definition
4. **Centralized Registry**: All subagents defined in main agent file
5. **Explicit Tool Control**: Fine-grained allowlist/denylist

### Limitations

1. No built-in batch processing
2. No display nicknames
3. Requires explicit tool listing

### Unique Features

**Template Variables**:
- `${KIMI_NOW}` - Current timestamp
- `${KIMI_WORK_DIR}` - Working directory
- `${KIMI_AGENTS_MD}` - Project documentation
- Custom variables via `system_prompt_args`

**Dynamic Subagent Creation**:
```yaml
# Create at runtime
name: "analyzer"
system_prompt: "You are a specialized analyzer..."
```

---

## Codex Details

### Strengths

1. **Batch Processing**: `spawn_agents_on_csv` for parallel workflows
2. **Display Nicknames**: Human-readable agent names in UI
3. **Sandbox Modes**: Simple access control (`read-only`, `workspace-write`)
4. **Global Controls**: `max_threads`, `max_depth` in config.toml
5. **Built-in Specialization**: `default`, `worker`, `explorer` agents

### Limitations

1. No inheritance (each file standalone)
2. No template variables
3. No dynamic agent creation
4. No centralized subagent registry

### Unique Features

**Batch Processing**:
```toml
# Process CSV with parallel agents
spawn_agents_on_csv:
  csv_path: "/tmp/tasks.csv"
  instruction: "Process {column_name}"
  output_csv_path: "/tmp/results.csv"
```

**Display Nicknames**:
```toml
nickname_candidates = ["Atlas", "Delta", "Echo"]
```

**Sandbox Control**:
```toml
sandbox_mode = "read-only"  # or "workspace-write"
```

---

## Feature Matrix

| Feature | Kimi CLI | Codex |
|---------|----------|-------|
| **Configuration** |
| YAML format | ✅ | ❌ |
| TOML format | ❌ | ✅ |
| Inheritance | ✅ `extend` | ❌ None |
| Template variables | ✅ `${VAR}` | ❌ |
| **Subagents** |
| Predefined subagents | ✅ Centralized | ✅ Distributed |
| Dynamic creation | ✅ `CreateSubagent` | ❌ |
| Batch processing | ❌ | ✅ CSV-based |
| Display nicknames | ❌ | ✅ |
| **Tool Control** |
| Explicit tool list | ✅ | ⚠️ Inherited |
| Tool exclusion | ✅ | ❌ |
| Sandbox modes | ❌ | ✅ |
| **Other** |
| External system prompt | ✅ | ❌ |
| Inline system prompt | ❌ | ✅ |
| Global concurrency limits | ❌ | ✅ |

---

## Migration Guides

### Kimi CLI → Codex

#### Step 1: Convert Format

**Before** (`agent.yaml`):
```yaml
version: 1
agent:
  name: reviewer
  system_prompt_path: ./system.md
  tools:
    - "kimi_cli.tools.file:ReadFile"
    - "kimi_cli.tools.file:Grep"
```

**After** (`reviewer.toml`):
```toml
name = "reviewer"
description = "Code reviewer agent"
developer_instructions = """
[Copy content from system.md here]
"""
```

#### Step 2: Handle Inheritance

**Before** (Kimi with inheritance):
```yaml
# base.yaml
agent:
  name: base
  tools: ["tool1", "tool2", "tool3"]

# child.yaml
agent:
  extend: ./base.yaml
  exclude_tools: ["tool3"]
```

**After** (Codex standalone):
```toml
# base.toml
name = "base"
description = "Base agent"

# child.toml
name = "child"
description = "Child agent"
# Copy needed tools/config from base
```

#### Step 3: Convert Subagents

**Before** (Kimi centralized):
```yaml
agent:
  subagents:
    coder:
      path: ./coder.yaml
      description: "Handle coding"
```

**After** (Codex distributed):
```toml
# .codex/agents/coder.toml
name = "coder"
description = "Handle coding"
developer_instructions = "..."
```

#### Step 4: Replace Template Variables

**Before** (Kimi):
```markdown
# system.md
Current time: ${KIMI_NOW}
Role: ${ROLE}
```

**After** (Codex):
```toml
developer_instructions = """
Current time will be provided in context.
Role: security expert  # Hardcode or remove dynamic parts
"""
```

#### Step 5: Add Batch Processing (Optional)

Leverage Codex's CSV batch processing where applicable:
```toml
# Previously: Loop with Task tool
# Now: spawn_agents_on_csv for parallel execution
```

### Codex → Kimi CLI

#### Step 1: Convert Format

**Before** (`reviewer.toml`):
```toml
name = "reviewer"
description = "Code reviewer"
developer_instructions = """
Review code for issues.
"""
```

**After** (`agent.yaml`):
```yaml
version: 1
agent:
  name: reviewer
  system_prompt_path: ./system.md
```

**system.md**:
```markdown
Review code for issues.
```

#### Step 2: Add Inheritance

**Before** (Codex standalone files with duplication):
```toml
# reviewer.toml
name = "reviewer"
model = "gpt-5.4"
sandbox_mode = "read-only"

# explorer.toml
name = "explorer"
model = "gpt-5.4"
sandbox_mode = "read-only"
```

**After** (Kimi with inheritance):
```yaml
# base.yaml
agent:
  name: base
  tools:
    - "kimi_cli.tools.file:ReadFile"
    - "kimi_cli.tools.file:Grep"

# reviewer.yaml
agent:
  extend: ./base.yaml
  name: reviewer
  system_prompt_path: ./reviewer.md

# explorer.yaml
agent:
  extend: ./base.yaml
  name: explorer
  system_prompt_path: ./explorer.md
```

#### Step 3: Centralize Subagents

**Before** (Codex distributed):
```toml
# .codex/agents/coder.toml
name = "coder"

# .codex/agents/reviewer.toml
name = "reviewer"
```

**After** (Kimi centralized):
```yaml
# main-agent.yaml
agent:
  subagents:
    coder:
      path: ./coder-sub.yaml
      description: "Handle coding"
    reviewer:
      path: ./reviewer-sub.yaml
      description: "Review code"
```

#### Step 4: Add Template Variables

Leverage Kimi's template system:
```yaml
agent:
  system_prompt_path: ./system.md
  system_prompt_args:
    ROLE: "security expert"
    FOCUS: "vulnerability detection"
```

```markdown
# system.md
You are a ${ROLE} focused on ${FOCUS}.
Current time: ${KIMI_NOW}
```

#### Step 5: Explicit Tool Control

Replace `sandbox_mode` with explicit tool lists:
```yaml
agent:
  tools:
    - "kimi_cli.tools.file:ReadFile"
    - "kimi_cli.tools.file:Grep"
    # No Shell tool = read-only equivalent
```

---

## Platform-Specific Patterns

### Pattern: PR Review Workflow

**Kimi Implementation**:
```yaml
# main-agent.yaml
agent:
  subagents:
    explorer:
      path: ./explorer.yaml
      description: "Map code changes"
    reviewer:
      path: ./reviewer.yaml
      description: "Find issues"
```

**Codex Implementation**:
```toml
# .codex/agents/explorer.toml
name = "explorer"
description = "Map code changes"
sandbox_mode = "read-only"

# .codex/agents/reviewer.toml
name = "reviewer"
description = "Find issues"
sandbox_mode = "read-only"
```

### Pattern: Batch Code Analysis

**Kimi** (sequential loop):
```yaml
# Loop with Task tool for each file
# No built-in batching
```

**Codex** (parallel CSV):
```toml
# spawn_agents_on_csv
# Parallel processing with automatic aggregation
```

### Pattern: Dynamic Specialist

**Kimi** (runtime creation):
```yaml
# Use CreateSubagent tool
# Define specialist based on task type
```

**Codex** (predefined variants):
```toml
# Define multiple agent variants upfront
# Select based on task type
```

---

## Recommendations

### When to Use Kimi CLI

- Need configuration inheritance to reduce duplication
- Want dynamic agent creation based on runtime context
- Prefer external system prompt files for version control
- Need fine-grained tool control

### When to Use Codex

- Need batch processing of many similar tasks
- Want simple sandbox-based access control
- Prefer standalone agent files for modularity
- Need display nicknames for UI clarity

---

## References

- [Kimi CLI Documentation](https://moonshotai.github.io/kimi-cli/en/customization/agents.html)
- [Codex Subagents Documentation](https://developers.openai.com/codex/subagents)
