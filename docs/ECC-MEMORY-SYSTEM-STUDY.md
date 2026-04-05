# ECC 记忆系统实现研究

**创建时间**: 2026-04-02 18:00
**参考来源**: OpenClaw 进阶手册 Vol.2 - Tip 26-28
**目标**: 深入理解 ECC 的记忆系统，对标我们的实现

---

## 🎯 ECC 记忆系统的三个核心功能

### 1. Memory Persistence Hooks

**功能**: 跨 session 的记忆持久化

**两个 Hook**:

**SessionStart Hook**:
- 触发时机：会话开始时
- 功能：自动加载记忆文件
- 读取位置: `~/.claude/projects/<project-hash>/memory.md`

**SessionEnd Hook**:
- 触发时机：会话结束时
- 功能：提取重要决策和模式，追加进记忆文件
- 写入位置: 同上

**关键特性**:
- ✅ 自动化：无需手动操作
- ✅ 项目级：每个项目独立的记忆
- ✅ 持久化：下次打开同一个项目，AI 记得上次的决策

---

### 2. Continuous Learning v2

**功能**: 团队级别的 AI 进化

**核心概念 - Instincts**:
- 从历史中学到的模式
- 带置信度评分（0 到 1）
- 低于 0.7 标记为"仍在验证"

**三个命令**:

**`/instinct-status`**:
- 查看 AI 学到了什么
- 显示每个 instinct 的置信度
- 示例输出:
  ```
  ✓ [0.92] 这个项目用 pnpm，不用 npm
  ✓ [0.87] 数据库列名用 snake_case
  ? [0.61] 偏好函数式写法（置信度偏低，仍在学习）
  ```

**`/instinct-export`**:
- 导出为文件
- 分享给团队
- 让所有人都规避踩过的坑

**`/evolve`**:
- 把相关 instincts 聚类
- 升华为正式的 Skill
- 形成可复用的知识

**核心价值**:
> 一个人踩过的坑，`/instinct-export` 之后发给团队，所有人都规避了。

---

### 3. Verification Loops

**功能**: 持续确认方向，防止走偏

**问题**: AI 经常在实现到一半时"走偏"
- 让它重构一个模块，它开始重写整个文件
- 还改了没让它动的接口

**解决方案**: 两种模式

**Checkpoint-based**:
- 用途：线性任务，定期打快照
- 操作：
  ```
  /checkpoint  # 打一个快照
  # 让 AI 继续工作
  # 50 行之后
  /verify      # 验证是否在预期轨道上
  ```
- 发现偏差立即回滚

**Continuous**:
- 用途：探索性任务
- 操作：持续评估输出质量
- 不打固定快照，持续监控

**适用场景**:
- 大文件重构 → Checkpoint 模式
- 多步迁移 → Checkpoint 模式
- 探索性任务 → Continuous 模式

---

## 📊 对标我们的实现

### Memory Persistence Hooks vs 我们的 WAL 协议

| 功能 | ECC Hooks | 我们的 WAL 协议 |
|------|-----------|----------------|
| **触发时机** | SessionStart/End | 每次关键信息 |
| **读取** | 自动加载 memory.md | 手动 memory_search |
| **写入** | 自动提取决策 | 手动 Retain 格式 |
| **验证** | 无 | wal-verify.sh 验证 |
| **重试** | 无 | 最多 3 次重试 |
| **自动化** | ✅ 完全自动 | ⚠️ 半自动 |

**我们的优势**:
- ✅ 有验证机制（wal-verify.sh）
- ✅ 有重试机制（失败自动重试）
- ✅ 结构化格式（Retain W/B/O）
- ✅ 健康监控（heartbeat-memory-check.sh）

**ECC 的优势**:
- ✅ 完全自动（无需手动触发）
- ✅ 项目级隔离
- ✅ SessionStart 自动加载

---

### Continuous Learning vs 我们的记忆系统

| 功能 | ECC CL v2 | 我们的系统 |
|------|-----------|-----------|
| **学习来源** | 历史对话 | 手动 Retain |
| **置信度** | ✅ 自动计算 | ⚠️ 手动标注 |
| **团队共享** | `/instinct-export` | ⚠️ 无 |
| **升华为 Skill** | `/evolve` | ⚠️ 无 |
| **验证机制** | 置信度 < 0.7 | ⚠️ 无 |

**我们可以学习的**:
- ✅ 自动置信度计算
- ✅ 团队共享机制
- ✅ Instinct → Skill 的升级路径

---

### Verification Loops vs 我们的检查机制

| 功能 | ECC Verification | 我们的检查 |
|------|-----------------|-----------|
| **检查点** | `/checkpoint` | ⚠️ 无 |
| **验证** | `/verify` | ⚠️ 无 |
| **回滚** | ✅ 支持 | ⚠️ 无 |
| **健康检查** | ⚠️ 无 | ✅ heartbeat-memory-check.sh |

**我们可以学习的**:
- ✅ Checkpoint 机制
- ✅ Verify 验证
- ✅ 回滚功能

---

## 🚀 我们可以实现的改进

### 改进 1: 自动置信度计算

**当前**: 手动标注 `O(c=0.9)`
**改进**: 自动计算置信度

**算法**:
```python
def calculate_confidence(statement, history):
    # 1. 检查是否多次出现
    occurrences = count_occurrences(statement, history)
    if occurrences >= 3:
        return 0.9

    # 2. 检查是否有证据支持
    if has_evidence(statement, history):
        return 0.8

    # 3. 检查是否是推测性表述
    if is_speculative(statement):
        return 0.6

    # 4. 默认中等置信度
    return 0.7
```

---

### 改进 2: 团队共享机制

**当前**: 每个人独立的 MEMORY.md
**改进**: 导出/导入 Instincts

**实现**:
```bash
# 导出个人的 Instincts
bash scripts/instinct-export.sh > my-instincts.json

# 导入团队的 Instincts
bash scripts/instinct-import.sh team-instincts.json

# 合并并去重
bash scripts/instinct-merge.sh my-instincts.json team-instincts.json
```

---

### 改进 3: Checkpoint 系统

**当前**: 无检查点机制
**改进**: 添加 checkpoint/verify 命令

**实现**:
```bash
# 打检查点
bash scripts/checkpoint.sh "开始重构数据采集模块"

# 验证进度
bash scripts/verify.sh

# 如果偏差，回滚
bash scripts/rollback.sh
```

---

### 改进 4: SessionStart 自动加载

**当前**: 手动 memory_search
**改进**: SessionStart Hook 自动加载

**实现**:
```python
# SessionStart Hook
def on_session_start():
    # 1. 读取项目记忆
    memory_file = get_project_memory()

    # 2. 搜索相关记忆
    relevant_memories = memory_search(memory_file)

    # 3. 注入到上下文
    inject_context(relevant_memories)
```

---

## 📋 实施计划

### 阶段 1: 自动置信度计算（本周）

**任务**:
- [ ] 分析历史对话，统计模式出现频率
- [ ] 实现自动置信度算法
- [ ] 整合到 Retain 自动提取脚本
- [ ] 测试验证

---

### 阶段 2: 团队共享机制（下周）

**任务**:
- [ ] 创建 instinct-export.sh
- [ ] 创建 instinct-import.sh
- [ ] 创建 instinct-merge.sh
- [ ] 设计 JSON 格式
- [ ] 测试团队协作

---

### 阶段 3: Checkpoint 系统（下周）

**任务**:
- [ ] 创建 checkpoint.sh
- [ ] 创建 verify.sh
- [ ] 创建 rollback.sh
- [ ] 实现快照存储
- [ ] 测试回滚功能

---

### 阶段 4: SessionStart Hook（未来）

**任务**:
- [ ] 研究 OpenClaw Hook 机制
- [ ] 实现 SessionStart Hook
- [ ] 实现 SessionEnd Hook
- [ ] 整合项目级记忆
- [ ] 测试自动化

---

## 🎯 核心学习点

### 1. 自动化是关键

> **ECC 的 Hooks 完全自动，无需手动操作**

我们的 WAL 协议虽然强大，但需要手动触发。未来可以借鉴 ECC 的自动化思路。

### 2. 置信度很重要

> **低于 0.7 的 instinct 标记为"仍在验证"，不会强制执行**

我们的 Retain 格式虽然有信心度，但没有使用这个机制来控制行为。

### 3. 团队级进化

> **一个人踩过的坑，/instinct-export 之后发给团队，所有人都规避了**

这是 Continuous Learning v2 最有价值的地方。我们的系统目前是个人级的。

### 4. 持续验证

> **Verification Loops 不只是跑测试，是持续确认方向**

我们的健康监控更偏向系统级，缺少任务级的验证机制。

---

## 📚 参考资料

- OpenClaw 进阶手册 Vol.2 - Tip 26-28
- ECC Longform Guide
- ECC v1.5.0

---

**状态**: 📖 研究完成
**下一步**: 实施改进计划
**预计完成**: 阶段 1（本周），阶段 2-3（下周），阶段 4（未来）
