# 三种拓扑架构 - 系统思维指南

**创建时间**: 2026-04-04
**目的**: 理解不同架构的适用场景，选择最优架构

---

## 🎯 三种拓扑架构

### 1️⃣ 星型架构（Star Topology）⭐

#### 架构图

```
        用户
         ↓
    主控 Agent
    /   |   \
   /    |    \
  A     B     C
 (独立)(独立)(独立)
```

#### 特点

- **主 Agent**: 负责任务分发和结果汇总
- **子 Agent**: 并行独立执行，互不通信
- **数据流**: 一对多，单向流动

#### 适用场景

✅ **任务之间没有依赖关系**
- 同时查询 4 个不同的数据源
- 并行处理多个独立文件
- 同时测试多个功能模块
- 批量处理独立任务

#### 示例

```python
# 任务：同时查询 4 个数据源

# 主控 Agent 分发任务
results = []

# 并行分发
results.append(sessions_spawn(task="查询数据库A", label="query-db-a"))
results.append(sessions_spawn(task="查询数据库B", label="query-db-b"))
results.append(sessions_spawn(task="查询API C", label="query-api-c"))
results.append(sessions_spawn(task="查询文件D", label="query-file-d"))

# 汇总结果
summary = consolidate(results)
```

#### 优点

- ✅ 并行执行，速度快
- ✅ 任务独立，互不影响
- ✅ 容易理解和实现
- ✅ 失败隔离，一个失败不影响其他

#### 缺点

- ❌ 无法处理依赖关系
- ❌ 主 Agent 成为瓶颈
- ❌ 无法共享中间结果

---

### 2️⃣ 流水线架构（Pipeline Topology）⭐⭐

#### 架构图

```
  用户
   ↓
Agent A → Agent B → Agent C
   ↓        ↓         ↓
  数据1   数据2    最终结果
```

#### 特点

- **顺序依赖**: A 完成后才能执行 B
- **数据传递**: 通过 sessions_send 传递数据
- **链式流动**: 一对一，单向流动

#### 适用场景

✅ **任务有明确的顺序依赖**
- 研究 → 分析 → 撰写
- 抓取 → 清洗 → 分析
- 设计 → 开发 → 测试
- 翻译 → 校对 → 发布

#### 示例

```python
# 任务：研究 → 分析 → 撰写

# Step 1: 研究
research_result = sessions_spawn(
    task="研究市场趋势",
    label="research"
)

# Step 2: 分析（使用 sessions_send）
sessions_send(
    to="analyst-agent",
    message=f"研究数据已就绪，请分析: {research_result}"
)

# Step 3: 撰写（使用 sessions_send）
sessions_send(
    to="writer-agent",
    message=f"分析结果已就绪，请撰写报告"
)
```

#### 优点

- ✅ 清晰的依赖关系
- ✅ 数据传递明确
- ✅ 易于调试和追踪
- ✅ 适合复杂任务分解

#### 缺点

- ❌ 串行执行，速度慢
- ❌ 一个失败，全链中断
- ❌ 难以并行优化

---

### 3️⃣ 广播架构（Broadcast Topology）⭐⭐⭐

#### 架构图

```
      用户
       ↓
  主控 Agent
   /  |  \
  /   |   \
 A    B    C
  \   |   /
   \  |  /
   汇总结果
```

#### 特点

- **同一消息**: 发送给多个 Agent
- **并行处理**: 多个 Agent 同时处理
- **结果汇总**: 收集所有结果

#### 适用场景

✅ **通知型场景**
- 通知多个团队成员
- 多个角度分析同一问题
- 多个方案并行评估
- 多个模型同时预测

#### 示例

```python
# 任务：通知多个 Agent

# 主控 Agent 广播消息
tasks = [
    sessions_send(to="agent-a", message="新项目启动，请准备"),
    sessions_send(to="agent-b", message="新项目启动，请准备"),
    sessions_send(to="agent-c", message="新项目启动，请准备"),
]

# 或使用多个 sessions_spawn
results = [
    sessions_spawn(task="方案A", label="plan-a"),
    sessions_spawn(task="方案B", label="plan-b"),
    sessions_spawn(task="方案C", label="plan-c"),
]

# 汇总所有结果
summary = consolidate(results)
```

#### 优点

- ✅ 并行执行，速度快
- ✅ 多角度分析
- ✅ 结果多样
- ✅ 适合评估和选择

#### 缺点

- ❌ 结果可能不一致
- ❌ 需要额外的汇总逻辑
- ❌ 可能浪费资源

---

## 🎯 架构选择指南

### 决策树

```
开始
  ↓
任务之间有依赖吗？
  ├─ 是 → 流水线架构
  └─ 否 → 需要多个角度分析吗？
       ├─ 是 → 广播架构
       └─ 否 → 星型架构
```

### 对比表

| 特性 | 星型 | 流水线 | 广播 |
|------|------|--------|------|
| 执行方式 | 并行 | 串行 | 并行 |
| 依赖关系 | 无 | 有顺序 | 无 |
| 通信方式 | spawn | send | send/spawn |
| 速度 | 快 | 慢 | 快 |
| 复杂度 | 低 | 中 | 中 |
| 适用场景 | 独立任务 | 顺序任务 | 通知/评估 |

---

## 💡 实战案例

### 案例 1: 数据分析项目

**需求**: 抓取数据 → 清洗数据 → 分析数据 → 生成报告

**架构选择**: 流水线架构

**实现**:
```python
# Step 1: 抓取
data = sessions_spawn(task="抓取数据", label="fetch")

# Step 2: 清洗
sessions_send(to="cleaner", message=f"清洗数据: {data}")

# Step 3: 分析
sessions_send(to="analyst", message="分析清洗后的数据")

# Step 4: 报告
sessions_send(to="reporter", message="生成分析报告")
```

---

### 案例 2: 多源数据查询

**需求**: 同时查询 5 个不同的数据源

**架构选择**: 星型架构

**实现**:
```python
# 并行查询
results = []
results.append(sessions_spawn(task="查询DB1", label="query-db1"))
results.append(sessions_spawn(task="查询DB2", label="query-db2"))
results.append(sessions_spawn(task="查询API1", label="query-api1"))
results.append(sessions_spawn(task="查询API2", label="query-api2"))
results.append(sessions_spawn(task="查询文件", label="query-file"))

# 汇总结果
summary = consolidate(results)
```

---

### 案例 3: 方案评估

**需求**: 从 3 个不同角度评估同一个方案

**架构选择**: 广播架构

**实现**:
```python
# 广播任务
results = []
results.append(sessions_spawn(task="技术角度评估", label="tech-review"))
results.append(sessions_spawn(task="商业角度评估", label="business-review"))
results.append(sessions_spawn(task="风险角度评估", label="risk-review"))

# 汇总评估
summary = consolidate(results)
```

---

## 🚀 最佳实践

### 1. 画拓扑图

**在动手写代码之前，先画出来！**

```
用户
  ↓
主控 Agent
  ↓
┌─────────────────────────────────┐
│  任务复杂度评估                  │
│                                 │
│  简单（< 5 分钟）→ 直接分配      │
│  中等（5-15 分钟）→ 简单计划     │
│  复杂（> 15 分钟）→ 详细计划     │
└─────────────────────────────────┘
  ↓
选择架构
  ↓
执行
```

### 2. 明确通信方式

- **sessions_spawn**: 异步任务，等待结果
- **sessions_send**: Agent 间通信，可等待回复
- **message**: 向用户汇报

### 3. 设置验证点

- [ ] 任务理解正确
- [ ] 架构选择合理
- [ ] 通信方式明确
- [ ] 结果符合预期

### 4. 监控和调试

- 使用 sessions_list 查看活跃 session
- 使用 sessions_history 查看完整记录
- 定期验证进度

---

## 📊 总结

### 核心原则

1. **根据任务选拓扑**，不是越复杂越好
2. **画拓扑图再写代码**，30 分钟 vs 调试 2 天
3. **明确通信方式**，spawn vs send
4. **设置验证点**，及时发现问题

### 选择指南

- **独立任务** → 星型架构
- **顺序任务** → 流水线架构
- **通知/评估** → 广播架构

---

**最后更新**: 2026-04-04
**状态**: ✅ 完整指南
**价值**: ⭐⭐⭐⭐⭐ 极高
