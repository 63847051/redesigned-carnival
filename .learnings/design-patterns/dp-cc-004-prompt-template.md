# DP-CC-004: Prompt 模板模式

**创建时间**: 2026-03-20
**来源**: ClawCorp-OnePerson 项目深度研究
**状态**: ✅ 已实施

---

## 📊 设计模式概述

**问题**: 如何提高任务执行的一致性和准确性？

**解决方案**: 通过 Prompt 模板系统，为每个专家创建标准化的任务执行模板，确保任务理解准确、执行一致、输出符合要求。

**核心价值**:
- ✅ 统一的任务执行格式
- ✅ 清晰的角色定位
- ✅ 明确的输入输出要求
- ✅ 质量标准提醒

---

## 🎯 核心概念

### 1. Prompt 模板结构

```markdown
# {{EXPERT_NAME}} 任务模板

**版本**: v1.0
**角色**: {{ROLE}}
**模型**: {{MODEL}}
**触发词**: {{TRIGGER_KEYWORDS}}

---

## 📋 任务执行格式

### 1. 角色定位
### 2. 输入要求
### 3. 输出要求
### 4. 质量标准
### 5. 工作流程
### 6. 注意事项
```

### 2. 变量占位符

```
{{REQUIREMENT}}      - 具体需求
{{OUTPUT_DIR}}       - 输出目录
{{TASK_TYPE}}        - 任务类型
{{QUALITY_STANDARD}} - 质量标准
{{TECH_STACK}}       - 技术栈
{{LANGUAGE}}         - 编程语言
{{FRAMEWORK}}        - 框架
{{ENVIRONMENT}}      - 环境
```

### 3. 模板应用流程

```
1. 选择合适的模板
2. 替换变量占位符
3. 生成最终 Prompt
4. 发送给 AI Agent
5. 收集结果
```

---

## 🏗️ 架构设计

### 组件结构

```
┌─────────────────────────────────────────────────────────┐
│                  Prompt 模板系统                          │
│                (Prompt Template System)                  │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ 模板管理 │        │ 变量替换 │        │ 模板验证 │
   │ Manager │        │ Renderer │        │ Validator│
   └─────────┘        └─────────┘        └─────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                    ┌───────┴───────┐
                    ▼               ▼
              [模板应用]      [质量检查]
```

---

## 📁 文件结构

```
~/.openclaw/workspace/
├── scripts/
│   └── prompt-template-manager.sh       # 模板管理脚本
└── prompts/
    ├── tech-task-template.md           # 技术任务模板
    ├── log-task-template.md            # 日志任务模板
    └── design-task-template.md         # 设计任务模板
```

---

## 🔧 使用方法

### 1. 列出所有模板

```bash
~/.openclaw/workspace/scripts/prompt-template-manager.sh list
```

### 2. 显示模板内容

```bash
~/.openclaw/workspace/scripts/prompt-template-manager.sh show tech-task-template
```

### 3. 应用模板

```bash
~/.openclaw/workspace/scripts/prompt-template-manager.sh apply tech-task-template /tmp/task-prompt.md
```

### 4. 验证模板

```bash
~/.openclaw/workspace/scripts/prompt-template-manager.sh validate tech-task-template
```

---

## 📊 Prompt 模板

### 技术任务模板（tech-task-template.md）

**角色**: 小新（技术支持专家）
**模型**: opencode/minimax-m2.5-free
**触发词**: 代码、爬虫、数据、API、前端、脚本、开发、编程

**核心部分**:
- ✅ 角色定位
- ✅ 输入要求（任务类型、具体需求、技术栈、输出目录、质量标准）
- ✅ 输出要求（代码文件、测试文件、说明文档）
- ✅ 质量标准（代码可运行、测试通过、文档完整、无敏感信息）
- ✅ 工作流程（需求分析 → 方案设计 → 代码实现 → 测试验证 → 文档编写）
- ✅ 注意事项（代码规范、注释清晰、安全考虑）

---

### 日志任务模板（log-task-template.md）

**角色**: 小蓝（工作日志管理专家）
**模型**: glmcode/glm-4.5-air
**触发词**: 日志、记录、工作、任务、进度、统计、汇总

**核心部分**:
- ✅ 角色定位
- ✅ 输入要求（任务类型、工作来源、具体需求、目标表格、时间范围）
- ✅ 输出要求（日志记录、任务更新、统计报告、汇总文档）
- ✅ 质量标准（信息完整、格式正确、无错误、格式一致）
- ✅ 工作流程（读取数据 → 分析需求 → 更新记录 → 生成报告）
- ✅ 注意事项（数据准确、格式统一、及时更新）

---

### 设计任务模板（design-task-template.md）

**角色**: 室内设计专家
**模型**: glmcode/glm-4.7
**触发词**: 设计、图纸、平面图、立面图、天花、地面、排砖、柜体、会议室

**核心部分**:
- ✅ 角色定位
- ✅ 输入要求（任务类型、项目信息、具体需求、设计范围、质量要求）
- ✅ 输出要求（设计图纸、技术文档、变更说明）
- ✅ 质量标准（图纸清晰、尺寸准确、符合要求、命名规范）
- ✅ 工作流程（需求确认 → 方案设计 → 图纸绘制 → 质量检查）
- ✅ 注意事项（设计规范、尺寸标注、图层管理）

---

## 🎯 应用场景

### 场景 1: 技术任务执行

```bash
# 1. 应用模板
~/.openclaw/workspace/scripts/prompt-template-manager.sh apply tech-task-template /tmp/task-prompt.md

# 2. 替换变量
sed -i 's/{{REQUIREMENT}}/写一个Python爬虫/g' /tmp/task-prompt.md
sed -i 's/{{OUTPUT_DIR}}\/root\/output/g' /tmp/task-prompt.md

# 3. 发送给小新
opencode -m opencode/minimax-m2.5-free run "$(cat /tmp/task-prompt.md)"
```

### 场景 2: 日志任务执行

```bash
# 1. 应用模板
~/.openclaw/workspace/scripts/prompt-template-manager.sh apply log-task-template /tmp/task-prompt.md

# 2. 替换变量
sed -i 's/{{REQUIREMENT}}/更新今日工作日志/g' /tmp/task-prompt.md

# 3. 发送给小蓝
# (使用 glmcode/glm-4.5-air 模型)
```

### 场景 3: 设计任务执行

```bash
# 1. 应用模板
~/.openclaw/workspace/scripts/prompt-template-manager.sh apply design-task-template /tmp/task-prompt.md

# 2. 替换变量
sed -i 's/{{REQUIREMENT}}/设计3F会议室平面图/g' /tmp/task-prompt.md

# 3. 发送给设计专家
# (使用 glmcode/glm-4.7 模型)
```

---

## 📈 预期效果

| 指标 | 当前 | 优化后 | 提升 |
|------|------|--------|------|
| **任务执行一致性** | 基准 | +40% | **40%** |
| **任务理解准确率** | 基准 | +35% | **35%** |
| **输出质量稳定性** | 基准 | +30% | **30%** |

---

## 💡 最佳实践

### 1. 统一模板格式

**原则**:
- 所有模板使用相同结构
- 统一的变量命名规范
- 一致的质量标准

### 2. 变量命名规范

**原则**:
- 使用大写字母
- 用双花括号包围
- 名称清晰明确

**示例**:
```
{{REQUIREMENT}}
{{OUTPUT_DIR}}
{{TASK_TYPE}}
```

### 3. 模板版本管理

**原则**:
- 每个模板有版本号
- 记录创建和修改时间
- 保留历史版本

### 4. 定期审查和更新

**原则**:
- 每月审查模板效果
- 根据反馈优化模板
- 添加新的变量和标准

---

## 🔍 调试技巧

### 1. 验证模板完整性

```bash
~/.openclaw/workspace/scripts/prompt-template-manager.sh validate tech-task-template
```

### 2. 查看模板内容

```bash
~/.openclaw/workspace/scripts/prompt-template-manager.sh show tech-task-template
```

### 3. 测试模板应用

```bash
# 应用模板到测试文件
~/.openclaw/workspace/scripts/prompt-template-manager.sh apply tech-task-template /tmp/test.md

# 检查变量替换
cat /tmp/test.md | grep '{{'
```

---

## 🚀 未来改进

### 自动变量替换

- 自动检测和替换变量
- 支持默认值
- 变量验证

### 模板效果分析

- 跟踪模板使用效果
- 分析任务完成率
- 优化模板内容

### 集成到工作流

- 与任务依赖检查集成
- 与专家分配集成
- 与质量检查集成

---

## 📚 参考资料

- **ClawCorp 深度研究**: `/root/.openclaw/workspace/projects/clawcorp-study/CLAWCORP_DEEP_STUDY.md`
- **进化方案**: `/root/.openclaw/workspace/projects/clawcorp-study/EVOLUTION_PLAN_V5.17.md`
- **Phase 1 报告**: `/root/.openclaw/workspace/projects/clawcorp-study/PHASE-1-COMPLETION-REPORT.md`
- **Phase 2 报告**: `/root/.openclaw/workspace/projects/clawcorp-study/PHASE-2-COMPLETION-REPORT.md`
- **Phase 3 报告**: `/root/.openclaw/workspace/projects/clawcorp-study/PHASE-3-COMPLETION-REPORT.md`
- **原项目**: https://github.com/YUCC-edu/clawcorp-oneperson

---

## 🔗 与 Phase 1 + Phase 2 + Phase 3 的集成

### 完整工作流

```bash
# 1. 检查任务依赖
~/.openclaw/workspace/scripts/check-task-dependencies.sh check TASK-001

# 2. 分配专家
~/.openclaw/workspace/scripts/allocate-experts-fixed.sh allocate TASK-001 tech

# 3. 应用 Prompt 模板
~/.openclaw/workspace/scripts/prompt-template-manager.sh apply tech-task-template /tmp/task-prompt.md

# 4. 替换变量并执行
sed -i 's/{{REQUIREMENT}}/写一个Python脚本/g' /tmp/task-prompt.md
opencode -m opencode/minimax-m2.5-free run "$(cat /tmp/task-prompt.md)"

# 5. 质量检查
~/.openclaw/workspace/scripts/task-quality-check.sh check TASK-001 tech /path/to/output

# 6. 释放专家
~/.openclaw/workspace/scripts/allocate-experts-fixed.sh release TASK-001 tech
```

---

**创建时间**: 2026-03-20
**版本**: 1.0.0
**状态**: ✅ 已实施并测试

---

*本设计模式基于 ClawCorp-OnePerson 项目的深度研究，实现了 Prompt 模板系统，为每个专家创建标准化的任务执行模板，预期将任务执行一致性提升 40%以上。*
