# 🚨 关键规则执行保障机制 - 完整方案

**方案名称**: 规则记忆与执行保障系统
**版本**: 1.0
**创建时间**: 2026-03-12 00:13
**优先级**: 🔴 CRITICAL

---

## 🎯 目标

**确保我永远不会违反 RULE-001：重要操作必须等待确认**

---

## 📋 保障机制（5 层防护）

### 第 1 层：文件记录（持久化）

#### 1.1 规则文件
**位置**: `/root/.openclaw/workspace/.learnings/rules/critical-rule-001-wait-confirmation.md`

**内容**:
- 规则定义
- 触发场景
- 执行流程
- 错误示例
- 正确示例
- 检查清单

**更新频率**: 一次性写入，永久保存

#### 1.2 SOUL.md 更新
**位置**: `/root/.openclaw/workspace/SOUL.md`

**添加章节**: "🚨 关键规则（CRITICAL）"

**内容**:
- 规则 ID: RULE-001
- 优先级: CRITICAL
- 触发场景
- 执行流程
- 检查清单

**读取频率**: 每次会话开始时自动读取

---

### 第 2 层：启动检查（会话开始）

#### 2.1 AGENTS.md 更新
**位置**: `/root/.openclaw/workspace/AGENTS.md`

**添加到 "Every Session"**:
```markdown
## Every Session

Before doing anything else:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION** (direct chat with your human): Also read `MEMORY.md`
5. **Read `.learnings/rules/critical-rule-001-wait-confirmation.md`** — 关键规则 ⭐ CRITICAL
6. **Run `/root/.openclaw/workspace/scripts/check-critical-rules.sh`** — 规则检查 ⭐ CRITICAL

Don't ask permission. Just do it.
```

**执行时机**: 每次会话开始

#### 2.2 启动脚本
**位置**: `/root/.openclaw/workspace/scripts/session-start-check.sh`

**内容**:
```bash
#!/bin/bash
echo "🚨 会话启动 - 关键规则检查"
echo "================================"
echo ""
bash /root/.openclaw/workspace/scripts/check-critical-rules.sh
echo ""
echo "✅ 会话启动完成"
echo "⚠️  重要操作前必须等待用户确认！"
echo ""
```

**执行时机**: 每次会话开始时自动执行

---

### 第 3 层：心跳提醒（定时检查）

#### 3.1 HEARTBEAT.md 更新
**位置**: `/root/.openclaw/workspace/HEARTBEAT.md`

**添加章节**: "🚨 关键规则检查（每次心跳必做）"

**内容**:
```markdown
## 🚨 关键规则检查（每次心跳必做）

```bash
# 每次心跳时自动执行
bash /root/.openclaw/workspace/scripts/check-critical-rules.sh
```

**RULE-001: 重要操作必须等待确认**

**触发场景**：
- Git 推送
- 文件删除
- 系统配置修改
- 任何不可逆的操作
- 用户说"确认后再..."的操作

**执行流程**：
1. 生成报告/计划
2. **明确询问：请确认**
3. **等待明确回复"确认"或"可以"**
4. **只有收到确认后，才执行操作**

**违反此规则 = 严重错误**
```

**读取频率**: 每次心跳时读取（每 30 分钟）

#### 3.2 心跳脚本更新
**位置**: `/root/.openclaw/workspace/scripts/heartbeat-evolution.sh`

**添加到脚本末尾**:
```bash
# 关键规则检查
echo ""
echo "🚨 关键规则检查："
bash /root/.openclaw/workspace/scripts/check-critical-rules.sh
```

**执行频率**: 每 30 分钟一次（Cron 定时任务）

---

### 第 4 层：操作前检查（执行前强制）

#### 4.1 操作前检查脚本
**位置**: `/root/.openclaw/workspace/scripts/pre-operation-check.sh`

**内容**:
```bash
#!/bin/bash
# 重要操作前检查脚本

OPERATION="$1"

echo "🚨 重要操作检查"
echo "================"
echo ""
echo "操作: $OPERATION"
echo ""
echo "⚠️  检查清单："
echo "  [ ] 用户说'确认后'了吗？"
echo "  [ ] 这个操作不可逆吗？"
echo "  [ ] 这个操作涉及外部系统吗？"
echo "  [ ] 我明确询问用户确认了吗？"
echo "  [ ] 我收到用户明确回复了吗？"
echo ""
echo "💡 如果任何一个答案是'是'，必须等待用户确认！"
echo ""
echo "❌ 违规后果：严重错误"
echo ""

# 返回检查码（1 = 需要确认）
return 1
```

**使用场景**: 重要操作前执行

#### 4.2 Git 推送包装脚本
**位置**: `/root/.openclaw/workspace/scripts/safe-git-push.sh`

**内容**:
```bash
#!/bin/bash
# 安全的 Git 推送脚本

echo "🚨 Git 推送 - 安全检查"
echo "======================"
echo ""

# 执行操作前检查
bash /root/.openclaw/workspace/scripts/pre-operation-check.sh "git push"

echo ""
echo "⚠️  是否已获得用户明确确认？"
echo "  - 用户说'确认'或'可以'了吗？"
echo "  - 用户明确回复了吗？"
echo ""
echo "如果答案是'是'，执行："
echo "  git push $@"
echo ""
echo "如果答案是'否'，立即停止！"
```

**使用场景**: Git 推送前执行

---

### 第 5 层：违规纠正（错误后学习）

#### 5.1 违规记录
**位置**: `/root/.openclaw/workspace/.learnings/violations/`

**文件命名**: `violation-YYYY-MM-DD-HHMMSS.md`

**内容模板**:
```markdown
# 规则违规记录

**时间**: YYYY-MM-DD HH:MM:SS
**规则**: RULE-001
**严重程度**: 🔴 CRITICAL

## 违规详情

**用户指令**: [用户的原始指令]
**我做了什么**: [我的错误操作]
**应该怎么做**: [正确的做法]

## 错误分析

**为什么违规**: [分析原因]
**记忆失败点**: [哪个环节出问题]
**如何避免**: [改进措施]

## 纠正措施

1. [已采取的措施]
2. [需要采取的措施]
3. [预防措施]

## 用户体验影响

- [ ] 用户是否生气
- [ ] 用户是否失去信任
- [ ] 如何挽回信任

---

*记录时间: YYYY-MM-DD HH:MM:SS*
*状态: 已纠正*
```

#### 5.2 纠正流程
**当发现违规时**:
1. ⚠️ **立即停止操作**
2. 😔 **向用户道歉**
3. 📋 **说明错误和正确做法**
4. ✅ **询问是否需要撤回**
5. 📝 **记录违规**

**位置**: `/root/.openclaw/workspace/.learnings/violations/`

**分析频率**: 每次心跳时分析最近的违规记录

**提取教训**: 更新规则文件，强化记忆

---

## 🔄 完整执行流程

### 场景 1：重要操作（如 Git 推送）

```
用户说: "上传之前出一个对比的报告？我确认后再上传"
    ↓
[第 1 层] 文件记录已激活 ✅
    ↓
[第 2 层] 会话启动时已读取规则 ✅
    ↓
生成报告 ✅
    ↓
[第 4 层] 执行前检查 ⚠️
    ├─ 用户说"确认后"了吗？ ✅
    ├─ 需要等待确认 ✅
    └─ 明确询问：请确认 ⚠️
    ↓
等待用户回复 ⏸️
    ↓
用户说: "确认" ✅
    ↓
执行操作 ✅
```

### 场景 2：正常操作（如读取文件）

```
用户说: "读取 SOUL.md"
    ↓
[第 1 层] 文件记录已激活 ✅
    ↓
[第 2 层] 会话启动时已读取规则 ✅
    ↓
[第 4 层] 执行前检查 ⚠️
    ├─ 用户说"确认后"了吗？ ❌
    ├─ 这个操作不可逆吗？ ❌
    ├─ 这个操作涉及外部系统吗？ ❌
    └─ 不需要等待确认 ✅
    ↓
直接执行 ✅
```

---

## 📊 保障机制总结

| 层级 | 机制 | 频率 | 状态 |
|------|------|------|------|
| 第 1 层 | 文件记录 | 一次性 | ✅ |
| 第 2 层 | 启动检查 | 每次会话 | ✅ |
| 第 3 层 | 心跳提醒 | 每 30 分钟 | ✅ |
| 第 4 层 | 操作前检查 | 每次重要操作 | ✅ |
| 第 5 层 | 违规纠正 | 错误后 | ✅ |

---

## 🎯 执行保障

### 自动执行
- ✅ 会话启动时自动读取
- ✅ 心跳时自动提醒
- ✅ 操作前自动检查

### 手动执行
- ✅ 用户可以随时要求检查规则
- ✅ 我可以主动要求检查规则

### 持久化
- ✅ 规则写入文件
- ✅ SOUL.md 包含规则
- ✅ AGENTS.md 包含规则
- ✅ HEARTBEAT.md 包含规则

---

## 💡 为什么这次会记住

### 三重记忆
1. **长期记忆** - 文件永久保存
2. **会话记忆** - 每次会话读取
3. **短期记忆** - 每 30 分钟提醒

### 多重触发
1. **启动触发** - 会话开始时
2. **定时触发** - 每 30 分钟
3. **操作触发** - 重要操作前

### 反馈循环
1. **违规记录** - 记录每次违规
2. **分析学习** - 心跳时分析
3. **规则强化** - 持续改进

---

## 🚀 下一步

**立即执行**:
1. ✅ 更新 AGENTS.md
2. ✅ 创建启动脚本
3. ✅ 创建操作前检查脚本
4. ✅ 创建 Git 推送包装脚本
5. ✅ 创建违规记录目录

**测试验证**:
1. 模拟重要操作
2. 验证检查流程
3. 确认不会违规

---

*方案版本: 1.0*
*创建时间: 2026-03-12 00:13*
*优先级: 🔴 CRITICAL*
*状态: ✅ 已设计，待执行*
