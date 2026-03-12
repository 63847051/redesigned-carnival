# OpenClaw Control Center

**版本**: v1.0.0
**安装日期**: 2026-03-12
**状态**: ✅ 运行中

---

## 🎯 项目简介

OpenClaw Control Center 是一个 Web UI 控制面板，用于管理和监控 OpenClaw Agent 系统。

---

## ✨ 功能特性

- 🖥️ **Web UI 界面** - 可视化控制面板
- 📊 **实时监控** - Agent 状态监控
- 🛡️ **安全模式** - 只读访问，保护系统
- 🔐 **本地认证** - 安全访问控制

---

## 🚀 快速开始

### 安装步骤

```bash
# 1. 克隆项目
git clone <your-repo>/openclaw-control-center.git
cd openclaw-control-center

# 2. 安装依赖
npm install

# 3. 配置环境
cp .env.example .env

# 4. 构建项目
npm run build

# 5. 启动服务
bash start-control-center.sh
```

### 配置说明

编辑 `.env` 文件：
```bash
GATEWAY_URL=http://127.0.0.1:18789
OPENCLAW_HOME=/root/.openclaw
READONLY_MODE=true
UI_HOST=0.0.0.0
UI_PORT=4310
```

---

## 📊 版本历史

### v1.0.0 (2026-03-12)
- ✅ 初始安装
- ✅ 外网访问配置
- ✅ 只读模式启用
- ✅ 安全配置完成

---

## 🔗 访问地址

- **本地**: http://127.0.0.1:4310
- **外网**: http://43.134.63.176:4310

---

## 🛠️ 管理命令

```bash
# 启动
bash start-control-center.sh

# 停止
pkill -f "control-center"

# 查看日志
tail -f /tmp/control-center.log
```

---

**备份时间**: 2026-03-12 22:03
**运行状态**: ✅ 正常
