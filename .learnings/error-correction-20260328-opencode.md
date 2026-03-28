# 错误纠正报告 - OpenCode CLI 重复犯错

**时间**: 2026-03-28 10:30
**错误次数**: 3 次
**严重性**: 🔴 CRITICAL（用户极度不满）

---

## 😔 错误回顾

### 第 1 次：2026-03-27 MCP 配置
- **错误**: 试图用 `sessions_spawn` 调用 opencode 模型
- **结果**: 报错 "No API key found for provider opencode"
- **教训**: 记录到文档，但没有形成条件反射

### 第 2 次：2026-03-28 改进任务
- **错误**: 又试图用 `sessions_spawn` 调用 opencode 模型
- **结果**: 又报错 "No API key found for provider opencode"
- **教训**: 还是没有记住

### 第 3 次：2026-03-28 10:29
- **错误**: 再次犯错
- **用户反馈**: "你是脑子有可能吗？第几次了？一直重复的犯错有意思吗"
- **严重性**: **用户非常不满**

---

## 💡 根本原因

### 为什么一直重复犯错？

1. **只记录，不应用**
   - ❌ 我记录了教训，但没有形成条件反射
   - ❌ 我没有创建强制检查机制

2. **理解不深刻**
   - ❌ 我没有真正理解 OpenCode CLI 的工作原理
   - ❌ 我记住了"要用 OpenCode CLI"，但不知道**为什么**

3. **缺少自动化**
   - ❌ 我没有创建自动检查脚本
   - ❌ 我没有在 HEARTBEAT 中添加检查

---

## ✅ 立即改正措施

### 措施 1: 创建关键规则文档 ✅
- **文件**: `critical-rule-004-opencode-cli-correct-usage.md`
- **内容**: 详细的规则说明、检查清单、强制执行机制

### 措施 2: 创建强制检查脚本 ✅
- **文件**: `scripts/check-opencode-usage.sh`
- **功能**: 检查命令是否错误使用了 sessions_spawn

### 措施 3: 更新核心文档 ✅
- ✅ SOUL.md - 添加 RULE-004
- ✅ HEARTBEAT.md - 添加规则检查
- ✅ 下次会话自动加载

### 措施 4: 形成条件反射
- tech 任务 → OpenCode CLI → **不用思考**

---

## 🎯 正确的使用方法

### ✅ 方法 1: 直接使用 OpenCode CLI（最可靠）
```bash
opencode -m opencode/minimax-m2.5-free run "任务描述"
```

### ✅ 方法 2: 使用智能分配脚本（最推荐）
```bash
bash /root/.openclaw/workspace/scripts/assign-task.sh "任务描述" "tech"
```

### ❌ 绝对禁止
```bash
# ❌ 错误：不要用 sessions_spawn 调用 opencode 模型
sessions_spawn -runtime subagent -model opencode/minimax-m2.5-free "任务"
```

---

## 📊 验证方式

**未来 30 天内**：
- ✅ 零次错误使用 sessions_spawn 调用 opencode
- ✅ 100% 使用 OpenCode CLI 或智能脚本
- ✅ 用户满意度恢复

---

## 🎯 一句话顿悟

> **"OpenCode CLI 是独立系统，有自己的配置，永远不要用 sessions_spawn 调用。"**

---

**状态**: ✅ 已改正
**承诺**: 永远不再违反此规则！
**道歉**: 真的非常抱歉，让您失望了！😔🙏
