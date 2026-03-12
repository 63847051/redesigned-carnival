# 多模型子 Agent 架构方案

## 🎯 优化目标

1. **独立思考** - 每个 agent 有自己的会话和记忆
2. **模型分流** - 简单任务用便宜模型,复杂任务用强大模型
3. **持久化** - 子 agent 保持运行,不每次重新启动

## 📊 模型选择策略

### 任务分类

| 任务类型 | 使用模型 | 原因 | 成本 |
|---------|---------|------|------|
| 工作日志记录 | GLM-4-Flash | 简单结构化任务 | 💰 低 |
| 简单查询 | GLM-4-Flash | 信息检索 | 💰 低 |
| 复杂设计 | GLM-4-Plus | 需要创意和专业性 | 💰💰 中 |
| 技术支持 | GLM-4-Flash | 代码和调试 | 💰 低 |
| 项目管理 | GLM-4.7 | 复杂决策和协调 | 💰💰💰 高 |

## 🏗️ 架构设计

### 方案 A: 持久化子 Agent (推荐)

**特点**:
- ✅ 真正的独立思考和记忆
- ✅ 可以保持上下文
- ✅ 精确控制模型
- ⚠️ 需要管理多个会话

**实现**:
```
sessions_spawn {
  label: "小蓝",
  model: "glm-4-flash",
  mode: "session",
  thread: true,
  task: "工作日志专家配置..."
}
```

**调度**:
- 主控 agent 通过 `sessions_send` 转发任务
- 子 agent 独立处理并回复
- 可以持续对话

### 方案 B: Skill + 模型覆盖 (轻量)

**特点**:
- ✅ 简单易管理
- ✅ 自动触发
- ❌ 仍在主控会话中执行
- ❌ 模型覆盖可能不生效

**实现**:
- 在 skill 中指定 `model: "glm-4-flash"`
- 主控加载 skill 时尝试切换模型

### 方案 C: 混合架构 (平衡)

**特点**:
- 📋 小蓝: 持久化子 agent (高频使用)
- 🏠 设计专家: skill 按需加载 (低频)
- 💻 技术支持: skill 按需加载 (低频)

## 🚀 推荐实现

### 第1步: 创建小蓝持久化子 Agent

```bash
# 通过 OpenClaw API 创建
sessions_spawn \
  --label "小蓝" \
  --model "glm-4-flash" \
  --mode "session" \
  --thread true \
  --task "工作日志专家"
```

### 第2步: 主控调度逻辑

```
用户消息 → 主控分析 →
  ├─ 工作日志相关 → sessions_send("小蓝", 消息)
  ├─ 设计任务 → 加载 design-skill
  └─ 技术问题 → 加载 tech-skill
```

### 第3步: 成本优化

**GLM-4-Flash** (便宜):
- 小蓝: 工作日志记录
- 小蓝: 简单查询
- 技术支持: 基础代码

**GLM-4-Plus** (中等):
- 室内设计专家
- 复杂分析任务

**GLM-4.7** (强大):
- 主控: 任务分配和决策
- 复杂项目管理

## 📝 配置示例

### 小蓝配置

```yaml
agent:
  id: xiaolan
  name: 小蓝
  model: glm-4-flash
  runtime: subagent
  mode: session
  thread: true

capabilities:
  - record_worklog
  - query_worklog
  - update_status

context:
  - table: 蓝色光标工作日志
    token: BISAbNgYXa7Do1sc36YcBChInnS
    id: tbl5s8TEZ0tKhEm7
```

### 主控配置

```yaml
agent:
  id: main
  name: 大领导
  model: glm-4.7

routing:
  - trigger: "小蓝|工作日志|记录"
    action: forward_to_agent
    target: xiaolan

  - trigger: "设计|图纸|效果图"
    action: load_skill
    skill: interior-design

  - trigger: "代码|编程|技术"
    action: load_skill
    skill: tech-support
```

## 💰 成本对比

### 当前架构
- 所有任务: GLM-4.7
- 日志记录: ~2000 tokens/次
- 10次记录 = 20,000 tokens

### 优化后
- 日志记录: GLM-4-Flash
- 日志记录: ~1000 tokens/次
- 10次记录 = 10,000 tokens
- **节省 50% token**

## 🔄 工作流程

### 场景1: 记录工作日志

```
用户: "小蓝,记录整理茶水柜"
  ↓
主控: 识别到"小蓝"关键词
  ↓
主控: sessions_send("xiaolan", "记录整理茶水柜")
  ↓
小蓝: 独立处理 (GLM-4-Flash)
  ↓
小蓝: 调用飞书 API
  ↓
小蓝: 回复 "✅ 已记录..."
  ↓
用户: 收到小蓝的回复
```

### 场景2: 复杂设计任务

```
用户: "帮我设计会议室布局"
  ↓
主控: 识别到设计任务
  ↓
主控: 加载 interior-design skill
  ↓
主控: 使用 GLM-4-Plus 执行
  ↓
主控: 输出设计方案
```

## ⚙️ 实现清单

- [ ] 创建小蓝持久化子 agent
- [ ] 配置主控路由规则
- [ ] 测试模型切换
- [ ] 验证成本节省
- [ ] 创建其他专业 agent (按需)

## 🎯 下一步

你想先实现哪个方案?
1. **方案A**: 完整的持久化子 agent 系统
2. **方案C**: 混合架构 (只创建小蓝子 agent,其他用 skill)
3. **逐步试点**: 先测试小蓝子 agent,验证后再扩展
