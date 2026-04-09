# OpenClaw Daemon - 使用指南

**版本**: v1.0
**创建时间**: 2026-04-07
**状态**: ✅ 核心功能完成

---

## 🎯 核心功能

### 1. Agent 生命周期管理

**启动 Agent**:
```python
daemon.spawn_agent(
    agent_id="main",
    driver_type=DriverType.SUBAGENT,
    config={"model": "glmcode/glm-4.7"}
)
```

**发送消息**:
```python
daemon.send_message_to_agent("main", "Hello!")
```

**状态监控**:
```python
# 自动心跳检测
# 每 30 秒检查一次
# 自动检测进程退出
```

---

## 🏗️ 架构组件

### 控制平面
- ✅ WebSocket 连接管理
- ✅ 提示词组装
- ✅ Agent 状态缓存

### 进程状态机
- ✅ Agent 生命周期
- ✅ 状态转换
- ✅ 冷启动 vs 恢复会话

### 驱动适配器
- ✅ SubagentDriver（重启模式）
- ✅ ACPDriver（注入模式）
- ✅ OpenCodeDriver（混合模式）

---

## 📊 Agent 状态

```
COLD_START → RUNNING → IDLE → WAKE_UP → RUNNING
```

**关键差异**:
- **Subagent**: 不支持 stdin 注入，新消息需重启
- **ACP**: 支持 stdin 注入，忙时也能接收消息

---

## 🚀 使用方法

### 启动 Daemon

```bash
# 启动 Daemon
python3 openclaw_daemon.py
```

### 测试

```python
# 测试启动 Agent
daemon = OpenClawDaemon()
await daemon.start()

# 启动一个 Agent
await daemon.spawn_agent(
    "main",
    DriverType.SUBAGENT,
    {"model": "glmcode/glm-4.7"}
)

# 发送消息
await daemon.send_message_to_agent("main", "测试消息")
```

---

## 🎯 中期优化进度

- [x] 实现 Daemon 架构（核心功能）
- [ ] 创建 Driver 适配器（完整实现）
- [ ] 支持 Web UI

---

## 💡 关键特性

**自动化**: 心跳检测、状态监控、自动恢复
**灵活性**: 支持多种驱动类型
**可靠性**: 进程管理、状态持久化

---

**OpenClaw Daemon v1.0 - Agent 生命周期管理器！** 🚀
