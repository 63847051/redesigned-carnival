# DP-CC-001: 任务依赖调度模式

**创建时间**: 2026-03-20
**来源**: ClawCorp-OnePerson 项目深度研究
**状态**: ✅ 已实施

---

## 📊 设计模式概述

**问题**: 如何自动处理复杂的任务依赖关系，支持并行/串行混合执行？

**解决方案**: 通过任务依赖图、可执行条件检测、优先级队列和并行调度，实现智能的任务调度系统。

**核心价值**:
- ✅ 自动检测任务可执行状态
- ✅ 支持并行/串行混合执行
- ✅ 依赖图自动流转
- ✅ 任务优先级管理

---

## 🎯 核心概念

### 1. 任务状态机

```
pending → running → completed
                    ↘ failed
```

### 2. 任务可执行条件

```javascript
function canRun(task) {
  if (task.status !== 'pending') return false;
  if (!task.depends_on) return true;

  // 所有依赖必须完成
  return task.depends_on.every(depId => {
    const dep = findTask(depId);
    return dep.status === 'completed';
  });
}
```

### 3. 并行控制

```javascript
const maxParallel = 5;
const currentRunning = getRunningCount();
const slotsAvailable = maxParallel - currentRunning;

// 最多启动 slotsAvailable 个新任务
for (let i = 0; i < Math.min(runnable.length, slotsAvailable); i++) {
  spawnTask(runnable[i]);
}
```

---

## 🏗️ 架构设计

### 组件结构

```
┌─────────────────────────────────────────────────────────┐
│                    任务调度器                             │
│                  (Task Scheduler)                        │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ 依赖检查 │        │ 优先级  │        │ 并行调度 │
   │ Checker │        │  Queue  │        │Scheduler│
   └─────────┘        └─────────┘        └─────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                    ┌───────┴───────┐
                    ▼               ▼
              [任务执行]      [状态跟踪]
```

---

## 📁 文件结构

```
~/.openclaw/workspace/
├── scripts/
│   ├── check-task-dependencies.sh      # 依赖检查脚本
│   ├── task-priority-queue.sh          # 优先级队列脚本
│   └── parallel-execution-scheduler.sh # 并行调度脚本
└── tasks/
    ├── index.json                       # 任务索引
    ├── priority-queue.json              # 优先级队列
    ├── execution-status.json            # 执行状态
    └── *.json                           # 各个任务文件
```

---

## 🔧 使用方法

### 1. 初始化任务系统

```bash
~/.openclaw/workspace/scripts/check-task-dependencies.sh init
```

### 2. 创建任务

```bash
# 手动创建任务文件
cat > ~/.openclaw/workspace/tasks/TASK-001.json << EOF
{
  "task_id": "TASK-001",
  "name": "示例任务",
  "status": "pending",
  "depends_on": [],
  "priority": 2,
  "created_at": "2026-03-20T12:00:00Z"
}
EOF
```

### 3. 检查任务依赖

```bash
~/.openclaw/workspace/scripts/check-task-dependencies.sh check TASK-001
```

### 4. 添加任务依赖

```bash
~/.openclaw/workspace/scripts/check-task-dependencies.sh add TASK-002 TASK-001
```

### 5. 列出可执行任务

```bash
~/.openclaw/workspace/scripts/check-task-dependencies.sh runnable
```

### 6. 添加到优先级队列

```bash
~/.openclaw/workspace/scripts/task-priority-queue.sh init
~/.openclaw/workspace/scripts/task-priority-queue.sh add TASK-001 1  # 优先级 1（关键）
~/.openclaw/workspace/scripts/task-priority-queue.sh add TASK-002 2  # 优先级 2（高）
```

### 7. 调度并启动任务

```bash
~/.openclaw/workspace/scripts/parallel-execution-scheduler.sh schedule
```

### 8. 查看执行状态

```bash
~/.openclaw/workspace/scripts/parallel-execution-scheduler.sh status
```

---

## 📊 脚本功能说明

### check-task-dependencies.sh

**功能**:
- ✅ 初始化任务系统
- ✅ 检查任务依赖
- ✅ 列出所有任务
- ✅ 列出可执行任务
- ✅ 生成任务依赖图
- ✅ 添加任务依赖

**使用方法**:
```bash
check-task-dependencies.sh init
check-task-dependencies.sh check <task-id>
check-task-dependencies.sh list
check-task-dependencies.sh runnable
check-task-dependencies.sh graph
check-task-dependencies.sh add <task-id> <deps>
```

---

### task-priority-queue.sh

**功能**:
- ✅ 初始化优先级队列
- ✅ 添加任务到队列
- ✅ 获取下一个任务
- ✅ 列出队列中的所有任务
- ✅ 从队列中移除任务
- ✅ 更新任务优先级
- ✅ 清空队列

**优先级说明**:
- 1 - 关键任务（最高优先级）
- 2 - 高优先级
- 3 - 普通优先级（默认）
- 4 - 低优先级

**使用方法**:
```bash
task-priority-queue.sh init
task-priority-queue.sh add <task-id> [priority]
task-priority-queue.sh next
task-priority-queue.sh list
task-priority-queue.sh remove <task-id>
task-priority-queue.sh update <task-id> <priority>
task-priority-queue.sh clear
```

---

### parallel-execution-scheduler.sh

**功能**:
- ✅ 调度并启动可执行任务
- ✅ 启动指定任务
- ✅ 完成指定任务
- ✅ 显示执行状态
- ✅ 重置执行状态

**配置**:
- MAX_PARALLEL=5（最大并行任务数）

**使用方法**:
```bash
parallel-execution-scheduler.sh schedule
parallel-execution-scheduler.sh start <task-id>
parallel-execution-scheduler.sh complete <task-id> [success|fail]
parallel-execution-scheduler.sh status
parallel-execution-scheduler.sh reset
```

---

## 🎯 应用场景

### 场景 1: 简单任务执行

```
TASK-001 (无依赖) → 可立即执行
```

### 场景 2: 串行任务执行

```
TASK-001 → TASK-002 → TASK-003
```

### 场景 3: 并行任务执行

```
TASK-001 ──┐
           ├──→ TASK-003 (可并行)
TASK-002 ──┘
```

### 场景 4: 混合执行

```
TASK-001 ──┐
           ├──→ TASK-003 ──→ TASK-005
TASK-002 ──┘              └──→ TASK-004
```

---

## 📈 预期效果

| 指标 | 当前 | 优化后 | 提升 |
|------|------|--------|------|
| **任务并行度** | 2-3 个 | 5-10 个 | **100%+** |
| **任务完成率** | 80% | 95%+ | **15%+** |
| **调度效率** | 手动 | 自动 | **显著提升** |

---

## 💡 最佳实践

### 1. 合理设置任务优先级

- 关键任务：优先级 1
- 高优先级：优先级 2
- 普通任务：优先级 3（默认）
- 低优先级：优先级 4

### 2. 避免循环依赖

❌ 错误示例：
```
TASK-001 → TASK-002 → TASK-001
```

✅ 正确示例：
```
TASK-001 → TASK-002 → TASK-003
```

### 3. 合理设置并行度

- 根据系统资源调整 MAX_PARALLEL
- 建议值：3-10
- 过大可能导致资源竞争

### 4. 定期检查执行状态

```bash
# 每分钟检查一次
watch -n 60 ~/.openclaw/workspace/scripts/parallel-execution-scheduler.sh status
```

---

## 🔍 调试技巧

### 1. 查看任务依赖图

```bash
~/.openclaw/workspace/scripts/check-task-dependencies.sh graph > tasks.dot
dot -Tpng tasks.dot -o tasks.png
```

### 2. 查看任务详细信息

```bash
cat ~/.openclaw/workspace/tasks/TASK-001.json | jq .
```

### 3. 查看执行状态

```bash
cat ~/.openclaw/workspace/tasks/execution-status.json | jq .
```

---

## 🚀 未来改进

### Phase 2: 角色池化管理

- 为每个专家类型设置最大并行数
- 动态分配模型资源

### Phase 3: 质量门禁系统

- 定义任务完成的质量标准
- 自动检查输出质量

### Phase 4: Prompt 模板系统

- 为每个专家创建 Prompt 模板
- 提高任务执行的一致性

---

## 📚 参考资料

- **ClawCorp 深度研究**: `/root/.openclaw/workspace/projects/clawcorp-study/CLAWCORP_DEEP_STUDY.md`
- **进化方案**: `/root/.openclaw/workspace/projects/clawcorp-study/EVOLUTION_PLAN_V5.17.md`
- **原项目**: https://github.com/YUCC-edu/clawcorp-oneperson

---

**创建时间**: 2026-03-20
**版本**: 1.0.0
**状态**: ✅ 已实施并测试

---

*本设计模式基于 ClawCorp-OnePerson 项目的深度研究，实现了智能的任务依赖调度系统，支持并行/串行混合执行，预期将任务并行度提升 100%以上。*
