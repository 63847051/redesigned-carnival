# 当前系统能力分析

**分析时间**: 2026-03-08 22:23:57

## 已安装的Skills

- **agent-browser**: description: A fast Rust-based headless browser automation CLI with Node.js fallback that enables AI agents to navigate, click, type, and snapshot pages via structured commands.
- **agent-team-orchestration**: Orchestrate multi-agent teams with defined roles, task lifecycles, handoff protocols, and review workflows. Use when: (1) Setting up a team of 2+ agents with different specializations, (2) Defining task routing and lifecycle (inbox → spec → build → review → done), (3) Creating handoff protocols between agents, (4) Establishing review and quality gates, (5) Managing async communication and artifact sharing between agents.
- **feishu-worklog**: 小蓝
- **github**: Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries.
- **notion**: description: Notion API for creating and managing pages, databases, and blocks.
- **obsidian**: description: Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli.
- **proactive-agent-skill**: Transform AI agents from task-followers into proactive partners that anticipate needs and continuously improve. Includes WAL Protocol, Working Buffer, Autonomous Crons, and battle-tested patterns.
- **self-improving**: description: Self-reflection + Self-criticism + Self-learning + Self-organizing memory. Agent evaluates its own work, catches mistakes, and improves permanently. Use this skill before starting work and after responding to the user.
- **summarize**: description: Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube).
- **tavily-search**: description: AI-optimized web search via Tavily API. Returns concise, relevant results for AI agents.
- **tencentcloud-lighthouse-skill**: description: Manage Tencent Cloud Lighthouse (轻量应用服务器) — auto-setup mcporter + MCP, query instances, monitoring & alerting, self-diagnostics, firewall, snapshots, remote command execution (TAT). Use when user asks about Lighthouse or 轻量应用服务器. NOT for CVM or other cloud server types.
- **tencent-docs**: description: 腾讯文档，提供完整的腾讯文档操作能力。当用户需要操作腾讯文档时使用此skill，包括：(1) 创建各类在线文档（智能文档、Word、Excel、幻灯片、思维导图、流程图）(2) 查询、搜索文档空间与文件 (3) 管理空间节点、文件夹结构 (4) 读取文档内容 (5) 编辑操作智能表。
- **weather**: description: Get current weather and forecasts (no API key required).

## 系统能力矩阵

### 进化能力
- ✅ 8步进化流程
- ✅ 4步自我改进
- ✅ 错误模式分析
- ✅ 自动记忆组织

### 持久化能力
- ✅ WAL Protocol
- ✅ SESSION-STATE管理
- ✅ working-buffer日志

### 学习能力
- ✅ 项目学习分离
- ✅ 领域学习分离
- ✅ 修正记录追踪

### 协作能力
- ✅ Agent团队编排
- ✅ 任务生命周期管理
- ✅ 质量检查流程

### 缺失能力
- ❌ 自主技能发现 ⭐
- ❌ 自动技能安装
- ❌ 技能质量评估

