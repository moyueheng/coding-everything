# coding-everything Project Documentation

## Project Overview

This project (`coding-everything`) is a Git submodule wrapper that includes the **Superpowers** project - a comprehensive software development workflow framework for AI coding agents. Superpowers provides a collection of composable "skills" that guide AI agents through systematic, disciplined software development workflows.

**Upstream Repository**: https://github.com/obra/superpowers.git

### What is Superpowers?

Superpowers is a workflow framework designed to be used with AI coding assistants (Claude Code, Codex, OpenCode). It ensures that AI agents:

1. **Don't jump into coding immediately** - Instead, they first brainstorm and refine specifications
2. **Follow systematic processes** - TDD, structured debugging, code review workflows
3. **Use skills automatically** - Each skill triggers when relevant to the task at hand

The core philosophy emphasizes:
- **Test-Driven Development (TDD)** - Write tests first, always
- **Systematic over ad-hoc** - Process over guessing
- **Complexity reduction** - Simplicity as primary goal
- **Evidence over claims** - Verify before declaring success

## Project Structure

```
coding-everything/
├── README.md                 # Project title
├── .gitmodules              # Git submodule configuration
├── AGENTS.md                # This file
└── upstream/
    └── superpowers/         # Git submodule: the actual superpowers project
        ├── .claude-plugin/  # Claude Code plugin configuration
        ├── .codex/          # Codex integration files
        ├── .opencode/       # OpenCode integration files
        ├── .github/         # GitHub configuration (FUNDING.yml)
        ├── agents/          # Agent configuration files
        │   └── code-reviewer.md
        ├── commands/        # Predefined command templates
        │   ├── brainstorm.md
        │   ├── execute-plan.md
        │   └── write-plan.md
        ├── docs/            # Documentation
        │   ├── testing.md           # Testing guide
        │   ├── README.codex.md      # Codex setup instructions
        │   ├── README.opencode.md   # OpenCode setup instructions
        │   ├── plans/               # Example implementation plans
        │   └── windows/             # Windows-specific docs
        ├── hooks/           # Session hooks
        │   ├── hooks.json
        │   └── session-start.sh     # Injects superpowers context on session start
        ├── lib/             # Core library code
        │   └── skills-core.js       # Skill resolution and management utilities
        ├── skills/          # **Core skills library (see below)**
        └── tests/           # Test suites
            ├── claude-code/         # Claude Code integration tests
            ├── explicit-skill-requests/  # Skill request tests
            ├── opencode/            # OpenCode tests
            ├── skill-triggering/    # Skill auto-trigger tests
            └── subagent-driven-dev/ # Subagent development tests
```

## Technology Stack

- **Primary Languages**: 
  - Shell scripts (Bash) - for hooks and automation
  - JavaScript (Node.js) - for core library and plugins
  - Python - for test utilities and analysis
  
- **Configuration Formats**: JSON, YAML frontmatter in skill files

- **Supported Platforms**:
  - **Claude Code** - Via plugin marketplace (`obra/superpowers-marketplace`)
  - **Codex** - Via skill discovery in `~/.agents/skills/superpowers/`
  - **OpenCode** - Via plugin system

- **Plugin Version**: 4.3.0 (as of 2026-02-12)

## Skills Library

All skills are located in `upstream/superpowers/skills/`. Each skill is a directory containing at minimum a `SKILL.md` file with YAML frontmatter.

### Skill Format

```yaml
---
name: skill-name
description: Use when [condition] - [what it does]
---

<EXTREMELY-IMPORTANT>
Critical instructions that must be followed
</EXTREMELY-IMPORTANT>

## Skill content with diagrams, guidelines, etc.
```

### Available Skills

| Skill | Purpose | Type |
|-------|---------|------|
| `using-superpowers` | Entry point - teaches how to find and use skills | Rigid |
| `brainstorming` | Socratic design refinement before coding | Rigid |
| `using-git-worktrees` | Create isolated workspace on new branch | Rigid |
| `writing-plans` | Create detailed implementation plans | Rigid |
| `executing-plans` | Batch execution with human checkpoints | Rigid |
| `subagent-driven-development` | Fast iteration with two-stage review | Rigid |
| `test-driven-development` | RED-GREEN-REFACTOR cycle | Rigid |
| `systematic-debugging` | 4-phase root cause analysis | Rigid |
| `verification-before-completion` | Ensure fixes actually work | Rigid |
| `requesting-code-review` | Pre-review checklist | Rigid |
| `receiving-code-review` | Responding to feedback | Flexible |
| `finishing-a-development-branch` | Merge/PR decision workflow | Rigid |
| `dispatching-parallel-agents` | Concurrent subagent workflows | Rigid |
| `writing-skills` | Create new skills following best practices | Rigid |

**Skill Types**:
- **Rigid**: Follow exactly. Don't adapt away discipline (TDD, debugging)
- **Flexible**: Adapt principles to context (patterns, some workflows)

## Core Workflow

The Superpowers framework enforces this development workflow:

```
1. Brainstorming → Refine ideas through questions, save design document
         ↓
2. Using Git Worktrees → Create isolated workspace, verify clean tests
         ↓
3. Writing Plans → Break work into 2-5 minute tasks with verification steps
         ↓
4. Executing Plans / Subagent-Driven-Dev → Implement with reviews
         ↓
5. Test-Driven Development → RED (failing test) → GREEN (pass) → REFACTOR
         ↓
6. Requesting Code Review → Review against plan, report issues by severity
         ↓
7. Finishing a Development Branch → Verify tests, present merge options
```

**Key Rule**: The agent checks for relevant skills before ANY task. Mandatory workflows, not suggestions.

## Development Conventions

### When Working on Skills

1. **Always invoke skills first** - Before any response or action, check if a skill applies (even 1% chance)
2. **Follow skill types**:
   - Rigid skills: Follow exactly, no adaptation
   - Flexible skills: Apply principles to context
3. **Skill priority**: Process skills (brainstorming, debugging) before implementation skills
4. **User instructions say WHAT, not HOW** - "Add X" doesn't mean skip workflows

### Skill Development

To create or modify skills:

1. Follow the `writing-skills` skill (it contains the complete guide)
2. Each skill needs:
   - `SKILL.md` with YAML frontmatter (name, description)
   - Clear `<EXTREMELY-IMPORTANT>` section for mandatory rules
   - Process flow diagrams (Graphviz dot format)
   - Checklists when applicable
3. Skills can include supporting files (scripts, examples, templates)

### Code Style

- **Shell scripts**: Use `set -euo pipefail`, include error handling
- **JavaScript**: ES modules, clear exports, JSDoc comments
- **Documentation**: Markdown with clear sections, good/bad examples

## Testing

### Test Structure

Located in `upstream/superpowers/tests/`:

```
tests/
├── claude-code/                    # Claude Code integration tests
│   ├── test-helpers.sh
│   ├── test-subagent-driven-development.sh
│   ├── test-subagent-driven-development-integration.sh
│   ├── analyze-token-usage.py
│   └── run-skill-tests.sh
├── opencode/                       # OpenCode-specific tests
│   ├── test-plugin-loading.sh
│   ├── test-skills-core.sh
│   └── test-tools.sh
├── explicit-skill-requests/        # Explicit skill invocation tests
├── skill-triggering/              # Auto-trigger verification
└── subagent-driven-dev/           # Subagent workflow tests
```

### Running Tests

**Integration Tests** (requires Claude Code installed):
```bash
cd upstream/superpowers/tests/claude-code
./test-subagent-driven-development-integration.sh
```

**Requirements**:
- Run from superpowers plugin directory (not temp directories)
- Claude Code must be available as `claude` command
- For dev testing: `"superpowers@superpowers-dev": true` in `~/.claude/settings.json`

**Test Duration**: Integration tests can take 10-30 minutes as they execute real implementation plans with multiple subagents.

### Test Coverage

Tests verify:
- Skill tool invocation
- Subagent dispatching (Task tool)
- TodoWrite usage for tracking
- Implementation file creation
- Test passing
- Git commit workflow compliance

## Key Configuration Files

### `.claude-plugin/plugin.json`
Plugin metadata for Claude Code marketplace.

### `hooks/hooks.json`
Defines SessionStart hook that injects superpowers context.

### `lib/skills-core.js`
Core utilities for:
- Extracting YAML frontmatter from skills
- Finding skills in directories
- Resolving skill paths (personal skills override superpowers)
- Checking for updates

## Security Considerations

1. **Hook execution**: SessionStart hook runs shell script - review carefully
2. **Skill content**: Skills can include shell commands - validate before execution
3. **Git operations**: Skills perform git operations (branching, committing) - ensure user awareness
4. **Subagent dispatching**: Subagents have same permissions as parent - sandbox when possible

## Updating the Submodule

To update the superpowers submodule to latest upstream:

```bash
cd upstream/superpowers
git fetch origin
git checkout main  # or specific version tag
cd ../..
git add upstream/superpowers
git commit -m "Update superpowers to vX.Y.Z"
```

## License

MIT License - See `upstream/superpowers/LICENSE`

## Resources

- **Upstream Repository**: https://github.com/obra/superpowers
- **Marketplace**: https://github.com/obra/superpowers-marketplace
- **Issues**: https://github.com/obra/superpowers/issues
- **Blog Post**: https://blog.fsck.com/2025/10/09/superpowers/
