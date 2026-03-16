# on_message 触发器设计

**创建时间**: 2026-03-16
**来源**: 基于 Clawith 的 Aware 机制

---

## 🎯 核心理念

**从闹钟到心跳** - 不是定时醒来看看，而是有变化立刻响应！

**问题**:
- 传统 Heartbeat（30 分钟轮询）太慢
- 难以应对实时任务
- 无法响应 Agent 之间的消息

**解决方案**:
- **on_message 触发器** - 监听特定消息，实时响应
- **自适应触发** - 根据任务进展自主创建、调整、删除触发器

---

## 📐 实现方案

### 方案 1: 使用 OpenClaw 的原生机制（推荐）⭐

**OpenClaw 已有的机制**:
- ✅ **消息监听** - Gateway 自动监听所有消息
- ✅ **会话路由** - 根据消息自动路由到对应 session
- ✅ **触发器** - 通过消息内容触发 action

**实现方式**:
```markdown
# 在 HEARTBEAT.md 中定义 on_message 触发器

## on_message 触发器

### 监听用户消息
```yaml
triggers:
  - type: on_message
    from: "user:ou_e356e8a931ed343100de9c449020964b"
    action: "立即处理任务"
    priority: high
```

### 监听 Agent 消息
```yaml
triggers:
  - type: on_message
    from: "agent:opencode"
    action: "继续执行任务"
    priority: medium
```
```

---

### 方案 2: 使用脚本包装（备用）

**创建监听脚本**:
```bash
#!/bin/bash
# on_message 触发器脚本

MESSAGE_SOURCE=$1
TRIGGER_ACTION=$2

echo "📨 监听消息来源: $MESSAGE_SOURCE"
echo "🎯 触发动作: $TRIGGER_ACTION"

# 使用 OpenClaw 的 sessions_list 工具
# 监听来自特定来源的消息
while true; do
    # 检查新消息
    NEW_MESSAGES=$(openclaw sessions list --recent --from "$MESSAGE_SOURCE")
    
    if [ -n "$NEW_MESSAGES" ]; then
        echo "🔔 收到新消息，执行触发动作"
        eval "$TRIGGER_ACTION"
    fi
    
    sleep 5  # 每 5 秒检查一次
done
```

**使用示例**:
```bash
# 监听用户消息
scripts/on-message-trigger.sh "user:ou_xxx" "执行任务"

# 监听 Agent 消息
scripts/on-message-trigger.sh "agent:builder" "继续执行"
```

---

## 🎯 使用场景

### 场景 1: 实时响应用户消息

**触发器定义**:
```yaml
triggers:
  - type: on_message
    from: "user:ou_e356e8a931ed343100de9c449020964b"
    action: "分析任务类型并分配"
    priority: high
    cooldown_seconds: 10
```

**执行流程**:
1. 用户发送消息
2. Gateway 立即路由到主控 session
3. 主控分析任务类型
4. 分配给合适的 Agent
5. 立即响应

---

### 场景 2: 协调多个 Agent

**触发器定义**:
```yaml
triggers:
  - type: on_message
    from: "agent:opencode"
    action: "汇总技术成果"
    priority: medium
    
  - type: on_message
    from: "agent:assistant"
    action: "整理工作日志"
    priority: low
```

**执行流程**:
1. 子 Agent 完成任务
2. 发送"任务完成"消息
3. 主控立即响应
4. 汇总成果
5. 反馈用户

---

### 场景 3: 等待回复后继续

**触发器定义**:
```yaml
triggers:
  - type: on_message
    from: "user:ou_e356e8a931ed343100de9c449020964b"
    action: "确认后继续执行"
    awaiting_response: true
    focus_ref: "task-123"
```

**执行流程**:
1. Agent 发起任务
2. 等待用户确认
3. 收到"确认"消息
4. 立即继续执行
5. 自动删除触发器

---

## 📊 与 Heartbeat 的对比

| 特性 | Heartbeat | on_message |
|------|-----------|------------|
| **触发方式** | 定时轮询（30 分钟） | 事件驱动（即时） |
| **响应速度** | 慢（最多 30 分钟延迟） | 快（秒级响应） |
| **资源消耗** | 低（定时检查） | 中（持续监听） |
| **适用场景** | 后台任务 | 实时协作 |
| **消息来源** | 系统定时 | 用户/Agent |

---

## 💡 最佳实践

### 1. 合理使用触发器

**使用 on_message**:
- ✅ 需要实时响应的任务
- ✅ 协调多个 Agent
- ✅ 等待用户确认

**使用 Heartbeat**:
- ✅ 后台定期任务
- ✅ 系统健康检查
- ✅ 数据同步

---

### 2. 设置合理的冷却时间

```yaml
triggers:
  - type: on_message
    cooldown_seconds: 10  # 10 秒冷却时间
```

**避免**: 过于频繁触发导致资源浪费

---

### 3. 关联到 Focus Item（关注点）

```yaml
triggers:
  - type: on_message
    focus_ref: "task-123"  # 关联到任务 123
```

**好处**:
- 任务完成后自动删除触发器
- 避免触发器泄漏
- 提高系统可维护性

---

## 🚀 实施步骤

### Phase 1: 设计阶段（当前）
- ✅ 研究 Clawith 的 on_message 机制
- ✅ 设计集成方案
- ✅ 编写设计文档

### Phase 2: 实验阶段（下一步）
- ⏳ 创建 on_message 触发器脚本
- ⏳ 在测试环境验证
- ⏳ 测试响应速度

### Phase 3: 集成阶段（长期）
- ⏳ 集成到 HEARTBEAT.md
- ⏳ 优化触发器管理
- ⏳ 建立监控机制

---

## 📚 参考资料

**Clawith 源码**:
- https://github.com/dataelement/Clawith
- backend/app/models/trigger.py
- backend/app/services/agent_context.py

**OpenClaw 文档**:
- https://docs.openclaw.ai/gateway/configuration
- https://docs.openclaw.ai/tools/subagents

---

**最后更新**: 2026-03-16 16:00
**维护者**: 大领导系统 v5.16.0
