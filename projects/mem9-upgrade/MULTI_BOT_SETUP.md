# 多飞书机器人配置指南

**目标**: 配置多个飞书机器人，每个对应不同的 Agent
**更新**: 2026-03-15

---

## 🎯 配置目标

### 机器人规划

**机器人 1: 主助手（Lucky）**
- App ID: `cli_a90df9a07db8dcb1`（已有）
- 用途: 日常助手
- Agent: main

**机器人 2: 工作助手**
- App ID: 需要创建
- 用途: 工作相关
- Agent: work（新建）

---

## 📋 步骤 1: 创建新的飞书机器人

### 方法 1: 一键创建（推荐）

**访问链接**: https://open.feishu.cn/page/openclaw?form=multiAgent

1. 打开链接
2. 扫码创建新机器人
3. 获取新的 App ID 和 App Secret

### 方法 2: 手动创建

1. 打开飞书开放平台: https://open.feishu.cn/
2. 创建应用
3. 启用机器人能力
4. 获取凭证

---

## 📋 步骤 2: 创建新的 Agent

### 创建工作助手 Agent

```bash
# 创建新的工作空间
mkdir -p ~/.openclaw/workspace-work

# 创建配置
cat > ~/.openclaw/workspace-work/AGENT.md << 'EOF'
# 工作助手 Agent

**名称**: 工作助手
**用途**: 处理工作相关任务
**模型**: GLM-4.7

**主要功能**:
- 工作日志管理
- 任务跟踪
- 项目管理
EOF
```

---

## 📋 步骤 3: 更新配置文件

### 完整配置示例

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "name": "主助手",
        "default": true,
        "workspace": "~/.openclaw/workspace",
        "model": {
          "primary": "glmcode/glm-4.7"
        }
      },
      {
        "id": "work",
        "name": "工作助手",
        "workspace": "~/.openclaw/workspace-work",
        "model": {
          "primary": "glmcode/glm-4.7"
        }
      }
    ]
  },
  
  "session": {
    "dmScope": "per-account-channel-peer"
  },
  
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_a90df9a07db8dcb1",
      "appSecret": "7CERQM7oIW4YTEbSaieAfZMplHBxJTPJ",
      "streaming": true,
      "threadSession": true,
      "requireMention": false,
      
      "accounts": {
        "default": {},
        
        "work": {
          "appId": "cli_work_yyy",  // 替换为实际的 App ID
          "appSecret": "work_secret_yyy",  // 替换为实际的 App Secret
          "botName": "工作助手",
          "dmPolicy": "allowlist",
          "allowFrom": ["ou_e356e8a931ed343100de9c449020964b"]  // 你的用户 ID
        }
      },
      
      "groupPolicy": "open"
    }
  },
  
  "bindings": [
    { 
      "agentId": "main", 
      "match": { "channel": "feishu", "accountId": "default" } 
    },
    { 
      "agentId": "work", 
      "match": { "channel": "feishu", "accountId": "work" } 
    }
  ]
}
```

---

## 📋 步骤 4: 应用配置

### 方法 1: 手动编辑

```bash
# 备份当前配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup

# 编辑配置
nano ~/.openclaw/openclaw.json
```

### 方法 2: 使用命令

```bash
# 设置会话隔离
openclaw config set session.dmScope "per-account-channel-peer" --json

# 重启 Gateway
systemctl --user restart openclaw-gateway
```

---

## 📋 步骤 5: 验证配置

### 检查路由绑定

```bash
openclaw agents bindings
```

**期望输出**：
```
• main → feishu:default
• work → feishu:work
```

### 检查渠道状态

```bash
openclaw channels list
```

### 查看日志

```bash
openclaw logs --follow
```

---

## 🎯 使用方法

### 与主助手对话

在飞书中私聊 **Lucky**（主助手机器人）：
```
你好
```
→ 路由到 `main` Agent

### 与工作助手对话

在飞书中私聊 **工作助手**（新机器人）：
```
帮我记录工作日志
```
→ 路由到 `work` Agent

---

## 🔍 故障排查

### 问题 1: 机器人没有响应

**检查**：
```bash
openclaw gateway status
openclaw logs --follow
```

### 问题 2: 路由不正确

**检查**：
```bash
openclaw agents bindings
```

### 问题 3: 会话混乱

**检查**：
```bash
openclaw config get session.dmScope
```

应该是 `per-account-channel-peer`

---

## 📝 配置检查清单

- [ ] 创建新的飞书机器人
- [ ] 获取新的 App ID 和 App Secret
- [ ] 创建新的工作空间
- [ ] 更新 openclaw.json
- [ ] 设置会话隔离
- [ ] 配置路由绑定
- [ ] 重启 Gateway
- [ ] 验证配置

---

## 🎯 准备好了吗？

**需要的**：
1. 新的飞书机器人 App ID 和 App Secret
2. 确认要创建工作助手 Agent

**下一步**：
1. 创建新机器人
2. 告诉我新的凭证
3. 我帮你更新配置

---

**准备好了吗？开始创建新的机器人吧！** 🚀
