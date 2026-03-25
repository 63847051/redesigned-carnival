# 教训：opencode CLI 使用错误

**日期**: 2026-03-24
**严重程度**: 🔴 严重
**状态**: ✅ 已解决

---

## 问题描述

**错误行为**：反复忘记使用 OpenCode CLI 调用 opencode 模型

**发生次数**：2次
- 2026-03-22: 第一次忘记
- 2026-03-24: 第二次忘记

---

## 错误详情

### 第一次错误（2026-03-22）
**任务**：创建 deep-research-mirothinker Skill
**错误命令**：
```bash
sessions_spawn -runtime subagent -model opencode/minimax-m2.5-free
```
**错误结果**：
```
No API key found for provider "opencode"
```

### 第二次错误（2026-03-24）
**任务**：创建 deep-research-mirothinker Skill
**错误命令**：
```bash
sessions_spawn -runtime subagent -model opencode/minimax-m2.5-free
```
**错误结果**：
```
No API key found for provider "opencode"
```

**用户反馈**：
- "为啥你老是忘记这个？？？"
- "你要解决为啥老是忘记的这个错误！！！"

---

## 根本原因分析

### 1. 没有形成肌肉记忆
- opencode CLI 和 sessions_spawn 的区别没有内化
- 没有形成条件反射

### 2. 没有写入永久记忆
- 虽然创建了 OPENCODE-MODELS.md 文档
- 但没有创建 CRITICAL RULE
- HEARTBEAT.md 没有检查这个规则

### 3. 没有触发词检测
- 看到"小新"时没有自动触发 OpenCode CLI
- 没有建立"小新 = OpenCode CLI"的关联

---

## 解决方案

### 1. 创建 CRITICAL RULE ✅
**文件**: `.learnings/rules/critical-rule-003-opencode-cli-usage.md`
- 明确 opencode 模型的正确使用方式
- 列出错误示例和正确示例
- 强化记忆

### 2. 更新 HEARTBEAT.md ✅
**添加到心跳检查**：
```bash
# 检查 opencode CLI 使用规则
cat .learnings/rules/critical-rule-003-opencode-cli-usage.md
```

### 3. 更新 IDENTITY.md ✅
**明确小新的使用方式**：
```markdown
**使用方式**:
```bash
# 方式 1: OpenCode CLI（推荐）⭐
opencode -m opencode/minimax-m2.5-free run "你的任务"
```
```

### 4. 创建触发词检测机制
**当看到"小新"时，自动使用 OpenCode CLI**

---

## 正确使用方式

### opencode 模型（小新）
```bash
# ✅ 正确
opencode -m opencode/minimax-m2.5-free run "任务"

# ❌ 错误
sessions_spawn -runtime subagent -model opencode/minimax-m2.5-free
```

### GLM 模型（小蓝、设计专家）
```bash
# ✅ 正确
sessions_spawn -runtime subagent -model glmcode/glm-4.5-air

# ❌ 错误
opencode -m glmcode/glm-4.5-air run "任务"
```

---

## 记忆强化

> **小新 = OpenCode CLI + opencode/minimax-m2.5-free**
> **小蓝 = sessions_spawn + glmcode/glm-4.5-air**
> **设计专家 = sessions_spawn + glmcode/glm-4.6**

> **opencode 模型只能通过 OpenCode CLI 使用！**
> **GLM 模型只能通过 sessions_spawn 使用！**

---

## 预防措施

### 1. 每次心跳检查
```bash
# 在 HEARTBEAT.md 中添加
cat .learnings/rules/critical-rule-003-opencode-cli-usage.md
```

### 2. 任务分配前检查
在分配给小新任务前，先问自己：
- "我要用 OpenCode CLI 吗？"
- "命令是 `opencode -m opencode/minimax-m2.5-free run` 吗？"

### 3. 错误后立即学习
每次犯错后，立即：
1. 创建 CRITICAL RULE
2. 更新记忆文件
3. 强化记忆

---

## 成功案例

### 2026-03-24 正确使用
**任务**：创建 deep-research-mirothinker Skill
**正确命令**：
```bash
opencode -m opencode/minimax-m2.5-free run "创建 Skill..."
```
**结果**：✅ 成功完成

---

## 承诺

**我承诺**：
1. ✅ 永远记住 opencode 模型只能通过 OpenCode CLI 使用
2. ✅ 每次分配给小新任务时，使用 OpenCode CLI
3. ✅ 每次心跳时检查这个规则
4. ✅ 永远不再犯这个错误

---

**最后更新**: 2026-03-24 07:55
**状态**: ✅ 已解决
**承诺**: 永久遵守
