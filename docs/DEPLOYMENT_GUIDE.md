# 系统部署指南

**版本**: v5.12.0
**更新时间**: 2026-03-15
**适用系统**: OpenCloudOS / CentOS / RHEL 系列

---

## 📋 目录

1. [环境要求](#环境要求)
2. [安装步骤](#安装步骤)
3. [配置说明](#配置说明)
4. [启动和验证](#启动和验证)
5. [常见问题](#常见问题)

---

## 环境要求

### 系统要求
- **操作系统**: OpenCloudOS 9+ / CentOS 7+ / RHEL 7+
- **架构**: x86_64
- **内存**: 最低 1GB，推荐 2GB+
- **磁盘**: 最低 20GB，推荐 50GB+

### 软件依赖

#### Node.js
```bash
# 检查 Node.js 版本（需要 v18+）
node --version

# 如果未安装，使用 nvm 安装
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
```

#### Python
```bash
# 检查 Python 版本（需要 3.8+）
python3 --version

# 安装基础包
pip3 install requests beautifulsoup4
```

#### Git
```bash
# 检查 Git 版本
git --version

# 如果未安装
yum install -y git
```

---

## 安装步骤

### 1. 克隆仓库

```bash
# 克隆主仓库
git clone https://github.com/63847051/redesigned-carnival.git
cd redesigned-carnival

# 或者使用你的 fork
git clone https://github.com/YOUR_USERNAME/redesigned-carnival.git
cd redesigned-carnival
```

### 2. 安装 OpenClaw

```bash
# 使用 npm 全局安装
npm install -g openclaw@latest

# 验证安装
openclaw --version
```

### 3. 配置系统

#### 3.1 复制配置文件

```bash
# 创建配置目录
mkdir -p ~/.openclaw

# 复制仓库中的配置文件
cp openclaw.json ~/.openclaw/
cp -r workspace ~/.openclaw/
```

#### 3.2 设置 API Keys

参考 `docs/SECRETS_SETUP.md` 配置你的 API Keys：

```bash
# 编辑配置文件
nano ~/.openclaw/openclaw.json
```

**重要字段**:
- `models.providers.*.apiKey` - 各模型提供商的 API Key
- `channels.feishu.appId` - 飞书应用 ID
- `channels.feishu.appSecret` - 飞书应用密钥

### 4. 安装插件

```bash
# 飞书插件
openclaw plugin install @larksuite/openclaw-lark

# QQ 机器人（可选）
openclaw plugin install @sliverp/qqbot

# 钉钉机器人（可选）
openclaw plugin install @largezhou/ddingtalk

# 企业微信（可选）
openclaw plugin install @mocrane/wecom
```

### 5. 配置飞书应用

#### 5.1 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`

#### 5.2 配置权限

在飞书开放平台，为应用开启以下权限：

**基础权限**:
- 获取与发送单聊消息
- 获取与发送群组消息
- 读取用户信息
- 获取用户基本信息

**高级权限**（如需要）:
- 查看、评论和导出云文档
- 获取和发送日历事件
- 任务管理

#### 5.3 发布应用

- 在飞书开放平台发布应用
- 获取应用凭证
- 在企业内启用应用

---

## 配置说明

### OpenClaw 配置文件结构

```json
{
  "models": {
    "providers": {
      "glmcode": {
        "baseUrl": "https://open.bigmodel.cn/api/anthropic",
        "apiKey": "YOUR_GLMCODE_API_KEY"
      }
    }
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "YOUR_FEISHU_APP_ID",
      "appSecret": "YOUR_FEISHU_APP_SECRET",
      "domain": "feishu"
    }
  },
  "gateway": {
    "port": 18789,
    "mode": "local"
  }
}
```

### 模型配置

系统支持多个模型提供商：

**智谱 AI (GLM)**:
- 模型: GLM-5, GLM-4.7, GLM-4.6, GLM-4.5-Air
- 用途: 中文任务、设计任务、复杂决策

**Groq**:
- 模型: Llama-3.3-70B, Mixtral-8x7B
- 用途: 代码任务、超快速响应

**Google**:
- 模型: Gemini-2.5-Flash
- 用途: 日常对话、快速问答

**NVIDIA**:
- 模型: GPT-OSS-120B
- 用途: 代码编写、技术任务

### 工作区配置

工作区位于: `~/.openclaw/workspace`

**重要目录**:
- `docs/` - 文档
- `scripts/` - 自动化脚本
- `skills/` - 技能目录
- `memory/` - 记忆系统
- `.learnings/` - 学习记录

---

## 启动和验证

### 1. 启动 OpenClaw Gateway

```bash
# 启动服务
openclaw gateway start

# 查看状态
openclaw gateway status

# 查看日志
tail -f ~/.openclaw/logs/gateway.log
```

### 2. 验证飞书连接

#### 2.1 私聊测试
1. 在飞书中找到你的机器人应用
2. 发送消息: "你好"
3. 应该收到回复

#### 2.2 群聊测试
1. 将机器人加入飞书群
2. 在群里 @机器人
3. 发送: "@机器人 你好"
4. 应该收到回复

### 3. 验证核心功能

#### 测试 1: 系统状态
```
@机器人 系统状态
```

#### 测试 2: 查看日程
```
@机器人 今天有什么日程
```

#### 测试 3: 工作日志
```
@机器人 记录工作：完成系统部署
```

### 4. 检查日志

```bash
# Gateway 日志
tail -f ~/.openclaw/logs/gateway.log

# 错误日志
tail -f ~/.openclaw/logs/errors.log

# 性能日志
tail -f ~/.openclaw/logs/performance.log
```

---

## 常见问题

### Q1: Gateway 无法启动

**检查步骤**:
```bash
# 1. 检查端口占用
lsof -i:18789

# 2. 检查配置文件
cat ~/.openclaw/openclaw.json | jq .

# 3. 查看详细日志
openclaw gateway start --verbose
```

**常见原因**:
- 端口被占用
- 配置文件格式错误
- API Key 无效

### Q2: 飞书机器人无响应

**检查步骤**:
```bash
# 1. 检查 Gateway 状态
openclaw gateway status

# 2. 检查飞书配置
cat ~/.openclaw/credentials/feishu-pairing.json

# 3. 测试飞书连接
openclaw doctor
```

**常见原因**:
- 应用未发布
- 权限未开启
- 网络连接问题

### Q3: API 限流

**症状**: 模型调用失败，提示限流

**解决方案**:
- 系统已配置三层 fallback 防护
- 主模型限流时自动切换到备用模型
- 检查 `openclaw.json` 中的 fallback 配置

### Q4: 内存不足

**症状**: 系统变慢，进程被杀

**解决方案**:
```bash
# 1. 检查内存使用
free -h

# 2. 清理日志文件
rm -rf ~/.openclaw/logs/*.log

# 3. 重启 Gateway
openclaw gateway restart
```

### Q5: 磁盘空间不足

**症状**: 无法写入文件

**解决方案**:
```bash
# 1. 检查磁盘使用
df -h

# 2. 清理备份
rm -rf ~/.openclaw/backups/daily/*

# 3. 清理日志
rm -rf ~/.openclaw/logs/*.log
```

---

## 高级配置

### 1. 多 Agent 配置

系统支持创建多个独立 Agent：

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "name": "主控"
      },
      {
        "id": "tech",
        "name": "技术",
        "workspace": "/root/.openclaw/workspace-tech"
      }
    ]
  }
}
```

### 2. 模型路由配置

根据任务类型自动选择模型：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "glmcode/glm-4.7",
        "fallback": [
          "glmcode/glm-4.6",
          "google/gemini-2.5-flash",
          "groq/llama-3.3-70b-versatile"
        ]
      }
    }
  }
}
```

### 3. 技能隔离规则

配置不同的专家 Agent 处理不同任务：

参考 `workspace/agents/skill-isolation-rules.md`

---

## 维护和更新

### 定期更新

```bash
# 更新 OpenClaw
npm update -g openclaw

# 更新插件
openclaw plugin update @larksuite/openclaw-lark

# 更新仓库
cd ~/redesigned-carnival
git pull origin master
```

### 备份

```bash
# 手动备份
bash ~/.openclaw/workspace/scripts/backup-before-update.sh

# 备份配置
cp ~/.openclaw/openclaw.json ~/backup/
cp -r ~/.openclaw/workspace ~/backup/
```

### 监控

```bash
# 系统状态
openclaw gateway status

# 性能监控
cat ~/.openclaw/logs/performance.log

# 错误日志
cat ~/.openclaw/logs/errors.log
```

---

## 获取帮助

### 文档
- GitHub: https://github.com/63847051/redesigned-carnival
- Wiki: [待添加]

### 社区
- OpenClaw Discord: [待添加]
- 飞书群: [待添加]

### 问题反馈
- GitHub Issues: https://github.com/63847051/redesigned-carnival/issues

---

**部署指南版本**: v5.12.0
**最后更新**: 2026-03-15
**维护者**: 幸运小行星
