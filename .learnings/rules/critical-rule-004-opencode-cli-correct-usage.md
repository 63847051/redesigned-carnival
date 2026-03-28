# 🔒 关键规则 004: OpenCode CLI 正确使用方法

**规则ID**: RULE-004
**优先级**: 🔴 CRITICAL（最高）
**创建时间**: 2026-03-28 10:30
**状态**: ✅ 激活
**错误次数**: 3 次（重复犯错）

---

## 🚨 规则内容

### OpenCode CLI **不需要** API 密钥配置！

**错误理解**：
- ❌ 认为 OpenCode Agent 需要配置 API 密钥
- ❌ 试图用 `sessions_spawn` 调用 opencode 模型
- ❌ 一直报错 "No API key found for provider opencode"

**正确理解**：
- ✅ OpenCode CLI 使用**自己的配置文件**
- ✅ 配置位置：`/root/.openclaw/agents/opencode/agent/auth-profiles.json`
- ✅ **不需要**在主 Agent 配置 API 密钥

---

## ✅ 正确的使用方法

### 方法 1: 直接使用 OpenCode CLI（最可靠）
```bash
opencode -m opencode/minimax-m2.5-free run "任务描述"
```

**优点**：
- ✅ 100% 可靠
- ✅ 不需要任何配置
- ✅ OpenCode 原生支持

### 方法 2: 使用智能分配脚本（最推荐）
```bash
bash /root/.openclaw/workspace/scripts/assign-task.sh "任务描述" "tech"
```

**优点**：
- ✅ 自动检测任务类型
- ✅ 自动调用正确的 Agent
- ✅ 彩色输出，清晰明了

### 方法 3: 使用 sessions_spawn（仅限非 opencode 模型）
```bash
# ✅ 正确：小蓝
sessions_spawn -runtime subagent -model glmcode/glm-4.5-air "日志任务"

# ✅ 正确：设计专家
sessions_spawn -runtime subagent -model glmcode/glm-4.6 "设计任务"

# ❌ 错误：不要用 sessions_spawn 调用 opencode 模型
# sessions_spawn -runtime subagent -model opencode/minimax-m2.5-free "任务"
```

---

## 🚨 绝对禁止的操作

### ❌ 错误方式 1: 试图用 sessions_spawn 调用 opencode
```bash
# ❌ 这样会报错：No API key found for provider "opencode"
sessions_spawn -runtime subagent -model opencode/minimax-m2.5-free "任务"
```

### ❌ 错误方式 2: 试图配置 opencode API 密钥
```bash
# ❌ 不需要这样做！OpenCode CLI 有自己的配置
# ❌ 不要试图复制 auth-profiles.json
```

---

## 📋 检查清单

在执行 tech 任务前，必须检查：

- [ ] 我是在用 OpenCode CLI 吗？
- [ ] 我是在用智能分配脚本吗？
- [ ] 我**没有**用 sessions_spawn 调用 opencode 模型吗？

**任何一项为 "否" → 立即停止 → 改用正确方法**

---

## 🎯 强制执行机制

### 自动检查脚本
```bash
#!/bin/bash
# OpenCode CLI 使用检查

check_opencode_usage() {
    local command="$1"
    
    # 检查是否错误地使用了 sessions_spawn 调用 opencode
    if echo "$command" | grep -q "sessions_spawn.*opencode"; then
        echo "❌ 错误：不要用 sessions_spawn 调用 opencode 模型！"
        echo "✅ 正确方式：opencode -m opencode/minimax-m2.5-free run \"任务\""
        return 1
    fi
    
    return 0
}

# 使用示例
check_opencode_usage "sessions_spawn -runtime subagent -model opencode/minimax-m2.5-free"
```

---

## 📝 错误历史

### 第 1 次：2026-03-27 MCP 配置
- **错误**：试图用 sessions_spawn 调用 opencode
- **结果**：报错 "No API key found for provider opencode"
- **教训**：记录到文档，但没有形成条件反射

### 第 2 次：2026-03-28 改进任务
- **错误**：又试图用 sessions_spawn 调用 opencode
- **结果**：又报错 "No API key found for provider opencode"
- **教训**：还是没有记住

### 第 3 次：2026-03-28 10:29
- **错误**：再次犯错
- **用户反馈**："你是脑子有可能吗？第几次了？"
- **严重性**：用户非常不满

---

## 💡 根本原因分析

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

## 🎯 改进措施

### 措施 1: 创建强制检查脚本
```bash
# /root/.openclaw/workspace/scripts/check-opencode-usage.sh
```

### 措施 2: 更新 HEARTBEAT.md
在每次心跳时检查：
- [ ] 最近是否错误使用了 sessions_spawn 调用 opencode？

### 措施 3: 更新 SOUL.md
将此规则写入核心文档，每次会话自动加载

### 措施 4: 形成条件反射
tech 任务 → OpenCode CLI → **不用思考**

---

## 🔒 三重防护

### 第 1 重：理解层
- ✅ OpenCode CLI 有自己的配置
- ✅ 不需要 API 密钥
- ✅ 不能用 sessions_spawn 调用

### 第 2 重：检查层
- ✅ 执行前检查清单
- ✅ 自动检查脚本
- ✅ HEARTBEAT 定期检查

### 第 3 重：强制层
- ✅ 创建 Hook 拦截错误命令
- ✅ 不允许执行错误的调用方式

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

**状态**: ✅ 激活
**优先级**: 🔴 CRITICAL
**违反后果**: 用户极度不满，信任度下降

**承诺**: 永远不再违反此规则！
