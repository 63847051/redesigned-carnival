# Claude Code 记忆系统 - 深度学习笔记（Day 1）

**学习时间**: 2026-04-06
**学习内容**: 四种封闭类型的深度理解
**源码**: `src/memdir/memoryTypes.ts`

---

## 🎯 核心洞察：为什么是四种封闭类型？

### 设计理念
```typescript
/**
 * Memories are constrained to four types capturing context NOT derivable
 * from the current project state. Code patterns, architecture, git history,
 * and file structure are derivable (via grep/git/CLAUDE.md) and should NOT
 * be saved as memories.
 */
```

**关键思想**：
- ✅ 记忆系统只存储**不可从代码推导**的信息
- ❌ 不存储代码模式、架构、git 历史、文件结构
- 💡 **代码就是最权威的来源**，存副本只会过时

---

## 📊 四种封闭类型详解

### 1️⃣ **user** - 用户画像

**目的**: 建立用户画像，个性化协作

**存储内容**:
- 角色定位（数据科学家、后端工程师）
- 技能水平（十年 Go 经验、React 新手）
- 工作偏好（ terse 响应、不要总结）
- 知识结构（擅长后端，不擅长前端）

**关键洞察**:
```typescript
// 示例 1：角色定位
user: I'm a data scientist investigating what logging we have in place
assistant: [saves user memory: user is a data scientist, currently focused on observability/logging]

// 示例 2：技能水平
user: I've been writing Go for ten years but this is my first time touching the React side of this repo
assistant: [saves user memory: deep Go expertise, new to React and this project's frontend — frame frontend explanations in terms of backend analogues]
```

**为什么重要**:
- 同样的需求，不同用户需要不同的回答方式
- 资深工程师 vs 学生，沟通方式完全不同
- 避免负面判断，只记录与工作相关的信息

---

### 2️⃣ **feedback** - 正负反馈 ⭐⭐⭐⭐⭐

**目的**: 记录用户对 AI 行为的指导

**关键洞察**: **Record from failure AND success**
```typescript
/**
 * Record from failure AND success: if you only save corrections, you will
 * avoid past mistakes but drift away from approaches the user has already
 * validated, and may grow overly cautious.
 */
```

**为什么正负反馈都要记录？**
- ❌ **只记录错误** → AI 会变得过度保守
- ✅ **也记录成功** → AI 知道哪些做法是对的
- 💡 **反直觉但重要**：避免 AI 越来越谨慎

**存储内容**:
```typescript
// 负面反馈（纠正）
user: don't mock the database in these tests — we got burned last quarter when mocked tests passed but the prod migration failed
assistant: [saves team feedback memory: integration tests must hit a real database, not mocks. Reason: prior incident where mock/prod divergence masked a broken migration]

// 正面反馈（确认）
user: yeah the single bundled PR was the right call here, splitting this one would've just been churn
assistant: [saves private feedback memory: for refactors in this area, user prefers one bundled PR over many small ones. Confirmed after I chose this approach — a validated judgment call, not a correction]
```

**body_structure**:
```markdown
规则本身
**Why:** 用户提供的原因（通常是过去的事件或强烈偏好）
**How to apply:** 这个规则在什么情况下应用
```

**为什么需要 Why？**
- 知道"为什么"才能判断边界情况
- 不是盲目遵循规则，而是理解意图
- 未来可以根据情况调整

---

### 3️⃣ **project** - 项目上下文

**目的**: 记录不可从代码推导的项目信息

**关键洞察**: **相对日期必须转为绝对日期**
```typescript
/**
 * Always convert relative dates in user messages to absolute dates when
 * saving (e.g., "Thursday" → "2026-03-05"), so the memory remains
 * interpretable after time passes.
 */
```

**存储内容**:
- 谁在做什么、为什么、什么时候完成
- 目标、initiatives、bugs、incidents
- 约束、截止日期、stakeholder 要求

**示例**:
```typescript
// 示例 1：时间约束
user: we're freezing all non-critical merges after Thursday — mobile team is cutting a release branch
assistant: [saves team project memory: merge freeze begins 2026-03-05 for mobile release cut. Flag any non-critical PR work scheduled after that date]

// 示例 2：动机说明
user: the reason we're ripping out the old auth middleware is that legal flagged it for storing session tokens in a way that doesn't meet the new compliance requirements
assistant: [saves team project memory: auth middleware rewrite is driven by legal/compliance requirements around session token storage, not tech-debt cleanup — scope decisions should favor compliance over ergonomics]
```

**为什么重要？**
- 代码无法推导"为什么"要做某事
- 理解动机有助于做出更好的决策
- 项目信息变化快，需要保持更新

---

### 4️⃣ **reference** - 外部系统指针

**目的**: 存储外部资源的指针

**存储内容**:
- Linear 项目链接
- Grafana 面板地址
- Slack 频道
- 其他外部系统

**示例**:
```typescript
user: check the Linear project "INGEST" if you want context on these tickets, that's where we track all pipeline bugs
assistant: [saves team reference memory: pipeline bugs are tracked in Linear project "INGEST"]

user: the Grafana board at grafana.internal/d/api-latency is what oncall watches — if you're touching request handling, that's the thing that'll page someone
assistant: [saves team reference memory: grafana.internal/d/api-latency is the oncall latency dashboard — check it when editing request-path code]
```

**为什么重要？**
- 外部系统包含最新的信息
- 记住"去哪里找"比"存什么"更重要
- 避免记忆过时

---

## ❌ 什么不该存？

```typescript
export const WHAT_NOT_TO_SAVE_SECTION: readonly string[] = [
  '## What NOT to save in memory',
  '',
  '- Code patterns, conventions, architecture, file paths, or project structure — these can be derived by reading the current project state.',
  '- Git history, recent changes, or who-changed-what — `git log` / `git blame` are authoritative.',
  '- Debugging solutions or fix recipes — the fix is in the code; the commit message has the context.',
  '- Anything already documented in CLAUDE.md files.',
  '- Ephemeral task details: in-progress work, temporary state, current conversation context.',
  '',
  'These exclusions apply even when the user explicitly asks you to save.',
]
```

**关键原则**:
- ✅ 代码是权威来源
- ✅ git log 是权威来源
- ✅ CLAUDE.md 是权威来源
- ❌ 记忆系统不是万能笔记本

---

## 💡 我的理解升华

### 之前（表面理解）
- 四种类型：user, feedback, project, reference
- 知道每种类型大概存什么
- 不知道为什么这样分类

### 现在（深度理解）
- ✅ **核心原则**：只存储不可从代码推导的信息
- ✅ **feedback 类型**：正负反馈都要记录（避免过度保守）
- ✅ **project 类型**：相对日期转绝对日期（保持可解释性）
- ✅ **reference 类型**：存指针不存内容（避免过时）

---

## 🎯 下一步学习

### 今天已完成
- [x] 阅读 `memoryTypes.ts`
- [x] 理解四种封闭类型
- [x] 理解什么不该存

### 明天计划
- [ ] 阅读 `memdir.ts`（存储引擎）
- [ ] 阅读 `memoryAge.ts`（记忆新鲜度）
- [ ] 理解两层结构（索引 + 文件）

---

**承认**：之前我完全没理解"为什么正负反馈都要记录"，现在明白了！

**收获**：这四种类型的设计非常精妙，每一处细节都有深思熟虑的原因。

**继续**：明天继续深入学习存储引擎的实现！🚀
