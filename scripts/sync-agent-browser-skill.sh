#!/usr/bin/env sh

set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SKILL_DIR="$REPO_ROOT/skills/agent-browser"
BASE_URL="https://raw.githubusercontent.com/vercel-labs/agent-browser/main"
UPSTREAM_REPO="https://github.com/vercel-labs/agent-browser"
UPSTREAM_SHA=$(git ls-remote "$UPSTREAM_REPO.git" refs/heads/main | awk '{print $1}')
SYNC_DATE=$(date +%F)

mkdir -p "$SKILL_DIR/references" "$SKILL_DIR/templates"

fetch() {
    remote_path=$1
    local_path=$2
    curl -fsSL "$BASE_URL/$remote_path" -o "$local_path"
}

fetch "skills/agent-browser/SKILL.md" "$SKILL_DIR/SKILL.md"
fetch "skills/agent-browser/references/authentication.md" "$SKILL_DIR/references/authentication.md"
fetch "skills/agent-browser/references/commands.md" "$SKILL_DIR/references/commands.md"
fetch "skills/agent-browser/references/profiling.md" "$SKILL_DIR/references/profiling.md"
fetch "skills/agent-browser/references/proxy-support.md" "$SKILL_DIR/references/proxy-support.md"
fetch "skills/agent-browser/references/session-management.md" "$SKILL_DIR/references/session-management.md"
fetch "skills/agent-browser/references/snapshot-refs.md" "$SKILL_DIR/references/snapshot-refs.md"
fetch "skills/agent-browser/references/video-recording.md" "$SKILL_DIR/references/video-recording.md"
fetch "skills/agent-browser/templates/authenticated-session.sh" "$SKILL_DIR/templates/authenticated-session.sh"
fetch "skills/agent-browser/templates/capture-workflow.sh" "$SKILL_DIR/templates/capture-workflow.sh"
fetch "skills/agent-browser/templates/form-automation.sh" "$SKILL_DIR/templates/form-automation.sh"
fetch "LICENSE" "$SKILL_DIR/LICENSE.upstream"

cat >"$SKILL_DIR/UPSTREAM.md" <<EOF
# agent-browser 来源信息

- 来源仓库：$UPSTREAM_REPO
- 跟踪路径：\`skills/agent-browser/\`
- 跟踪分支：\`main\`
- 当前同步 SHA：\`$UPSTREAM_SHA\`
- 最近同步日期：\`$SYNC_DATE\`
- 上游许可证：Apache-2.0（见 \`LICENSE.upstream\`）

## 同步命令

\`\`\`bash
./scripts/sync-agent-browser-skill.sh
\`\`\`

## 约束

- 保持 \`SKILL.md\`、\`references/\`、\`templates/\` 与上游目录结构一致
- 不在同步脚本里引入额外依赖；仅使用 \`sh\`、\`curl\`、\`git\`、\`awk\`
- 若需要本地定制，优先新增配套文档，不直接改写上游镜像内容
EOF

chmod 755 "$SKILL_DIR/templates/"*.sh

echo "[OK] synced $SKILL_DIR from $UPSTREAM_REPO@$UPSTREAM_SHA"
