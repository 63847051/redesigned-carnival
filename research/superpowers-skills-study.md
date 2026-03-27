# Superpowers 技能系统深度研究报告

**研究时间**: 2026-03-26  
**研究目标**: 深入研究 Superpowers 的技能实现，提取最佳实践  
**仓库**: https://github.com/obra/superpowers

---

## 一、技能清单

### 1.1 完整技能列表

Superpowers 提供了 **14 个核心技能**，分为 4 大类别：

| 类别 | 技能名称 | 功能描述 |
|------|----------|----------|
| **核心开发** | brainstorming | 在编写代码前进行创意工作，通过苏格拉底式提问细化需求 |
| | using-git-worktrees | 并行开发分支管理 |
| | writing-plans | 详细实现计划编写 |
| | subagent-driven-development | 子代理快速迭代开发（两阶段审查） |
| | test-driven-development | RED-GREEN-REFACTOR 测试驱动开发 |
| | requesting-code-review | 代码审查前检查清单 |
| | finishing-a-development-branch | 合并/PR 决策工作流 |
| **调试** | systematic-debugging | 4 阶段根因分析过程 |
| | verification-before-completion | 完成前验证 |
| **协作** | executing-plans | 批量执行与检查点 |
| | dispatching-parallel-agents | 并发子代理工作流 |
| | receiving-code-review | 响应代码审查反馈 |
| **元技能** | writing-skills | 创建新技能的最佳实践（含测试方法论） |
| | using-superpowers | 技能系统介绍和使用指南 |

---

## 二、核心技能深度分析

### 2.1 brainstorming 技能

**触发条件**: 任何创造性工作之前——创建功能、构建组件、添加功能或修改行为

#### 核心机制

```
HARD-GATE: 未获得用户批准前，禁止调用任何实现技能、编写代码、脚手架项目
```

#### 工作流程

```
探索项目上下文 → 询问澄清问题（一次一个）→ 提出 2-3 种方案 → 
展示设计 → 用户批准 → 编写设计文档 → 调用 writing-plans 技能
```

#### 关键实践

| 实践 | 描述 |
|------|------|
| **一次只问一个问题** | 避免用多个问题淹没用户 |
| **多选优先** | 封闭问题比开放问题更容易回答 |
| **YAGNI 原则** | 从所有设计中 ruthlessly 删除不必要的功能 |
| **探索替代方案** | 在确定方案前始终提出 2-3 种方法 |
| **增量验证** | 展示设计，获得批准后再继续 |
| **视觉伴侣** | 复杂 UI 问题可提供浏览器可视化辅助 |

#### 设计文档存储

```
docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
```

#### 与我们系统的对比

| 方面 | Superpowers | 我们的系统 |
|------|-------------|-----------|
| 触发机制 | 上下文感知自动触发 | 大领导判断后触发 |
| 设计审批 | 严格的 HARD-GATE | 取决于任务复杂度 |
| 文档存储 | 标准化路径 | 无标准化 |

---

### 2.2 writing-plans 技能

**触发条件**: 拥有需求或规格说明的多步骤任务

#### 核心机制

**任务粒度**: 每个步骤 2-5 分钟

```
"Write the failing test" - step
"Run it to make sure it fails" - step
"Write minimal code" - step
"Run tests" - step
"Commit" - step
```

#### 计划文档结构

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development

**Goal:** [One sentence]

**Architecture:** [2-3 sentences]

**Tech Stack:** [Key technologies]

---

### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Write minimal implementation**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**
```

#### 关键约束

1. **无占位符**: 不允许 "TBD"、"TODO"、"implement later"
2. **精确路径**: 每个文件必须有精确路径
3. **完整代码**: 每个代码步骤必须包含实际代码
4. **自我审查**: 检查覆盖范围、占位符、类型一致性

#### 执行选项

| 选项 | 描述 |
|------|------|
| **Subagent-Driven (推荐)** | 每个任务分配新子代理，任务间审查 |
| **Inline Execution** | 当前会话中使用 executing-plans 批量执行 |

#### 与我们系统的对比

| 方面 | Superpowers | 我们的系统 |
|------|-------------|-----------|
| 任务粒度 | 2-5 分钟精确拆分 | 取决于复杂度 |
| 代码要求 | 每步必须有实际代码 | 可能只是描述 |
| 审查机制 | 两阶段审查（规范→质量） | 简单检查 |

---

### 2.3 test-driven-development 技能

**触发条件**: 实现任何功能或错误修复之前

#### 核心铁律

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

违反此规则 = 删除代码，重新开始。

#### RED-GREEN-REFACTOR 循环

```
RED → Verify RED → GREEN → Verify GREEN → REFACTOR → Next
```

| 阶段 | 描述 | 必做 |
|------|------|------|
| **RED** | 编写一个失败的测试 | ✅ 观看测试失败 |
| **Verify RED** | 确认测试失败原因正确 | ✅ MANDATORY |
| **GREEN** | 编写最小代码通过测试 | ❌ 不要过度设计 |
| **Verify GREEN** | 确认测试通过，其他测试也通过 | ✅ MANDATORY |
| **REFACTOR** | 清理代码（不添加行为） | 保持测试绿色 |

#### 常见借口与现实

| 借口 | 现实 |
|------|------|
| "太简单，不需要测试" | 简单代码也会出错，测试只需 30 秒 |
| "之后写测试" | 测试立即通过 = 什么都没证明 |
| "手动测试过了" | 手动测试是临时的，不能重跑 |
| "TDD 太慢" | TDD 比调试快 |

#### 验证检查清单

- [ ] 每个新函数/方法都有测试
- [ ] 每个测试失败原因正确（功能缺失，非拼写错误）
- [ ] 编写最小代码通过每个测试
- [ ] 所有测试通过，输出无错误/警告

#### 与我们系统的对比

| 方面 | Superpowers | 我们的系统 |
|------|-------------|-----------|
| TDD 强制 | 铁律，无例外 | 可选，用户可跳过 |
| 测试验证 | 强制验证 RED 和 GREEN | 简单运行测试 |
| 反模式 | 详细反模式参考 | 无 |

---

## 三、最佳实践总结

### 3.1 设计原则

| 原则 | 描述 | 应用 |
|------|------|------|
| **YAGNI** | You Aren't Gonna Need It | 删除所有不必要功能 |
| **DRY** | Don't Repeat Yourself | 代码和任务都不重复 |
| **TDD** | Test-Driven Development | 先写测试，再写代码 |
| **复杂度最小化** | Simplicity as primary goal | 小文件，单一职责 |
| **证据优先** | Evidence over claims | 验证后再声明成功 |

### 3.2 工作流程

| 原则 | 描述 |
|------|------|
| **系统化优于临时** | Process over guessing |
| **验证优先** | Verify before declaring success |
| **小步提交** | 频繁提交，每次增量 |
| **无代码不动手** | No production code without test first |
| **根因分析** | Always find root cause before fixing |

### 3.3 技能设计模式

#### 技能文件结构

```
skills/
  skill-name/
    SKILL.md              # 主参考（必需）
    supporting-file.*     # 仅在需要时
```

#### YAML 前置说明

```yaml
---
name: skill-name-with-hyphens
description: Use when [具体触发条件]
---
```

**描述规则**:
- 以 "Use when..." 开头
- 描述触发条件，不是技能流程
- 使用第三人称
- 包含关键词（错误信息、症状、同义词）

#### 流程图使用

**仅用于**:
- 非显而易见的决策点
- 过程循环可能过早停止
- "何时用 A vs B" 决策

**从不用于**:
- 参考材料 → 用表格、列表
- 代码示例 → 用 Markdown 块
- 线性指令 → 用编号列表

#### 技能测试方法论

技能创建 = 代码的 TDD：

| TDD 概念 | 技能创建 |
|----------|----------|
| 测试用例 | 带子代理的压力场景 |
| 生产代码 | 技能文档（SKILL.md）|
| 测试失败（RED）| 无技能时 Agent 违反规则 |
| 测试通过（GREEN）| 有技能时 Agent 遵守 |
| 重构 | 关闭漏洞同时保持合规 |

---

## 四、改进建议

### 4.1 技能触发机制

#### 当前问题
- 我们的系统：大领导判断后触发
- 缺乏上下文自动感知

#### 改进方案

1. **添加技能检查清单**
   - 在每次任务开始前检查是否有适用技能
   - 使用关键词匹配 + 上下文分析

2. **创建技能映射表**

```markdown
| 任务类型 | 适用技能 |
|----------|----------|
| 新功能开发 | brainstorming → writing-plans → TDD |
| Bug 修复 | systematic-debugging → TDD |
| 多任务 | dispatching-parallel-agents |
| 代码审查 | requesting-code-review |
```

### 4.2 技能组合

#### 当前问题
- 我们的系统：独立技能使用
- 缺乏链式调用

#### 改进方案

1. **定义技能链**

```markdown
# 开发流程技能链

brainstorming (设计)
    ↓
writing-plans (计划)
    ↓
subagent-driven-development (执行)
    ↓
requesting-code-review (审查)
    ↓
finishing-a-branch (完成)
```

2. **添加技能组合文档**
   - 说明何时从一个技能过渡到另一个
   - 定义强制过渡点（如 brainstorming → writing-plans）

### 4.3 技能测试

#### 当前问题
- Superpowers：每个技能都有测试
- 我们的系统：缺乏测试

#### 改进方案

1. **创建测试场景**

```markdown
## 技能测试场景

### brainstorming 技能

**压力场景**:
- 用户说"帮我写个登录功能"
- Agent 应该如何反应？

**预期行为**:
1. 检查项目上下文
2. 询问澄清问题
3. 提出方案
4. 展示设计
5. 获得批准前不写代码
```

2. **自动化测试**

```bash
# 测试 brainstorming 技能
./test-skill.sh brainstorming <<EOF
用户：帮我写个登录功能
EOF
```

### 4.4 文档标准化

#### 当前问题
- 无统一的技能文档格式
- 缺乏设计文档存储标准

#### 改进方案

1. **采用 Superpowers 格式**

```
docs/
  superpowers/
    specs/          # 设计文档
      YYYY-MM-DD-<topic>-design.md
    plans/         # 实现计划
      YYYY-MM-DD-<feature>.md
```

2. **创建技能模板**

```yaml
---
name: skill-name
description: Use when [触发条件]
---

# Skill Name

## Overview
[1-2 句核心原则]

## When to Use
[触发条件和症状]

## Process
[详细流程]

## Checklist
- [ ] Step 1
- [ ] Step 2
```

### 4.5 实施路线图

| 阶段 | 任务 | 优先级 |
|------|------|--------|
| **Phase 1** | 创建技能检查清单 | 高 |
| **Phase 2** | 定义技能链和过渡规则 | 高 |
| **Phase 3** | 为核心技能创建测试场景 | 中 |
| **Phase 4** | 采用 Superpowers 文档格式 | 中 |
| **Phase 5** | 添加 TDD 强制机制 | 低 |

---

## 五、结论

Superpowers 提供了一个成熟的技能系统，其核心理念：

1. **强制工作流**：通过 HARD-GATE 和铁律确保流程不被跳过
2. **系统化方法**：每个技能都有明确的阶段和检查清单
3. **测试驱动**：技能本身也通过 TDD 方法创建和验证
4. **自动化触发**：上下文感知自动激活相关技能

我们的系统需要改进的地方：
- 添加技能自动检查机制
- 定义技能链和过渡规则
- 为技能创建测试场景
- 采用标准化的文档格式
- 考虑强制 TDD 流程

**核心借鉴**：Superpowers 的成功在于将软件开发最佳实践（YAGNI、DRY、TDD）系统化，并通过技能机制确保它们被严格遵循。

---

*报告生成时间: 2026-03-26*
*信息来源: https://github.com/obra/superpowers*
