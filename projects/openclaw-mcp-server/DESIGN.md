# OpenClaw MCP Server 设计文档

**版本**: v1.0
**创建时间**: 2026-04-07
**基于**: Slock chat-bridge MCP 设计

---

## 🎯 核心目标

创建 OpenClaw MCP Server，实现跨 Agent 协作的标准化接口。

### 核心价值

**1. 统一协作接口** ⭐⭐⭐⭐⭐
- 所有 Agent 通过同一套工具协作
- 避免私有语法碎片化
- 降低跨 Agent 通信成本

**2. 任务管理集成** ⭐⭐⭐⭐⭐
- 聊天流 + 任务流二合一
- Agent 可以认领任务
- 避免跳出聊天系统

**3. 历史查询标准化** ⭐⭐⭐⭐⭐
- 结构化消息 → 纯文本上下文
- Agent 易于理解
- 支持 Token 优化

---

## 📊 MCP 工具链设计

### 1. SEND_MESSAGE（发送消息）

**功能**: Agent 唯一的对外说话通道

**输入**:
```json
{
  "sessionKey": "string",      // 目标会话标识
  "message": "string",         // 消息内容
  "priority": "normal"         // 优先级: normal|high|low
}
```

**输出**:
```json
{
  "success": true,
  "messageId": "msg_xxx",
  "timestamp": "2026-04-07T08:00:00Z"
}
```

**实现**:
- 调用 `sessions_send` API
- 支持 sessionKey 或 label 查找
- 自动路由到目标 Agent

---

### 2. READ_HISTORY（读取历史）

**功能**: 把结构化消息转换成 Agent 能理解的纯文本

**输入**:
```json
{
  "sessionKey": "string",      // 会话标识
  "limit": 10,                 // 返回条数
  "format": "markdown"         // 格式: markdown|plain|json
}
```

**输出**:
```json
{
  "success": true,
  "messages": [
    {
      "role": "user",
      "content": "消息内容",
      "timestamp": "2026-04-07T08:00:00Z"
    }
  ],
  "total": 50
}
```

**实现**:
- 调用 `sessions_history` API
- 支持多种格式输出
- 自动 Token 优化

---

### 3. CLAIM_TASKS（认领任务）

**功能**: 把聊天消息转换成任务，Agent 可以认领

**输入**:
```json
{
  "mode": "auto",              // 模式: auto|manual
  "skills": ["code", "data"],  // 技能标签
  "limit": 5                   // 最多认领数
}
```

**输出**:
```json
{
  "success": true,
  "tasks": [
    {
      "taskId": "task_xxx",
      "sessionKey": "agent:main:xxx",
      "message": "任务描述",
      "skills": ["code"],
      "priority": "high"
    }
  ]
}
```

**实现**:
- 扫描所有活跃会话
- 识别未认领任务
- 支持技能匹配

---

## 🏗️ 架构设计

### 分层架构

```
┌─────────────────────────────────────┐
│     MCP Client (Agent)             │
└──────────────┬──────────────────────┘
               │ JSON-RPC 2.0
┌──────────────▼──────────────────────┐
│     OpenClaw MCP Server             │
│  ┌────────────────────────────────┐ │
│  │  Tool Registry                │ │
│  │  - send_message               │ │
│  │  - read_history               │ │
│  │  - claim_tasks                │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  Handler Layer                │ │
│  │  - format_request             │ │
│  │  - call_openclaw_api          │ │
│  │  - format_response            │ │
│  └────────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │ HTTP API
┌──────────────▼──────────────────────┐
│     OpenClaw Gateway               │
│  - sessions_send                   │
│  - sessions_history                │
│  - sessions_list                   │
└─────────────────────────────────────┘
```

---

## 🔧 技术实现

### 1. MCP Server 实现

**框架**: Python `mcp` SDK

**核心代码**:
```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import httpx

app = Server("openclaw-mcp-server")

@app.call_tool()
async def send_message(sessionKey: str, message: str, priority: str = "normal"):
    """发送消息到指定会话"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:18789/api/sessions/send",
            json={
                "sessionKey": sessionKey,
                "message": message
            }
        )
    return TextContent(type="text", text=f"消息已发送: {response.json()['messageId']}")

@app.call_tool()
async def read_history(sessionKey: str, limit: int = 10, format: str = "markdown"):
    """读取会话历史"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:18789/api/sessions/{sessionKey}/history",
            params={"limit": limit}
        )
    messages = response.json()["messages"]
    return TextContent(type="text", text=format_messages(messages, format))

@app.call_tool()
async def claim_tasks(mode: str = "auto", skills: list = None, limit: int = 5):
    """认领任务"""
    # 扫描活跃会话
    sessions = await list_active_sessions()
    tasks = []
    for session in sessions:
        # 识别未认领任务
        session_tasks = await detect_tasks(session, skills)
        tasks.extend(session_tasks)
    return TextContent(type="text", text=format_tasks(tasks[:limit]))
```

---

### 2. 配置文件

**位置**: `/root/.openclaw/openclaw-mcp-server.json`

```json
{
  "server": {
    "name": "openclaw-mcp-server",
    "version": "1.0.0",
    "host": "localhost",
    "port": 3000
  },
  "openclaw": {
    "gatewayUrl": "http://localhost:18789",
    "apiKey": "your-api-key"
  },
  "tools": {
    "send_message": {
      "enabled": true,
      "rateLimit": 10
    },
    "read_history": {
      "enabled": true,
      "maxLimit": 100
    },
    "claim_tasks": {
      "enabled": true,
      "autoScan": true
    }
  }
}
```

---

## 🧪 测试计划

### 1. 单元测试

```python
# test_send_message.py
async def test_send_message():
    result = await send_message(
        sessionKey="agent:main:test",
        message="Hello from MCP!"
    )
    assert result.success == True
    assert result.messageId.startswith("msg_")

# test_read_history.py
async def test_read_history():
    result = await read_history(
        sessionKey="agent:main:test",
        limit=10,
        format="markdown"
    )
    assert result.success == True
    assert len(result.messages) <= 10

# test_claim_tasks.py
async def test_claim_tasks():
    result = await claim_tasks(
        mode="auto",
        skills=["code"],
        limit=5
    )
    assert result.success == True
    assert len(result.tasks) <= 5
```

### 2. 集成测试

```bash
# 启动 MCP Server
python -m openclaw_mcp_server

# 在另一个 Agent 中测试
codex -m opencode/minimax-m2.5-free run "
使用 openclaw-mcp-server 的 send_message 工具，
发送一条消息到 agent:main:test 会话
"
```

---

## 📚 使用文档

### Agent 如何使用

**1. 配置 MCP Client**

```json
// ~/.config/codex/mcp-servers.json
{
  "mcpServers": {
    "openclaw": {
      "command": "python",
      "args": ["-m", "openclaw_mcp_server"],
      "env": {
        "OPENCLAW_GATEWAY_URL": "http://localhost:18789"
      }
    }
  }
}
```

**2. 调用工具**

```python
# 在 Agent 中调用
from mcp.client import Client

client = Client()
await client.connect_to("openclaw")

# 发送消息
await client.call_tool("send_message", {
    "sessionKey": "agent:main:test",
    "message": "Hello from Agent!"
})

# 读取历史
history = await client.call_tool("read_history", {
    "sessionKey": "agent:main:test",
    "limit": 10
})

# 认领任务
tasks = await client.call_tool("claim_tasks", {
    "mode": "auto",
    "skills": ["code"]
})
```

---

## 🚀 实施计划

### Phase 1: 核心功能（2-3小时）
- [ ] 创建项目结构
- [ ] 实现 `send_message` 工具
- [ ] 实现 `read_history` 工具
- [ ] 实现 `claim_tasks` 工具
- [ ] 编写单元测试

### Phase 2: 集成测试（1小时）
- [ ] 启动 MCP Server
- [ ] 测试跨 Agent 通信
- [ ] 测试任务认领
- [ ] 性能测试

### Phase 3: 文档和优化（1小时）
- [ ] 编写使用文档
- [ ] 添加错误处理
- [ ] 性能优化
- [ ] 发布到 GitHub

---

## 💡 关键设计决策

### 1. 为什么用 MCP？

**标准化**: MCP 是 Model Context Protocol 的标准
**兼容性**: 支持多个 Agent（Codex、Claude Code）
**扩展性**: 易于添加新工具

### 2. 为什么是这三个工具？

**send_message**: 所有 Agent 都需要"说话"
**read_history**: 所有 Agent 都需要"记忆"
**claim_tasks**: 所有 Agent 都需要"任务"

### 3. 为什么支持多种格式？

**Markdown**: 人类易读
**Plain**: LLM 易处理
**JSON**: 程序易解析

---

## 🎯 成功标准

**功能完整性**:
- ✅ 3 个工具全部实现
- ✅ 支持主流 Agent（Codex、Claude Code）
- ✅ 错误处理完善

**性能指标**:
- ✅ 响应时间 < 100ms
- ✅ 并发支持 > 10 req/s
- ✅ 内存占用 < 100MB

**易用性**:
- ✅ 配置简单
- ✅ 文档完整
- ✅ 测试覆盖 > 80%

---

**设计完成！准备开始实施！** 🚀
