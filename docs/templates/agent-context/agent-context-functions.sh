# Configure these paths for your machine.
export PROJECTS_AI_ROOT="$HOME/<projects-dir>"
export LIFE_AI_ROOT="$HOME/<life-dir>"
export OBSIDIAN_AI_ROOT="$LIFE_AI_ROOT/<obsidian-vault>"

# OpenCode uses OPENCODE_CONFIG_CONTENT to inject workspace instructions and skills.
_oc_with_root() {
  local root="${1:?root is required}"
  shift
  local cfg

  cfg="$(jq -nc \
    --arg agents "$root/AGENTS.md" \
    --arg agents_skills "$root/.agents/skills" \
    --arg opencode_skills "$root/.opencode/skills" \
    '{
      "$schema": "https://opencode.ai/config.json",
      "instructions": [$agents],
      "skills": {
        "paths": [$agents_skills, $opencode_skills]
      }
    }')"

  OPENCODE_CONFIG_CONTENT="$cfg" opencode "$@"
}

ocp() { _oc_with_root "$PROJECTS_AI_ROOT" "$@"; }
ocl() { _oc_with_root "$LIFE_AI_ROOT" "$@"; }
oco() { _oc_with_root "$OBSIDIAN_AI_ROOT" "$@"; }

# Kimi CLI uses --skills-dir for skills; AGENTS.md still needs .kimi/AGENTS.md or symlink.
_kimi_with_root() {
  local root="${1:?root is required}"
  shift
  local args=()

  args+=(--add-dir "$root")
  [ -d "$root/.agents/skills" ] && args+=(--skills-dir "$root/.agents/skills")
  [ -d "$root/.claude/skills" ] && args+=(--skills-dir "$root/.claude/skills")
  [ -d "$root/.codex/skills" ] && args+=(--skills-dir "$root/.codex/skills")

  for d in \
    "$PWD/.kimi/skills" \
    "$PWD/.claude/skills" \
    "$PWD/.codex/skills" \
    "$PWD/.agents/skills"
  do
    [ -d "$d" ] && args+=(--skills-dir "$d")
  done

  kimi "${args[@]}" "$@"
}

kimip() { _kimi_with_root "$PROJECTS_AI_ROOT" "$@"; }
kimil() { _kimi_with_root "$LIFE_AI_ROOT" "$@"; }
kimio() { _kimi_with_root "$OBSIDIAN_AI_ROOT" "$@"; }
