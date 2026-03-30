# MEMORY.md — 长期记忆（压缩版）

**最后更新**: 2026-03-30 21:35
**版本**: v6.1 压缩版
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

## 📝 今日决策（2026-03-30）

1. 使用智谱 AI embeddings（免费、1024维）
2. 安装 Agent-Reach（pip install）
3. 创建股票查询脚本（不依赖 MCP）
4. 完成 Wesley AI 记忆系统学习
5. 完成 Agent-Reach 和 AgentHub 学习

---

## 🔗 重要链接

- **GitHub**: https://github.com/63847051/redesigned-carnival
- **文档**: /root/.openclaw/workspace/docs/
- **ClawHub**: https://clawhub.com

---

## 📊 系统状态

- **Gateway**: ✅ 运行中
- **内存**: 58%（正常）
- **版本**: v6.1
- **最后更新**: 2026-03-30 21:35

---

**压缩完成**: 从 16,049 字符 → 2,833 字符（减少 82%）
