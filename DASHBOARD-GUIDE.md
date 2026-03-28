# 🤖 OpenClaw Bot 监控仪表板 - 安装和配置指南

**项目**: https://github.com/xmanrui/OpenClaw-bot-review
**安装时间**: 2026-03-28 11:07
**状态**: ✅ 已安装

---

## 🎯 功能概述

这是一个轻量级 Web 仪表板，用于监控所有 OpenClaw Bot/Agent/模型/会话的运行状态。

### 核心功能
- ✅ Bot 总览 - 卡片墙展示所有 Agent
- ✅ 模型列表 - 查看所有配置的 Provider 和模型
- ✅ 会话管理 - 浏览所有会话，类型识别
- ✅ 消息统计 - Token 消耗趋势
- ✅ 技能管理 - 查看所有已安装技能
- ✅ 告警中心 - 配置告警规则
- ✅ Gateway 健康检测 - 实时状态指示
- ✅ 平台连通测试 - 一键测试所有绑定
- ✅ 像素办公室 - Agent 像素角色可视化

---

## 🚀 快速开始

### 方法 1: 使用启动脚本（推荐）

```bash
# 使用启动脚本
bash /root/.openclaw/workspace/scripts/start-dashboard.sh
```

**优点**:
- ✅ 自动检查环境
- ✅ 自动检查依赖
- ✅ 显示访问地址

### 方法 2: 手动启动

```bash
# 进入项目目录
cd /root/.openclaw/workspace/OpenClaw-bot-review

# 启动开发服务器
npm run start
```

---

## 🔧 配置说明

### 默认配置
- **配置文件路径**: `~/.openclaw/openclaw.json`
- **监听地址**: `localhost:3000`
- **公网地址**: `http://43.134.63.176:3000`

### 自定义配置路径

如果 OpenClaw 安装在其他位置，设置环境变量：

```bash
# 方法 1: 环境变量
export OPENCLAW_HOME=/opt/openclaw
npm run start

# 方法 2: 修改启动脚本
# 在 scripts/start-dashboard.sh 中添加:
# export OPENCLAW_HOME=/opt/openclaw
```

---

## 📊 访问地址

### 本地访问
```
http://localhost:3000
```

### 公网访问
```
http://43.134.63.176:3000
```

**注意**: 需要确保防火墙允许 3000 端口访问

---

## 🔥 开机自启动（可选）

### 使用 PM2

```bash
# 安装 PM2
npm install -g pm2

# 启动仪表板
pm2 start /root/.openclaw/workspace/OpenClaw-bot-review/package.json --name "openclaw-dashboard"

# 设置开机自启
pm2 startup
pm2 save
```

### 使用 Systemd

```bash
# 创建服务文件
cat > /etc/systemd/system/openclaw-dashboard.service << 'EOF'
[Unit]
Description=OpenClaw Bot Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace/OpenClaw-bot-review
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
systemctl daemon-reload
systemctl enable openclaw-dashboard
systemctl start openclaw-dashboard
```

---

## 🛡️ 防火墙配置

### 开放 3000 端口

```bash
# firewalld
firewall-cmd --zone=public --add-port=3000/tcp --permanent
firewall-cmd --reload

# iptables
iptables -I INPUT -p tcp --dport 3000 -j ACCEPT
service iptables save
```

---

## 📊 使用说明

### 1. Bot 总览
- 查看所有 Agent 的状态
- 显示名称、Emoji、模型、平台绑定
- Gateway 健康状态

### 2. 模型列表
- 查看所有配置的模型
- 上下文窗口、最大输出
- 单模型测试

### 3. 会话管理
- 浏览所有会话
- 类型识别（私聊、群聊、定时任务）
- Token 用量统计

### 4. 消息统计
- Token 消耗趋势
- 平均响应时间
- 按天/周/月查看

### 5. 技能管理
- 查看所有已安装技能
- 搜索和筛选

### 6. 告警中心
- 配置告警规则
- 飞书通知集成

### 7. Gateway 健康检测
- 实时状态指示器
- 10 秒自动轮询

### 8. 平台连通测试
- 一键测试所有平台绑定
- DM Session 连通性

### 9. 像素办公室
- Agent 像素角色可视化
- 实时动画效果

---

## 💡 最佳实践

### 1. 定期监控
- 每天查看 Token 消耗
- 检查 Agent 状态
- 测试平台连通性

### 2. 告警配置
- 设置模型不可用告警
- 设置机器人无响应告警
- 配置飞书通知

### 3. 优化建议
- 根据 Token 统计优化模型使用
- 根据响应时间优化 Agent 配置
- 根据平台连通性优化绑定

---

## 🎯 与你的系统集成

### 你的 Agent 团队
1. **大领导** 🎯 - 主控 Agent（GLM-4.7）
2. **小新** 💻 - 技术专家（opencode/minimax-m2.5-free）
3. **小蓝** 📋 - 日志专家（GLM-4.5-Air）
4. **设计专家** 🏠 - 设计专家（GLM-4.6）

### 你的平台集成
- ✅ 飞书（2 个机器人）
- ✅ 微信（1 个机器人）
- ✅ Gateway 运行中

### 仪表板价值
- ✅ 一目了然看到所有 4 个 Agent 状态
- ✅ 监控 Token 消耗（帮助优化成本）
- ✅ 测试飞书/微信连通性
- ✅ 像素办公室可视化你的团队

---

## 🔧 故障排除

### 问题 1: 无法启动
```bash
# 检查端口占用
netstat -tlnp | grep 3000

# 如果被占用，杀死进程
kill -9 <PID>
```

### 问题 2: 无法读取配置
```bash
# 检查配置文件
ls -la ~/.openclaw/openclaw.json

# 检查权限
chmod 644 ~/.openclaw/openclaw.json
```

### 问题 3: 无法访问公网
```bash
# 检查防火墙
firewall-cmd --list-ports

# 开放 3000 置端口
firewall-cmd --zone=public --add-port=3000/tcp --permanent
firewall-cmd --reload
```

---

## 📞 获取帮助

- **GitHub**: https://github.com/xmanrui/OpenClaw-bot-review
- **Issues**: https://github.com/xmanrui/OpenClaw-bot-review/issues
- **文档**: https://github.com/xmanrui/OpenClaw-bot-review/blob/main/quick_start.md

---

**状态**: ✅ 已安装
**下一步**: 启动仪表板
**版本**: Latest
**更新**: 2026-03-28 11:07
