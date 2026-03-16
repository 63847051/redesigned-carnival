# Relationship 系统 - 组织关系图谱

**创建时间**: 2026-03-16
**来源**: 基于 Clawith 的 Relationship 机制

---

## 🎯 核心理念

**每个 Agent 都要"认人"** - 知道老板是谁、同事是谁、谁的性格随和、谁老改需求！

---

## 📐 组织架构

### 主控 Agent（大领导）

```yaml
agent:
  id: main
  name: 大领导
  role: 项目总监
  level: 1  # 最高权限
  
  # 职责
  responsibilities:
    - 任务分配
    - 进度监督
    - 质量把关
    - 结果汇总
  
  # 权限
  permissions:
    - sessions_spawn  # 可以创建子 Agent
    - sessions_send    # 可以发送消息给子 Agent
    - subagents        # 可以管理子 Agent
    - all_tools        # 可以使用所有工具
  
  # 性格
  personality:
    style: 专业、高效、严格
    communication: 简洁直接
    decision_making: 快速果断
  
  # 工作方式
  work_style:
    - 分析任务类型
    - 分配给合适的 Agent
    - 监督执行进度
    - 审核输出质量
    - 汇总成果汇报
```

---

### 专业团队

#### 💻 小新（技术支持专家）

```yaml
agent:
  id: opencode
  name: 小新
  role: 技术支持专家
  level: 2  # 专业权限
  
  # 职责
  responsibilities:
    - 所有编程和技术相关任务
    - 代码编写、调试、技术问题解决
    - 脚本开发、架构建议
  
  # 触发词
  triggers:
    keywords:
      - 代码
      - 爬虫
      - 数据
      - API
      - 前端
      - 脚本
      - 开发
      - 编程
  
  # 性格
  personality:
    style: 严谨、专业、高效
    communication: 技术性强
    decision_making: 逻辑推理
  
  # 协作风格
  collaboration_style:
    - 独立工作
    - 定期汇报
    - 专注技术
  
  # 模型配置
  model:
    default: opencode/minimax-m2.5-free
    backup: groq/llama-3.3-70b-versatile
    fallback: glmcode/glm-4.6
  
  # 工作空间
  workspace:
    type: independent
    path: /root/.openclaw/workspace-opencode
```

---

#### 📋 小蓝（工作日志管理专家）

```yaml
agent:
  id: assistant
  name: 小蓝
  role: 工作日志管理专家
  level: 2  # 专业权限
  
  # 职责
  responsibilities:
    - 工作日志记录和管理
    - 任务进度跟踪
    - 数据统计和汇总
  
  # 触发词
  triggers:
    keywords:
      - 日志
      - 记录
      - 工作
      - 任务
      - 进度
      - 统计
      - 汇总
  
  # 性格
  personality:
    style: 细致、耐心、有条理
    communication: 清晰详细
    decision_making: 数据驱动
  
  # 协作风格
  collaboration_style:
    - 需要明确指令
    - 按部就班
    - 注重细节
  
  # 模型配置
  model:
    default: glmcode/glm-4.5-air
    backup: glmcode/glm-4.6
    fallback: google/gemini-2.5-flash
  
  # 工作空间
  workspace:
    type: independent
    path: /root/.openclaw/workspace-assistant
  
  # 飞书集成
  feishu:
    app_token: BISAbNgYXa7Do1sc36YcBChInnS
    table_id: tbl5s8TEZ0tKhEm7
```

---

## 🤝 关系网络

### 协作关系图

```
用户
  ↓ 任务请求
大领导（主控）
  ↓ 分析任务
  ├→ 小新（技术支持）
  │   ↓ 执行并汇报
  │   大领导
  │
  └→ 小蓝（日志管理）
      ↓ 执行并汇报
      大领导
        ↓ 汇总
      用户
```

---

### 通信方式

**主控 Agent → 子 Agent**:
```python
# 通过 sessions_spawn 调用
sessions_spawn(
    runtime="subagent",
    agentId="opencode",
    message="执行技术任务"
)
```

**子 Agent → 主控 Agent**:
```python
# 通过消息传递
sessions_send(
    sessionKey="main",
    message="任务完成，汇报结果"
)
```

**用户 → 主控 Agent**:
```python
# 通过飞书消息
# Gateway 自动路由
```

---

### 权限层级

| Level | Agent | 权限 |
|-------|-------|------|
| **Level 1** | 主控 Agent（大领导） | 最高权限 |
| **Level 2** | 专业 Agent（小新、小蓝） | 专业权限 |
| **Level 3** | 工具脚本 | 执行权限 |

**权限控制**:
- Level 1 可以创建和管理 Level 2 Agent
- Level 2 只能执行专业任务
- Level 3 只能执行特定命令

---

## 🔄 协作协议

### 任务分配协议

```yaml
protocol:
  name: task_allocation
  
  steps:
    1. 用户 → 大领导：任务请求
    2. 大领导 → 分析任务类型
    3. 大领导 → 分配给合适的 Agent
       - 技术任务 → 小新
       - 日志任务 → 小蓝
    4. Agent → 执行并汇报
    5. 大领导 → 汇总并反馈用户
  
  rules:
    - 单写者原则：一个文件只有一个写者
    - 调度时序：依赖关系清晰的顺序
    - 优先级：用户 > 主控 > 专业 Agent
```

---

### 冲突解决协议

```yaml
protocol:
  name: conflict_resolution
  
  rules:
    1. 优先级：主控 > 专业 Agent
    2. 协商：大领导协调
    3. 仲裁：用户最终决定
  
  examples:
    - 两个 Agent 需要同一资源 → 大领导协调分配
    - Agent 意见不一致 → 大领导仲裁
    - 用户不满意 → 用户最终决定
```

---

## 💡 实施方案

### 方案 1: 创建 relationships.md

```markdown
# 大领导系统的关系图谱

## 组织架构

### 主控 Agent（大领导）
- ID: main
- 名称: 大领导
- 角色: 项目总监

### 专业团队

#### 💻 小新（技术支持专家）
- ID: opencode
- 职责: 所有编程和技术相关任务
- 触发词: 代码、爬虫、数据、API、前端

#### 📋 小蓝（工作日志管理专家）
- ID: assistant
- 职责: 工作日志记录和管理
- 触发词: 日志、记录、工作、任务

## 关系网络

### 协作关系
- 大领导 → 小新：技术任务分配
- 大领导 → 小蓝：日志管理任务

### 通信方式
- 主控 Agent：直接调用
- 子 Agent：通过 sessions_spawn

### 权限层级
- Level 1：主控 Agent
- Level 2：专业 Agent
```

---

### 方案 2: 集成到 AGENTS.md

```markdown
## 组织关系

### 主控 Agent（大领导）
- 职责：任务分配和监督
- 理念："专业的事交给专业的人"

### 专业团队

#### 💻 小新（技术支持专家）
- Agent ID: opencode
- 模型: opencode/minimax-m2.5-free
- 触发词: 代码、爬虫、数据、API、前端

#### 📋 小蓝（工作日志管理专家）
- Agent ID: assistant
- 模型: glmcode/glm-4.5-air
- 触发词: 日志、记录、工作、任务

### 协作机制
- 显性协作（消息传递）
- 隐性协作（共享文件）
- 混合模式（灵活切换）
```

---

### 方案 3: 动态关系管理（长期）

```python
# 创建关系管理脚本
cat > scripts/manage-relationships.py << 'EOF'
#!/usr/bin/env python3
"""关系管理脚本 - 管理 Agent 之间的关系"""

import json

# 定义关系
relationships = {
    "main": {
        "name": "大领导",
        "role": "项目总监",
        "level": 1,
        "colleagues": ["opencode", "assistant"],
        "permissions": ["all"]
    },
    "opencode": {
        "name": "小新",
        "role": "技术支持专家",
        "level": 2,
        "boss": "main",
        "colleagues": ["assistant"],
        "permissions": ["code", "technical"]
    },
    "assistant": {
        "name": "小蓝",
        "role": "日志管理专家",
        "level": 2,
        "boss": "main",
        "colleagues": ["opencode"],
        "permissions": ["logs", "tasks"]
    }
}

# 保存关系
with open("relationships.json", "w") as f:
    json.dump(relationships, f, indent=2)

print("✅ 关系图谱已保存")
EOF

chmod +x scripts/manage-relationships.py
```

---

## 📊 与 Clawith 的对比

| 特性 | Clawith | 大领导系统 |
|------|---------|-----------|
| **关系管理** | 图数据库 | 文件定义 |
| **持久身份** | soul.md | SOUL.md |
| **长期记忆** | memory.md | MEMORY.md |
| **工作空间** | 独立容器 | 独立目录 |
| **关系图谱** | 可视化 | Markdown |

---

## 🚀 实施步骤

### Phase 1: 设计阶段（当前）
- ✅ 研究 Clawith 的 Relationship 机制
- ✅ 设计关系图谱
- ✅ 编写设计文档

### Phase 2: 实验阶段（下一步）
- ⏳ 创建 relationships.md
- ⏳ 集成到 AGENTS.md
- ⏳ 测试协作流程

### Phase 3: 优化阶段（长期）
- ⏳ 动态关系管理
- ⏳ 可视化关系图谱
- ⏳ 自动化关系建立

---

## 📚 参考资料

**Clawith 源码**:
- https://github.com/dataelement/Clawith
- backend/app/services/agent_context.py

**OpenClaw 文档**:
- https://docs.openclaw.ai/tools/subagents
- https://docs.openclaw.ai/concepts/multi-agent

---

**最后更新**: 2026-03-16 16:05
**维护者**: 大领导系统 v5.16.0
