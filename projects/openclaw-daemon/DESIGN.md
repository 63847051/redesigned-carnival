# OpenClaw Daemon 架构设计文档

**版本**: v1.0
**创建时间**: 2026-04-07
**基于**: Slock Daemon 架构

---

## 🎯 核心目标

创建 OpenClaw Daemon - 一个本地守护进程，负责 Agent 生命周期管理和会话状态维护。

---

## 🏗️ 架构设计

### 整体分层

```
┌─────────────────────────────────────┐
│     控制平面 (Control Plane)        │
│  - DaemonConnection                 │
│  - Prompt Assembly                  │
│  - AgentManager Cache               │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│     进程状态机 (State Machine)       │
│  - Cold Start → Running → Idle      │
│  - 会话生命周期管理                  │
│  - 状态转换逻辑                     │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│     驱动适配器 (Driver Adapters)     │
│  - SubagentDriver                    │
│  - ACPDriver                         │
│  - OpenCodeDriver                   │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│     运行时 I/O (Runtime I/O)        │
│  - Spawned CLI Process               │
│  - JSON Event Parser                 │
│  - MCP Bridge                        │
└─────────────────────────────────────┘
```

---

## 📊 核心组件

### 1. 控制平面 (Control Plane)

#### DaemonConnection
- **功能**: WebSocket 连接管理
- **职责**: 
  - 连接 OpenClaw Gateway
  - 处理连接/断开/重连
  - 心跳检测（最多 70s 无流量）
  
#### PromptAssembly
- **功能**: 提示词组装
- **职责**:
  - 格式化输入
  - 拼接系统提示词
  - 判断冷启动 vs 恢复会话
  
#### AgentManagerCache
- **功能**: Agent 状态缓存
- **职责**:
  - 缓存 Agent 运行态
  - 配置、子进程、会话 ID
  - 判断"忙时注入" vs "重启"

---

### 2. 进程状态机 (State Machine)

#### Agent 生命周期

```
Cold Start（冷启动）
    ↓
Running（运行中）
    ↓
Idle/Sleep（空闲）
    ↓
Wake Up（唤醒）
    ↓
Running（运行中）
```

#### 关键差异点

**Claude/OpenCode**（支持 stdin 注入）:
- ✅ 在 `Running` 状态下继续接收消息
- ✅ 忙时收到新消息直接注入
- ✅ 不中断当前会话

**Subagent**（不支持 stdin 注入）:
- ❌ 必须先进入 `Idle`
- ❌ 收到新消息后重启
- ❌ 更容易卡顿

---

### 3. 驱动适配器 (Driver Adapters)

#### SubagentDriver
- **模式**: `exec/resume` 重启模式
- **特点**: 
  - 不支持 `stdin` 通知
  - 新消息必须触发重启
  - 更容易卡顿

#### ACPDriver
- **模式**: 常驻会话 + `stdin` 注入
- **特点**:
  - 支持 `stdin` 实时通知
  - 忙时也能接收新消息
  - 更像"在线同事"

#### OpenCodeDriver
- **模式**: 混合模式
- **特点**:
  - 通过 CLI 调用
  - 独立配置
  - 需要特殊处理

---

### 4. 运行时 I/O (Runtime I/O)

#### Spawned CLI Process
- **功能**: 启动 CLI Agent 进程
- **职责**:
  - 在 Agent 工作目录启动
  - 读取本地 `MEMORY.md`
  - 管理进程生命周期

#### JSON Event Parser
- **功能**: 解析 Agent 输出
- **职责**:
  - 解析标准输出
  - 转换成 UI 事件
  - 提取关键信息

#### MCP Bridge
- **功能**: MCP 协议桥接
- **职责**:
  - 工具调用转换
  - 任务认领
  - 状态更新

---

## 🔄 运行流程

### 1. 启动流程

```bash
# 1. 启动 Daemon
openclaw-daemon start

# 2. 连接 Gateway
openclaw-daemon connect

# 3. 加载配置
openclaw-daemon load-config

# 4. 启动 Agent
openclaw-daemon spawn-agent --agent-id main
```

### 2. 消息处理流程

```python
# 1. 接收消息
message = receive_message()

# 2. 判断 Agent 状态
agent_state = get_agent_state(message.session_key)

# 3. 决策
if agent_state == "running" and supports_stdin(agent):
    # 忙时注入
    inject_message(agent, message)
else:
    # 重启 Agent
    restart_agent(agent, message)
```

### 3. 会话管理

```python
# 冷启动新会话
if session_key not in cache:
    agent = cold_start(session_key)
    cache.set(session_key, agent)

# 恢复旧会话
else:
    agent = cache.get(session_key)
    resume_session(agent)
```

---

## 🎯 关键差异：Codex vs Claude

| 特性 | Subagent | ACP |
|------|----------|-----|
| **核心模式** | 依赖 `exec/resume` | 常驻会话 + `stdin` 注入 |
| **新消息处理** | 必须重启会话 | 忙时也能接收 |
| **体验问题** | 一旦被 `system event` 投喂，极易空转或卡顿 | 更像"在线同事" |

---

## 💡 实现优先级

### Phase 1: 核心功能（1-2天）
- [ ] Daemon 进程框架
- [ ] WebSocket 连接管理
- [ ] 基本状态机

### Phase 2: 驱动适配器（2-3天）
- [ ] SubagentDriver
- [ ] ACPDriver
- [ ] OpenCodeDriver

### Phase 3: 高级功能（3-5天）
- [ ] 提示词组装
- [ ] Agent 状态缓存
- [ ] MCP Bridge

---

## 📚 参考资料

- **Slock Daemon**: 用户提供的 4 张图解
- **OpenClaw Gateway**: `/root/.openclaw/openclaw.json`
- **Agent 配置**: `/root/.openclaw/workspace/IDENTITY.md`

---

**设计完成！准备开始实施！** 🚀
