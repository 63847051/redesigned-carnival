# MEMORY.md — 长期记忆

## 关于幸运小行星

- **姓名**: 幸运小行星
- **角色**: 技术开发者 / 项目管理者
- **平台**: 腾讯云轻量服务器
- **系统**: OpenCloudOS 9
- **OpenClaw**: AI 代理框架 (2026.2.26)
- **时区**: GMT+8

---

## 2026-03-13 重要更新

### 🚀 系统升级到 v5.10
- **版本**: 5.10（API 数据完整性保障）
- **升级时间**: 2026-03-13 08:20
- **新增功能**: API 分页处理模式 + 数据完整性检查清单

### 📡 API 数据完整性保障（新增 Level 7）
- **设计模式**: DP-API-001（API 分页处理模式）
- **检查清单**: CL-API-001（API 数据获取检查清单）
- **文档**:
  - `.learnings/design-patterns/api-pagination-pattern.md`
  - `.learnings/checklist/api-data-fetch-checklist.md`

### 🐛 错误修复
- **问题**: 飞书数据读取不完整（只读 10 条，实际 40 条）
- **原因**: 没有处理 API 分页
- **解决**:
  1. 创建 API 分页处理模式
  2. 创建 4 阶段检查清单
  3. 整合到 SOUL.md
  4. 深度学习和改进

### 🔐 安全改进
- **修复**: `shield-guard-coordinator.sh` API Key 泄露
- **措施**: 移除明文密钥，改用环境变量
- **推送**: 成功推送到 GitHub（分支 master）

## 2026-03-12 重要更新

### 🎉 OpenClaw Control Center 安装成功
- **位置**: `/root/.openclaw/control-center`
- **外网访问**: http://43.134.63.176:4310
- **状态**: ✅ 运行中
- **模式**: 只读（安全）

### 📦 GitHub 备份仓库
- **默认仓库**: https://github.com/63847051/redesigned-carnival
- **完整备份**: 473 个文件，906MB
- **API Keys**: 已清理为占位符

---

## 当前运行状态

### 核心服务
- **飞书 Gateway**: ✅ 运行中
- **EvoMap 节点**: node_3cfe84b91a567bd4, 声誉 54.35, 积分 500
- **系统健康**: Gateway 重启 5 次, 内存使用 57%
- **系统版本**: v5.10（API 数据完整性保障）

### 重要项目
- **🧬 双轨进化系统**: Self-Improvement + EvoMap Evolution
- **🛡️ 防护拯救系统**: 6 层崩溃防护
- **📱 飞书 Gateway 管理**: 自动监控和恢复
- **🧠 PAI 学习系统**: 学习信号捕获 + 每日报告 + 可视化仪表板（2026-03-05 集成）
- **🎯 项目管理**: 蓝色光标上海办公室工作日志（40 条任务，77.5% 完成率）
- **👥 独立子 Agent 系统**: Skill 隔离规则系统 v1.0 (2026-03-04 实施)
- **📡 API 数据完整性**: 分页处理模式 + 检查清单（2026-03-13 新增）

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
6. **团队协作** - 室内设计专家 + 技术支持专家

### ClawHub 技能（18 个）
- agent-browser, ai-meeting-notes, obsidian
- automation-workflows, daily-rhythm, para-second-brain
- reflect-learn, self-improving-agent, stock-monitor-skill
- airtable-automation, agent-builder, tavily-search
- summarize, find-skills, github, notion, weather

### PAI 学习系统（2026-03-05 深化版 v2.0）🧠
- ✅ **v1.0 基础版**（2026-03-05 早期）
  - 学习信号捕获系统（自动记录任务数据）
  - 每日分析报告系统（自动生成学习报告）
  - 可视化仪表板系统（实时展示学习曲线）
  - 集成到心跳系统（完全自动化）

- ✅ **v2.0 深化版**（2026-03-05 深化）
  - **三层记忆系统**（Hot/Warm/Cold 分层存储）
  - **智能分析引擎**（成功模式、失败根因、复杂度趋势）
  - **智能建议系统**（优化建议、风险预警、行动计划）
  - **完整工作流**（一键运行所有组件）

- 📍 访问地址: http://43.134.63.176/pai-dashboard/
- 📍 配置文件: `/root/.openclaw/workspace/.pai-learning/CONFIG.md`
- 📍 脚本目录: `/root/.openclaw/workspace/scripts/pai-*.sh`
- 🎯 三步战略: 1. 集成到日常工作（✅）+ 2. 独立 Agent 系统（⏳）+ 3. 深化 PAI 学习（🔄 阶段 1 完成）

---

## 🚨 重要教训

### 升级失败事件 (2026-03-01)
**OpenClaw 2026.2.15 → 2026.2.26 升级导致失联 20 分钟**

- **原因**: 新版本新增 Control UI 安全校验,配置不兼容
- **教训**: 升级前必须检查版本变更日志、验证配置兼容性
- **防护**: 已创建安全升级脚本 (`scripts/safe-upgrade.sh`)
- **记忆**: `.learnings/errors/upgrade-failure-20260301.md`

### 脚本文件缺失 (2026-03-02)
**备份脚本在配置前被调用**

- **原因**: 文档提到脚本但尚未创建
- **教训**: 配置文档和实际文件要同步
- **解决**: 已创建所有备份和升级脚本

---

## 学习路径

### EvoMap 进化资产市场

#### Level 1: 连接和观察 ✅ (100%)
- ✅ 注册 EvoMap 节点
- ✅ 安装 Evolver 客户端
- ✅ 学习 EvoMap 文档
- ✅ 了解 GEP-AA2A 协议
- ✅ 准备好 v2 资产包

#### Level 2: 发布资产包 ⏳ (0%)
- ⏳ 等待 EvoMap Hub 恢复
- ⏳ 发布 v2 资产包

#### Level 3: 赚取积分 ⏳ (0%)
- ⏳ 认领和完成任务
- ⏳ 提升声誉到 60+

---

## 系统配置

### 服务器信息
- **公网 IP**: 43.134.63.176
- **内网 IP**: 10.3.0.8
- **开放端口**: 80 (HTTP), 18789 (Gateway), 22 (SSH)

### 重要文件位置
- **配置**: /root/.openclaw/openclaw.json
- **凭证**: /root/.openclaw/credentials/feishu-pairing.json ⭐⭐⭐⭐⭐
- **日志**: /root/.openclaw/logs/
- **工作区**: /root/.openclaw/workspace/
- **备份**: /root/.openclaw/backups/

### 技术栈
- **Node.js**: v22.22.0
- **操作系统**: OpenCloudOS (Linux 6.6.117-45.1.oc9.x86_64)
- **AI 框架**: OpenClaw 2026.2.26
- **默认模型**: GLM-4.7 (glmcode)

---

## 成功案例

### 飞书 Gateway 自动恢复
- **问题**: Gateway 停止
- **解决**: 创建安全重启脚本
- **结果**: 自动恢复,带飞书通知

### 可视化仪表板部署
- **问题**: 无法外部访问
- **解决**: 切换到 80 端口,配置云安全组
- **结果**: 成功访问 http://43.134.63.176

### EvoMap 节点注册
- **问题**: 新节点注册
- **解决**: 生成唯一 node_id
- **结果**: 成功,声誉 54.35, 积分 500

### 蓝色光标项目接入
- **任务**: 飞书云文档工作日志管理
- **解决**: 读取多维表格,10 条记录
- **状态**: ✅ 成功接入

### PAI 学习系统集成 (2026-03-05)
- **任务**: 集成 PAI 学习系统到日常工作
- **完成**: 学习信号捕获 + 每日报告 + 可视化仪表板
- **结果**: ✅ 完整集成，系统已启用

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

## 工作团队（Skill 隔离规则系统 v1.0）

### 主控 Agent（大领导 🎯）
- **职责**: 任务分配和监督
- **理念**: "专业的事交给专业的人"
- **模型**: GLM-4.7 (主控决策)
- **隔离系统**: 触发词检测 + 角色边界 + 越界转发

### 专业团队成员（2026-03-04 升级）

- 🏠 **室内设计专家**
  - **职责**: 所有室内设计相关任务
  - **模型**: GLM-4.7 (中文优化,适合设计)
  - **隔离**: 只处理设计任务,不处理代码或日志
  - **触发词**: 设计、图纸、平面图、立面图、天花、地面、排砖、柜体、会议室

- 💻 **技术支持专家**
  - **职责**: 编程和技术相关任务
  - **模型**: GPT-OSS-120B (免费,代码专家)
  - **隔离**: 只处理技术任务,不处理设计或日志
  - **触发词**: 代码、爬虫、数据、API、前端、脚本、开发、编程

- 📋 **小蓝 (工作日志管理专家)**
  - **职责**: 记录、更新、跟踪工作日志
  - **模型**: GLM-4.5-Air (免费,快速响应)
  - **隔离**: 只处理日志任务,不处理设计或代码
  - **触发词**: 日志、记录、工作、任务、进度、统计、汇总
  - **飞书表格**: 蓝色光标上海办公室工作日志
  - **app_token**: BISAbNgYXa7Do1sc36YcBChInnS
  - **table_id**: tbl5s8TEZ0tKhEm7
  - **字段**: 内容、创建日期、完成时间、备注、附件、项目状态、项目类型、优先级别

**配置文件**: `/root/.openclaw/workspace/agents/skill-isolation-rules.md`
**实施报告**: `/root/.openclaw/workspace/IMPLEMENTATION-REPORT.md`

## 💰 模型分配策略 (70% 免费)

### 免费模型 (70% 任务)
- **GLM-4.5-Air** - 超快速响应、工作日志记录
- **GLM-4.6** - 中文任务、简单设计
- **GPT-OSS-120B** (OpenRouter) - 代码编写、技术支持
- **Gemini 2.5 Flash** - 日常对话、问答

### 主模型 (30% 任务)
- **GLM-4.7** - 数据分析、复杂设计
- **GLM-5** - 关键决策、战略规划

### 完整策略文档
- `/root/.openclaw/workspace/.learnings/design-patterns/model-allocation-rules-v2.md`
- `/root/.openclaw/workspace/.learnings/design-patterns/free-llm-api-resources.md`

---

## 备份和恢复

### 自动备份
- **位置**: /root/.openclaw/backups/daily/YYYYMMDD/
- **时间**: 每日凌晨 2 点（如果配置了 cron）
- **保留**: 最近 7 天

### 手动备份脚本
- **快速备份**: `bash /root/.openclaw/workspace/scripts/backup-before-update.sh`
- **安全升级**: `bash /root/.openclaw/workspace/scripts/safe-upgrade.sh`
- **恢复配对**: `bash /root/.openclaw/workspace/scripts/restore-pairing.sh <备份目录>`

### 心跳和监控
- **心跳进化**: `bash /root/.openclaw/workspace/scripts/heartbeat-evolution.sh`
- **兼容性检查**: `bash /root/.openclaw/workspace/scripts/check-upgrade-compatibility.sh`
- **PAI 学习**: `bash /root/.openclaw/workspace/scripts/pai-*.sh`

---

*最后更新: 2026-03-05*
*状态: ✅ 运行正常*
*PAI 学习系统: 🧠 已启用*