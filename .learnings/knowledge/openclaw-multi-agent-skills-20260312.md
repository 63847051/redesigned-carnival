# 📚 OpenClaw Multi-Agent 技能学习总结

**学习时间**: 2026-03-12 00:21
**来源**: OpenClaw 官方文档
**主题**: Multi-Agent Routing

---

## 🎯 核心概念

### 什么是 Agent？

一个 **Agent** 是一个完整的大脑，拥有独立的：

- **Workspace**（工作区）- 文件、AGENTS.md、SOUL.md、USER.md
- **State directory**（状态目录）- auth profiles, model registry
- **Session store**（会话存储）- 聊天历史 + 路由状态

### 关键路径

```
Config: ~/.openclaw/openclaw.json
State dir: ~/.openclaw
Workspace: ~/.openclaw/workspace（或 ~/.openclaw/workspace-<agentId>）
Agent dir: ~/.openclaw/agents/<agentId>/agent
Sessions: ~/.openclaw/agents/<agentId>/sessions
```

---

## 🚀 快速开始

### 1. 创建多个 Agent

```bash
# 创建工作助手
openclaw agents add work

# 创建编码助手
openclaw agents add coding

# 创建社交助手
openclaw agents add social
```

每个 Agent 会获得：
- 独立的 workspace（SOUL.md, AGENTS.md, USER.md）
- 独立的 agentDir
- 独立的 session store

### 2. 创建频道账户

为每个 Agent 在不同频道创建账户：

**Discord**:
- 每个 Agent 一个 bot
- 启用 Message Content Intent
- 复制每个 token

**Telegram**:
- 通过 BotFather 为每个 Agent 创建一个 bot
- 复制每个 token

**WhatsApp**:
- 为每个账户链接不同的电话号码
```bash
openclaw channels login --channel whatsapp --account work
```

### 3. 添加 Agent 和 Bindings

在配置文件中添加：

```json5
{
  agents: {
    list: [
      { id: "main", workspace: "~/.openclaw/workspace-main" },
      { id: "coding", workspace: "~/.openclaw/workspace-coding" },
      { id: "social", workspace: "~/.openclaw/workspace-social" },
    ],
  },
  bindings: [
    { agentId: "main", match: { channel: "discord", accountId: "default" } },
    { agentId: "coding", match: { channel: "discord", accountId: "coding" } },
    { agentId: "social", match: { channel: "whatsapp", accountId: "personal" } },
  ],
  channels: {
    discord: {
      accounts: {
        default: { token: "DISCORD_BOT_TOKEN_MAIN" },
        coding: { token: "DISCORD_BOT_TOKEN_CODING" },
      },
    },
    whatsapp: {
      accounts: {
        personal: { ... },
        work: { ... },
      },
    },
  },
}
```

### 4. 重启并验证

```bash
# 重启 Gateway
openclaw gateway restart

# 验证 bindings
openclaw agents list --bindings

# 检查频道状态
openclaw channels status --probe
```

---

## 🎯 多个 Agent = 多个人，多个个性

使用 **多个 Agent**，每个 `agentId` 成为完全独立的角色：

- **不同的电话号码/账户**（每个 channel accountId）
- **不同的个性**（每个 agent workspace 文件如 AGENTS.md 和 SOUL.md）
- **独立的 auth + sessions**（除非明确启用，否则没有交叉串扰）

这让 **多个人** 可以共享一个 Gateway 服务器，同时保持他们的 AI "大脑"和数据隔离。

---

## 📋 路由规则（消息如何选择 Agent）

Bindings 是**确定性**的，**最具体优先**：

1. `peer` match（精确的 DM/group/channel id）
2. `parentPeer` match（线程继承）
3. `guildId + roles`（Discord 角色路由）
4. `guildId`（Discord）
5. `teamId`（Slack）
6. `accountId` match for a channel
7. channel-level match（`accountId: "*"`）
8. fallback to default agent（`agents.list[].default`）

---

## 🔧 一个 WhatsApp 号码，多个人（DM 分割）

你可以将**不同的 WhatsApp DM** 路由到不同的 agent，同时保持在**一个 WhatsApp 账户**上。

匹配发送者 E.164（如 `+15551234567`）与 `peer.kind: "direct"`。回复仍然来自同一个 WhatsApp 号码（没有每 agent 发送者身份）。

**示例**：

```json5
{
  agents: {
    list: [
      { id: "alex", workspace: "~/.openclaw/workspace-alex" },
      { id: "mia", workspace: "~/.openclaw/workspace-mia" },
    ],
  },
  bindings: [
    {
      agentId: "alex",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230001" } },
    },
    {
      agentId: "mia",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230002" } },
    },
  ],
  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15551230001", "+15551230002"],
    },
  },
}
```

---

## 🎓 实战示例

### Discord Bots per Agent

每个 Discord bot 账户映射到唯一的 `accountId`。将每个账户绑定到一个 agent 并保持每个 bot 的 allowlist。

```json5
{
  agents: {
    list: [
      { id: "main", workspace: "~/.openclaw/workspace-main" },
      { id: "coding", workspace: "~/.openclaw/workspace-coding" },
    ],
  },
  bindings: [
    { agentId: "main", match: { channel: "discord", accountId: "default" } },
    { agentId: "coding", match: { channel: "discord", accountId: "coding" } },
  ],
  channels: {
    discord: {
      groupPolicy: "allowlist",
      accounts: {
        default: {
          token: "DISCORD_BOT_TOKEN_MAIN",
          guilds: {
            "123456789012345678": {
              channels: {
                "222222222222222222": { allow: true, requireMention: false },
              },
            },
          },
        },
        coding: {
          token: "DISCORD_BOT_TOKEN_CODING",
          guilds: {
            "123456789012345678": {
              channels: {
                "333333333333333333": { allow: true, requireMention: false },
              },
            },
          },
        },
      },
    },
  },
}
```

---

## 💡 关键要点

### Auth Profiles 是 Per-Agent

每个 agent 从自己的文件读取：
```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

Main agent credentials **不会**自动共享。永远不要在 agents 之间重用 `agentDir`（这会导致 auth/session 冲突）。

### Skills 是 Per-Agent

通过每个 workspace 的 `skills/` 文件夹，共享技能可从 `~/.openclaw/skills` 获得。

---

## 🚀 下一步

**为你的系统创建多个 Agent**：

```bash
# 创建室内设计专家 Agent
openclaw agents add builder

# 创建技术专家 Agent
openclaw agents add tech

# 创建小蓝 Agent
openclaw agents add ops
```

每个 Agent 都可以有独立的：
- SOUL.md（个性）
- USER.md（用户偏好）
- Skills（技能）
- Session（会话历史）

---

*学习完成时间: 2026-03-12 00:21*
*来源: OpenClaw 官方文档 - Multi-Agent Routing*
*版本: 自主进化系统 5.8*
