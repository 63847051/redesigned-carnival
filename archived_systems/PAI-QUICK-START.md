# PAI 快速参考指南 v3.0

**更新时间**: 2026-03-06
**版本**: v3.0（添加操作前检查）
**状态**: ✅ 已部署

---

## 🎯 PAI 系统三大核心功能

### 1️⃣ 学习信号捕获（事后记录）
**脚本**: `pai-learning-capture.sh`
**用途**: 任务完成后自动记录数据
**使用时机**: 每次任务完成后

```bash
bash scripts/pai-learning-capture.sh <类型> <复杂度> <结果> <描述>
```

**示例**:
```bash
bash scripts/pai-learning-capture.sh 设计 4 1 完成会议室平面图
bash scripts/pai-learning-capture.sh 错误 3 0 日期时间戳计算错误
```

---

### 2️⃣ 操作前检查（事前预防）⭐ NEW
**脚本**: `pai-pre-check.sh`
**用途**: 执行任务前检查历史错误和类似任务
**使用时机**: 每次执行任务前（特别是容易出错的）

```bash
bash scripts/pai-pre-check.sh <关键词1> [关键词2] [关键词3]
```

**示例**:
```bash
# 检查时间戳相关的历史错误
bash scripts/pai-pre-check.sh 时间戳 日期

# 检查飞书表格相关的历史任务
bash scripts/pai-pre-check.sh 飞书 表格

# 检查设计相关的经验
bash scripts/pai-pre-check.sh 设计 图纸
```

**输出内容**:
1. 🔍 Hot Memory 中的错误记录
2. 📊 Hot Memory 中的类似任务
3. 📅 今天的错误记录
4. ⚠️ 警告和建议

---

### 3️⃣ 智能查询助手（快速查询）⭐ NEW
**脚本**: `pai-ask.sh`
**用途**: 快速查询 PAI 记忆和历史记录
**使用时机**: 任何时候需要了解历史经验

```bash
bash scripts/pai-ask.sh <查询内容>
```

**示例**:
```bash
# 查询时间戳相关的记录
bash scripts/pai-ask.sh 时间戳错误

# 查询飞书表格相关的任务
bash scripts/pai-ask.sh 飞书表格

# 查询设计相关的任务
bash scripts/pai-ask.sh 设计图纸

# 特殊命令
bash scripts/pai-ask.sh --stats     # 显示统计信息
bash scripts/pai-ask.sh --recent    # 显示最近 10 条记录
bash scripts/pai-ask.sh --errors    # 显示所有错误记录
bash scripts/pai-ask.sh --success   # 显示所有成功记录
```

---

## 🚀 推荐工作流程

### 标准流程（所有任务）

```
1. 接收任务
   ↓
2. 操作前检查（如果容易出错）
   bash scripts/pai-pre-check.sh <关键词>
   ↓
3. 执行任务
   ↓
4. 记录学习信号
   bash scripts/pai-learning-capture.sh <类型> <复杂度> <结果> <描述>
   ↓
5. 完成 ✅
```

### 快速流程（简单任务）

```
1. 接收任务
   ↓
2. 执行任务
   ↓
3. 记录学习信号
   bash scripts/pai-learning-capture.sh ...
   ↓
4. 完成 ✅
```

### 查询流程（需要了解历史）

```
1. 需要了解某方面的经验
   ↓
2. 智能查询
   bash scripts/pai-ask.sh <查询内容>
   ↓
3. 查看结果和建议
   ↓
4. 应用到当前任务 ✅
```

---

## 📊 当前系统状态

### 数据统计（2026-03-06）
- **总记录数**: 20 条
- **成功记录**: 19 条
- **失败记录**: 1 条
- **成功率**: 95.0%
- **平均复杂度**: 4.4/5

### 自动运行
- **频率**: 每 6 小时
- **脚本**: `pai-auto-exec.sh`
- **功能**: 完整工作流、分析、建议、仪表板更新

---

## 🛡️ 防止重复错误的机制

### 机制 1: 操作前检查
- ✅ 自动检测历史错误
- ✅ 显示类似任务
- ✅ 检查今天的错误
- ✅ 提供警告和建议

### 机制 2: 智能查询
- ✅ 快速查询历史记录
- ✅ 按关键词搜索
- ✅ 按成功/失败过滤
- ✅ 统计分析

### 机制 3: 记录和反思
- ✅ 自动记录每次任务
- ✅ 情感分析
- ✅ 复杂度评估
- ✅ 成功率跟踪

---

## 💡 使用建议

### 什么时候使用操作前检查？

**必须使用**：
- 涉及时间戳计算
- 涉及日期格式
- 涉及文件删除或修改
- 之前犯过错误的任务

**建议使用**：
- 重要的设计任务
- 复杂的技术任务
- 不确定的操作

### 什么时候使用智能查询？

**快速查询**：
- 需要了解某方面的经验
- 需要查看历史错误
- 需要查看成功案例
- 需要了解系统状态

---

## 📋 完整命令参考

### 操作前检查
```bash
# 基本用法
bash scripts/pai-pre-check.sh <关键词>

# 示例
bash scripts/pai-pre-check.sh 时间戳
bash scripts/pai-pre-check.sh 飞书 表格
bash scripts/pai-pre-check.sh 日期 格式
```

### 智能查询
```bash
# 基本查询
bash scripts/pai-ask.sh <查询内容>

# 特殊命令
bash scripts/pai-ask.sh --stats     # 统计信息
bash scripts/pai-ask.sh --recent    # 最近 10 条
bash scripts/pai-ask.sh --errors    # 所有错误
bash scripts/pai-ask.sh --success   # 所有成功
bash scripts/pai-ask.sh --help      # 帮助信息
```

### 学习信号捕获
```bash
# 基本用法
bash scripts/pai-learning-capture.sh <类型> <复杂度> <结果> <描述>

# 成功示例
bash scripts/pai-learning-capture.sh 设计 4 1 完成会议室平面图

# 失败示例
bash scripts/pai-learning-capture.sh 错误 3 0 时间戳计算错误
```

---

## 🎯 未来改进方向

### 阶段 1: 智能提醒（已完成 ✅）
- ✅ 操作前检查脚本
- ✅ 智能查询脚本
- ✅ 快速参考指南

### 阶段 2: 集成到工作流（计划中）
- ⏳ 集成到小蓝（工作日志管理专家）
- ⏳ 集成到室内设计专家
- ⏳ 集成到技术支持专家

### 阶段 3: 自动预警（未来）
- ⏳ 自动检测危险操作
- ⏳ 自动提醒历史错误
- ⏳ 自动提供最佳实践

---

## 📝 相关文档

- **配置文档**: `.pai-learning/CONFIG.md`
- **v1.0 完成报告**: `PAI-INTEGRATION-COMPLETE.md`
- **v2.0 完成报告**: `PAI-DEEPENING-COMPLETE.md`
- **v3.0 完成报告**: `PAI-V3-UPGRADE-COMPLETE.md`（待创建）

---

## ✅ 升级总结

### 新增功能
1. ✅ `pai-pre-check.sh` - 操作前检查脚本
2. ✅ `pai-ask.sh` - 智能查询助手
3. ✅ `PAI-QUICK-START.md` - 快速参考指南

### 核心改进
1. ✅ 从"事后记录"到"事前预防"
2. ✅ 从"被动查询"到"主动检查"
3. ✅ 从"数据记录器"到"学习助手"

### 防护能力
1. ✅ 自动检测历史错误
2. ✅ 显示类似任务和经验
3. ✅ 智能查询和建议
4. ✅ 防止重复犯错

---

**PAI 系统现在真正有用了吗？**

**是的！现在 PAI 系统：**
- ✅ 记录数据（事后）
- ✅ 预防错误（事前）
- ✅ 智能查询（随时）
- ✅ 提供建议（主动）

**从"数据记录器"进化成"学习助手"！** 🎉

---

*更新时间: 2026-03-06 16:30*
*版本: v3.0*
*状态: ✅ 已部署并测试*
