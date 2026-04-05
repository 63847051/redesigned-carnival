# 🚀 OpenClaw 自主进化系统 v7.0 - 完整部署指南

**生成时间**: 2026-04-05 08:40
**系统版本**: v7.0（TradingAgents 集成版）
**目标**: 在新服务器上复刻一模一样的系统

---

## 📋 目录

1. [系统概览](#系统概览)
2. [硬件要求](#硬件要求)
3. [软件依赖](#软件依赖)
4. [安装步骤](#安装步骤)
5. [配置文件](#配置文件)
6. [核心能力](#核心能力)
7. [技能系统](#技能系统)
8. [脚本工具](#脚本工具)
9. [数据备份](#数据备份)
10. [故障排查](#故障排查)

---

## 系统概览

### 🧠 系统架构

**自主进化系统 v7.0** 是一个整合了以下能力的完整系统：

- ✅ **PAI 学习系统** - 持续学习和进化
- ✅ **超级进化大脑** - 6层防护机制
- ✅ **自主迭代系统** - 5步流程 + 压缩
- ✅ **WAL Protocol** - 状态恢复
- ✅ **结构化记忆系统** - 长期记忆管理
- ✅ **TradingAgents 特性** - 辩论机制 + 分层决策
- ✅ **Multi-Agent 系统** - 大领导 + 3个专业 Agent
- ✅ **三重防护机制** - 永不违反关键规则
- ✅ **HeyCube AI 记忆管家** - 结构化个人档案
- ✅ **DeerFlow 技能库** - 26+ 专业技能
- ✅ **上下文优化模块** - Token 节省 40%
- ✅ **MCP 增强模块** - OAuth + 工具扩展

### 🎯 核心理念

> **"专业的事交给专业的人"**

**工作流程**：
```
用户 → 大领导 → 分析任务 → 分配给专家 → 执行 → 汇报
```

**Agent 团队**：
- **大领导** 🎯 - 主控 Agent（GLM-4.7）
- **小新** 💻 - 技术支持（opencode/minimax-m2.5-free）
- **小蓝** 📋 - 工作日志（GLM-4.5-Air）
- **设计专家** 🏠 - 室内设计（GLM-4.6）

---

## 硬件要求

### 最低配置

- **CPU**: 2 核心以上
- **内存**: 4GB 以上（推荐 8GB）
- **磁盘**: 20GB 以上可用空间
- **网络**: 稳定的互联网连接

### 推荐配置

- **CPU**: 4 核心
- **内存**: 8GB
- **磁盘**: 50GB SSD
- **系统**: OpenCloudOS 9 / CentOS 8+ / Ubuntu 20.04+

### 当前生产环境

- **服务器**: 腾讯云轻量服务器
- **公网 IP**: 43.134.63.176
- **内网 IP**: 10.3.0.8
- **系统**: OpenCloudOS (Linux 6.6.117-45.1.oc9.x86_64)
- **Node.js**: v22.22.0
- **Python**: 3.11.6

---

## 软件依赖

### 1. 系统工具

```bash
# 更新系统
yum update -y  # OpenCloudOS/CentOS
# 或
apt update && apt upgrade -y  # Ubuntu

# 安装基础工具
yum install -y git curl wget bash python3 python3-pip nodejs npm
```

### 2. Node.js 环境

```bash
# 安装 Node.js v22（推荐）
curl -fsSL https://rpm.nodesource.com/setup_22.x | bash -
yum install -y nodejs

# 验证安装
node --version  # 应该显示 v22.22.0 或更高
npm --version
```

### 3. Python 环境

```bash
# 安装 Python 3.11
yum install -y python3 python3-pip python3-devel

# 验证安装
python3 --version  # 应该显示 3.11.6 或更高
pip3 --version
```

### 4. OpenClaw CLI

```bash
# 安装 OpenClaw
npm install -g openclaw

# 验证安装
openclaw --version
openclaw doctor
```

### 5. OpenCode CLI（重要！）

```bash
# 安装 OpenCode Agent
npm install -g @opencode/cli

# 验证安装
opencode --version  # 应该显示 1.2.17 或更高

# 查看可用模型
opencode models
```

### 6. Python 依赖包

```bash
# 安装核心依赖
pip3 install --upgrade pip
pip3 install beautifulsoup4 requests scrapling html2text

# 验证安装
pip3 list | grep -E "scrapling|html2text|beautifulsoup4"
```

---

## 安装步骤

### 步骤 1: 克隆配置仓库

```bash
# 进入工作目录
cd /root

# 克隆 GitHub 仓库
git clone https://github.com/63847051/redesigned-carnival.git openclaw-workspace

# 备份原始 workspace（如果存在）
mv /root/.openclaw/workspace /root/.openclaw/workspace.backup.$(date +%Y%m%d)

# 创建符号链接
ln -s /root/openclaw-workspace /root/.openclaw/workspace
```

### 步骤 2: 配置 OpenClaw

```bash
# 初始化 OpenClaw
openclaw init

# 配置模型提供商
openclaw config set models.mode merge
openclaw config set models.providers.glmcode.baseUrl https://open.bigmodel.cn/api/anthropic
openclaw config set models.providers.glmcode.apiKey YOUR_GLMCODE_API_KEY
openclaw config set models.providers.glmcode.api anthropic-messages
```

**获取 API Key**：
- 智谱 AI: https://open.bigmodel.cn/
- 注册账号 → 创建 API Key

### 步骤 3: 配置 OpenCode Agent

```bash
# 初始化 OpenCode
opencode init

# 登录 OpenCode（免费）
opencode login

# 验证模型可用性
opencode models opencode --verbose
```

### 步骤 4: 安装技能系统

```bash
# 进入 workspace
cd /root/.openclaw/workspace

# 技能已包含在仓库中，无需额外安装
# 验证技能数量
find . -name "SKILL.md" -type f | wc -l  # 应该显示 180+
```

### 步骤 5: 配置飞书集成（可选）

```bash
# 编辑配置文件
vi /root/.openclaw/openclaw.json

# 添加飞书配置
{
  "channels": {
    "feishu": {
      "appId": "cli_a90df9a07db8dcb1",
      "appSecret": "YOUR_FEISHU_APP_SECRET",
      "encryptKey": "YOUR_ENCRYPT_KEY",
      "verificationToken": "YOUR_VERIFICATION_TOKEN"
    }
  }
}
```

**获取飞书凭证**：
- 飞书开放平台: https://open.feishu.cn/
- 创建企业自建应用 → 获取凭证

### 步骤 6: 启动 Gateway

```bash
# 启动 OpenClaw Gateway
openclaw gateway start

# 检查状态
systemctl --user status openclaw-gateway

# 查看日志
journalctl --user -u openclaw-gateway -f
```

### 步骤 7: 验证安装

```bash
# 运行诊断
openclaw doctor

# 检查 Gateway
curl http://localhost:18789/health

# 测试对话
echo "测试消息" | openclaw chat
```

---

## 配置文件

### 1. OpenClaw 主配置

**位置**: `/root/.openclaw/openclaw.json`

**核心配置**：
```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "glmcode": {
        "baseUrl": "https://open.bigmodel.cn/api/anthropic",
        "apiKey": "YOUR_GLMCODE_API_KEY",
        "api": "anthropic-messages",
        "models": [
          {"id": "glm-5", "name": "GLM-5"},
          {"id": "glm-4.7", "name": "GLM-4.7"},
          {"id": "glm-4.6", "name": "GLM-4.6"},
          {"id": "glm-4.5-air", "name": "GLM-4.5-Air"},
          {"id": "glm-4.5", "name": "GLM-4.5"}
        ]
      },
      "groq": {
        "baseUrl": "https://api.groq.com/openai/v1",
        "apiKey": "YOUR_GROQ_API_KEY",
        "models": [
          {"id": "llama-3.3-70b-versatile", "name": "Llama-3.3-70B"}
        ]
      }
    }
  },
  "defaultModel": "glmcode/glm-4.7",
  "runtime": "agent=main",
  "shell": "bash"
}
```

### 2. Workspace 核心文件

**位置**: `/root/.openclaw/workspace/`

**必需文件**：
```
workspace/
├── SOUL.md              # 系统灵魂（进化能力）
├── AGENTS.md            # Agent 团队规则
├── IDENTITY.md          # 大领导身份
├── TOOLS.md             # 工具配置
├── MEMORY.md            # 长期记忆
├── USER.md              # 用户信息
├── HEARTBEAT.md         # 心跳检查
├── scripts/             # 脚本工具（60+）
├── skills/              # 技能系统（180+）
├── agents/              # Agent 配置
├── docs/                # 文档
└── memory/              # 记忆存储
```

### 3. 关键脚本权限

```bash
# 确保所有脚本可执行
chmod +x /root/.openclaw/workspace/scripts/*.sh
chmod +x /root/.openclaw/workspace/skills/*/scripts/*.sh

# 验证权限
ls -la /root/.openclaw/workspace/scripts/ | head -20
```

---

## 核心能力

### 🧠 自主进化系统

**位置**: `/root/.openclaw/workspace/scripts/self-evolution-system.sh`

**功能**：
- PAI 学习系统
- 超级进化大脑
- 6层防护机制
- 错误模式分析
- 自动学习

**使用**：
```bash
# 手动触发进化
bash /root/.openclaw/workspace/scripts/self-evolution-system.sh

# 查看进化报告
cat /root/.openclaw/workspace/.learnings/evolution-reports/latest.md
```

### 🛡️ 三重防护机制

**位置**: `/root/.openclaw/workspace/scripts/check-critical-rules.sh`

**功能**：
- 第1重：确认词白名单
- 第2重：操作前检查清单
- 第3重：阶段性确认机制

**关键规则**：
- RULE-001: 重要操作必须等待确认
- RULE-004: OpenCode CLI 正确使用
- RULE-005: 备份前必须更新 README.md

**使用**：
```bash
# 检查规则状态
bash /root/.openclaw/workspace/scripts/check-critical-rules.sh

# 查看规则详情
cat /root/.openclaw/workspace/.learnings/rules/critical-rule-*.md
```

### 🎯 Multi-Agent 系统

**大领导**（主控）：
- 聊天、分配、监督、汇报
- 模型: GLM-4.7

**小新**（技术）：
- 代码、爬虫、数据、API
- 模型: opencode/minimax-m2.5-free
- 调用: `opencode -m opencode/minimax-m2.5-free run "任务"`

**小蓝**（日志）：
- 日志、记录、工作、任务
- 模型: GLM-4.5-Air
- 调用: `sessions_spawn -runtime subagent -model glmcode/glm-4.5-air`

**设计专家**（设计）：
- 设计、图纸、平面图
- 模型: GLM-4.6
- 调用: `sessions_spawn -runtime subagent -model glmcode/glm-4.6`

### 🧠 记忆系统

**MEMORY.md**（长期记忆）：
- 位置: `/root/.openclaw/workspace/MEMORY.md`
- 大小: < 3000 字符（压缩版）
- 更新: 每日自动整理

**每日日志**：
- 位置: `/root/.openclaw/workspace/memory/YYYY-MM-DD.md`
- 格式: Markdown
- 归档: 30 天后自动归档

**HeyCube AI**（结构化档案）：
- 位置: `/root/.openclaw/workspace/personal-db.sqlite`
- CLI: `/root/.openclaw/workspace/scripts/personal-db.py`
- 功能: 8 大域分类

**使用**：
```bash
# 搜索记忆
~/.agents/skills/memory-search-hook/scripts/search.sh "关键词"

# 更新记忆
~/.agents/skills/memory-update/SKILL.md "内容" "important"

# 查看健康状态
bash /root/.openclaw/workspace/scripts/heartbeat-memory-check.sh
```

---

## 技能系统

### 📊 技能统计

- **总技能数**: 180+
- **核心技能**: 42
- **DeerFlow 技能**: 16
- **自定义技能**: 30+

### 🎯 重要技能

**1. feishu-doc** - 飞书文档操作
- 位置: `~/.local/share/pnpm/global/5/.pnpm/openclaw@2026.4.2_@napi-rs+canvas@0.1.97/node_modules/openclaw/dist/extensions/feishu/skills/feishu-doc/SKILL.md`
- 功能: 读写飞书文档

**2. web-content-fetcher** - 网页内容提取
- 位置: `/root/.openclaw/workspace/skills/web-content-fetcher/`
- 支持: 微信、GitHub、知乎、CSDN
- 依赖: scrapling, html2text

**3. deerflow-skill-creator** - 技能创建
- 位置: `/root/.openclaw/workspace/skills/deerflow-skill-creator/`
- 功能: 创建和优化 Agent 技能

**4. chart-visualization** - 图表可视化
- 位置: `/root/.openclaw/workspace/projects/deerflow-study/deer-flow-source/skills/public/chart-visualization/`
- 功能: 26 种图表类型

**5. deep-research** - 深度研究
- 位置: `/root/.openclaw/workspace/skills/deep-research-mirothinker/`
- 功能: 多角度系统性调研

### 🔧 技能使用

```bash
# 查看所有技能
ls /root/.openclaw/workspace/skills/

# 查看技能详情
cat /root/.openclaw/workspace/skills/<skill-name>/SKILL.md

# 安装新技能
bash /root/.openclaw/workspace/skills/deerflow-find-skills/scripts/install-skill.sh <skill-url>
```

---

## 脚本工具

### 📜 脚本统计

- **总脚本数**: 60+
- **核心脚本**: 20
- **自动化脚本**: 15
- **辅助脚本**: 25+

### 🎯 重要脚本

**1. self-evolution-system.sh** - 自主进化
```bash
bash /root/.openclaw/workspace/scripts/self-evolution-system.sh
```

**2. check-critical-rules.sh** - 规则检查
```bash
bash /root/.openclaw/workspace/scripts/check-critical-rules.sh
```

**3. complete-backup.sh** - 完整备份
```bash
bash /root/.openclaw/workspace/scripts/complete-backup.sh
```

**4. assign-task.sh** - 智能任务分配
```bash
bash /root/.openclaw/workspace/scripts/assign-task.sh "任务" "类型"
```

**5. fetch-web-content.sh** - 网页内容提取
```bash
~/.openclaw/workspace/scripts/fetch-web-content.sh <URL>
```

**6. personal-db.py** - HeyCube AI 记忆
```bash
python3 /root/.openclaw/workspace/scripts/personal-db.py list
python3 /root/.openclaw/workspace/scripts/personal-db.py get profile.career
```

**7. stock-query.py** - 股票查询
```bash
python3 /root/.openclaw/workspace/scripts/stock-query.py
```

**8. wal-protocol-automation.sh** - WAL Protocol
```bash
bash /root/.openclaw/workspace/scripts/wal-protocol-automation.sh restore
bash /root/.openclaw/workspace/scripts/wal-protocol-automation.sh daily
```

**9. doc-quality-check.sh** - 文档质量检查
```bash
/root/.openclaw/workspace/scripts/doc-quality-check.sh
/root/.openclaw/workspace/scripts/doc-quality-check.sh -v
/root/.openclaw/workspace/scripts/doc-quality-check.sh -j
```

**10. heartbeat-memory-check.sh** - 记忆健康检查
```bash
bash /root/.openclaw/workspace/scripts/heartbeat-memory-check.sh
```

### 🔧 脚本权限管理

```bash
# 确保所有脚本可执行
find /root/.openclaw/workspace/scripts/ -name "*.sh" -exec chmod +x {} \;
find /root/.openclaw/workspace/skills/ -name "*.sh" -exec chmod +x {} \;

# 验证权限
ls -la /root/.openclaw/workspace/scripts/ | grep "\.sh"
```

---

## 数据备份

### 💾 备份策略

**1. 自动备份（每日）**
```bash
# 位置: /root/.openclaw/workspace/scripts/auto-backup.sh
# 频率: 每日凌晨 3:00
# 保留: 最近 7 天
```

**2. 完整备份（手动）**
```bash
# 使用完整备份脚本
bash /root/.openclaw/workspace/scripts/complete-backup.sh

# 备份内容:
# - 配置文件（openclaw.json）
# - workspace（所有文件）
# - 记忆系统（MEMORY.md + 日志）
# - GitHub 推送
```

**3. GitHub 备份（每次重要更新）**
```bash
# 位置: https://github.com/63847051/redesigned-carnival
# 频率: 每次重要变更后
# 内容: 完整 workspace
```

### 🔄 恢复流程

**从 GitHub 恢复**：
```bash
# 克隆仓库
git clone https://github.com/63847051/redesigned-carnival.git /root/.openclaw/workspace

# 恢复配置
cp /root/.openclaw/openclaw.json.backup /root/.openclaw/openclaw.json

# 重启 Gateway
openclaw gateway restart
```

**从本地备份恢复**：
```bash
# 解压备份
tar -xzf openclaw-backup-YYYYMMDD_HHMMSS.tar.gz -C /root/.openclaw/

# 重启服务
systemctl --user restart openclaw-gateway
```

---

## 故障排查

### 🔍 常见问题

**1. Gateway 无法启动**
```bash
# 检查状态
systemctl --user status openclaw-gateway

# 查看日志
journalctl --user -u openclaw-gateway --no-pager -n 50

# 检查配置
python3 -c "import json; json.load(open('/root/.openclaw/openclaw.json'))"

# 重新启动
openclaw gateway restart
```

**2. 模型调用失败**
```bash
# 检查 API Key
openclaw config get models.providers.glmcode.apiKey

# 测试连接
openclaw doctor

# 查看模型列表
openclaw models
```

**3. OpenCode CLI 不可用**
```bash
# 检查安装
opencode --version

# 重新安装
npm install -g @opencode/cli

# 登录
opencode login

# 验证模型
opencode models opencode --verbose
```

**4. 技能加载失败**
```bash
# 检查技能文件
ls -la /root/.openclaw/workspace/skills/

# 验证 SKILL.md
cat /root/.openclaw/workspace/skills/<skill-name>/SKILL.md

# 检查权限
chmod +x /root/.openclaw/workspace/skills/*/scripts/*.sh
```

**5. 记忆系统异常**
```bash
# 检查 MEMORY.md
cat /root/.openclaw/workspace/MEMORY.md

# 运行健康检查
bash /root/.openclaw/workspace/scripts/heartbeat-memory-check.sh

# 查看日志
ls -la /root/.openclaw/workspace/memory/
```

### 🚨 紧急恢复

**系统完全崩溃**：
```bash
# 1. 停止 Gateway
openclaw gateway stop

# 2. 备份当前状态
cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.emergency

# 3. 从 GitHub 恢复
cd /root
mv .openclaw/workspace .openclaw/workspace.corrupt
git clone https://github.com/63847051/redesigned-carnival.git .openclaw/workspace

# 4. 恢复配置
cp /root/.openclaw/openclaw.json.emergency /root/.openclaw/openclaw.json

# 5. 重启 Gateway
openclaw gateway start
```

---

## 📊 系统验证清单

### ✅ 安装验证

- [ ] Node.js v22+ 已安装
- [ ] Python 3.11+ 已安装
- [ ] OpenClaw CLI 已安装
- [ ] OpenCode CLI 已安装并登录
- [ ] 所有脚本可执行
- [ ] 技能系统完整（180+ SKILL.md）
- [ ] Gateway 运行正常
- [ ] 模型调用测试通过
- [ ] 飞书集成配置完成（如需要）

### ✅ 功能验证

- [ ] 大领导可以聊天和分配任务
- [ ] 小新可以执行技术任务
- [ ] 小蓝可以记录工作日志
- [ ] 设计专家可以处理设计任务
- [ ] 自主进化系统可以运行
- [ ] 三重防护机制正常
- [ ] 记忆系统可以读写
- [ ] 网页内容提取可以工作
- [ ] 备份系统可以运行

### ✅ 性能验证

- [ ] Gateway 响应时间 < 2s
- [ ] 内存使用 < 80%
- [ ] CPU 使用 < 50%
- [ ] 磁盘空间充足 > 10GB

---

## 🎯 快速部署脚本

为了方便快速部署，我为你准备了一个自动化脚本：

```bash
#!/bin/bash
# 快速部署脚本 - OpenClaw 自主进化系统 v7.0

set -e

echo "🚀 开始部署 OpenClaw 自主进化系统 v7.0..."

# 1. 检查系统
echo "📋 检查系统环境..."
if [ ! -f /etc/redhat-release ]; then
    echo "⚠️  警告: 推荐使用 OpenCloudOS/CentOS"
fi

# 2. 安装依赖
echo "📦 安装系统依赖..."
yum update -y
yum install -y git curl wget python3 python3-pip

# 3. 安装 Node.js
echo "📦 安装 Node.js..."
curl -fsSL https://rpm.nodesource.com/setup_22.x | bash -
yum install -y nodejs

# 4. 安装 OpenClaw
echo "📦 安装 OpenClaw CLI..."
npm install -g openclaw

# 5. 安装 OpenCode
echo "📦 安装 OpenCode CLI..."
npm install -g @opencode/cli

# 6. 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip3 install beautifulsoup4 requests scrapling html2text

# 7. 克隆配置
echo "📦 克隆配置仓库..."
cd /root
git clone https://github.com/63847051/redesigned-carnival.git openclaw-workspace
mv /root/.openclaw/workspace /root/.openclaw/workspace.backup.$(date +%Y%m%d) || true
ln -s /root/openclaw-workspace /root/.openclaw/workspace

# 8. 设置权限
echo "🔧 设置脚本权限..."
find /root/.openclaw/workspace/scripts/ -name "*.sh" -exec chmod +x {} \;
find /root/.openclaw/workspace/skills/ -name "*.sh" -exec chmod +x {} \;

# 9. 配置 OpenClaw
echo "🔧 配置 OpenClaw..."
echo "请输入您的智谱 AI API Key:"
read -r GLM_API_KEY
openclaw config set models.providers.glmcode.apiKey "$GLM_API_KEY"
openclaw config set defaultModel glmcode/glm-4.7

# 10. 配置 OpenCode
echo "🔧 配置 OpenCode..."
opencode login

# 11. 启动 Gateway
echo "🚀 启动 OpenClaw Gateway..."
openclaw gateway start

# 12. 验证
echo "🔍 验证安装..."
sleep 5
openclaw doctor
opencode --version

echo "✅ 部署完成！"
echo "📚 使用指南: https://github.com/63847051/redesigned-carnival"
echo "💬 开始对话: openclaw chat"
```

**保存并运行**：
```bash
# 保存脚本
cat > /root/deploy-openclaw.sh << 'EOF'
# （上面的脚本内容）
EOF

# 运行脚本
chmod +x /root/deploy-openclaw.sh
bash /root/deploy-openclaw.sh
```

---

## 📚 更多资源

### 📖 文档

- **OpenClaw 官方文档**: https://docs.openclaw.ai
- **系统源码**: https://github.com/63847051/redesigned-carnival
- **ClawHub 技能市场**: https://clawhub.com

### 💬 社区

- **Discord 社区**: https://discord.com/invite/clawd
- **GitHub Issues**: https://github.com/openclaw/openclaw/issues

### 🎓 学习资源

- **PAI 学习系统**: `/root/.openclaw/workspace/docs/PAI-LEARNING-SYSTEM.md`
- **TradingAgents 学习**: `/root/.openclaw/workspace/CLAUDE-CODE-COMPLETE-LEARNING.md`
- **进化计划**: `/root/.openclaw/workspace/EVOLUTION-PLAN-v7.1.md`

---

## 🎯 总结

这就是完整的 **OpenClaw 自主进化系统 v7.0** 部署指南！

**系统特点**：
- ✅ 完全自动化运行
- ✅ 自主学习和进化
- ✅ 多 Agent 协同工作
- ✅ 三重防护机制
- ✅ 完整的记忆系统
- ✅ 180+ 专业技能
- ✅ 60+ 实用脚本

**核心价值**：
> **"专业的事交给专业的人"** - 大领导负责沟通，专业 Agent 负责执行

**下一步**：
1. 按照本指南在新服务器上部署
2. 配置 API Keys（智谱 AI、飞书等）
3. 启动 Gateway 并验证
4. 开始使用！

---

**文档生成时间**: 2026-04-05 08:40
**系统版本**: v7.0（TradingAgents 集成版）
**作者**: 大领导 🎯
**许可**: MIT

---

**祝你部署顺利！** 🚀✨
