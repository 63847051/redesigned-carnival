# OpenClaw MCP Server - 完整测试与部署指南

**版本**: v2.1
**更新**: 2026-04-07

---

## 🎯 项目概述

OpenClaw MCP Server 是一个基于 MCP 协议的跨 Agent 协作工具，通过 OpenClaw CLI 实现标准化接口。

### 核心功能

1. **list_sessions** - 列出所有会话
2. **send_message** - 发送消息到指定渠道
3. **get_status** - 获取系统状态

---

## 📦 安装

### 1. 安装依赖

```bash
cd /root/.openclaw/workspace/projects/openclaw-mcp-server

# 安装 Python 依赖
pip install mcp

# 验证安装
python -c "import mcp; print(mcp.__version__)"
```

### 2. 验证 OpenClaw CLI

```bash
# 检查版本
openclaw --version

# 测试列出会话
openclaw sessions --json | head -20
```

---

## 🧪 测试

### 快速测试

```bash
# 进入项目目录
cd /root/.openclaw/workspace/projects/openclaw-mcp-server

# 测试列出会话
openclaw sessions --json --active 120

# 测试获取状态
systemctl --user is-active openclaw-gateway
```

### 集成测试

创建测试脚本 `test_mcp.sh`:

```bash
#!/bin/bash

echo "🧪 OpenClaw MCP Server 测试"
echo "=============================="
echo ""

# 测试 1: 列出会话
echo "📊 测试 1: 列出活跃会话"
openclaw sessions --json --active 120 | python -m json.tool | head -30
echo ""

# 测试 2: 获取状态
echo "📋 测试 2: 系统状态"
echo "Gateway: $(systemctl --user is-active openclaw-gateway)"
echo "版本: $(openclaw --version)"
echo ""

# 测试 3: 发送消息（可选）
echo "📤 测试 3: 发送测试消息"
echo "是否发送？(y/n)"
read -r answer

if [ "$answer" = "y" ]; then
    openclaw message send \
        --channel feishu \
        --target "ou_e356e8a931ed343100de9c449020964b" \
        --message "MCP Server 测试消息" \
        --json
fi

echo ""
echo "✅ 测试完成"
```

运行测试:

```bash
chmod +x test_mcp.sh
./test_mcp.sh
```

---

## 🚀 部署

### 方式 1: 作为 MCP Server 运行

```bash
# 启动 MCP Server（stdio 模式）
cd /root/.openclaw/workspace/projects/openclaw-mcp-server
python -m openclaw_mcp_server
```

### 方式 2: 在 Agent 中使用

#### Codex 配置

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
      "cwd": "/root/.openclaw/workspace/projects/openclaw-mcp-server"
    }
  }
}
```

#### Claude Code 配置

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
      "cwd": "/root/.openclaw/workspace/projects/openclaw-mcp-server"
    }
  }
}
```

---

## 📚 使用示例

### 在 Agent 中调用

```python
# 列出活跃会话
await call_tool("list_sessions", {
    "activeMinutes": 120,
    "allAgents": True,
    "json": True
})

# 发送消息到飞书
await call_tool("send_message", {
    "channel": "feishu",
    "target": "ou_e356e8a931ed343100de9c449020964b",
    "message": "Hello from MCP!"
})

# 获取系统状态
await call_tool("get_status", {})
```

---

## 🔧 故障排查

### 问题 1: MCP SDK 未安装

**错误**: `ModuleNotFoundError: No module named 'mcp'`

**解决**:
```bash
pip install mcp
```

### 问题 2: OpenClaw CLI 不可用

**错误**: `openclaw: command not found`

**解决**:
```bash
# 检查安装
which openclaw

# 重新安装
npm install -g openclaw
```

### 问题 3: 权限问题

**错误**: `Permission denied`

**解决**:
```bash
# 检查 Gateway 状态
systemctl --user status openclaw-gateway

# 重启 Gateway
systemctl --user restart openclaw-gateway
```

---

## 📊 架构说明

### MCP 工具链

```
Agent (Codex/Claude Code)
    ↓ MCP Protocol
OpenClaw MCP Server
    ↓ subprocess
OpenClaw CLI
    ↓ WebSocket
OpenClaw Gateway
    ↓
目标渠道 (Feishu/Telegram)
```

### 数据流

1. Agent 调用 MCP 工具
2. MCP Server 接收请求
3. 调用 OpenClaw CLI
4. CLI 通过 Gateway 发送消息
5. 返回结果给 Agent

---

## 🎯 下一步优化

1. **添加更多工具**
   - `claim_tasks` - 任务认领
   - `read_history` - 历史记录
   - `create_session` - 创建会话

2. **性能优化**
   - 缓存会话列表
   - 异步处理
   - 批量操作

3. **错误处理**
   - 重试机制
   - 超时控制
   - 详细日志

---

## 💡 关键设计决策

### 为什么用 subprocess 而不是 HTTP API？

**原因**:
- OpenClaw 没有 REST API
- CLI 是官方推荐方式
- 避免版本兼容问题

### 为什么只实现 3 个工具？

**原因**:
- 覆盖核心功能
- 快速验证价值
- 渐进式开发

---

## ✅ 成功标准

- [x] 列出会话功能正常
- [x] 发送消息功能正常
- [x] 获取状态功能正常
- [x] 支持 Codex 集成
- [x] 支持 Claude Code 集成

---

**OpenClaw MCP Server v2.1 - 让 Agent 协作更简单！** 🚀
