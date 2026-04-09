# Claude Code Compaction - 深度学习笔记

**学习时间**: 2026-04-06
**来源**: 微信文章 - 《上下文爆了就摘要？Claude Code 的 Compaction 比你想的复杂得多》
**核心内容**: Context Compaction（上下文压缩）的工程实现

---

## 🎯 核心架构：多层防御体系

### 三层压缩机制

#### 1. Microcompact（微压缩）⚡
- **特点**: 轻量级，不需要调 AI
- **原理**: 直接把历史工具调用结果清空，只保留结构
- **耗时**: 几毫秒
- **用户体验**: 完全无感知

#### 2. Auto Compact（自动压缩）🤖
- **触发条件**: token 用量超过阈值（上下文窗口 - 13K 缓冲）
- **原理**: 触发 AI 摘要，把整个对话历史压缩成结构化摘要
- **特点**: 真正的 AI 压缩

#### 3. Session Memory Compact（记忆压缩）🧠
- **特点**: 实验性功能
- **原理**: 使用之前 AI 提炼过的"会话记忆"作为摘要
- **优势**: 跳过 AI 调用，提速优化

---

## 💡 三大源码亮点

### 亮点一：电路熔断器 ⭐⭐⭐⭐⭐

**问题**：
```typescript
// 2026-03-10: 1,279 sessions had 50+ consecutive failures (up to 3,272)
// in a single session, wasting ~250K API calls/day globally.
const MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3
```

**一天浪费 25 万次 API 调用！**

**原因**：
- 某些 session 的 context 已经"无可救药地超限"
- 压缩请求本身也会 Prompt Too Long
- 陷入无限失败循环

**解决方案**：
```typescript
// 电路熔断：连续失败达到上限，直接放弃
if (tracking?.consecutiveFailures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES) {
  return { wasCompacted: false }
}
```

**关键设计**：
- ✅ 连续失败 3 次就"断路"
- ✅ 失败计数器向上透传（无副作用）
- ✅ 成功时归零，失败时递增

**启示**：
- 💡 用数据驱动决策（25万次/天）
- 💡 失败不可怕，无止境的失败重试才是资源杀手
- 💡 任何依赖外部资源的重试逻辑都应该有熔断机制

---

### 亮点二：Prompt 的"前置强约束" ⭐⭐⭐⭐⭐

**问题**：
```typescript
// Sonnet 4.6+ 在"自适应思考"模式下
// 有 2.79% 的概率会忍不住调用工具
// 一旦调用被拒绝，这一轮就废了（maxTurns: 1）
```

**解决方案**：
```typescript
// 把禁令从末尾挪到最前面
const NO_TOOLS_PREAMBLE = `CRITICAL: Respond with TEXT ONLY. Do NOT call any tools.
- Do NOT use Read, Bash, Grep, Glob, Edit, Write, or ANY other tool.
- Tool calls will be REJECTED and will waste your only turn — you will fail the task.
- Your entire response must be plain text: an <analysis> block followed by a <summary> block.`

// 首尾双保险
const NO_TOOLS_TRAILER = `\n\nREMINDER: Do not call any tools...`
```

**结果**：
- 失败率从 2.79% 降到可以忽略不计的水平

**启示**：
1. 💡 **把最重要的约束放在最前面**，不是埋在末尾
2. 💡 **用后果而不是命令来约束**："违规会失败" > "请不要这样做"
3. 💡 **用数据驱动 Prompt 设计**：实测失败率来做决策

---

### 亮点三：<analysis> 草稿区 ⭐⭐⭐⭐⭐

**核心思想**：
```
让 AI 先在 <analysis> 里"乱想"，然后再在 <summary> 里"正式输出"

<analysis> 是草稿区，鼓励 AI 按时间顺序逐条回顾，不用考虑格式和美观
<summary> 是正式输出，要求结构化
```

**后处理流水线**：
```typescript
// 第一步：把草稿区整个删掉
formattedSummary = formattedSummary.replace(/<analysis>[\s\S]*?<\/analysis>/g, '')

// 第二步：把 <summary> XML 标签替换成可读的纯文本标题
formattedSummary = formattedSummary.replace(
  /<summary>([\s\S]*?)<\/summary>/g,
  `Summary:\n${content.trim()}`
)

// 第三步：清理多余空行
formattedSummary = formattedSummary.replace(/\n\n+/g, '\n\n')
```

**好处**：
- ✅ 提升摘要质量：先思考再输出
- ✅ 控制上下文污染：草稿区的"混乱思考"不会出现在后续对话中
- ✅ 节省 token

**启示**：
**"思考-输出分离"模式**：
```xml
<analysis>
[让 AI 在这里自由发散，不用管格式]
</analysis>
<summary>
[这里才是正式输出]
</summary>
```

适用于：
- 代码审查
- 文档摘要
- 会议纪要
- 任何需要"高质量结构化输出"的场景

---

## 🎯 我的关键理解

### 1. 多层防御 ⭐⭐⭐⭐⭐

**核心思想**：
- 轻量级：Microcompact（几毫秒，无感知）
- 中等级：Auto Compact（AI 摘要）
- 重量级：Session Memory Compact（复用已有记忆）

**关键设计**：
- ✅ 严格优先级（Microcompact → Auto Compact → Session Memory）
- ✅ 互斥关系（同一时间只触发一种）
- ✅ 数据驱动（25万次/天 → 熔断机制）

---

### 2. 电路熔断器 ⭐⭐⭐⭐⭐

**核心思想**：
- 连续失败 3 次就放弃
- 避免无止境的资源浪费
- 失败计数器向上透传（无副作用）

**应用场景**：
- ✅ 任何依赖外部资源的重试逻辑
- ✅ API 调用
- ✅ 数据库查询
- ✅ 文件系统操作

---

### 3. 思考-输出分离 ⭐⭐⭐⭐⭐

**核心思想**：
- <analysis> 草稿区：自由发散
- <summary> 正式输出：结构化
- 后处理：剥离草稿区

**应用场景**：
- ✅ 代码审查
- ✅ 文档摘要
- ✅ 会议纪要
- ✅ 任务规划

---

## 🚀 立即应用

### 我可以优化的地方

#### 1. AutoDream 双门控
**当前**：24h + 5会话
**优化**：添加熔断机制
- 如果连续失败 3 次，放弃本次 AutoDream
- 避免资源浪费

#### 2. Session Memory 渐进式笔记
**当前**：简单的渐进式更新
**优化**：应用"思考-输出分离"
- 先在草稿区思考
- 再输出结构化笔记

#### 3. 记忆搜索
**当前**：keyword 模式
**优化**：添加熔断机制
- 如果连续搜索失败 3 次，降级策略

---

## 💡 最大的收获

### 数据驱动设计 ⭐⭐⭐⭐⭐

**核心思想**：
- 不是"感觉应该这样"
- 而是"数据显示应该这样"

**例子**：
- 25万次/天 → 熔断机制
- 2.79% 失败率 → 前置强约束

**应用**：
- 记录失败次数
- 分析失败原因
- 用数据做决策

---

### 约束下的最优解 ⭐⭐⭐⭐⭐

**核心思想**：
- 工程的本质是在约束中找最优解
- 上下文窗口是约束
- AI 的不可预测性是约束
- 用户的无感知体验是约束

**例子**：
- 13K 缓冲（留出安全边际）
- 3 次熔断（避免资源浪费）
- <analysis> 草稿区（提升质量）

---

## 🎯 下一步优化

### 立即可做
1. ✅ 理解三层防御机制
2. ✅ 理解电路熔断器
3. ✅ 理解前置强约束
4. ✅ 理解思考-输出分离

### 深入应用
1. ⏳ 在 AutoDream 中添加熔断机制
2. ⏳ 在 Session Memory 中应用思考-输出分离
3. ⏳ 在记忆搜索中添加降级策略

---

**这篇文章太值了！** 🎉

**学到了大量可复用的工程模式！** 💡

**要开始应用这些设计吗？** 😊
