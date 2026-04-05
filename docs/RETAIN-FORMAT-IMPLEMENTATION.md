# Retain 格式实施计划

**创建时间**: 2026-04-02 11:50
**参考来源**: Wesley AI 日记 - OpenClaw Agent Team 记忆系统 v2.0
**目标**: 逐步改进记忆系统，按照可学习点的顺序实施

---

## 📋 实施顺序

### ✅ 1. 采用 Retain 格式（当前任务）

**目标**: 在每日日志中添加结构化记忆提取

**Retain 格式规范**:
```markdown
## Retain

### 世界知识 (W) - World Facts
- W @领域: 具体的事实性知识（客观、持久）
- W @API: API 使用规范和限制

### 行为记录 (B) - Behavior
- B @Agent: Agent 执行的具体行动
- B @项目: 项目进展和里程碑

### 观点偏好 (O) - Opinions
- O(c=0.9) @策略: 带信心度的观点和偏好
- O(c=0.7) @趋势: 不确定性的观察
```

**实施步骤**:
1. ✅ 创建 Retain 格式文档和模板
2. ⬜ 更新每日日志模板，包含 Retain 段落
3. ⬜ 创建提取脚本，自动生成 Retain 段落
4. ⬜ 测试和验证

---

### ⬜ 2. 加强过期清理机制

**目标**: 自动归档和定期审计

**实施内容**:
- 自动归档 30 天以上日志到 `memory/archive/`
- 定期审计 MEMORY.md，删除过时规则
- 添加清理脚本到心跳检查

---

### ⬜ 3. 完善健康监控

**目标**: 每日检查记忆系统状态

**检查清单**:
- MEMORY.md 是否超出 2000 tokens？
- 每日日志是否有 Retain 段落？
- SESSION-STATE.md 是否超过 24h 未更新？
- 有没有相互矛盾的规则？
- 最近 7 天有没有重复事故？

---

### ⬜ 4. 强化 WAL 协议执行

**目标**: 确保"先写再回复"不被绕过

**实施内容**:
- 添加写文件验证机制
- 确保 WAL 协议在所有场景下生效
- 添加失败重试机制

---

## 🎯 当前任务：Step 1 - 采用 Retain 格式

### Phase 1: 创建文档和模板 ✅ 已完成

**完成内容**:
- ✅ 创建实施计划文档
- ✅ 创建 Retain 格式规范文档（RETAIN-FORMAT-SPEC.md，3348 字符）
- ✅ 创建每日日志模板（templates/daily-log-template.md，958 字符）
- ✅ 创建今日日志并使用 Retain 格式（11 条目：5W + 4B + 2O）

**完成时间**: 2026-04-02 11:55

---

### Phase 2: 创建提取脚本（下一步）

**目标**: 自动从对话中提取 Retain 条目

**脚本功能**:
- 分析对话内容
- 识别 W/B/O 类型信息
- 生成结构化 Retain 段落
- 追加到每日日志

---

## 📚 参考资源

- Wesley AI 日记原文: https://mp.weixin.qq.com/s/QO90WBfHDZuNGUCFezWyow
- Claude Code 记忆系统: https://mp.weixin.qq.com/s/4GbmkQURpPRm1xiOMv7Mew

---

**状态**: 🔄 进行中 - Phase 1 完成
**下一步**: 创建 Retain 提取脚本
