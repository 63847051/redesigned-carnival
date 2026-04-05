# 后续学习路线图

**创建时间**: 2026-04-02 22:30
**基于**: 今日学习成果 + 实际需求
**目标**: 建立完整的能力体系

---

## 🎯 学习方向概览

### 优先级排序

| 优先级 | 学习内容 | 时间 | 价值 | 难度 |
|--------|---------|------|------|------|
| 🔴 **高** | **团队共享机制** | 3-4 小时 | 团队级进化 | 中等 |
| 🟡 **中** | **Checkpoint 系统** | 2-3 小时 | 防止走偏 | 中等 |
| 🟢 **低** | **自动触发机制** | 2-3 小时 | 扩展能力 | 简单 |

---

## 📋 详细学习计划

### 方向 1: 团队共享机制 ⭐ **强烈推荐**

**为什么重要**:
- **"一个人踩过的坑，团队都能规避"**
- 这是 Continuous Learning v2 最有价值的地方
- 从个人级进化到团队级

**学习内容**（基于 ECC Tip 27）:

#### 1.1 Instincts 概念
- Instincts 是"学到的规则"（不同于硬编码的规则）
- 置信度 0.7-1.0 才会执行
- 低于 0.7 标记为"仍在验证"

#### 1.2 核心命令
- `/instinct-status` - 查看学到了什么
- `/instinct-export` - 导出为文件
- `/instinct-import` - 导入团队经验
- `/instinct-evolve` - 升华为 Skill

#### 1.3 实现方式
- **格式**: JSON 文件
- **存储**: `.instincts/` 目录
- **合并**: 自动去重、解决矛盾
- **分享**: 通过 Git、文件传输

**预计时间**: 3-4 小时
**价值**: 🟡 团队级进化

**产出**:
- `scripts/instinct-export.sh` - 导出个人经验
- `scripts/instinct-import.sh` - 导入团队经验
- `scripts/instinct-merge.sh` - 合并去重
- `scripts/instinct-evolve.sh` - 升华为 Skill
- `docs/TEAM-SHARING-GUIDE.md` - 使用指南

**参考**:
- ECC Tip 27: Continuous Learning v2
- Continuous Learning vs Manual Instincts

---

### 方向 2: Checkpoint 系统

**为什么重要**:
- AI 经常在长任务中"走偏"
- 防止"让它重构一个模块，它开始重写整个文件"
- 持续确认方向，防止偏离目标

**学习内容**（基于 ECC Tip 28）:

#### 2.1 Checkpoint 概念
- **快照**: 保存当前状态
- **验证**: 确认进度符合预期
- **回滚**: 恢复到之前的快照

#### 2.2 两种模式
- **Checkpoint-based**: 每 N 步打一个快照
- **Continuous**: 每一步都验证

#### 2.3 核心命令
- `/checkpoint` - 打快照
- `/verify` - 验证进度
- `/rollback <id>` - 回滚到快照

#### 2.4 实现方式
- **快照存储**: `.checkpoints/` 目录
- **元数据**: JSON 文件（时间、描述、文件列表）
- **回滚机制**: 恢复文件、Git reset

**预计时间**: 2-3 小时
**价值**: 🟡 防止走偏

**产出**:
- `scripts/checkpoint.sh` - 创建快照
- `scripts/verify.sh` - 验证进度
- `scripts/rollback.sh` - 回滚到快照
- `docs/CHECKPOINT-GUIDE.md` - 使用指南

**参考**:
- ECC Tip 28: Verification Loops
- Checkpoint-based vs Continuous

---

### 方向 3: 自动触发机制

**为什么重要**:
- 让 Agent 真正"自己跑起来"
- 不需要每次手动触发
- 定时任务、文件监控、状态检测

**学习内容**（基于 OpenClaw Tip 1-5）:

#### 3.1 Cron 表达式
```json
{
  "triggers": {
    "cron": {
      "daily-9am": "0 9 * * *",
      "every-hour": "0 * * * *"
    }
  }
}
```

**注意**: ⚠️ **时区问题** - Cron 是 UTC，不是 GMT+8

#### 3.2 Webhook 触发
- `/hooks/wake` - 唤醒 Agent
- `/hooks/agent` - 触发特定 Agent
- 需要配置 Token 保护

#### 3.3 Gmail Pub/Sub
- 邮件触发 Agent
- 监听特定邮件
- 自动回复

#### 3.4 Browser Control
- 操作真实浏览器
- 自动化网页操作
- 定时检查网页

**预计时间**: 2-3 小时
**价值**: 🟢 扩展能力

**产出**:
- `configs/cron-example.json` - Cron 配置示例
- `scripts/setup-webhook.sh` - Webhook 配置
- `docs/AUTO-TRIGGER-GUIDE.md` - 使用指南

**参考**:
- OpenClaw Tip 1: Cron + Timezone
- OpenClaw Tip 2: Webhooks
- OpenClaw Tip 3: Gmail Pub/Sub
- OpenClaw Tip 4: Browser Control

---

## 🚀 推荐学习顺序

### 本周（如果还有时间）

**推荐**: 团队共享机制 ⭐
- 时间: 3-4 小时
- 优先级: 🔴 最高
- 理由: 从个人级进化到团队级

---

### 下周

**推荐**:
1. Checkpoint 系统（2-3 小时）
2. 自动触发机制（2-3 小时）

**原因**:
- Checkpoint 防止走偏（实用）
- 自动触发扩展能力（锦上添花）

---

## 📊 对比分析

### 团队共享机制 vs Checkpoint 系统

| 维度 | 团队共享 | Checkpoint |
|------|---------|-----------|
| **价值** | 团队级进化 | 防止走偏 |
| **难度** | 中等 | 中等 |
| **时间** | 3-4 小时 | 2-3 小时 |
| **影响** | 长期 | 短期 |
| **适用** | 多人团队 | 长任务 |
| **优先级** | 🔴 高 | 🟡 中 |

**结论**: 先做团队共享，再做 Checkpoint

---

### Checkpoint 系统 vs 自动触发

| 维度 | Checkpoint | 自动触发 |
|------|-----------|---------|
| **价值** | 防止走偏 | 扩展能力 |
| **难度** | 中等 | 简单 |
| **时间** | 2-3 小时 | 2-3 小时 |
| **影响** | 质量 | 效率 |
| **适用** | 长任务 | 定时任务 |
| **优先级** | 🟡 中 | 🟢 低 |

**结论**: 先做 Checkpoint，再做自动触发

---

## 💡 学习策略

### 原则 1: 先解决重要问题
- 🔴 团队共享 > 🟡 Checkpoint > 🟢 自动触发

### 原则 2: 边学边用
- 学习后立即应用
- 实际应用中验证
- 持续改进优化

### 原则 3: 不贪多
- 一次学一个
- 学透为止
- 避免"样样通，样样松"

---

## 🎯 成功指标

### 团队共享机制
- ✅ 能够导出个人经验
- ✅ 能够导入团队经验
- ✅ 能够自动去重
- ✅ 能够升华为 Skill

### Checkpoint 系统
- ✅ 能够创建快照
- ✅ 能够验证进度
- ✅ 能够回滚到快照
- ✅ 防止任务走偏

### 自动触发机制
- ✅ 配置 Cron 定时任务
- ✅ 配置 Webhook 触发
- ✅ 理解时区问题
- ✅ 能够自动化执行

---

## 📚 参考资料

- ECC Tip 27: Continuous Learning v2
- ECC Tip 28: Verification Loops
- OpenClaw Tip 1: Cron + Timezone
- OpenClaw Tip 2: Webhooks
- OpenClaw Tip 3: Gmail Pub/Sub
- OpenClaw Tip 4: Browser Control

---

**状态**: 📖 学习计划已制定
**下一步**: 选择一个方向开始学习
**建议**: 从团队共享机制开始 ⭐

---

你想从哪个开始？我强烈建议从**团队共享机制**开始！😊
