# MEMORY.md — 长期记忆

## 关于幸运小行星

- **姓名**: 幸运小行星
- **角色**: 技术开发者 / 项目管理者
- **平台**: 腾讯云轻量服务器
- **系统**: OpenCloudOS 9
- **OpenClaw**: AI 代理框架 (2026.3.13)
- **时区**: GMT+8

---

## ⭐ 永久规则（2026-03-22 固化）

### 角色定位和工作机制

**大领导（主控 Agent）**：
- ✅ 负责和幸运小行星**实时互动聊天**
- ✅ 负责**汇报工作进度**
- ✅ 负责**分配任务给团队成员**
- ✅ 负责**监督执行质量**
- ✅ 负责**汇总成果反馈**
- ❌ **不做具体执行工作**（代码、日志、设计）

**专业 Agent 团队**：

1. **💻 小新（技术支持专家）**
   - 职责：所有编程和技术相关任务
   - 模型：`opencode/minimax-m2.5-free`（免费代码专家）⭐
   - **重要**: 这是 opencode Agent 自己的免费模型
   - **详细文档**: `/root/.openclaw/workspace/docs/OPENCODE-MODELS.md`
   - 触发词：代码、爬虫、数据、API、前端、脚本、开发、编程

2. **📋 小蓝（工作日志管理专家）**
   - 职责：工作日志记录和管理
   - 模型：glmcode/glm-4.5-air（免费快速）
   - 触发词：日志、记录、工作、任务、进度、统计、汇总
   - 当前项目：蓝色光标上海办公室工作日志

3. **🏠 室内设计专家**
   - 职责：所有室内设计相关任务
   - 模型：glmcode/glm-4.6（中文优化）
   - 触发词：设计、图纸、平面图、立面图、天花、地面、排砖、柜体

**沟通隔离规则**：
- ✅ 只有大领导（我）和幸运小行星沟通
- ❌ 专业 Agent 不直接和幸运小行星沟通
- ✅ 所有结果通过大领导汇总后反馈

**工作流程**：
```
幸运小行星 → 大领导 → 分析任务 → 分配给专家 → 执行 → 汇报给大领导 → 反馈给幸运小行星
```

**核心理念**："专业的事交给专业的人"

**永久固化**：
- ✅ IDENTITY.md - 我的身份和团队
- ✅ AGENTS.md - 永久规则
- ✅ MEMORY.md - 长期记忆
- ✅ 每次会话启动时自动加载

---

## 2026-03-22 重大更新：角色定位固化 🎯

### 🎉 核心改进

**版本**: v5.25.0 → v5.25.0
**更新时间**: 2026-03-22 09:30

**关键决策**：
- ✅ 明确大领导职责：**沟通、分配、监督、汇报**
- ✅ 新增沟通隔离规则：**唯一沟通渠道**
- ✅ 永久固化到 IDENTITY.md、AGENTS.md、MEMORY.md

**原因**：
- 避免混乱：多个 Agent 同时回复会让用户困惑
- 保证质量：大领导负责质量把关和结果汇总
- 清晰职责：我负责沟通，他们负责执行

**实施**：
- ✅ 更新 IDENTITY.md（4082 字符）
- ✅ 更新 AGENTS.md（8633 字符）
- ✅ 更新 MEMORY.md（本文件）
- ✅ 每次会话启动时自动加载

**承诺**：永久遵守这套机制

---

## 2026-03-22 QMD Memory Search 完整部署 🚀

### 安装成功

**方案**: Groq API（方案 B）
**版本**: @tobilu/qmd v2.0.1
**状态**: ✅ 完整部署完成

**核心功能**：
- ✅ 全文搜索（BM25）- < 1 秒
- ✅ 语义搜索（Groq API）- 2-5 秒
- ✅ 38 个文件已索引
- ✅ Memory Skill 已创建
- ✅ 软链接已创建（全局可用）

**命令**：
- `qmd-search "关键词"` - 搜索记忆
- `qmd-get memory/file.md` - 查看文件
- `qmd-multi "memory/**/*.md"` - 批量查看

**文档**：
- 安装报告：`.learnings/improvements/qmd-installation-report-20260322.md`
- Skill 文档：`skills/qmd-memory/SKILL.md`
- 软链接报告：`skills/qmd-memory/SYMLINK-REPORT.md`

**优势**：
- 命令长度从 70 字符 → 10 字符（减少 86%）
- 全局可用（任何目录）
- 更好的集成（Skills、脚本、alias）

---

## 2026-03-17 系统升级到 v5.16.0 🚀

### 🎉 重大更新

**版本**: v5.13.0 → v5.16.0（Git 硬重置）

**核心亮点**：
- ✅ **65% Token 节省**（子 Agent: 4300 → 1500）
- ✅ **33-40% 响应速度提升**
- ✅ **Clawith 集成**（on_message + Relationship）
- ✅ **AutoSkill + XSKILL 系统**

### 📊 升级过程

**遇到的问题**：
1. 尝试升级到 v5.13（使用后台脚本，超时失联 3 小时）
2. 发现 GitHub 已有 v5.16（版本落后）
3. 推送冲突（本地和远程分歧）

**最终解决方案**：
```bash
git fetch origin main
git reset --hard origin/main
```

**结果**：
- ✅ 成功升级到 v5.16.0
- ✅ 保留了 Golutra 研究项目
- ✅ Gateway 运行正常
- ✅ 获得所有新功能

---

## 2026-03-15 Golutra 研究与系统进化 🚀

### 🎯 任务：学习 golutra 项目并进化大领导系统

**研究时间**: 2026-03-15
**研究版本**: golutra v1.0
**研究者**: 小新（技术支持专家）

### 📊 Golutra 项目深度分析

**技术栈**:
- Frontend: Vue 3
- Backend: Rust
- Framework: Tauri (桌面应用)
- Platforms: Windows, macOS

**核心特性**:
1. ✅ 多 Agent 并行执行（不限数量）
2. ✅ 自动化编排（从分析到部署）
3. ✅ CLI 兼容（Claude, Gemini, Codex, OpenCode, Qwen, OpenClaw）
4. ✅ 隐形终端与上下文感知
5. ✅ 可视化界面（Agent Grid + 实时日志）
6. ✅ 自组织 AI 团队概念

---

## 当前运行状态

### 核心服务
- **飞书 Gateway**: ✅ 运行中
- **EvoMap 节点**: node_3cfe84b91a567bd4, 声誉 54.35, 积分 500
- **系统健康**: Gateway 重启 5 次, 内存使用 33%
- **系统版本**: v5.25.0（角色定位固化版）

### 重要项目
- **🧬 双轨进化系统**: Self-Improvement + EvoMap Evolution
- **🛡️ 防护拯救系统**: 6 层崩溃防护
- **📱 飞书 Gateway 管理**: 自动监控和恢复
- **🧠 PAI 学习系统**: 学习信号捕获 + 每日报告 + 可视化仪表板
- **🎯 项目管理**: 蓝色光标上海办公室工作日志
- **📡 QMD Memory Search**: 快速记忆检索（38 个文件已索引）
- **👥 角色定位固化**: 大领导 + 专业 Agent 团队

---

## 工作偏好

### 沟通风格
- **简洁直接**: 避免冗余,直击要点
- **平台**: 飞书（不支持 Markdown 表格）
- **格式**: 小标题、清晰分隔、项目符号

### 工作领域
- 数据分析、数据采集、爬虫开发
- 前端 UI 设计、文档编写
- 项目管理、工作日志

---

## 技能掌握

### 已掌握技能
1. **自主项目管理** - 去中心化协调, STATE.yaml 模式
2. **EvoMap 进化资产市场** - 发布 Gene/Capsule/Event
3. **动态仪表板** - 可视化监控,实时图表
4. **飞书 Gateway 管理** - 配置、监控、恢复
5. **系统监控** - 健康检查、资源监控
6. **团队协作** - 室内设计专家 + 技术支持专家 + 工作日志专家

### ClawHub 技能（18 个）
- agent-browser, ai-meeting-notes, obsidian
- automation-workflows, daily-rhythm, para-second-brain
- reflect-learn, self-improving-agent, stock-monitor-skill
- airtable-automation, agent-builder, tavily-search
- summarize, find-skills, github, notion, weather

---

## 🚨 重要教训

### 系统升级事件 (2026-03-17) ✅ 已解决
**v5.13 → v5.16 升级，最终通过 Git 硬重置成功**

- **问题**: 尝试升级到 v5.13，发现 GitHub 已有 v5.16
- **症状**: 升级超时导致 3 小时失联
- **最终解决**: Git 硬重置到 origin/main
- **教训**:
  - ❌ 不要用后台运行升级脚本
  - ❌ 不要使用复杂的升级脚本
  - ✅ 定期 git pull 保持版本同步
  - ✅ 遇到问题用 Git 硬重置快速恢复

---

## 系统配置

### 服务器信息
- **公网 IP**: 43.134.63.176
- **内网 IP**: 10.3.0.8
- **开放端口**: 80 (HTTP), 18789 (Gateway), 22 (SSH)

### 重要文件位置
- **配置**: /root/.openclaw/openclaw.json
- **凭证**: /root/.openclaw/credentials/feishu-pairing.json
- **日志**: /root/.openclaw/logs/
- **工作区**: /root/.openclaw/workspace/
- **备份**: /root/.openclaw/backups/

### 技术栈
- **Node.js**: v22.22.0
- **操作系统**: OpenCloudOS (Linux 6.6.117-45.1.oc9.x86_64)
- **AI 框架**: OpenClaw 2026.3.13
- **默认模型**: GLM-4.7 (glmcode)

---

## 成功案例

### QMD Memory Search 部署 (2026-03-22)
- **任务**: 快速记忆检索系统
- **完成**: Groq API 配置 + 38 个文件索引 + 全局命令
- **结果**: ✅ 完整部署，搜索速度 < 1 秒

### 角色定位固化 (2026-03-22)
- **任务**: 明确大领导和专业 Agent 的职责
- **完成**: 沟通隔离规则 + 永久固化到核心文档
- **结果**: ✅ 规则已固化，每次会话自动加载

### 飞书 Gateway 自动恢复
- **问题**: Gateway 停止
- **解决**: 创建安全重启脚本
- **结果**: 自动恢复,带飞书通知

---

## 待办事项

### 优先级高
- 发布 EvoMap v2 资产包（等待 Hub 恢复）
- 优化仪表板（添加更多指标、图表）

### 优先级中
- 学习更多 GitHub awesome-openclaw-usecases
- 探索更多 EvoMap 功能（任务、Swarm、Recipe）
- 深化 PAI 学习（三层记忆系统）

### 优先级低
- 提升 EvoMap 声誉到 60+
- 认领和完成更多任务

---

## 工作团队（Skill 隔离规则系统 v1.2）

**配置文件**: `/root/.openclaw/workspace/agents/skill-isolation-rules.md`

---

## 💰 模型分配策略 (70% 免费)

### 免费模型 (70% 任务)
- **GLM-4.5-Air** - 超快速响应、工作日志记录
- **GLM-4.6** - 中文任务、简单设计
- **opencode/minimax-m2.5-free** - 代码编写、技术支持
- **Gemini 2.5 Flash** - 日常对话、问答

### 主模型 (30% 任务)
- **GLM-4.7** - 数据分析、复杂设计
- **GLM-5** - 关键决策、战略规划

---

## 备份和恢复

### 自动备份
- **位置**: /root/.openclaw/backups/daily/YYYYMMDD/
- **时间**: 每日凌晨 2 点（如果配置了 cron）
- **保留**: 最近 7 天

### 手动备份脚本
- **快速备份**: `bash /root/.openclaw/workspace/scripts/backup-before-update.sh`
- **安全升级**: `bash /root/.openclaw/workspace/scripts/simple-upgrade-v5.16.sh`
- **恢复配对**: `bash /root/.openclaw/workspace/scripts/restore-pairing.sh <备份目录>`

---

*最后更新: 2026-03-22*
*状态: ✅ v5.25.0 运行正常*
*核心改进: 角色定位固化 + 沟通隔离规则*
