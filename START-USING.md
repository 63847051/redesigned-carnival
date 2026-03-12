# 🚀 立即行动指南 - 大领导 PAI 系统

**创建时间**: 2026-03-05 08:24
**系统版本**: v7.0
**模式**: 实战应用模式 🎯

---

## ✅ 系统现状检查

### 🟢 所有系统运行正常
- ✅ 三层记忆系统：10 条 Hot Memory
- ✅ 学习信号：12 条已记录
- ✅ 可视化仪表板：可访问
- ✅ 自动运行：已配置（每 6 小时）
- ✅ 集成接口：已创建

**系统就绪度**: 🟢 100%

---

## 🎯 立即行动步骤

### 步骤 1: 了解如何使用（2 分钟）

#### 完成任务后，捕获学习信号
```bash
bash /root/.openclaw/workspace/scripts/pai-learning-capture.sh <类型> <复杂度1-5> <成功1/0> <描述>
```

**示例**:
```bash
# 完成设计任务
bash scripts/pai-learning-capture.sh 设计 4 1 完成3F平面图

# 完成技术任务
bash scripts/pai-learning-capture.sh 技术 5 1 修复数据库连接

# 遇到错误
bash scripts/pai-learning-capture.sh 系统 3 0 Gateway崩溃

# 完成日志记录
bash scripts/pai-learning-capture.sh 日志 2 1 更新工作日志
```

**参数说明**:
- **类型**: 设计/技术/日志/系统/进化/防护/其他
- **复杂度**: 1-5（1=简单，5=复杂）
- **成功**: 1=成功，0=失败
- **描述**: 简短描述

---

### 步骤 2: 查看系统状态（每天 1 次）

#### 方式 1: 命令行
```bash
bash /root/.openclaw/workspace/scripts/big-leader-pai.sh status
```

#### 方式 2: 可视化仪表板
**URL**: http://43.134.63.176/pai-dashboard/

**显示内容**:
- 📊 学习曲线
- 📈 任务类型分布
- 🎯 成功率趋势
- 📉 复杂度趋势

---

### 步骤 3: 让系统自动运行（无需操作）

**系统会自动**:
- 每 6 小时自动运行
- 捕获学习信号
- 生成分析报告
- 生成智能建议
- 更新仪表板
- 调用超级进化大脑（需要时）

**下次自动运行**: 约 6 小时后（14:00）

---

### 步骤 4: 查看分析报告（每天 1 次）

#### 每日报告
```bash
cat /root/.openclaw/workspace/.pai-learning/reports/$(date +%Y-%m-%d)-report.md
```

#### 快速分析
```bash
cat /root/.openclaw/workspace/.pai-learning/analysis-reports/quick-analysis-$(date +%Y-%m-%d).md
```

#### 智能建议
```bash
cat /root/.openclaw/workspace/.pai-learning/advice-reports/quick-advice-$(date +%Y-%m-%d).md
```

---

## 💡 使用场景

### 场景 1: 完成蓝色光标设计任务
```bash
# 任务：修改3F男女更衣室排砖平面图
bash scripts/pai-learning-capture.sh 设计 4 1 完成3F男女更衣室排砖平面图
```

**系统自动**:
1. 记录到 Hot Memory
2. 分析：设计任务，复杂度 4，成功
3. 建议：继续跟踪类似任务
4. 更新仪表板

---

### 场景 2: 遇到技术问题
```bash
# 任务：修复数据库连接
bash scripts/pai-learning-capture.sh 技术 5 1 修复数据库连接问题

# 如果失败
bash scripts/pai-learning-capture.sh 技术 5 0 数据库连接失败需要进一步排查
```

**系统自动**:
1. 记录成功或失败
2. 分析技术模式
3. 建议：成功方法或改进方向

---

### 场景 3: 系统错误
```bash
# 任务：Gateway 崩溃
bash scripts/pai-learning-capture.sh 系统 3 0 Gateway崩溃重启成功
```

**系统自动**:
1. 记录失败
2. 调用超级进化大脑防护层
3. 错误分析
4. 生成改进建议

---

### 场景 4: 记录工作日志
```bash
# 任务：更新工作日志
bash scripts/pai-learning-capture.sh 日志 2 1 更新蓝色光标工作日志
```

**系统自动**:
1. 记录日志任务
2. 分析日志模式
3. 优化日志流程

---

## 🎯 每日检查清单

### 每天早上（1 分钟）
- [ ] 查看可视化仪表板
- [ ] 检查系统状态

### 每次任务后（10 秒）
- [ ] 捕获学习信号

### 每天晚上（1 分钟）
- [ ] 查看智能建议
- [ ] 查看分析报告

---

## 📊 数据积累目标

### 第 1 周
- **目标**: 积累 50+ 条学习信号
- **重点**: 习惯使用系统

### 第 2 周
- **目标**: 积累 100+ 条学习信号
- **重点**: 观察模式和建议

### 第 3-4 周
- **目标**: 积累 200+ 条学习信号
- **重点**: 基于数据优化

---

## 🚀 高级使用（可选）

### 手动运行完整工作流
```bash
bash /root/.openclaw/workspace/scripts/pai-workflow.sh
```

### 测试集成接口
```bash
# 错误处理集成
bash scripts/pai-integration.sh error 测试错误 '测试上下文'

# 风险预警集成
bash scripts/pai-integration.sh risk 中风险 '测试上下文'

# 进化建议集成
bash scripts/pai-integration.sh evolve 测试任务 '测试上下文'
```

---

## 🎉 开始使用！

### 立即行动
1. **下次完成任务后**，捕获学习信号
2. **今天晚上**，查看仪表板和分析报告
3. **明天早上**，检查自动运行日志

### 不需要担心
- ✅ 系统会自动运行
- ✅ 系统会自动分析
- ✅ 系统会自动建议
- ✅ 系统会自动进化

---

**系统已就绪，开始实战应用！** 🚀

---

*创建时间: 2026-03-05 08:24*
*系统版本: v7.0*
*模式: 实战应用*
