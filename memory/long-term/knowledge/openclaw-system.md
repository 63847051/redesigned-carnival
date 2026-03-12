# OpenClaw 系统知识

**创建时间**: 2026-03-09
**最后更新**: 2026-03-09
**分类**: 系统架构

---

## 系统概览

**OpenClaw**: AI 代理框架
**版本**: 2026.2.26
**服务器**: 腾讯云轻量服务器 (43.134.63.176)

---

## 核心组件

### 1. Gateway 系统
- **端口**: 18789
- **状态**: ✅ 运行中
- **控制面板**: http://127.0.0.1:18789/
- **重启次数**: 5 次

### 2. 飞书集成
- **状态**: ✅ 已配置
- **功能**: 消息收发、文件上传、多维表格操作
- **配对文件**: `/root/.openclaw/credentials/feishu-pairing.json`

### 3. 模型配置
- **默认模型**: GLM-4.7 (glmcode)
- **备用模型**: GLM-4.5-Air, GLM-4.6, GLM-5
- **API 提供商**: 智谱 AI (https://open.bigmodel.cn/api/anthropic)

---

## 文件结构

```
/root/.openclaw/
├── workspace/              # 工作区
│   ├── agents/            # Agent 配置
│   ├── scripts/           # 自动化脚本
│   ├── skills/            # 技能包
│   ├── memory/            # 记忆系统
│   └── .learnings/        # 学习记录
├── credentials/           # 凭证
│   └── feishu-pairing.json
├── logs/                  # 日志
├── backups/               # 备份
└── openclaw.json          # 配置文件
```

---

## 重要脚本

### 进化系统
- `super-evolution-system.sh` - 主脚本
- `heartbeat-evolution.sh` - 心跳进化
- `ses-auto.sh` - 自动集成

### 防护系统
- `ses-protection-integrated.sh` - 集成防护
- `check-upgrade-compatibility.sh` - 兼容性检查

### PAI 学习系统
- `pai-workflow.sh` - 完整工作流
- `pai-learning-capture.sh` - 学习信号捕获

---

## 配置文件

### openclaw.json
**位置**: `/root/.openclaw/openclaw.json`
**最后更新**: 2026-03-09
**版本**: v78427926339d36d30d6a62a935aa86d4215eb700c52a88db830e58acc31bca66

**重要配置项**:
- `gateway.port`: 18789
- `agents.defaults.model`: glmcode/glm-4.7
- `skills.load.paths`: 技能加载路径

---

## 常用命令

### Gateway 管理
```bash
# 检查状态
openclaw gateway status

# 启动 Gateway
openclaw gateway start

# 停止 Gateway
openclaw gateway stop

# 重启 Gateway
openclaw gateway restart
```

### 渠道管理
```bash
# 列出渠道
openclaw channels list

# 添加渠道
openclaw channels add --channel <channel>

# 渠道状态
openclaw channels status --probe
```

### 诊断
```bash
# 系统诊断
openclaw doctor

# 自动修复
openclaw doctor --fix

# 查看状态
openclaw status
```

---

## 常见问题

### Gateway 无法启动
**检查**:
```bash
systemctl --user status openclaw-gateway
journalctl --user -u openclaw-gateway --no-pager
```

### 配置文件错误
**修复**:
```bash
openclaw doctor --fix
```

### 飞书连接失败
**检查**:
```bash
ls -la /root/.openclaw/credentials/feishu-pairing.json
```

---

## 性能指标

- **内存使用**: 44.8%
- **Gateway 重启次数**: 5 次
- **运行时间**: 28 分钟（最近一次）

---

## 关联信息

- **配置文件**: `/root/.openclaw/openclaw.json`
- **凭证目录**: `/root/.openclaw/credentials/`
- **日志目录**: `/root/.openclaw/logs/`
- **工作区**: `/root/.openclaw/workspace/`

---

*标签: #系统 #OpenClaw #架构 #配置*
