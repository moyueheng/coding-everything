# 上游仓库更新报告

**日期**: 2026-03-19  
**执行者**: update-upstream-repos skill

---

## 变更概览

| 仓库 | 旧 SHA | 新 SHA | Commit 数 | 变更文件 |
|------|--------|--------|-----------|----------|
| `upstream/product-manager-skills` | `0c59857` | `2a2f27c` | 5 | 3 files changed, 633 insertions(+), 6 deletions(-) |

**其他仓库**: superpowers, everything-claude-code, ui-ux-pro-max-skill, humanizer-zh, obsidian-skills 当前均为最新版本，无更新。

---

## upstream/product-manager-skills 详情

### Commit 列表

| 日期 | SHA | 说明 |
|------|-----|------|
| 2026-03-18 | `2a2f27c` | Update README: mark Claude Code plugin marketplace as now available |
| 2026-03-18 | `b301d29` | Update CLAUDE.md: mark PR #2 markphelps as merged |
| 2026-03-18 | `d1fa484` | Merge pull request #2 from markphelps/feat/claude-code-plugin-marketplace |
| 2026-03-17 | `1ee9131` | chore: update marketplace.json |
| 2026-03-15 | `a30cfe1` | Add Claude Code plugin marketplace for skill distribution |

### 主要变更

#### 1. 新增 Claude Code Plugin Marketplace 支持

新增 `.claude-plugin/marketplace.json`，包含 **46 个 PM skills** 的完整元数据：

- **discovery** (10): company-research, customer-journey-map, discovery-interview-prep, jobs-to-be-done, lean-ux-canvas, opportunity-solution-tree, problem-framing-canvas, problem-statement, proto-persona
- **strategy** (9): pestel-analysis, positioning-statement, positioning-workshop, prd-development, press-release, prioritization-advisor, product-strategy-session, roadmap-planning, tam-sam-som-calculator, eol-message
- **delivery** (7): epic-breakdown-advisor, epic-hypothesis, storyboard, user-story, user-story-mapping, user-story-mapping-workshop, user-story-splitting
- **finance** (6): acquisition-channel-advisor, business-health-diagnostic, feature-investment-advisor, finance-based-pricing-advisor, finance-metrics-quickref, saas-economics-efficiency-metrics, saas-revenue-growth-metrics
- **career** (4): altitude-horizon-framework, director-readiness-advisor, executive-onboarding-playbook, vp-cpo-readiness-advisor
- **ai** (5): ai-shaped-readiness-advisor, context-engineering-advisor, pol-probe, pol-probe-advisor, recommendation-canvas
- **meta** (2): workshop-facilitation, skill-authoring-workflow

每个 skill 包含：`name`, `source`, `description`, `category`, `tags`, `strict` 字段。

#### 2. 文档更新

- **README.md**: 添加 Claude Code Plugin Marketplace badge，更新安装说明
  ```bash
  /plugin marketplace add deanpeters/Product-Manager-Skills
  /plugin install jobs-to-be-done@pm-skills
  ```
- **CLAUDE.md**: 更新 PR #2 合并状态，标记 marketplace.json 已进入 main

---

## 值得关注

### ✅ 推荐吸收

| 内容 | 说明 | 适用场景 |
|------|------|----------|
| `marketplace.json` 格式 | Claude Code Plugin 标准格式，可作为其他 skill 发布到 marketplace 的模板 | 本项目 skills 若需发布到 Claude Code marketplace |
| v0.75 Pedagogic-First 理念 | 更新强调 skill 既要增强 agent 能力，也要教育人类 PM | 编写新 skill 时的设计原则参考 |

### 📋 后续行动建议

1. **无紧急同步需求**: 本次更新仅涉及 product-manager-skills 自身的 marketplace 配置，不影响本项目现有 skill 功能
2. **可作为参考**: 若未来需要将本项目的 skills 发布到 Claude Code marketplace，可参考 `marketplace.json` 的格式和分类方式
3. **技能迁移继续**: [PM Skills 迁移待办](./docs/product-manager-skills-migration-backlog.md) 可继续按原计划进行，无需因本次更新调整

---

## 验证

```bash
# submodule 状态确认
git submodule status upstream/product-manager-skills
# +2a2f27c71c562dd6b6797c8f4d224825d6005c7f upstream/product-manager-skills (heads/main)

# 文件变更确认
git diff --submodule=short HEAD
# diff --git a/upstream/product-manager-skills b/upstream/product-manager-skills
# index 0c59857..2a2f27c 160000
```

---

*报告由 update-upstream-repos skill 自动生成*
