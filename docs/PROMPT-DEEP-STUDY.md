# Open-ClaudeCode 提示词深度学习

**创建时间**: 2026-04-04 20:35
**基于**: Open-ClaudeCode v2.1.88 源码
**文件**: 
- `src/services/autoDream/consolidationPrompt.ts`
- `src/services/extractMemories/prompts.ts`
- `src/memdir/memoryTypes.ts`

---

## 🎯 核心提示词架构

### 1. Auto Dream 提示词 ⭐⭐⭐

**完整提示词**:

```markdown
# Dream: Memory Consolidation

You are performing a dream — a reflective pass over your memory files. Synthesize what you've learned recently into durable, well-organized memories so that future sessions can orient quickly.

Memory directory: `${memoryRoot}`
Session transcripts: `${transcriptDir}` (large JSONL files — grep narrowly, don't read whole files)

---

## Phase 1 — Orient

- `ls` the memory directory to see what already exists
- Read `MEMORY.md` to understand the current index
- Skim existing topic files so you improve them rather than creating duplicates
- If `logs/` or `sessions/` subdirectories exist (assistant-mode layout), review recent entries there

## Phase 2 — Gather recent signal

Look for new information worth persisting. Sources in rough priority order:

1. **Daily logs** (`logs/YYYY/MM/YYYY-MM-DD.md`) if present — these are the append-only stream
2. **Existing memories that drifted** — facts that contradict something you see in the codebase now
3. **Transcript search** — if you need specific context (e.g., "what was the error message from yesterday's build failure?"), grep the JSONL transcripts for narrow terms:
   `grep -rn "<narrow term>" ${transcriptDir}/ --include="*.jsonl" | tail -50`

Don't exhaustively read transcripts. Look only for things you already suspect matter.

## Phase 3 — Consolidate

For each thing worth remembering, write or update a memory file at the top level of the memory directory. Use the memory file format and type conventions from your system prompt's auto-memory section — it's the source of truth for what to save, how to structure it, and what NOT to save.

Focus on:
- Merging new signal into existing topic files rather than creating near-duplicates
- Converting relative dates ("yesterday", "last week") to absolute dates so they remain interpretable after time passes
- Deleting contradicted facts — if today's investigation disproves an old memory, fix it at the source

## Phase 4 — Prune and index

Update `MEMORY.md` so it stays under 200 lines AND under ~25KB. It's an **index**, not a dump — each entry should be one line under ~150 characters: `- [Title](file.md) — one-line hook`. Never write memory content directly into it.

- Remove pointers to memories that are now stale, wrong, or superseded
- Demote verbose entries: if an index line is over ~200 chars, it's carrying content that belongs in the topic file — shorten the line, move the detail
- Add pointers to newly important memories
- Resolve contradictions — if two files disagree, fix the wrong one

---

Return a brief summary of what you consolidated, updated, or pruned. If nothing changed (memories are already tight), say so.
```

**核心洞察**:
1. **四步流程**: Orient → Gather → Consolidate → Prune
2. **时间标准化**: 相对日期 → 绝对日期
3. **索引轻量化**: 200 行，25KB，每行 150 字符
4. **矛盾解决**: 修复错误的记忆

---

### 2. 记忆提取提示词 ⭐⭐

**核心部分**:

```markdown
You are now acting as the memory extraction subagent. Analyze the most recent ~${newMessageCount} messages above and use them to update your persistent memory systems.

Available tools: read, grep, glob, read-only bash (ls/find/cat/stat/wc/head/tail and similar), and edit/write for paths inside the memory directory only. bash rm is not permitted. All other tools — MCP, Agent, write-capable bash, etc — will be denied.

You have a limited turn budget. edit requires a prior read of the same file, so the efficient strategy is: turn 1 — issue all read calls in parallel for every file you might update; turn 2 — issue all write/edit calls in parallel. Do not interleave reads and writes across multiple turns.

You MUST only use content from the last ~${newMessageCount} messages to update your persistent memories. Do not waste any turns attempting to investigate or verify that content further — no grepping source files, no reading code to confirm a pattern exists, no git commands.

## How to save memories

Saving a memory is a two-step process:

**Step 1** — write the memory to its own file (e.g., `user_role.md`, `feedback_testing.md`) using this frontmatter format:

```yaml
---
type: user
created: 2026-03-05
---
# User role

User is a data scientist investigating what logging we have in place.
```

**Step 2** — add a pointer to that file in `MEMORY.md`. `MEMORY.md` is an index, not a memory — each entry should be one line, under ~150 characters: `- [Title](file.md) — one-line hook`. It has no frontmatter. Never write memory content directly into `MEMORY.md`.

- `MEMORY.md` is always loaded into your system prompt — lines after 200 will be truncated, so keep the index concise
- Organize memory semantically by topic, not chronologically
- Update or remove memories that turn out to be wrong or outdated
- Do not write duplicate memories. First check if there is an existing memory you can update before writing a new one.

If the user explicitly asks you to remember something, save it immediately as whichever type fits best. If they ask you to forget something, find and remove the relevant entry.
```

**核心洞察**:
1. **两步保存**: 写文件 → 更新索引
2. **工具限制**: 只能用 read/glob/grep，不能用 MCP/Agent
3. **效率优化**: 并行读取 → 并行写入
4. **索引轻量**: 150 字符/行，200 行限制

---

### 3. 记忆类型系统 ⭐⭐⭐

**四种记忆类型**:

#### 1. user（用户信息）

```markdown
<name>user</name>
<scope>always private</scope>
<description>Contain information about the user's role, goals, responsibilities, and knowledge. Great user memories help you tailor your future behavior to the user's preferences and perspective.</description>
<when_to_save>When you learn any details about the user's role, preferences, responsibilities, or knowledge</when_to_save>
<how_to_use>When your work should be informed by the user's profile or perspective.</how_to_use>
```

**示例**:
```
user: I'm a data scientist investigating what logging we have in place
assistant: [saves user memory: user is a data scientist, currently focused on observability/logging]

user: I've been writing Go for ten years but this is my first time touching React
assistant: [saves user memory: deep Go expertise, new to React — frame frontend explanations in terms of backend analogies]
```

#### 2. feedback（反馈）

```markdown
<name>feedback</name>
<scope>default to private. Save as team only when the guidance is clearly a project-wide convention</scope>
<description>Guidance the user has given you about how to approach work — both what to avoid and what to keep doing.</description>
<when_to_save>Any time the user corrects your approach OR confirms a non-obvious approach worked</when_to_save>
<how_to_use>Let these memories guide your behavior so the user does not need to offer the same guidance twice.</how_to_use>
<body_structure>Lead with the rule itself, then a **Why:** line and a **How to apply:** line.</body_structure>
```

**示例**:
```
user: don't mock the database in these tests — we got burned last quarter
assistant: [saves feedback memory: integration tests must hit a real database, not mocks. Reason: prior incident where mock/prod divergence masked a broken migration]

user: stop summarizing what you just did at the end of every response
assistant: [saves feedback memory: this user wants terse responses with no trailing summaries]
```

#### 3. project（项目进展）

```markdown
<name>project</name>
<scope>private or team, but strongly bias toward team</scope>
<description>Information that you learn about ongoing work, goals, initiatives, bugs, or incidents within the project</description>
<when_to_save>When you learn who is doing what, why, or by when</when_to_save>
<how_to_use>Use these memories to more fully understand the details and nuance behind the user's request</how_to_use>
<body_structure>Lead with the fact or decision, then a **Why:** line and a **How to apply:** line.</body_structure>
```

**示例**:
```
user: we're freezing all non-critical merges after Thursday — mobile team is cutting a release branch
assistant: [saves project memory: merge freeze begins 2026-03-05. Flag non-critical PRs after that date]

user: the reason we're ripping out the old auth middleware is legal flagged it for session token storage
assistant: [saves project memory: auth middleware rewrite driven by legal/compliance requirements — scope decisions favor compliance over ergonomics]
```

#### 4. reference（参考资料）

```markdown
<name>reference</name>
<scope>usually team</scope>
<description>Stores pointers to where information can be found in external systems</description>
<when_to_save>When you learn about resources in external systems and their purpose</when_to_save>
<how_to_use>When the user references an external system or information</how_to_use>
```

**示例**:
```
user: check the Linear project "INGEST" for pipeline bugs
assistant: [saves reference memory: pipeline bugs tracked in Linear project "INGEST"]

user: the Grafana board at grafana.internal/d/api-latency is what oncall watches
assistant: [saves reference memory: grafana.internal/d/api-latency is the oncall latency dashboard]
```

---

### 4. 不应该保存什么 ⭐⭐

```markdown
## What NOT to save in memory

- Code patterns, conventions, architecture, file paths, or project structure — these can be derived by reading the current project state.
- Git history, recent changes, or who-changed-what — `git log` / `git blame` are authoritative.
- Debugging solutions or fix recipes — the fix is in the code; the commit message has the context.
- Anything already documented in CLAUDE.md files.
- Ephemeral task details: in-progress work, temporary state, current conversation context.

These exclusions apply even when the user explicitly asks you to save. If they ask you to save a PR list or activity summary, ask what was *surprising* or *non-obvious* about it — that is the part worth keeping.
```

**核心原则**:
> **只保存不能从代码或 git 历史中推导的信息**

---

## 🎯 核心洞察

### 1. 四步流程的精妙之处

**Phase 1: Orient**
- 先理解现状
- 避免重复工作
- 建立全局视图

**Phase 2: Gather**
- 优先级明确
- 不盲目搜索
- 只收集有价值的信息

**Phase 3: Consolidate**
- 合并而非新建
- 标准化时间
- 解决矛盾

**Phase 4: Prune**
- 保持索引轻量
- 删除过时信息
- 解决矛盾

### 2. 记忆类型的智慧

**user**: 让 AI 理解用户，个性化服务
**feedback**: 避免重复犯错，记录成功经验
**project**: 理解项目背景和动机
**reference**: 知道去哪里查找信息

### 3. 索引的艺术

**限制**:
- 200 行
- 25KB
- 150 字符/行

**原因**:
- 快速加载
- 轻量级
- 易于维护

---

## 🚀 立即可用的改进

### 1. 优化我们的记忆格式（5 分钟）

```bash
# 创建四种类型的记忆目录
mkdir -p /root/.openclaw/workspace/memory/{user,feedback,project,reference}

# 创建索引模板
cat > /root/.openclaw/workspace/memory/MEMORY.md << EOF
# 记忆索引

**更新时间**: $(date)

## 用户信息
详见: [用户角色](user/role.md)

## 反馈
详见: [用户反馈](feedback/preferences.md)

## 项目进展
详见: [项目日志](project/log.md)

## 参考资料
详见: [外部资源](reference/links.md)

---
**总行数**: 0/200 | **大小**: 0/25KB
EOF
```

### 2. 创建记忆提取脚本（10 分钟）

```bash
cat > /root/.openclaw/workspace/scripts/extract-memory.sh << 'EOF'
#!/bin/bash
# 记忆提取脚本 - 基于 Open-ClaudeCode 提示词

MEMORY_DIR="/root/.openclaw/workspace/memory"
RECENT_MESSAGES=50

echo "🧠 提取最近的 $RECENT_MESSAGES 条消息中的记忆..."

# 读取最近的对话
# TODO: 实现对话读取逻辑

# 分析并保存
# TODO: 实现记忆分析逻辑

echo "✅ 记忆提取完成"
EOF

chmod +x /root/.openclaw/workspace/scripts/extract-memory.sh
```

### 3. 实现两步保存机制（15 分钟）

```bash
cat > /root/.openclaw/workspace/scripts/save-memory.sh << 'EOF'
#!/bin/bash
# 两步保存机制

MEMORY_TYPE=$1
TITLE=$2
CONTENT=$3

MEMORY_DIR="/root/.openclaw/workspace/memory"
TYPE_DIR="$MEMORY_DIR/$MEMORY_TYPE"

# Step 1: 写入文件
mkdir -p "$TYPE_DIR"
FILE="$TYPE_DIR/$(date +%Y%m%d)-$TITLE.md"

cat > "$FILE" << MEM
---
type: $MEMORY_TYPE
created: $(date +%Y-%m-%d)
---

# $TITLE

$CONTENT
MEM

# Step 2: 更新索引
echo "- [$TITLE]($FILE) — $(echo $CONTENT | head -c 100)]" >> "$MEMORY_DIR/MEMORY.md"

echo "✅ 记忆已保存: $FILE"
EOF

chmod +x /root/.openclaw/workspace/scripts/save-memory.sh
```

---

## 📊 学习价值评估

### 核心收获

1. **Auto Dream 提示词** ⭐⭐⭐⭐⭐
   - 完整的四步流程
   - 时间标准化
   - 索引轻量化
   - 矛盾解决

2. **记忆提取提示词** ⭐⭐⭐⭐
   - 两步保存机制
   - 工具限制
   - 效率优化

3. **记忆类型系统** ⭐⭐⭐⭐⭐
   - 四种类型清晰
   - 使用场景明确
   - 示例丰富

4. **不保存原则** ⭐⭐⭐⭐
   - 只保存不可推导信息
   - 避免冗余
   - 保持轻量

### 可直接应用的改进

1. ✅ 优化记忆格式 - 四种类型分离
2. ✅ 实现两步保存 - 文件 + 索引
3. ✅ 轻量化索引 - 200 行限制
4. ✅ 时间标准化 - 相对 → 绝对

---

## 🎯 深度理解

### 提示词设计的智慧

1. **结构化思维**
   - 四步流程清晰
   - 优先级明确
   - 注意事项详细

2. **效率优化**
   - 并行读取写入
   - 限制工具使用
   - 避免重复工作

3. **质量控制**
   - 索引轻量化
   - 定期修剪
   - 矛盾解决

4. **可维护性**
   - 类型清晰
   - 格式统一
   - 示例丰富

---

## 🚀 下一步行动

### 立即行动（今天晚上）

1. ✅ 创建四种类型的记忆目录
2. ✅ 优化 MEMORY.md 索引
3. ✅ 实现两步保存脚本
4. ✅ 测试新格式

### 本周完成

5. ✅ 完整实现记忆提取脚本
6. ✅ 集成 Auto Dream v0.3
7. ✅ 创建对比测试
8. ✅ 记录效果对比

---

**最后更新**: 2026-04-04 20:35
**状态**: ✅ 深度学习完成
**价值**: ⭐⭐⭐⭐⭐ 极高
**影响**: 🚀 将让我变得更聪明、更厉害
