# Claude Code 记忆系统 - 深度学习笔记（Day 2）

**学习时间**: 2026-04-06
**学习内容**: 自动记忆提取机制
**源码**: `src/services/extractMemories/extractMemories.ts`, `prompts.ts`

---

## 🎯 核心机制：自动记忆提取

### 设计理念
```typescript
/**
 * Extracts durable memories from the current session transcript
 * and writes them to the auto-memory directory.
 *
 * It runs once at the end of each complete query loop (when the model produces
 * a final response with no tool calls) via handleStopHooks in stopHooks.ts.
 *
 * Uses the forked agent pattern (runForkedAgent) — a perfect fork of the main
 * conversation that shares the parent's prompt cache.
 */
```

**关键思想**：
- ✅ 每轮对话完成后自动触发
- ✅ 后台 fork 子代理执行
- ✅ 非阻塞，用户无感知
- ✅ 共享父进程的 prompt 缓存

---

## 🔄 两回合策略 ⭐⭐⭐⭐⭐

### 为什么需要两回合？

```typescript
/**
 * You have a limited turn budget. ${FILE_EDIT_TOOL_NAME} requires a prior
 * ${FILE_READ_TOOL_NAME} of the same file, so the efficient strategy is:
 * turn 1 — issue all ${FILE_READ_TOOL_NAME} calls in parallel for every file
 * you might update; turn 2 — issue all ${FILE_WRITE_TOOL_NAME}/${FILE_EDIT_TOOL_NAME}
 * calls in parallel. Do not interleave reads and writes across multiple turns.
 */
```

**核心原因**：
- `FILE_EDIT_TOOL_NAME` 要求先 `FILE_READ_TOOL_NAME` 同一个文件
- 两回合策略：第一轮并行读，第二轮并行写
- 最大化并行效率

**具体流程**：

#### 第一回合（Turn 1）：并行读取
```typescript
// 所有读取请求并行发出
FILE_READ user_role.md
FILE_READ feedback_testing.md
FILE_READ project_deadline.md
FILE_READ reference_linear.md
```

#### 第二回合（Turn 2）：并行写入
```typescript
// 所有写入请求并行发出
FILE_EDIT user_role.md
FILE_EDIT feedback_testing.md
FILE_WRITE project_new.md
```

**为什么这样设计？**
- ✅ 最大化并行效率
- ✅ 减少轮次消耗
- ✅ 避免读写交错

---

## 🛡️ 互斥设计 ⭐⭐⭐⭐⭐

### 防止主代理和子代理冲突

```typescript
/**
 * If the main agent writes memories, the forked extraction is redundant.
 * runExtraction skips the agent and advances the cursor past this range,
 * making the main agent and the background agent mutually exclusive per turn.
 */
```

**检测机制**：
```typescript
function hasMemoryWritesSince(
  messages: Message[],
  sinceUuid: string | undefined,
): boolean {
  // 检查主代理是否已经写入了记忆
  // 如果是，跳过本次提取
}
```

**为什么重要？**
- ✅ 避免主代理和子代理同时写入
- ✅ 防止冲突和重复
- ✅ 确保数据一致性

---

## 🔒 工具权限限制

### 子代理的严格权限

```typescript
/**
 * Available tools: ${FILE_READ_TOOL_NAME}, ${GREP_TOOL_NAME}, ${GLOB_TOOL_NAME},
 * read-only ${BASH_TOOL_NAME} (ls/find/cat/stat/wc/head/tail and similar), and
 * ${FILE_EDIT_TOOL_NAME}/${FILE_WRITE_TOOL_NAME} for paths inside the memory
 * directory only. ${BASH_TOOL_NAME} rm is not permitted. All other tools — MCP,
 * Agent, write-capable ${BASH_TOOL_NAME}, etc — will be denied.
 */
```

**允许的工具**：
- ✅ `FILE_READ_TOOL_NAME` - 读取任意文件
- ✅ `GREP_TOOL_NAME` - 搜索
- ✅ `GLOB_TOOL_NAME` - 文件匹配
- ✅ 只读 `BASH_TOOL_NAME` - ls, find, cat, stat, wc, head, tail
- ✅ `FILE_EDIT_TOOL_NAME` / `FILE_WRITE_TOOL_NAME` - **仅限记忆目录内**

**禁止的工具**：
- ❌ `BASH_TOOL_NAME` rm - 删除命令
- ❌ MCP 工具
- ❌ Agent 工具
- ❌ 写权限的 `BASH_TOOL_NAME`

**为什么这么严格？**
- ✅ 防止子代理做危险操作
- ✅ 限制在记忆管理范围内
- ✅ 避免验证兔子洞

---

## ⚠️ 轮次上限

```typescript
/**
 * You have a limited turn budget.
 */
```

**约束**：
- 轮次上限：5 轮
- 明确禁止：不许 grep 源码，不许 git log，不许确认文件是否存在

**为什么限制？**
- ✅ 防止子代理陷入验证兔子洞
- ✅ 节省宝贵的轮次预算
- ✅ 专注于记忆提取，不做调查

---

## 💡 我的关键理解

### 1. 两回合策略的精妙之处

**之前**：我以为就是简单的读-写

**现在**：理解了为什么分成两回合
- 第一回合：并行读取所有可能需要的文件
- 第二回合：并行写入所有需要更新的文件
- 最大化并行效率，减少轮次消耗

**为什么重要？**
- 子代理的轮次是宝贵的（最多 5 轮）
- 每一轮都要消耗 token
- 两回合策略是最优解

---

### 2. 互斥设计的必要性

**之前**：没有考虑主代理和子代理的冲突

**现在**：理解了为什么需要互斥
- 主代理手动写入记忆时，子代理跳过
- 避免两人同时写同一个文件
- 确保数据一致性

**为什么重要？**
- 避免冲突和重复
- 提取是冗余的，跳过不影响功能
- 用户说"帮我记住这个"，主代理已经写了

---

### 3. 工具权限限制的安全考虑

**之前**：子代理应该有完整权限

**现在**：理解了为什么要严格限制
- 子代理只能操作记忆目录
- 不能删除文件（rm 禁止）
- 不能调用 MCP、Agent 等危险工具

**为什么重要？**
- 安全第一：防止子代理做危险操作
- 范围限制：专注于记忆管理
- 避免兔子洞：不许调查验证

---

## 🎯 下一步学习

### 今天已完成
- [x] 理解自动记忆提取机制
- [x] 理解两回合策略
- [x] 理解互斥设计
- [x] 理解工具权限限制

### 明天计划
- [ ] 阅读 `memoryAge.ts` - 记忆新鲜度系统
- [ ] 阅读 `memoryScan.ts` - Sonnet 召回引擎
- [ ] 理解异步预取机制

---

## 📝 关键收获

### 最大的惊讶
**两回合策略**：不是简单的读-写，而是并行读 + 并行写

**为什么惊讶？**
- 之前没想过这个问题
- 以为是自然的读-写-读-写
- 实际上两回合是最优解

### 最大的启发
**互斥设计**：主代理和子代理不能同时写

**为什么启发？**
- 不是简单地在后台运行
- 需要考虑并发控制
- 检测主代理行为，动态调整

---

**承认**：之前完全不理解为什么要两回合，现在明白了！

**收获**：这个设计的每个细节都有深思熟虑的原因。

**继续**：明天继续学习记忆召回机制！🚀
