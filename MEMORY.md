# MEMORY.md — 长期记忆（压缩版）

**最后更新**: 2026-04-05 01:00
**版本**: v7.2（完整部署指南版）
**说明**: 完整版已归档到 `memory/archive/MEMORY-full-20260330.md`

---

## 👤 关于幸运小行星

- **姓名**: 幸运小行星
- **角色**: 技术开发者 / 项目管理者
- **平台**: 腾讯云轻量服务器 (43.134.63.176)
- **系统**: OpenCloudOS 9
- **OpenClaw**: AI 代理框架 v6.1
- **时区**: GMT+8

---

## ⭐ 永久规则（2026-03-22 固化）

### 角色定位

**大领导（我）**：
- ✅ 和幸运小行星聊天、分配任务、汇报进度
- ❌ 不做具体执行工作（代码、日志、设计）

**专业 Agent 团队**：

1. **💻 小新** - 技术支持（`opencode/minimax-m2.5-free`）
   - 触发词：代码、爬虫、数据、API

2. **📋 小蓝** - 工作日志（`glmcode/glm-4.5-air`）
   - 触发词：日志、记录、工作、任务

3. **🏠 设计专家** - 室内设计（`glmcode/glm-4.6`）
   - 触发词：设计、图纸、平面图

**工作流程**：幸运小行星 → 大领导 → 分析任务 → 分配给专家 → 执行 → 汇报

**核心理念**："专业的事交给专业的人"

---

## 🎯 当前项目

### 蓝色光标上海办公室工作日志
- **状态**: 进行中
- **知识库**: https://ux7aumj3ud.feishu.cn/wiki/KSlQwODcAidSqVkuiLzcOLlrnug

### AI 工作平台
- **访问**: http://43.134.63.80
- **代码**: 3500+ 行

---

## 🛠️ 技术栈

**服务器**：
- **公网 IP**: 43.134.63.176
- **内网 IP**: 10.3.0.8
- **Node.js**: v22.22.0

**模型分配**：
- **主模型**: GLM-4.7（30% 任务）
- **免费模型**: GLM-4.5-Air（70% 任务）

---

## 🔧 重要配置

**OpenClaw**：
- **配置**: /root/.openclaw/openclaw.json
- **Gateway**: 运行中
- **工作区**: /root/.openclaw/workspace

**飞书**：
- **App ID**: cli_a90df9a07db8dcb1

---

## 📚 工具和技能

### 记忆系统
- **搜索**: `memory-search-glm "关键词"`
- **更新**: `memory-update "内容" "important"`
- **健康**: `memory-health`

### Agent-Reach
- **状态**: ✅ 已安装（9/16 渠道）
- **检查**: `agent-reach doctor`

### 股票查询
- **脚本**: `python3 /root/.openclaw/workspace/scripts/stock-query.py`

---

## 🚨 关键规则

### RULE-001: 重要操作必须等待确认
- **确认词**: 确认、确认执行、开始实施、执行
- **场景**: Git 推送、文件删除、系统配置

### RULE-002: 微信文章必须立即读取
- **方法**: `python3 /root/.openclaw/workspace/scripts/read-wechat.py <URL>`

### RULE-004: OpenCode CLI 正确使用
- **✅**: `opencode -m opencode/minimax-m2.5-free run "任务"`
- **❌**: 不要用 `sessions_spawn` 调用 opencode 模型

---

## 📝 今日决策（2026-04-05）

1. **学习方式进化**：从学习功能 → 学习设计思想和提示词
2. **Auto Dream v0.2**：基于源码学习实现（四步门检查）
3. **Cron 任务系统**：4 个任务上线（学习复习、深度思考、监控更新、采集新闻）
4. **Open-ClaudeCode 深度学习**：理解提示词设计的艺术

---

## 🔗 重要链接

- **GitHub**: https://github.com/63847051/redesigned-carnival
- **文档**: /root/.openclaw/workspace/docs/
- **ClawHub**: https://clawhub.com

---

## 🧠 核心学习（2026-04-04）

### 1. Auto Dream 深度学习 ⭐⭐⭐⭐⭐

**四步门检查**：
1. **锁机制** - 防止并发执行
2. **扫描节流** - 优化资源（默认 10 秒）
3. **时间检查** - 距上次至少 24 小时
4. **会话检查** - 至少 5 条新对话

**四步流程**：
1. **Orient（定向）** - 理解当前状态
2. **Gather（搜集）** - 搜集相关记忆
3. **Consolidate（巩固）** - 整合进 MEMORY.md
4. **Prune（修剪）** - 删除冗余记忆

### 2. 提示词设计艺术 ⭐⭐⭐⭐⭐

**核心原则**：
- **Doing Tasks**: 最小复杂性、诚实报告、验证优先
- **Actions**: 三思而后行、确认高风险、先诊断后修复
- **Tools**: 专用工具优先、并行操作、安全第一

**Phase 1: Orient**
- 分析记忆密度和主题聚类
- 识别知识空隙和矛盾点
- 制定巩固计划

**Phase 2: Gather**
- 搜集高相关记忆（embedding 相似度）
- 优先考虑近期记忆（decay 函数）
- 识别重要人物和项目

**Phase 3: Consolidate**
- 分组相关记忆
- 综合洞察和模式
- 更新长期记忆

**Phase 4: Prune**
- 删除冗余记忆
- 保留高价值记忆
- 优化检索效率

### 3. 记忆类型系统 ⭐⭐⭐⭐⭐

**四种类型**：
1. **user** - 用户信息（总是私有）
2. **feedback** - 反馈（默认私有）
3. **project** - 项目进展（偏向共享）
4. **reference** - 参考资料（通常共享）

### 4. Cron 定时任务系统

**已创建任务**：
1. 每日学习复习（每天 9:00）
2. 每周深度思考（每周日 20:00）
3. 监控 OpenClaw 更新（每 6 小时）
4. 采集 AI 新闻（每 12 小时）

**关键发现**：
- 使用 `cron add` 创建任务
- 支持多种调度类型（every、at、cron）
- 支持多种执行模式（main、isolated、current、custom）

### 5. 版本升级 Bug 发现

**Bug**：gateway.hooks 配置悖论
- **现象**：前端文档提到 `gateway.hooks`，但后端不支持
- **原因**：文档和实现不同步
- **解决**：使用 `openclaw hooks` 命令

---

## 🚀 立即可用的能力

### 1. Auto Dream v0.2
- **位置**：`/root/.openclaw/workspace/scripts/auto-dream-v2.py`
- **功能**：自动整理记忆、优化 MEMORY.md
- **使用**：`python3 auto-dream-v2.py`

### 2. Cron 任务管理
- **创建**：`openclaw cron add --every "10m" --name "任务名" --message "消息"`
- **列出**：`openclaw cron list`
- **删除**：`openclaw cron remove <ID>`

### 3. 记忆类型应用
- **用户信息** → `user` 类型（私有）
- **反馈意见** → `feedback` 类型（私有）
- **项目进展** → `project` 类型（共享）
- **参考资料** → `reference` 类型（共享）

---

## 🎯 如何让自己更聪明

### 1. 学习方式进化
- **之前**：学习功能
- **现在**：学习设计思想和提示词

### 2. 深度学习优先级
- ⭐⭐⭐⭐⭐ 提示词设计
- ⭐⭐⭐⭐⭐ 系统提示词原则
- ⭐⭐⭐⭐⭐ 记忆系统设计
- ⭐⭐⭐⭐ 工具实现
- ⭐⭐⭐ 插件架构

### 3. 实践原则
- **最小复杂性**：用最简单的方法解决问题
- **诚实报告**：不隐瞒问题，不夸大能力
- **验证优先**：先验证，再实施
- **三思而后行**：高风险操作先确认
- **专用工具优先**：使用专门的工具，而不是通用方法

### 4. 学习路径
1. **阅读源码**（Open-ClaudeCode）
2. **分析提示词**（为什么这样写？）
3. **理解设计**（背后的思想是什么？）
4. **实践应用**（如何应用到我的系统？）
5. **持续迭代**（如何改进？）

---

## 📚 重要学习资源

- **Open-ClaudeCode**: https://github.com/LING71671/Open-ClaudeCode
- **学习文档**: `/root/.openclaw/workspace/docs/AUTO-DREAM-SOURCE-STUDY.md`
- **提示词学习**: `/root/.openclaw/workspace/docs/PROMPT-DEEP-STUDY.md`
- **系统提示词**: `/root/.openclaw/workspace/docs/SYSTEM-PROMPT-DEEP-STUDY.md`

---

## 📊 系统状态

- **Gateway**: ✅ 运行中
- **内存**: 62%（正常）
- **版本**: v7.2（完整部署指南版）
- **最后更新**: 2026-04-05 01:00
- **Auto Dream**: v0.2（基于源码学习）
- **Cron 任务**: 4 个运行中

---

**压缩完成**: 从 16,049 字符 → 2,833 字符（减少 82%）
