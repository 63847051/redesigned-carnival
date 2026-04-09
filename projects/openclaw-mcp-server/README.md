# OpenClaw MCP Server

**版本**: v1.0
**创建时间**: 2026-04-07
**基于**: Slock chat-bridge MCP 设计

---

## 🎯 核心目标

提供跨 Agent 协作的标准化接口，让所有 Agent 通过统一工具链协作。

---

## 🚀 快速开始

### 安装

```bash
# 克隆项目
cd /root/.openclaw/workspace/projects/openclaw-mcp-server

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 配置

创建配置文件 `config.json`:

```json
{
  "gatewayUrl": "http://localhost:18789",
  "apiKey": "your-api-key",
  "logLevel": "INFO"
}
```

### 启动

```bash
# 启动 MCP Server
python -m openclaw_mcp_server
```

---

## 📊 MCP 工具链

### 1. send_message（发送消息）

**功能**: 发送消息到指定的 OpenClaw 会话

**参数**:
- `sessionKey` (required): 目标会话标识
- `message` (required): 消息内容
- `priority` (optional): 优先级 (normal|high|low)

**示例**:
```json
{
  "sessionKey": "agent:main:session-id",
  "message": "Hello from MCP!",
  "priority": "normal"
}
```

---

### 2. read_history（读取历史）

**功能**: 读取会话历史记录

**参数**:
- `sessionKey` (required): 会话标识
- `limit` (optional): 返回条数 (默认: 10)
- `format` (optional): 输出格式 (markdown|plain|json)

**示例**:
```json
{
  "sessionKey": "agent:main:session-id",
  "limit": 20,
  "format": "markdown"
}
```

---

### 3. claim_tasks（认领任务）

**功能**: 认领待处理的任务

**参数**:
- `mode` (optional): 匹配模式 (auto|manual)
- `skills` (optional): 技能标签 (如 ["code", "data"])
- `limit` (optional): 最多认领数 (默认: 5)

**示例**:
```json
{
  "mode": "auto",
  "skills": ["code", "data"],
  "limit": 5
}
```

---

## 🔧 在 Agent 中使用

### Codex 配置

编辑 `~/.config/codex/mcp-servers.json`:

```json
{
  "mcpServers": {
    "openclaw": {
      "command": "python",
      "args": [
        "-m",
        "openclaw_mcp_server"
      ],
      "env": {
        "OPENCLAW_GATEWAY_URL": "http://localhost:18789",
        "OPENCLAW_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Claude Code 配置

编辑 `~/.config/claude-code/mcp-servers.json`:

```json
{
  "mcpServers": {
    "openclaw": {
      "command": "python",
      "args": [
        "-m",
        "openclaw_mcp_server"
      ],
      "env": {
        "OPENCLAW_GATEWAY_URL": "http://localhost:18789",
        "OPENCLAW_API_KEY": "your-api-key"
      }
    }
  }
}
```

### 使用示例

在 Agent 中调用:

```python
# 发送消息
await call_tool("send_message", {
    "sessionKey": "agent:main:test",
    "message": "Hello from Agent!"
})

# 读取历史
history = await call_tool("read_history", {
    "sessionKey": "agent:main:test",
    "limit": 10
})

# 认领任务
tasks = await call_tool("claim_tasks", {
    "mode": "auto",
    "skills": ["code"]
})
```

---

## 🧪 测试

### 单元测试

```bash
# 运行测试
python -m pytest tests/
```

### 集成测试

```bash
# 启动 MCP Server
python -m openclaw_mcp_server

# 在另一个终端测试
python tests/integration_test.py
```

---

## 📚 架构设计

详细设计文档: [DESIGN.md](./DESIGN.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

---

## 📄 许可证

MIT License

---

**OpenClaw MCP Server - 让 Agent 协作更简单！** 🚀
