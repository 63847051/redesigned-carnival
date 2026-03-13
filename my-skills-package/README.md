# 我的技能系统包

**打包时间**: 20260313_093113
**系统版本**: v5.10
**OpenClaw 版本**: 2026.2.26

---

## 📦 包含内容

### 技能列表
- agent-browser
- agent-team-orchestration
- feishu-worklog
- find-skills
- github
- multi-search-engine
- notion
- obsidian
- pdf
- proactive-agent-skill
- self-improving
- shadows-mcp-forge
- summarize
- tavily-search
- tencentcloud-lighthouse-skill
- tencent-docs
- weather
- wechat-reader
- word-docx


### 系统文件
- `SOUL.md` - 系统核心
- `IDENTITY.md` - 身份定义
- `USER.md` - 用户信息
- `AGENTS.md` - Agent 配置
- `TOOLS.md` - 工具配置
- `HEARTBEAT.md` - 心跳检查

### 学习系统
- `.learnings/` - 设计模式、最佳实践、错误记录
- `scripts/` - 自动化脚本

---

## 🚀 一键安装

### 方式 1: 自动安装（推荐）

```bash
cd my-skills-package
bash install.sh
```

### 方式 2: 手动安装

```bash
# 1. 复制技能到工作区
cp -r */your-skill/* /root/.openclaw/workspace/skills/

# 2. 复制系统文件
cp -r system/* /root/.openclaw/workspace/

# 3. 设置权限
chmod +x /root/.openclaw/workspace/scripts/*.sh
```

---

## 📋 系统要求

- OpenClaw: 2026.2.26 或更高
- Node.js: v22.22.0
- 操作系统: Linux (OpenCloudOS, Ubuntu, etc.)

---

## 🎯 快速开始

安装后，重启 Gateway：

```bash
systemctl --user restart openclaw-gateway
```

---

## 📚 更多信息

- **OpenClaw 文档**: https://docs.openclaw.ai
- **社区**: https://discord.com/invite/clawd
- **技能市场**: https://clawhub.com

---

**打包人**: 大领导 🎯
**系统版本**: v5.10
**打包时间**: 20260313_093113
