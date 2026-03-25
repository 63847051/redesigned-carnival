# RULE-003: OpenCode CLI 使用规则

**规则ID**: RULE-003
**优先级**: 🔴 CRITICAL（最高）
**创建时间**: 2026-03-24 07:55
**状态**: ✅ 激活
**版本**: v1.0

---

## 🚨 规则内容

### opencode 模型的正确使用方式

**❌ 错误方式**：
```bash
# 不要这样用！
sessions_spawn -runtime subagent -model opencode/minimax-m2.5-free
```

**✅ 正确方式**：
```bash
# 必须用 OpenCode CLI！
opencode -m opencode/minimax-m2.5-free run "任务"
```

---

## 📋 opencode 可用模型

### 免费模型（优先使用）
1. **opencode/minimax-m2.5-free** ⭐ 主要使用
2. **opencode/mimo-v2-pro-free** - 复杂任务
3. **opencode/nemotron-3-super-free** - 深度分析

### 查看所有模型
```bash
opencode models
```

---

## 🎯 使用场景

### 何时使用 opencode
- ✅ 代码编写任务
- ✅ 技术支持任务
- ✅ 小新的所有任务

### 何时使用 sessions_spawn
- ✅ GLM 模型任务（glmcode/glm-4.5-air 等）
- ✅ 小蓝的日志任务
- ✅ 设计专家的设计任务

---

## 🔍 触发词检测

**当看到以下关键词时，必须使用 OpenCode CLI**：
- "小新"
- "代码"
- "爬虫"
- "API"
- "技术支持"
- "编程"

---

## 🚨 违反此规则的后果

**历史错误**：
- 2026-03-22: 第一次忘记，用户批评
- 2026-03-24: 第二次忘记，用户强烈批评

**永远不要再犯！**

---

## 📝 记忆强化

> **opencode 模型只能通过 OpenCode CLI 使用！**
> **sessions_spawn 只能用于 GLM 模型！**
> **小新 = OpenCode CLI + opencode/minimax-m2.5-free！**

---

**违反此规则 = 严重错误**

**最后更新**: 2026-03-24 07:55
**版本**: v1.0
**状态**: ✅ 永久激活
