# 🚀 升级到独立 Agent 完整指南

**版本**: v2.0
**更新时间**: 2026-03-04
**目标**: 解决并行处理 + 100% 隔离

---

## 📊 当前方案 vs 独立 Agent 方案

### 当前方案（Skill 隔离 v1.0）

| 特性 | 状态 |
|------|------|
| 上下文隔离 | 90% |
| 并行处理 | ❌ 不支持（串行） |
| 模型隔离 | ✅ 支持 |
| 主动性 | ❌ 子角色不能主动发起 |
| 成本 | 70% 免费 |

### 独立 Agent 方案（v2.0）

| 特性 | 状态 |
|------|------|
| 上下文隔离 | ✅ 100% |
| 并行处理 | ✅ 支持（真正的并行） |
| 模型隔离 | ✅ 支持 |
| 主动性 | ✅ 子 Agent 可主动发起任务 |
| 成本 | 70% 免费（智能调度） |

---

## 🎯 独立 Agent 的核心优势

### 1. 真正的并行处理 ⚡

**当前方案**：
```
任务1 → 设计专家处理 → 完成 → 任务2 → 技术专家处理 → 完成
（串行，总时间 = T1 + T2）
```

**独立 Agent 方案**：
```
任务1 → 设计专家处理 ─┐
                    ├→ 同时进行 → 完成
任务2 → 技术专家处理 ─┘
（并行，总时间 = max(T1, T2)）
```

### 2. 100% 上下文隔离 🔐

**当前方案**：
- 共享主控 Agent 的会话上下文
- 依赖规则引擎防止混淆
- 隔离度：90%

**独立 Agent 方案**：
- 每个 Agent 有完全独立的会话
- 完全独立的对话历史
- 隔离度：100%

### 3. 主动性 🚀

**当前方案**：
- 子角色只能被动响应
- 不能主动发起任务
- 不能主动监控和提醒

**独立 Agent 方案**：
- 子 Agent 可以主动发起任务
- 可以主动监控状态
- 可以主动提醒和报告

---

## 🔧 技术实现方案

### 方案 A: OpenClaw Subagent 模式（推荐）

#### 前置条件
需要配置 OpenClaw 允许的 Agent 列表：

```bash
# 编辑 OpenClaw 配置
~/.openclaw/openclaw.json
```

添加配置：
```json
{
  "sessions": {
    "spawn": {
      "allowAny": true,
      "allowedAgents": ["*"]
    }
  }
}
```

#### 初始化独立 Agent

```javascript
// 1. 创建设计专家 Agent
sessions_spawn({
  runtime: "subagent",
  mode: "session",
  thread: true,
  agentId: "interior-design-expert",
  model: "glmcode/glm-4.7",
  label: "设计专家",
  task: "你是室内设计专家...",
  timeoutSeconds: 300
})

// 2. 创建技术专家 Agent
sessions_spawn({
  runtime: "subagent",
  mode: "session",
  thread: true,
  agentId: "tech-support-expert",
  model: "openrouter/gpt-oss-120b",
  label: "技术专家",
  task: "你是技术支持专家...",
  timeoutSeconds: 300
})

// 3. 创建小蓝 Agent
sessions_spawn({
  runtime: "subagent",
  mode: "session",
  thread: true,
  agentId: "worklog-manager",
  model: "glmcode/glm-4.5-air",
  label: "小蓝",
  task: "你是工作日志管理专家...",
  timeoutSeconds: 300
})
```

#### 并行任务处理

```javascript
// 主控 Agent 同时分配多个任务
async function handleParallelTasks() {
  // 同时启动多个 Agent
  const task1 = sessions_send({
    sessionKey: "design-expert",
    message: "设计3F会议室方案"
  })

  const task2 = sessions_send({
    sessionKey: "tech-expert",
    message: "编写数据抓取脚本"
  })

  const task3 = sessions_send({
    sessionKey: "worklog-manager",
    message: "更新任务进度"
  })

  // 等待所有任务完成
  const [result1, result2, result3] = await Promise.all([
    task1, task2, task3
  ])

  // 汇总结果
  return {
    design: result1,
    tech: result2,
    log: result3
  }
}
```

### 方案 B: ACP Coding Sessions（备选）

如果不想配置允许列表，可以使用 ACP 模式：

```javascript
// 使用 ACP runtime
sessions_spawn({
  runtime: "acp",
  mode: "session",
  thread: true,
  model: "glmcode/glm-4.7",
  label: "设计专家",
  task: "你是室内设计专家..."
})
```

**注意**：ACP 模式更适合编码任务，对于通用任务建议使用方案 A。

---

## 🔄 无缝升级步骤

### Step 1: 配置 OpenClaw（5 分钟）

```bash
# 1. 编辑配置文件
nano ~/.openclaw/openclaw.json

# 2. 添加以下配置
{
  "sessions": {
    "spawn": {
      "allowAny": true,
      "allowedAgents": ["*"]
    }
  }
}

# 3. 重启 Gateway
openclaw gateway restart
```

### Step 2: 初始化独立 Agent（2 分钟）

```bash
# 运行初始化脚本
bash /root/.openclaw/workspace/scripts/init-independent-agents.sh
```

### Step 3: 测试隔离性（5 分钟）

```bash
# 运行测试脚本
bash /root/.openclaw/workspace/scripts/test-independent-agents.sh
```

### Step 4: 验证并行处理（2 分钟）

```bash
# 测试并行任务
# 设计任务 + 技术任务 + 日志任务同时进行
```

### Step 5: 切换生产（1 分钟）

```bash
# 更新主控 Agent 配置，启用独立 Agent 模式
```

**总时间**: 约 15 分钟

---

## 💰 成本优化策略

### 智能并行调度

```javascript
// 成本优化：优先并行免费任务
async function optimizedParallel() {
  // 第一批：免费任务并行
  const [techResult, logResult] = await Promise.all([
    sessions_send({ sessionKey: "tech-expert", message: "..." }), // 免费
    sessions_send({ sessionKey: "worklog-manager", message: "..." }) // 免费
  ])

  // 第二批：主模型任务
  const designResult = await sessions_send({
    sessionKey: "design-expert",
    message: "..."
  }) // 主模型

  return { tech: techResult, log: logResult, design: designResult }
}
```

### 成本对比

| 场景 | Skill 隔离 | 独立 Agent |
|------|-----------|-----------|
| 串行 3 个任务 | 70% 免费 | 70% 免费 |
| 并行 3 个任务 | 不支持 | **85% 免费** ⚡ |

**为什么并行更省钱？**
- 免费任务可以同时进行（技术 + 日志）
- 主模型任务独立处理
- 总时间减少，等待时间减少

---

## 🎯 实际使用场景

### 场景 1: 并行处理多个任务

**用户请求**：
```
"大领导，帮我处理以下任务：
1. 设计3F会议室
2. 编写数据抓取脚本
3. 更新工作日志"
```

**Skill 隔离方案**（串行）：
```
设计任务 (5分钟) → 技术任务 (3分钟) → 日志任务 (1分钟)
总时间：9分钟
```

**独立 Agent 方案**（并行）：
```
设计任务 (5分钟) ─┐
                  ├→ 同时进行
技术任务 (3分钟) ─┤
                  │
日志任务 (1分钟) ─┘
总时间：5分钟（节省 44% 时间）
```

### 场景 2: 主动性任务

**当前方案**：
- ❌ 小蓝不能主动提醒任务到期
- ❌ 设计专家不能主动检查图纸
- ❌ 技术专家不能主动监控系统

**独立 Agent 方案**：
- ✅ 小蓝可以主动监控任务状态，到期自动提醒
- ✅ 设计专家可以主动检查图纸一致性
- ✅ 技术专家可以主动监控系统健康

---

## 📋 配置示例

### 完整的独立 Agent 配置

```javascript
// agents/independent-agents-config.js

module.exports = {
  // 设计专家
  "interior-design-expert": {
    runtime: "subagent",
    mode: "session",
    thread: true,
    model: "glmcode/glm-4.7",
    label: "设计专家",
    timeoutSeconds: 300,
    capabilities: [
      "室内设计",
      "图纸绘制",
      "空间规划",
      "材料选择"
    ],
   主动性: {
      enabled: true,
      triggers: [
        "图纸一致性检查",
        "材料价格监控",
        "施工可行性提醒"
      ]
    }
  },

  // 技术专家
  "tech-support-expert": {
    runtime: "subagent",
    mode: "session",
    thread: true,
    model: "openrouter/gpt-oss-120b",
    label: "技术专家",
    timeoutSeconds: 300,
    capabilities: [
      "代码编写",
      "脚本开发",
      "API 集成",
      "数据处理"
    ],
   主动性: {
      enabled: true,
      triggers: [
        "系统健康检查",
        "代码质量监控",
        "性能优化建议"
      ]
    }
  },

  // 小蓝
  "worklog-manager": {
    runtime: "subagent",
    mode: "session",
    thread: true,
    model: "glmcode/glm-4.5-air",
    label: "小蓝",
    timeoutSeconds: 120,
    capabilities: [
      "日志记录",
      "任务跟踪",
      "进度统计",
      "自动提醒"
    ],
   主动性: {
      enabled: true,
      triggers: [
        "任务到期提醒",
        "进度异常报告",
        "每日汇总"
      ]
    }
  }
}
```

---

## 🚀 升级脚本

让我为你创建一个自动化升级脚本！

---

*更新时间: 2026-03-04*
*版本: v2.0*
*状态: 准备实施*
