# MEMORY.md — 长期记忆

## 关于幸运小行星

- **姓名**: 幸运小行星
- **角色**: 技术开发者 / 项目管理者
- **平台**: 腾讯云轻量服务器
- **系统**: OpenCloudOS 9
- **OpenClaw**: AI 代理框架 (2026.2.26)
- **时区**: GMT+8

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
7. ✅ 统一 Agent 接口协议
8. ✅ 深度记忆层设计

**设计哲学**:
- 不替代现有工具，而是增强和编排它们
- 从"一个人 + 一个编辑器"进化为"一个人 + AI 军团"
- 计划进化为"自组织 AI 团队"，效率提升 30%+

### 🎓 提取的核心设计模式

**DP-GO-001: CLI 兼容层设计模式**
- 问题：如何在不改变用户习惯的前提下增强 CLI 工具？
- 解决：包装器模式 + 上下文注入 + 结果增强

**DP-GO-002: 并行执行编排模式**
- 问题：如何实现真正的并行执行而非串行切换？
- 解决：async/await + join_all + 结果自动聚合

**DP-GO-003: 提示词注入模式**
- 问题：如何在可视化界面中直接控制 Agent？
- 解决：提示词作为特殊指令注入终端流

**DP-GO-004: 自组织团队协议**
- 问题：如何按需组建 AI 团队？
- 解决：任务复杂度分析 + 自动创建 Agent + 动态分配角色

### 📋 大领导系统 v5.13.0 进化方案

**Phase 1: 架构优化（并行执行增强）**
- 并行执行编排器（ParallelExecutionOrchestrator）
- 任务优先级队列（PriorityTaskQueue）
- 结果自动聚合（ResultCollector）
- 预期效率提升: 40%

**Phase 2: 可视化增强（Web UI）**
- Vue 3 前端框架
- WebSocket 实时通信
- Agent 状态实时展示
- 日志流式更新
- 移动端适配

**Phase 3: 自组织能力（动态 Agent 创建）**
- 任务复杂度分析器（TaskComplexityAnalyzer）
- 动态 Agent 生成器（DynamicAgentGenerator）
- 自组织协议（SelfOrganizationProtocol）
- 按需组建 AI 团队

**Phase 4: 深度记忆（跨 Agent 共享）**
- 分布式记忆层（DistributedMemoryLayer）
- 知识毕业机制（KnowledgeGraduationSystem）
- 跨任务推理引擎（CrossTaskReasoningEngine）
- 跨 Agent 知识沉淀

### 📂 研究文档

**位置**: `/root/.openclaw/workspace/projects/golutra-study/`

1. **GOLUTRA_STUDY.md** (5707 字符)
   - 项目深度分析
   - 技术架构研究
   - 核心特性提取
   - 与大领导系统对比

2. **EVOLUTION_PLAN_V5.13.md** (13956 字符)
   - 4 个 Phase 详细方案
   - 技术实现方案
   - 预期成果和指标

3. **ROADMAP.md** (9558 字符)
   - 12 周实施计划
   - 每周任务清单
   - 里程碑和检查点

### 🎯 系统更新

**SOUL.md 更新到 v5.13.0**:
- 版本：5.13.0（Golutra 进化版）
- 新增 Level 9: Golutra 启发进化
- 新增 4 个核心设计模式
- 新增 4 个最佳实践
- 更新进化成果统计

**预期效率提升**: 30%+

**实施时间**: 12 周（3 个月）
**预计完成**: 2026-06-15

---

## 2026-03-13 晚间更新

### 🎉 新增工具和项目
1. **微信文章读取工具** ✅
   - wechat-article-reader（Python，快速导出）
   - wxmp-reader（浏览器自动化，支持截图）
   - 已成功导出 3 篇文章

2. **AI Team Dashboard** ✅
   - 位置: `/root/.openclaw/workspace/ai-team-dashboard`
   - 访问: http://43.134.63.176:3800
   - 状态: 运行中

3. **进化学习系统** ✅
   - 自动运行，完成 6 步进化流程
   - 生成本日进化报告

### 📚 文档更新
- **改进计划**: `.learnings/improvements/improvement_plan_20260313.md`
- **最佳实践 v1.0**: `.learnings/best_practices_v1.md`
- **安装报告**: `ai-team-dashboard/INSTALLATION_REPORT.md`

### 🎯 工作流程优化
- 微信文章: 多工具互补，快速/截图/分析
- 项目安装: 标准化 6 步流程
- Dashboard: 最小配置即可启动

---

## 2026-03-16 web-content-fetcher 集成与 OpenClaw 最佳实践 🌐

### 🎯 任务：安装、测试、集成 web-content-fetcher

**执行时间**: 2026-03-16 09:55 - 10:21
**系统版本**: v5.14.0 → v5.15.0
**执行者**: 大领导 🎯

### 📦 web-content-fetcher Skill

**项目**: https://github.com/shirenchuang/web-content-fetcher
**类型**: OpenClaw Skill
**功能**: 网页正文提取，永久免费，支持微信公众号

**技术栈**:
- Python 3.11+
- scrapling 0.4.1（网页内容提取）
- html2text 2025.4.15（HTML 转 Markdown）

**支持平台**:
- ✅ 微信公众号（专门优化）
- ✅ GitHub
- ✅ 知乎
- ✅ CSDN
- ✅ Substack
- ✅ Medium

**安装位置**:
- Skill 目录: `~/.openclaw/workspace/skills/web-content-fetcher/`
- 快捷脚本: `~/.openclaw/workspace/scripts/fetch-web-content.sh`

**使用方法**:
```bash
# 方法 1: 快捷脚本
~/.openclaw/workspace/scripts/fetch-web-content.sh <URL>

# 方法 2: 直接调用 Python
python3 ~/.openclaw/workspace/skills/web-content-fetcher/scripts/fetch.py <URL>
```

### ✅ 测试结果

#### GitHub 测试
- **链接**: https://github.com/shirenchuang/web-content-fetcher
- **结果**: ✅ 完美提取
- **质量**: Markdown 格式规范，标题、链接、列表完整

#### 微信公众号测试
- **链接**: https://mp.weixin.qq.com/s/-S03JzTFCd8Ez2grTx6WVg
- **标题**: AI大神40天养出一只精英龙虾军团
- **结果**: ✅ 完美提取
- **内容**: 5000+ 字符，格式规范，图片链接保留

### 🔧 系统更新

#### SOUL.md 更新（v5.15.0）
- 版本号升级: v5.14.0 → v5.15.0
- 新增核心能力: web-content-fetcher 集成
- RULE-002 增强: 从 3 种方法增加到 4 种
- 方法优先级重新排序:
  1. ⭐ web-content-fetcher Skill（新增）
  2. MCP 服务器工具
  3. 快速脚本（read-wechat.py）
  4. Python 代码（BeautifulSoup）

#### TOOLS.md 更新
- 章节标题: "微信公众号文章读取工具" → "网页内容提取工具"
- 新增方法 1 完整说明
- 支持平台列表更新
- 安装路径和依赖说明

### 📚 OpenClaw 最佳实践案例

**文章来源**: 智东西（微信公众号）
**文章标题**: AI大神40天养出一只精英龙虾军团
**作者**: Shubham Saboo（谷歌云高级AI产品经理）

#### 核心架构（三层）

**身份层**:
- SOUL.md - 定义智能体是谁、做什么、如何行动（控制在 60 行以内）
- IDENTITY.md - 智能体的名片（姓名、角色、气质、自我介绍）
- USER.md - 服务对象、偏好、背景

**操作层**:
- AGENTS.md - 行为规则、会话启动流程、文件读取顺序
- HEARTBEAT.md - 心跳状态检查（第一次出问题后再搭建）
- 特定角色指南 - 专业文件（写作风格、发文格式、真实案例）

**知识层**:
- MEMORY.md - 精选的长期记忆（只保留真正重要的信息）
- memory/YYYY-MM-DD.md - 每日会话日志（今天发生了什么、草拟什么、反馈）
- Shared Context - 跨智能体知识层（THESIS.md + FEEDBACK-LOG.md）

#### 6 个智能体系统
1. **Monica** - 幕僚长（协调）
2. **Dwight** - 研究智能体（信息检索）
3. **Kelly** - 推文写作
4. **Rachel** - 领英写作
5. **Ryan** - 文章策划
6. **Pam** - 任务调度

#### 40 天进化过程
- **第1天**: 需要大量纠正，比自己动手还费时间
- **第40天**: 自主运行，效率极高
- **方法**: 仅通过 Markdown 文件反馈学习
- **关键**: 不调整提示词、不更新模型、不重建架构
- **护城河**: 不断沉淀的上下文文件

#### 与大领导系统的对比

**相同点**:
- ✅ SOUL.md、IDENTITY.md、USER.md 结构完全一致
- ✅ AGENTS.md、HEARTBEAT.md 架构相同
- ✅ MEMORY.md + daily logs 记忆系统一致
- ✅ 基于 Markdown 文件的通信机制
- ✅ Multi-Agent 协作模式

**大领导系统的优势**:
- ✅ 更深度集成（运行在 OpenClaw 框架内）
- ✅ 规则保障机制（RULE-001 + RULE-002）
- ✅ 自主进化能力（PAI 学习 + 超级进化大脑）
- ✅ 三重防护机制
- ✅ 双轨进化（Self-Improvement + EvoMap）

#### 可借鉴的经验

1. **文件大小控制**
   - SOUL.md 控制在 60 行以内
   - 避免挤占实际工作的上下文空间

2. **HEARTBEAT.md 的时机**
   - 第一次出问题之后再去搭建
   - 只有亲身体会过哪里会崩，才能精准知道该监控什么

3. **共享文件设计**
   - 一个写入者、多个读取者
   - 避免协作冲突

4. **调度机制**
   - 按时间顺序分配智能体运行
   - 下游智能体依赖上游输出

5. **文件进化**
   - 从粗略草稿到丰富精准
   - 不断沉淀上下文就是护城河

### 💡 核心启发

1. **Markdown 文件是核心** - 不需要复杂的框架、消息队列、数据库
2. **反馈驱动进化** - 不需要调整模型，只需文件反馈
3. **三层架构清晰** - 身份、操作、知识
4. **记忆系统分层** - 长期、每日、共享
5. **规则保障重要** - 大领导系统的规则保障是额外的安全层

### 📊 成果总结

**技术成果**:
- ✅ web-content-fetcher 成功集成
- ✅ 系统升级到 v5.15.0
- ✅ RULE-002 从 3 种方法增加到 4 种
- ✅ 支持平台从 1 个扩展到 6 个

**知识成果**:
- ✅ 发现 OpenClaw 最佳实践案例
- ✅ 验证了大领导系统设计的正确性
- ✅ 提取了可借鉴的经验和教训
- ✅ 明确了未来的优化方向

**文档记录**:
- 测试报告: `.learnings/improvements/web-content-fetcher-test-report-20260316.md`
- 更新报告: `.learnings/improvements/soul-tools-update-v5.15-20260316.md`
- 今日日志: `memory/2026-03-16.md`

---

## 2026-03-13 上午更新

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