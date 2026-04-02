# 上游仓库更新报告（2026-04-02）

## 更新范围

- 更新时间：2026-04-02
- 更新方式：`git submodule update --remote`
- 后续处理：已执行 `uv run .agents/skills/update-upstream-repos/scripts/switch_updated_submodules_to_main.py`
- 覆盖仓库：`upstream/everything-claude-code`、`upstream/product-manager-skills`
- 最终状态：已变化的 submodule 已切回本地 `main`，`HEAD == origin/main`
- 证据来源：git diff、git log、上游 README/skills 文件

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | commit 数 | 结论 |
|------|--------|--------|-----------|------|
| `upstream/everything-claude-code` | `1abeff9` | `bf3fd69` | 6 | 新增 4 个 skill（含社交/内容工作流），改进安装可移植性 |
| `upstream/product-manager-skills` | `2a2f27c` | `4aa4196` | 2 | 新增产品感觉面试答题 skill，值得评估引入 |

## upstream/everything-claude-code

- 旧 SHA：`1abeff9be79ac0b1b06f87a04c57823e10d068ee`
- 新 SHA：`bf3fd69d2c93f699b6e1799951440f0f063cde6b`
- diff 统计：40 files changed, 1610 insertions(+), 205 deletions(-)

### Commit 列表

- `2026-04-02` `bf3fd69d` refactor: extract social graph ranking core
- `2026-04-01` `31525854` feat(skills): add brand voice and network ops lanes
- `2026-04-01` `8f636971` fix: port safe ci cleanup from backlog
- `2026-04-01` `9a6080f2` feat: sync the codex baseline and agent roles
- `2026-04-01` `dba5ae77` fix: harden install and codex sync portability
- `2026-04-01` `401966bc` feat: expand lead intelligence outreach channels

## upstream/product-manager-skills

- 旧 SHA：`2a2f27c71c562dd6b6797c8f4d224825d6005c7f`
- 新 SHA：`4aa4196c14873b84f5af7316e7f66328cb6dee4c`
- diff 统计：10 files changed, 568 insertions(+), 17 deletions(-)

### Commit 列表

- `2026-04-02` `4aa4196` Add product-sense-interview-answer skill (#4)
- `2026-03-31` `dc8dec7` Add product sense interview answer skill

## upstream/everything-claude-code 详情

### 新增 Skill

| Skill | 类型 | 用途 |
|-------|------|------|
| `brand-voice` | 工作流 | 从真实素材构建可复用的品牌声音 profile，用于内容、外联和社交工作流 |
| `connections-optimizer` | 工作流 | X/LinkedIn 社交网络重组：清理、扩展、外联草稿生成 |
| `social-graph-ranker` | 组件 | 社交图谱桥接价值评分（从 `lead-intelligence` 提取） |
| `manim-video` | 工作流 | 数学动画视频生成（含示例代码 `network_graph_scene.py`） |

### 调整

- `content-engine`、`crosspost`、`x-api`、`lead-intelligence` 等 skill 更新以配合新增工作流
- `lead-intelligence` 重构：社交图谱排名核心提取为独立 `social-graph-ranker`

### 修复

- `dba5ae77` harden install and codex sync portability - 提升安装和 Codex 同步的可移植性
- `8f636971` port safe ci cleanup from backlog - CI 清理逻辑

## upstream/product-manager-skills 详情

### 新增 Skill

| Skill | 类型 | 用途 |
|-------|------|------|
| `product-sense-interview-answer` | Component | PM 产品感觉面试答题框架：六段式回答结构（澄清→理由→目标→细分→痛点→方案） |

包含完整示例（Improve YouTube）和答题模板 `template.md`。

## 值得关注

### 1. everything-claude-code 新增社交/内容工作流套件

- **证据**：`brand-voice/SKILL.md`、`connections-optimizer/SKILL.md`、`31525854` commit
- **为什么重要**：这是一套完整的个人品牌建设工具链，从声音定义到社交网络优化再到内容发布。与本项目现有的 `work-market-research` 等 skill 形成互补。
- **建议动作**：评估是否引入到 `skills/` 目录，特别对于需要运营 X/LinkedIn 的用户有价值。

### 2. product-manager-skills 新增面试答题 skill

- **证据**：`skills/product-sense-interview-answer/SKILL.md`、`4aa4196` commit
- **为什么重要**：PM 面试准备是高频需求，该 skill 提供结构化答题框架（六段式），包含完整示例和模板。
- **建议动作**：考虑引入到 `skills/` 或作为 `upstream/product-manager-skills` 子模块持续跟踪。

### 3. everything-claude-code 安装可移植性改进

- **证据**：`dba5ae77` commit "fix: harden install and codex sync portability"
- **为什么重要**：可能修复了跨平台安装问题，对本项目用户有潜在收益。
- **建议动作**：如有安装问题可参照上游更新，暂不主动修改本项目的 `ce` CLI。

## 后续动作

- [ ] 评估是否引入 `brand-voice`、`connections-optimizer`、`product-sense-interview-answer` 到 `skills/`
- [ ] 如有社交/内容运营需求，测试上游 `brand-voice` + `connections-optimizer` 工作流
- [ ] 下次同步时继续使用 `switch_updated_submodules_to_main.py` 确保分支正确
- [ ] 监控 `everything-claude-code` 安装流程改进是否影响本项目 `ce` CLI 的兼容性
