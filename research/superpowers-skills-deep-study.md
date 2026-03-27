# Superpowers 技能系统深度研究报告

> 研究日期：2026-03-26
> 报告目标：深入分析 Superpowers 的技能系统，对比 AGENTS.md，提出改进建议

---

## 一、Superpowers 技能系统概览

### 1.1 项目背景

Superpowers 是由 Jesse Vincent 创建的 AI 编码代理技能框架，于 2025 年 10 月发布，截至 2026 年 3 月已获得 **114k+ GitHub Stars**，成为 GitHub 史上增长最快的开源项目之一。

**核心理念**：不是给 AI 代理更多工具，而是给它们更多**纪律**。

### 1.2 技能清单（14 个技能）

| 类别 | 技能名称 | 功能描述 |
|------|----------|----------|
| **测试** | test-driven-development | TDD 红-绿-重构循环 |
| **调试** | systematic-debugging | 四阶段根因分析 |
| **调试** | verification-before-completion | 完成前验证（证据优先） |
| **协作** | brainstorming | 苏格拉底式设计细化 |
| **协作** | writing-plans | 详细实施计划 |
| **协作** | executing-plans | 批量执行与检查点 |
| **协作** | dispatching-parallel-agents | 并行代理工作流 |
| **协作** | requesting-code-review | 代码审查请求 |
| **协作** | receiving-code-review | 代码审查反馈处理 |
| **协作** | using-git-worktrees | 并行开发分支 |
| **协作** | finishing-a-development-branch | 分支完成工作流 |
| **协作** | subagent-driven-development | 子代理驱动开发（两阶段审查） |
| **元** | writing-skills | 技能编写最佳实践 |
| **元** | using-superpowers | 技能系统入门 |

> 注：用户提及 15 个技能，实际为 14 个。

---

## 二、核心技能深度分析

### 2.1 brainstorming（头脑风暴）

**定位**：设计阶段 - 代码编写前必须触发

**核心原则**：
- 在任何创造性工作之前使用
- 通过苏格拉底式提问细化需求
- 不写代码，只做设计

**关键流程**：
1. 探索项目上下文（文件、文档、最近提交）
2. 提供视觉辅助（如需要）
3. 逐一提问理解需求
4. 提出 2-3 种方案及权衡
5. 分段展示设计，获取用户批准
6. 编写设计文档到 `docs/superpowers/specs/`
7. 自检spec
8. 用户审核
9. 触发 writing-plans

**HARD-GATE 机制**：
```
<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, 
or take any implementation action until you have presented a design and the 
user has approved it.
</HARD-GATE>
```

**反模式**：
- "这太简单了，不需要设计" → 所有项目都需要设计

---

### 2.2 test-driven-development（TDD）

**定位**：实施阶段 - 每次写代码前必须触发

**核心原则**：
- **铁律**：没有失败的测试就不能写生产代码
- 先写测试 → 看它失败 → 写最小代码让它通过 → 重构

**红-绿-重构循环**：

```
RED (写失败测试) → VERIFY RED (确认失败原因) → 
GREEN (最小代码) → VERIFY GREEN (确认通过) → 
REFACTOR (清理)
```

**强制验证**：
- 每次测试前必须运行测试命令
- 必须看到失败信息
- 测试通过后必须验证其他测试仍然通过

**反 Rationalization 表**：

| 借口 | 现实 |
|------|------|
| "太简单，不用测试" | 简单代码也会坏，测试只需30秒 |
| "之后再说" | 测试通过立即证明不了什么 |
| "手动测试过了" | 手动≠系统化，无记录无法重跑 |

---

### 2.3 systematic-debugging（系统调试）

**定位**：问题解决 - 任何bug、测试失败前触发

**核心原则**：
- **铁律**：没有根因分析就不能修复
- 症状修复就是失败

**四阶段流程**：

**Phase 1: 根因调查**
- 仔细阅读错误信息
- 稳定复现
- 检查最近变更
- 多组件系统：添加诊断日志
- 追踪数据流

**Phase 2: 模式分析**
- 找相似 working 代码
- 对比参考实现
- 识别差异

**Phase 3: 假设与测试**
- 形成单一假设
- 最小化测试
- 验证后继续

**Phase 4: 实施**
- 创建失败测试用例
- 实施单一修复
- 验证

**3 次修复失败 = 架构问题**：
```
If ≥ 3 fixes: STOP and question the architecture
```

---

### 2.4 subagent-driven-development（子代理驱动开发）

**定位**：计划执行 - 实施计划时使用

**核心原则**：
- 每个任务一个新子代理（隔离上下文）
- 两阶段审查：规格合规 → 代码质量

**执行流程**：
```
读取计划 → 提取任务 → 
为每个任务:
  1. 调度实施子代理
  2. 实施子代理实现、测试、提交、自检
  3. 调度规格审查子代理 → 确认合规?
  4. 调度代码质量审查子代理 → 批准?
  5. 修复问题 → 重新审查
  → 下一个任务
→ 最终代码审查
→ finishing-a-development-branch
```

**模型选择策略**：
- 机械实现任务（1-2文件）→ 快速便宜模型
- 集成判断任务（多文件）→ 标准模型
- 架构设计审查任务 → 最强模型

---

### 2.5 verification-before-completion（完成前验证）

**定位**：元技能 - 任何完成声明前必须触发

**核心原则**：
- **铁律**：没有新鲜验证证据就不能声称完成
- 证据在断言之前

**门控函数**：
```
BEFORE claiming any status:
1. IDENTIFY: 什么命令证明此声明?
2. RUN: 执行完整命令
3. READ: 完整输出，检查退出码
4. VERIFY: 输出确认声明?
   - NO: 用证据说明实际状态
   - YES: 带证据声明
5. ONLY THEN: 做出声明
```

**常见失败**：

| 声明 | 需要 | 不充分 |
|------|------|--------|
| 测试通过 | 测试输出：0 failures | 上次运行、"应该通过" |
| Linter干净 | Linter输出：0 errors | 部分检查、外推 |
| 构建成功 | 构建命令：exit 0 | Linter通过 |
| Bug修复 | 原始症状测试：pass | 代码改了、假定修复 |

---

### 2.6 writing-skills（编写技能）

**定位**：元技能 - 创建新技能时使用

**核心理念**：
- **编写技能就是 TDD 应用于流程文档**
- 测试用例（压力场景+子代理）→ 看失败 → 写技能 → 看通过 → 重构

**TDD 映射**：

| TDD 概念 | 技能创建 |
|----------|----------|
| 测试用例 | 压力场景+子代理 |
| 生产代码 | 技能文档(SKILL.md) |
| 测试失败(RED) | 无技能时代理违规(基线) |
| 测试通过(GREEN) | 有技能时代理合规 |
| 重构 | 堵住漏洞同时保持合规 |

**技能类型**：
- **Technique**: 具体方法+步骤
- **Pattern**: 思维方式
- **Reference**: API文档

**Claude 搜索优化(CSO)**：
- 描述字段：以 "Use when..." 开头，描述触发条件，不是工作流总结
- 关键词覆盖：错误信息、症状、同义词
- 描述性命名：动词-主动

---

## 三、最佳实践提取

### 3.1 纪律执行机制

**HARD-GATE（硬门控）**：
- brainstorming: 设计批准前不写代码
- TDD: 测试失败前不写代码
- 调试: 根因分析前不修复
- 验证: 运行命令前不声称成功

**反 Rationalization 表**：
- 每项技能都有"借口 vs 现实"表格
- 提前列出常见自我合理化

**红 Flags 列表**：
- 具体列出"停止"信号
- 如："code before test" = 删除，开始

### 3.2 强制工作流

**技能触发规则**：
```
If there is even a 1% chance a skill might apply → MUST invoke skill
```

**不可跳过**：
- 简单项目也需设计
- TDD 不可例外
- 验证不可跳过

### 3.3 子代理隔离

**关键原则**：
- Fresh subagent per task（新子代理 per 任务）
- 不继承主会话上下文
- 精确构建指令和上下文

### 3.4 证据导向

**verification-before-completion** 模板：
- 命令输出作为证据
- 截图/日志作为证据
- 禁止"应该"、"可能"、"看起来"

---

## 四、与 AGENTS.md 系统对比

### 4.1 架构对比

| 维度 | Superpowers | AGENTS.md |
|------|-------------|------------|
| **核心理念** | 纪律 > 工具 | 角色隔离 + 专业分工 |
| **技能机制** | 14个可组合技能 | 3个专业 Agent |
| **触发方式** | Skill工具自动检测 | 关键词触发 |
| **执行模式** | 子代理+两阶段审查 | 人工分配任务 |
| **验证方式** | 命令输出证据 | 人工确认 |
| **工作流** | 完整SDLC | 任务分发 |

### 4.2 关键差异

**Superpowers 优势**：
1. **强制流程**：技能必须触发，不可跳过
2. **TDD 集成**：每个代码变更必须测试驱动
3. **系统调试**：结构化根因分析
4. **证据验证**：声明必须带命令输出
5. **子代理隔离**：避免上下文污染

**AGENTS.md 优势**：
1. **角色清晰**：大领导-小新-小蓝-设计专家
2. **沟通隔离**：避免多Agent同时回复
3. **记忆系统**：长期记忆+短期记忆
4. **Heartbeat**：周期性主动检查
5. **HeyCube集成**：用户画像加载

### 4.3 互补分析

**可以借鉴 Superpowers**：
1. **HARD-GATE 机制**：关键节点必须获得批准
2. **TDD 强制执行**：技术任务必须测试驱动
3. **systematic-debugging**：结构化调试流程
4. **verification-before-completion**：证据导向声明

**AGENTS.md 独特价值**：
1. **团队角色模型**：清晰的组织结构
2. **沟通协议**：避免混乱
3. **记忆系统**：上下文保持
4. **Heartbeat**：主动服务能力

---

## 五、改进建议

### 5.1 短期改进（可立即实施）

**1. 添加 TDD 检查点**

在 AGENTS.md 中添加：
```markdown
### 小新技术任务 TDD 要求

技术任务必须遵循：
1. 先写失败测试
2. 验证测试失败原因
3. 写最小代码通过
4. 验证测试通过
5. 重构

禁止：
- 先写代码后补测试
- "之后再说"
- 跳过验证
```

**2. 添加验证要求**

```markdown
### 完成声明要求

任何"完成"、"通过"、"成功"声明必须：
- 包含命令输出证据
- 包含退出码
- 禁止"应该"、"可能"
```

### 5.2 中期改进（需要技能系统支持）

**1. 引入 skills/ 目录**

```
skills/
  tdd/
    SKILL.md
  debugging/
    SKILL.md
  verification/
    SKILL.md
```

**2. 技能触发检测**

在执行技术任务前：
1. 检查是否有相关技能
2. 加载技能
3. 遵循技能流程
4. 报告完成状态

### 5.3 长期改进（架构升级）

**1. 子代理工作流**

参考 subagent-driven-development：
- 大任务分解为子任务
- 每个子任务新子代理
- 两阶段审查

**2. 完整 SDLC 覆盖**

当前 AGENTS.md 流程：
```
用户 → 大领导 → 分配 → 执行 → 汇报
```

改进后：
```
用户 → 大领导
       ↓
    brainstorming (设计)
       ↓
    using-git-worktrees (隔离)
       ↓
    writing-plans (计划)
       ↓
    subagent-driven-development (执行)
       ↓
       ├── test-driven-development (TDD)
       ├── systematic-debugging (调试)
       └── verification-before-completion (验证)
       ↓
    requesting-code-review (审查)
       ↓
    finishing-a-development-branch (完成)
       ↓
    汇报结果
```

---

## 六、结论

Superpowers 的 14 个技能系统代表了 AI 编码代理的最佳实践，其核心价值在于：

1. **纪律优先**：强制流程，不可跳过
2. **证据导向**：声明必须有命令输出
3. **系统化**：每个领域都有结构化方法
4. **隔离执行**：子代理隔离上下文污染

AGENTS.md 的多 Agent 团队模型提供了清晰的角色分工和沟通协议，这是 Superpowers 所没有的。

**建议**：将 Superpowers 的技能机制与 AGENTS.md 的团队模型结合，形成既有纪律又有分工的高效工作流。

---

## 附录：技能快速参考表

| 技能 | 触发时机 | 核心产出 |
|------|----------|----------|
| brainstorming | 代码前 | 批准的设计文档 |
| using-git-worktrees | 实施前 | 隔离的工作目录 |
| writing-plans | 设计后 | 可执行的任务列表 |
| subagent-driven-development | 计划执行 | 实现的代码 |
| test-driven-development | 写代码前 | 通过的测试 |
| systematic-debugging | 遇到bug | 根因+修复 |
| verification-before-completion | 声称完成 | 验证证据 |
| requesting-code-review | 任务完成 | 审查反馈 |
| finishing-a-development-branch | 所有完成 | PR/合并决策 |

---

*报告完成 - 2026-03-26*
