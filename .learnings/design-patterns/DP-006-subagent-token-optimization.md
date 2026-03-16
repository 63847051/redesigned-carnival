# DP-006: 子 Agent Token 优化模式

**创建时间**: 2026-03-16
**作者**: 大领导系统 v5.15.1
**来源**: 基于 OpenClaw 多 Agent 协作最佳实践（娇姐文章）
**状态**: ✅ 设计完成，待验证

---

## 📋 模式概述

**问题**: 子 Agent 注入大量不必要的上下文文件（SOUL.md、IDENTITY.md、USER.md），导致 Token 开销过高

**解决方案**: 子 Agent 只注入必要的最小文件集，主 Agent 保留完整上下文

**效果**: 节省 30-50% Token，加快响应速度，保持核心能力不变

---

## 🎯 核心原则

### 原则 1: 身份 vs 技能分离

**SOUL.md 的作用**:
- ✅ 定义"身份"（我是谁、价值观、方法论）
- ❌ 不定义"技能"（代码能力、日志管理能力）

**技能来源**:
- 模型训练数据（主要）
- AGENTS.md（行为规则）
- TOOLS.md（工具说明）

**结论**: 子 Agent 不需要 SOUL.md 也能完成任务

---

### 原则 2: 主从上下文分层

**主 Agent（大领导）**:
- 注入完整上下文
- 需要 SOUL.md、IDENTITY.md、USER.md
- 理由: 需要全局视角做决策

**子 Agent（小新/小蓝）**:
- 注入最小上下文
- 只需要 AGENTS.md、TOOLS.md
- 理由: 只需执行具体任务

---

## 📊 注入文件对比

### 当前状态（所有 Agent 注入相同）

| 文件 | 主 Agent | 子 Agent | Token 占用 |
|------|----------|----------|------------|
| SOUL.md | ✅ | ✅ | ~2000 tokens |
| IDENTITY.md | ✅ | ✅ | ~500 tokens |
| USER.md | ✅ | ✅ | ~300 tokens |
| AGENTS.md | ✅ | ✅ | ~1000 tokens |
| TOOLS.md | ✅ | ✅ | ~500 tokens |
| **总计** | **~4300** | **~4300** | **100%** |

### 优化后（分层注入）

| 文件 | 主 Agent | 子 Agent | 说明 |
|------|----------|----------|------|
| SOUL.md | ✅ | ❌ | 主 Agent 需要全局视角 |
| IDENTITY.md | ✅ | ❌ | 主 Agent 需要身份定义 |
| USER.md | ✅ | ❌ | 主 Agent 需要用户信息 |
| AGENTS.md | ✅ | ✅ | 两者都需要行为规则 |
| TOOLS.md | ✅ | ✅ | 两者都需要工具说明 |
| **总计** | **~4300** | **~1500** | **节省 65%** |

---

## ⚠️ 不支持的配置字段（重要！）

**更新时间**: 2026-03-16 15:11

### 🔴 OpenClaw 不支持的字段

基于实践验证，以下字段**不在 OpenClaw Schema 中**，添加会导致 Gateway 崩溃：

| 字段 | 状态 | 说明 |
|------|------|------|
| `context` | ❌ 不支持 | 不在 Schema 中定义 |
| `context.excludeFiles` | ❌ 不支持 | 不在 Schema 中定义 |
| 任何未在文档中列出的字段 | ❌ 不支持 | 严格验证模式 |

### 🔴 事故记录

**时间**: 2026-03-16 14:42:39 - 14:43:48
**错误**: `agents.defaults.subagents: Unrecognized key: "context"`
**结果**: Gateway 反复崩溃重启（约 10 次）
**恢复**: 用户手动移除 `context` 字段
**修复**: 14:44 Gateway 恢复正常

**教训**:
1. ✅ 必须验证字段是否在 Schema 中
2. ✅ 不能随意添加未定义的配置字段
3. ✅ 实施前必须运行验证脚本

### ✅ 验证工具

**验证脚本**: `scripts/validate-config.sh`

**功能**:
- ✅ 检查 JSON 格式
- ✅ 检查 Gateway 状态
- ✅ 检查已知无效字段
- ✅ 提供修复建议

**使用方法**:
```bash
# 修改配置前验证
~/.openclaw/workspace/scripts/validate-config.sh

# 如果 Gateway 崩溃，查看日志
journalctl --user -u openclaw-gateway --since "10 minutes ago"
```

---

## 🔧 实施方案

## 🔧 实施方案

### ⚠️ 实施前检查清单（必读！）

**Step 1: 验证配置**
```bash
# 运行验证脚本
~/.openclaw/workspace/scripts/validate-config.sh
```

**Step 2: 检查文档**
```bash
# 查阅配置参考
open https://docs.openclaw.ai/gateway/configuration-reference
```

**Step 3: 测试环境验证**
```bash
# 在测试环境先试运行
# 观察是否有错误
```

**Step 4: 生产环境实施**
```bash
# 确认无问题后再应用到生产环境
```

---

### 方案 1: OpenClaw 配置级（部分实施）

**状态**: ⚠️ **部分实施**

**已生效的优化**:
```json
{
  "subagents": {
    "model": "opencode/minimax-m2.5-free",
    "runTimeoutSeconds": 300,
    "maxConcurrent": 8,
    "maxChildrenPerAgent": 5
  }
}
```

**未实施的部分**:
- ❌ `context.excludeFiles`（不支持，会导致崩溃）

**原因**: OpenClaw 不支持 `context` 字段

---

### 方案 2: 替代方案（推荐）

**在 `openclaw.json` 中配置**:

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "model": "opencode/minimax-m2.5-free",
        "runTimeoutSeconds": 300,
        "maxConcurrent": 8,
        "maxChildrenPerAgent": 5
      },
      "context": {
        "excludeFiles": ["SOUL.md", "IDENTITY.md", "USER.md"]
      }
    }
  }
}
```

**优点**:
- ✅ 全局生效，所有子 Agent 自动应用
- ✅ 无需修改代码
- ✅ 易于维护

**注意**: 需要确认 OpenClaw 是否支持 `context.excludeFiles` 配置

---

### 方案 2: 调用模板级（备用）

**在 IDENTITY.md 中添加子 Agent 调用模板**:

```markdown
## 子 Agent 调用标准模板

### 技术任务（小新）
```json
{
  "task": "具体任务描述",
  "agentId": "opencode",
  "model": "opencode/minimax-m2.5-free",
  "runTimeoutSeconds": 300,
  "thinking": "none",
  "mode": "run",
  "cleanup": "delete"
}
```

### 日志任务（小蓝）
```json
{
  "task": "具体任务描述",
  "model": "glmcode/glm-4.5-air",
  "runTimeoutSeconds": 300,
  "thinking": "none",
  "mode": "run",
  "cleanup": "delete"
}
```

**关键参数**:
- `runTimeoutSeconds`: 300（5 分钟超时）
- `thinking`: "none"（关闭扩展思考，节省 Token）
- `mode`: "run"（一次性执行，非持久会话）
- `cleanup`: "delete"（完成后立即归档）

---

## ⚠️ 风险评估

### 风险 1: 子 Agent 丢失"身份"感知 ⚠️

**可能性**: 低

**影响**: 
- 子 Agent 不知道自己是"大领导系统"的一部分
- 可能无法理解系统的价值观和原则

**缓解措施**:
- 在 AGENTS.md 中添加简要的身份说明
- 在任务描述中明确角色定位

**示例**:
```markdown
## AGENTS.md（子 Agent 版）

### 你是谁
你是"大领导系统"的一部分，负责技术支持工作。

### 你的角色
你是小新，技术支持专家。

### 你的职责
- 编程和技术相关任务
- 代码编写、调试、技术问题解决
```

---

### 风险 2: 关键规则未传递 ⚠️

**可能性**: 中

**影响**:
- RULE-001（重要操作必须等待确认）可能不被子 Agent 遵守
- 可能导致未授权的操作

**缓解措施**:
- 在 AGENTS.md 中明确列出关键规则
- 在任务描述中强调规则要求

**示例**:
```markdown
### 关键规则（必须遵守）

**RULE-001**: 重要操作必须等待确认
- Git 推送前必须询问用户
- 文件删除前必须询问用户
- 系统配置修改前必须询问用户
```

---

### 风险 3: 子 Agent 理解能力下降 ⚠️

**可能性**: 低

**影响**:
- 子 Agent 可能无法理解复杂的任务上下文
- 可能需要更多的澄清和反复

**缓解措施**:
- 在任务描述中提供充分的上下文
- 主 Agent 在分配任务时提供必要的背景信息

**示例**:
```markdown
### 任务描述模板

**背景**: [为什么需要这个任务]
**目标**: [要达成什么结果]
**约束**: [有什么限制条件]
**输出**: [期望的输出格式]
```

---

## ✅ 验证计划

### 阶段 1: 单元测试（1-2 天）

**测试用例**:
1. 简单任务: "写一个 Python 函数计算斐波那契数列"
2. 中等任务: "分析这段代码的性能瓶颈"
3. 复杂任务: "实现一个完整的 Web 爬虫"

**验证指标**:
- ✅ 任务完成质量（与优化前对比）
- ✅ Token 使用量（预期减少 30-50%）
- ✅ 响应时间（预期加快 20-30%）
- ✅ 是否遵守关键规则（RULE-001）

---

### 阶段 2: 集成测试（3-5 天）

**测试场景**:
1. 多次调用子 Agent（验证稳定性）
2. 并发调用（验证性能）
3. 长时间运行（验证内存使用）

**验证指标**:
- ✅ 子 Agent 是否稳定运行
- ✅ 是否有意外行为
- ✅ 是否遵守超时限制

---

### 阶段 3: 实际应用（1-2 周）

**真实任务**:
1. 日常工作日志管理
2. 技术问题排查
3. 代码编写和调试

**验证指标**:
- ✅ 用户满意度
- ✅ 工作效率是否提升
- ✅ Token 成本是否降低

---

## 📊 预期效果

### Token 节省

**场景 1: 简单任务**
- 优化前: ~5000 tokens
- 优化后: ~2000 tokens
- 节省: **60%**

**场景 2: 复杂任务**
- 优化前: ~10000 tokens
- 优化后: ~6000 tokens
- 节省: **40%**

**场景 3: 多次调用**
- 优化前: 每次 ~4300 tokens
- 优化后: 每次 ~1500 tokens
- 节省: **65%**

---

### 响应速度

**场景 1: 简单任务**
- 优化前: ~5 秒
- 优化后: ~3 秒
- 加快: **40%**

**场景 2: 复杂任务**
- 优化前: ~15 秒
- 优化后: ~10 秒
- 加快: **33%**

---

## 🎯 决策建议

### 立即实施（推荐）

**理由**:
1. ✅ 风险低（核心能力不受影响）
2. ✅ 收益高（节省 30-50% Token）
3. ✅ 易于回滚（配置可随时恢复）

**实施步骤**:
1. 先用方案 2（调用模板）进行测试
2. 验证无问题后，考虑方案 1（配置级）
3. 持续监控子 Agent 的表现

---

### 暂缓实施（保守）

**理由**:
1. ⚠️ 需要充分验证（1-2 周测试期）
2. ⚠️ 可能需要调整 AGENTS.md
3. ⚠️ 需要确保关键规则被遵守

**适用情况**:
- 对子 Agent 的质量要求极高
- 不容忍任何性能下降
- 有充足的时间进行测试

---

## 📚 参考资料

**来源**:
- 娇姐文章《先关注后阅读，娇姐怕失去上进的你》
- OpenClaw 多 Agent 协作最佳实践

**相关设计模式**:
- DP-001: CLI 兼容层设计模式
- DP-002: 并行执行编排模式
- DP-GO-001 ~ DP-GO-004: Golutra 相关模式

---

## 📝 更新日志

**2026-03-16**:
- ✅ 创建设计模式文档
- ✅ 完成风险评估
- ✅ 制定验证计划
- ✅ 提供决策建议

**待更新**:
- ⏳ 验证测试结果
- ⏳ 实际应用效果
- ⏳ 优化建议

---

**状态**: ✅ 设计完成，待验证

**下一步**: 等待用户确认后，开始实施测试

---

## ⚠️ 重要更新：不支持的字段（2026-03-16）

### 🔴 OpenClaw 不支持的字段

基于实践验证，以下字段**不在 OpenClaw Schema 中**，添加会导致 Gateway 崩溃：

| 字段 | 状态 | 说明 |
|------|------|------|
| `context` | ❌ 不支持 | 不在 Schema 中定义 |
| `context.excludeFiles` | ❌ 不支持 | 不在 Schema 中定义 |
| 任何未在文档中列出的字段 | ❌ 不支持 | 严格验证模式 |

### 🔴 事故记录

**时间**: 2026-03-16 14:42:39 - 14:43:48
**错误**: `agents.defaults.subagents: Rnrecognized key: "context"`
**结果**: Gateway 反复崩溃重启（约 10 次）
**恢复**: 用户手动移除 `context` 字段
**修复**: 14:44 Gateway 恢复正常

### ✅ 验证工具

**验证脚本**: `scripts/validate-config.sh`

**功能**:
- ✅ 检查 JSON 格式
- ✅ 检查 Gateway 状态
- ✅ 检查已知无效字段
- ✅ 提供修复建议

**使用方法**:
```bash
# 修改配置前验证
~/.openclaw/workspace/scripts/validate-config.sh

# 如果 Gateway 崩溃，查看日志
journalctl --user -u openclaw-gateway --since "10 minutes ago"
```

### 🔧 修改后的实施方案

**推荐方案**: 方案 2（替代方案）

**方案 2A: 在 AGENTS.md 中明确说明**
**方案 2B: 任务描述中明确要求**
**方案 2C: 探索代码层面的实现**（长期）

**详细说明**:
- 在子 Agent 的 AGENTS.md 中添加上下文边界说明
- 在任务描述中明确角色和职责
- 避免使用不支持的配置字段

### 📚 参考文档

- https://docs.openclaw.ai/gateway/configuration-reference
- https://docs.openclaw.ai/tools/subagents
- /root/.openclaw/extensions/openclaw-lark/README.md

---
