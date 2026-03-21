# 集成工作流使用指南

**版本**: v1.0
**创建时间**: 2026-03-20
**状态**: ✅ 完成

---

## 📊 概述

本文档介绍如何使用完整的集成工作流系统，该系统整合了 Phase 1 到 Phase 4 的所有功能。

---

## 🎯 系统架构

### 完整工作流

```
1. 任务依赖检查（Phase 1）
   ↓
2. 专家分配（Phase 2）
   ↓
3. Prompt 模板应用（Phase 4）
   ↓
4. 任务执行
   ↓
5. 质量检查（Phase 3）
   ↓
6. 专家释放
   ↓
7. 失败重试（可选）
```

---

## 🔧 使用方法

### 方法 1: 使用集成脚本

```bash
~/.openclaw/workspace/scripts/integrated-workflow.sh execute TASK-ID TYPE REQUIREMENT OUTPUT
```

**参数说明**:
- `TASK-ID`: 任务 ID（如 TASK-001）
- `TYPE`: 任务类型（tech/log/design）
- `REQUIREMENT`: 具体需求
- `OUTPUT`: 输出目录

**示例**:
```bash
# 技术任务
~/.openclaw/workspace/scripts/integrated-workflow.sh execute \
    TASK-001 \
    tech \
    "写一个Python爬虫脚本" \
    /root/output/TASK-001

# 日志任务
~/.openclaw/workspace/scripts/integrated-workflow.sh execute \
    TASK-002 \
    log \
    "更新工作日志" \
    /root/output/TASK-002

# 设计任务
~/.openclaw/workspace/scripts/integrated-workflow.sh execute \
    TASK-003 \
    design \
    "设计会议室平面图" \
    /root/output/TASK-003
```

---

### 方法 2: 分步执行

#### Step 1: 检查任务依赖

```bash
~/.openclaw/workspace/scripts/check-task-dependencies.sh check TASK-001
~/.openclaw/workspace/scripts/check-task-dependencies.sh runnable
```

#### Step 2: 分配专家

```bash
~/.openclaw/workspace/scripts/allocate-experts-fixed.sh allocate TASK-001 tech
```

#### Step 3: 应用 Prompt 模板

```bash
~/.openclaw/workspace/scripts/prompt-template-manager.sh apply tech-task-template /tmp/task-prompt.md
sed -i 's/{{REQUIREMENT}}/写一个Python脚本/g' /tmp/task-prompt.md
```

#### Step 4: 执行任务

```bash
# 使用 opencode 执行技术任务
opencode -m opencode/minimax-m2.5-free run "$(cat /tmp/task-prompt.md)"

# 或使用其他模型执行日志任务
# (使用 glmcode/glm-4.5-air)
```

#### Step 5: 质量检查

```bash
~/.openclaw/workspace/scripts/task-quality-check.sh check TASK-001 tech /path/to/output
```

#### Step 6: 释放专家

```bash
~/.openclaw/workspace/scripts/allocate-experts-fixed.sh release TASK-001 tech
```

---

## 📊 系统状态监控

### 查看专家池状态

```bash
~/.openclaw/workspace/scripts/allocate-experts-fixed.sh status
```

### 查看资源使用

```bash
~/.openclaw/workspace/scripts/monitor-expert-resources.sh usage
```

### 查看所有任务

```bash
~/.openclaw/workspace/scripts/check-task-dependencies.sh list
```

---

## 🎓 实际案例

### 案例 1: 批量技术任务

```bash
# 创建 3 个技术任务
~/.openclaw/workspace/scripts/integrated-workflow.sh execute TASK-001 tech "写Python爬虫" /root/output/TASK-001
~/.openclaw/workspace/scripts/integrated-workflow.sh execute TASK-002 tech "写API接口" /root/output/TASK-002
~/.openclaw/workspace/scripts/integrated-workflow.sh execute TASK-003 tech "写前端页面" /root/output/TASK-003
```

### 案例 2: 混合任务类型

```bash
# 技术任务
~/.openclaw/workspace/scripts/integrated-workflow.sh execute TASK-001 tech "写脚本" /root/output/TASK-001

# 日志任务
~/.openclaw/workspace/scripts/integrated-workflow.sh execute TASK-002 log "更新日志" /root/output/TASK-002

# 设计任务
~/.openclaw/workspace/scripts/integrated-workflow.sh execute TASK-003 design "设计图纸" /root/output/TASK-003
```

---

## 💡 最佳实践

### 1. 合理规划任务

- 将大任务分解为小任务
- 设置合理的依赖关系
- 避免循环依赖

### 2. 监控资源使用

- 定期检查专家池状态
- 避免过度分配资源
- 及时释放专家资源

### 3. 质量优先

- 严格执行质量检查
- 不达标的任务重新执行
- 持续优化输出质量

### 4. 错误处理

- 失败任务分析原因
- 自动重试机制
- 人工介入点

---

## 🔧 故障排除

### 问题 1: 专家池已满

**解决**: 等待其他任务完成，或增加专家池大小

### 问题 2: 任务依赖未满足

**解决**: 检查依赖任务状态，等待依赖完成

### 问题 3: 质量检查失败

**解决**: 根据质量报告优化输出，重新检查

---

## 📚 相关文档

- **Phase 1 报告**: `/root/.openclaw/workspace/projects/clawcorp-study/PHASE-1-COMPLETION-REPORT.md`
- **Phase 2 报告**: `/root/.openclaw/workspace/projects/clawcorp-study/PHASE-2-COMPLETION-REPORT.md`
- **Phase 3 报告**: `/root/.openclaw/workspace/projects/clawcorp-study/PHASE-3-COMPLETION-REPORT.md`
- **Phase 4 报告**: `/root/.openclaw/workspace/projects/clawcorp-study/PHASE-4-COMPLETION-REPORT.md`

---

**更新时间**: 2026-03-20
**版本**: 1.0.0
**状态**: ✅ 完成
