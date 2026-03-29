# agent-browser 来源信息

- 来源仓库：https://github.com/vercel-labs/agent-browser
- 跟踪路径：`skills/agent-browser/`
- 跟踪分支：`main`
- 当前同步 SHA：`dc26ff76679a1f3b0cf22651d06d79e40dfe88fe`
- 最近同步日期：`2026-03-29`
- 上游许可证：Apache-2.0（见 `LICENSE.upstream`）

## 同步命令

```bash
./scripts/sync-agent-browser-skill.sh
```

## 约束

- 保持 `SKILL.md`、`references/`、`templates/` 与上游目录结构一致
- 不在同步脚本里引入额外依赖；仅使用 `sh`、`curl`、`git`、`awk`
- 若需要本地定制，优先新增配套文档，不直接改写上游镜像内容
