# Agent 拓扑设计学习计划

**创建时间**: 2026-04-02 17:45
**参考来源**: OpenClaw 进阶手册 Vol.2 - Tip 12-14
**目标**: 掌握三种 Agent 拓扑架构，学会设计多 Agent 系统

---

## 🎯 学习目标

1. **理解三种拓扑架构**
   - 星型（Fan-Out）
   - 流水线（Pipeline）
   - 广播（Broadcast）

2. **学会选择合适的拓扑**
   - 根据任务结构选择
   - 避免过度设计

3. **掌握实现方法**
   - sessions_spawn 的使用
   - sessions_send 的使用
   - 组合使用两种通信方式

4. **学会画拓扑图**
   - 在写代码前先画图
   - 清晰标识通信方式

---

## 📋 三种拓扑架构

### 1. 星型（Fan-Out）

**结构**:
```
用户
  ↓
主 Agent
  ├─→ 子 Agent A
  ├─→ 子 Agent B
  └─→ 子 Agent C
```

**特点**:
- 主 Agent 分发任务
- 子 Agent 并行独立运行
- 子 Agent 之间不通信

**适用场景**:
- 任务之间没有依赖关系
- 需要同时处理多个数据源
- 并行执行提高效率

**示例**:
```
同时查四个数据源：
- GitHub API
- Jira API
- Slack API
- Email

主 Agent 分发任务，4 个子 Agent 并行查询
```

**实现方法**:
```python
# 主 Agent
tasks = [
    ("fetch-github", "获取 GitHub PR"),
    ("fetch-jira", "获取 Jira 变更"),
    ("fetch-slack", "获取 Slack 消息"),
    ("fetch-email", "获取邮件"),
]

for label, task in tasks:
    sessions_spawn(task=task, label=label)

# 等待所有子 Agent 完成
# 汇总结果
```

---

### 2. 流水线（Pipeline）

**结构**:
```
用户
  ↓
Agent A
  ↓ (sessions_send)
Agent B
  ↓ (sessions_send)
Agent C
  ↓
结果
```

**特点**:
- 顺序依赖：A 完成后 B 才能开始
- 数据流转：A 的输出是 B 的输入
- 使用 sessions_send 通信

**适用场景**:
- 研究→分析→撰写
- 数据采集→处理→生成报告
- 多步骤顺序处理

**示例**:
```
研究 → 分析 → 撰写

Agent A: 研究市场数据
  ↓ sessions_send
Agent B: 分析数据趋势
  ↓ sessions_send
Agent C: 撰写分析报告
```

**实现方法**:
```python
# Step 1: Agent A 完成研究
result_a = sessions_spawn(
    task="研究市场数据",
    label="research"
)

# Step 2: A 完成后触发 B
sessions_send(
    to="analyst-agent",
    message=f"数据已就绪：{result_a}，请分析"
)

# Step 3: B 完成后触发 C
# (在 analyst-agent 中)
sessions_send(
    to="writer-agent",
    message=f"分析完成，请撰写报告"
)
```

---

### 3. 广播（Broadcast）

**结构**:
```
用户
  ↓
主 Agent
  ├─→ Agent A
  ├─→ Agent B
  └─→ Agent C
(同一消息发给所有)
```

**特点**:
- 主 Agent 把同一个消息发给多个 Agent
- 所有 Agent 收到相同的内容
- 用于通知型场景

**适用场景**:
- 通知多个 Agent 更新
- 广播配置变更
- 分发相同任务

**示例**:
```
配置更新通知

主 Agent 检测到配置文件更新
  ↓ 广播
通知所有子 Agent 重新加载配置
```

**实现方法**:
```python
# 方式 1: 多个 sessions_spawn
tasks = ["agent-a", "agent-b", "agent-c"]
for agent in tasks:
    sessions_spawn(
        task="重新加载配置",
        label=agent
    )

# 方式 2: 多个 sessions_send
sessions_send(to="agent-a", message="配置已更新")
sessions_send(to="agent-b", message="配置已更新")
sessions_send(to="agent-c", message="配置已更新")
```

---

## 🔄 混合拓扑

**实际应用中往往是混合的**:

```
用户
  ↓
前台 Agent
  ├─→ sessions_spawn → 数据采集 Agent（星型）
  ├─→ sessions_spawn → 分析 Agent（星型）
  └─→ sessions_send → 后台 Agent（流水线）
       ↓
    后台 Agent
       ├─→ sessions_spawn → 子 Agent 1
       ├─→ sessions_spawn → 子 Agent 2
       └─→ sessions_spawn → 子 Agent 3
```

---

## 🎨 拓扑设计原则

### 原则 1: 先画图，再写代码

**为什么**?
- 画出来之后 30 分钟能实现
- 不画的话可能调试 2 天

**怎么做**?
```
1. 画出所有 Agent
2. 标识通信方式（send vs spawn）
3. 标识数据流向
4. 标注同步/异步
```

### 原则 2: 选择合适的拓扑

**任务特点** → **拓扑选择**

| 任务特点 | 推荐拓扑 | 原因 |
|---------|---------|------|
| 无依赖，可并行 | 星型 | 最大化并行 |
| 顺序依赖 | 流水线 | 保证顺序 |
| 通知型 | 广播 | 一次分发 |
| 复杂任务 | 混合 | 灵活组合 |

### 原则 3: 不是越复杂越好

**避免过度设计**:
- 简单任务不需要多 Agent
- 能用单 Agent 完成就不要拆
- 每增加一层复杂度，调试难度指数增长

---

## 🔧 实现工具

### sessions_spawn vs sessions_send

| | sessions_spawn | sessions_send |
|---|----------------|---------------|
| **场景** | 下发任务，等结果 | 向另一个 Agent 发消息 |
| **同步** | 异步，spawn 后不等 | 可以等对方回复 |
| **默认** | 默认开启 | 需要配置开启 |

**开启 sessions_send**:
```json
{
  "agents": {
    "agentToAgent": true
  }
}
```

### 监控 Agent

```python
# 查看所有活跃 session
sessions_list()

# 查看某个 session 的完整对话
sessions_history(session_id="q4-sales-analysis-2026")
```

**类比**:
- `sessions_list` = `ps aux`（概览）
- `sessions_history` = `tail -f logfile`（细节）

---

## 📊 设计检查清单

**在设计拓扑时，确认**:

- [ ] 每个 Agent 的职责清晰吗？
- [ ] Agent 之间的通信方式合理吗？
- [ ] 数据流向清晰吗？
- [ ] 是否有循环依赖？
- [ ] 是否过度设计了？
- [ ] 错误处理如何做？
- [ ] 如何监控和调试？

---

## 🎓 实践练习

### 练习 1: 设计一个数据采集系统

**需求**:
- 同时从 3 个 API 采集数据
- 数据汇总后发送通知

**设计**:
```
用户触发
  ↓
主 Agent
  ├─→ API 1 采集
  ├─→ API 2 采集
  └─→ API 3 采集
  ↓
汇总结果
  ↓
发送通知
```

**拓扑**: 星型 + 单个处理节点

---

### 练习 2: 设计一个内容生成系统

**需求**:
- 研究主题
- 生成大纲
- 撰写内容
- 发布到平台

**设计**:
```
用户输入主题
  ↓
研究 Agent
  ↓ sessions_send
大纲 Agent
  ↓ sessions_send
撰写 Agent
  ↓ sessions_send
发布 Agent
  ↓
完成通知
```

**拓扑**: 流水线

---

### 练习 3: 设计一个监控系统

**需求**:
- 定时检查多个服务
- 发现问题时通知多个渠道

**设计**:
```
定时触发
  ↓
监控 Agent
  ├─→ 检查服务 A
  ├─→ 检查服务 B
  └─→ 检查服务 C
  ↓
发现问题时
  ├─→ 发送邮件
  ├─→ 发送 Slack
  └─→ 发送 Telegram
```

**拓扑**: 星型（检查）+ 广播（通知）

---

## 📚 参考资料

- OpenClaw 进阶手册 Vol.2 - Tip 12-14
- OpenClaw GitHub: github.com/openclaw/openclaw
- ECC Longform Guide

---

**状态**: 📖 学习中
**下一步**: 实践练习，设计实际系统
**完成时间**: 预计本周完成
