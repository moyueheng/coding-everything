# Product Manager Skills 迁移待办

## 目标

将 `upstream/product-manager-skills` 中高价值、低耦合的 PM skill 分批引入本仓库自有配置层，采用本仓库命名规范（`work-` 前缀），避免跨模块隐式耦合。

源仓库：`upstream/product-manager-skills`

## 迁移批次

### Batch 1（优先，先迁移）

1. `problem-statement` -> `work-problem-statement`
2. `jobs-to-be-done` -> `work-jobs-to-be-done`
3. `user-story` -> `work-user-story`
4. `user-story-splitting` -> `work-user-story-splitting`
5. `user-story-mapping` -> `work-user-story-mapping`
6. `prd-development` -> `work-prd-development`
7. `prioritization-advisor` -> `work-prioritization-advisor`
8. `roadmap-planning` -> `work-roadmap-planning`
9. `discovery-interview-prep` -> `work-discovery-interview-prep`
10. `opportunity-solution-tree` -> `work-opportunity-solution-tree`

说明：以上 10 个覆盖问题定义、需求拆分、文档产出与路线图规划，适合作为 PM 基线能力包。

### Batch 2（次优先，受控迁移）

1. `discovery-process` -> `work-discovery-process`
2. `problem-framing-canvas` -> `work-problem-framing-canvas`
3. `positioning-statement` -> `work-positioning-statement`
4. `positioning-workshop` -> `work-positioning-workshop`
5. `press-release` -> `work-press-release`
6. `recommendation-canvas` -> `work-recommendation-canvas`

说明：偏策略与工作坊场景，建议在 Batch 1 稳定后再引入。

### Batch 3（按需迁移）

1. 财务与增长：
   - `saas-revenue-growth-metrics`
   - `saas-economics-efficiency-metrics`
   - `business-health-diagnostic`
   - `finance-based-pricing-advisor`
2. 领导力：
   - `director-readiness-advisor`
   - `vp-cpo-readiness-advisor`
   - `executive-onboarding-playbook`
3. 战略分析：
   - `pestel-analysis`
   - `tam-sam-som-calculator`
   - `company-research`

说明：场景依赖更强，不作为默认安装集。

## 暂不迁移项

1. `app/`（Streamlit beta）
2. `scripts/` 打包/发布工具链

原因：
- 避免引入额外重型运行栈与维护负担
- 当前目标是 skill 内容复用，不是复制上游工具链

## 迁移约束

1. 严格保留来源与许可信息（上游仓库许可证为 `CC BY-NC-SA 4.0`）
2. 每次迁移仅处理一个小批次，避免大规模改动
3. 迁移后必须补齐本仓库文档入口（`AGENTS.md`/相关 README）

