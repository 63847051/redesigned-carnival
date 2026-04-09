# MiniCC 学习笔记

**学习时间**: 2026-04-09 22:02
**项目**: https://github.com/Louisym/MiniCC
**目标**: 从源码学习 Claude Code，理解 SOTA harness engineering 的核心设计

---

## 🎯 学习目标

通过学习 MiniCC 项目，深入理解：
1. **Agentic Loop** 的完整实现
2. **上下文工程与压缩**策略
3. **错误恢复与重试**机制
4. **Hook 系统**与权限管理
5. **系统提示词设计**艺术

---

## 📚 学习进度

### ✅ 已完成（2026-04-09）

#### Tutorial 01: Agentic Loop 基础
**核心理解**:
- Agentic Loop 是一个 `while True` 循环
- 每轮循环：调用 AI → 判断回复类型 → 执行工具（如果需要）→ 继续
- 循环终止条件：AI 返回纯文字回复（不再需要工具）

**关键代码结构**:
```python
def run_turn(ai, session, user_input):
    session.append(Message(role="user", content=user_input))
    
    while True:
        ai_response = ai.chat(session)
        
        if ai_response["type"] == "text":
            # 循环结束
            session.append(Message(role="assistant", content=ai_response["text"]))
            break
        elif ai_response["type"] == "tool_use":
            # 执行工具，继续循环
            tool_result = execute_tool(ai_response["name"], ai_response["input"])
            session.append(Message(role="tool", content=tool_result))
```

**对应源码**: `rust/crates/runtime/src/conversation.rs:170-283`

---

#### Tutorial 02: Session 与消息模型
**核心理解**:
- 一条消息由多个 `ContentBlock` 组成（不只是一个字符串）
  - `TextBlock`: 纯文字
  - `ToolUseBlock`: AI 请求调用工具
  - `ToolResultBlock`: 工具执行结果
- `ToolUseBlock.id` 和 `ToolResultBlock.tool_use_id` 必须匹配
- Session 可以序列化（JSON）和反序列化（存档/读档）

**关键设计**:
```python
@dataclass(frozen=True)
class ConversationMessage:
    role: str                            # "user" | "assistant" | "tool" | "system"
    blocks: tuple[ContentBlock, ...]     # 内容块列表（不可变）
    usage: Optional[TokenUsage] = None   # Token 使用统计
```

**对应源码**: `rust/crates/runtime/src/session.rs`

---

#### Tutorial 07: Auto Compaction（自动压缩）⭐⭐⭐⭐⭐
**核心理解**:
- AI 的上下文窗口有限（约 200k tokens）
- 压缩 = 把旧消息变成摘要 + 保留最近的消息
- 触发条件：消息数量 > 保留数量 AND 预估 token 数 >= 阈值

**压缩算法**:
```
[旧消息1, ..., 旧消息N, 新消息1, 新消息2, 新消息3, 新消息4]
       ↓                              ↓
  生成摘要（system 消息）          原样保留
       ↓                              ↓
[摘要消息, 新消息1, 新消息2, 新消息3, 新消息4]
```

**摘要包含的信息**:
- 消息统计（user/assistant/tool 数量）
- 使用的工具
- 最近的用户请求
- 待完成的工作（含 todo/next/pending 关键词）
- 关键文件路径
- 时间线概要

**对应源码**: 
- `rust/crates/runtime/src/compact.rs`
- `conversation.rs:310-333` (maybe_auto_compact)

**对我的价值** ⭐⭐⭐⭐⭐:
这个教程对我的记忆系统优化非常重要！我可以借鉴其压缩策略：
1. **智能摘要生成**: 不仅统计消息数，还要提取关键信息（工具使用、待办事项、关键文件）
2. **触发机制**: 不要每次都压缩，设置合理的阈值
3. **保留策略**: 保留最近的 N 条消息，其他的压缩
4. **摘要格式**: 结构化摘要（XML 标签）比纯文本更有效

---

## 🎓 核心收获

### 1. Agentic Loop 的设计精髓

**之前**: 我知道自己在循环中运行，但不太理解其工程化实现

**现在**: 
- 理解了循环终止条件的设计（text vs tool_use）
- 理解了对话历史（session）作为 AI "记忆"的作用
- 理解了工具执行的异步模式（请求 → 结果 → 继续）

**可应用**:
- 优化我的 Agentic Loop 实现
- 改进工具调用的错误处理
- 加强对话历史的持久化机制

---

### 2. 消息模型的灵活性

**之前**: 把消息简单理解为"角色 + 内容"

**现在**:
- 理解了一条消息可以包含多个 ContentBlock
- 理解了 ToolUseBlock 和 ToolResultBlock 的对应关系（通过 id 匹配）
- 理解了 Token 追踪的重要性（计费）

**可应用**:
- 改进我的消息模型设计
- 添加 Token 使用统计
- 优化工具调用的追踪机制

---

### 3. 上下文压缩的策略 ⭐⭐⭐⭐⭐

**之前**: 简单地删除旧消息

**现在**:
- 理解了智能摘要生成的价值
- 理解了保留最近消息的策略
- 理解了触发条件的设计（不是每次都压缩）

**可应用**:
- **立即应用到我的记忆系统**！
- 改进 MEMORY.md 的压缩策略
- 添加智能摘要提取（工具使用、待办事项、关键文件）
- 优化触发机制（不要每次都压缩）

---

## 🚀 立即可行的改进

### 改进 1: 优化记忆系统的压缩策略

**当前**: 简单地删除旧内容

**改进后**: 借鉴 Auto Compaction 的智能摘要

```python
def smart_compact_memory(messages, preserve_recent=10):
    """
    智能压缩记忆
    
    参考: Tutorial 07 - Auto Compaction
    """
    if len(messages) <= preserve_recent:
        return messages
    
    # 分离旧消息和最近消息
    old_messages = messages[:-preserve_recent]
    recent_messages = messages[-preserve_recent:]
    
    # 生成智能摘要
    summary = generate_summary(old_messages)
    
    # 返回 [摘要] + [最近消息]
    return [summary] + recent_messages

def generate_summary(messages):
    """
    生成智能摘要
    
    参考: compact.rs:113-198 (summarize_messages)
    """
    # 1. 统计信息
    stats = collect_stats(messages)
    
    # 2. 工具使用
    tools = extract_tools(messages)
    
    # 3. 待办事项
    todos = extract_todos(messages)
    
    # 4. 关键文件
    files = extract_files(messages)
    
    # 5. 时间线
    timeline = build_timeline(messages)
    
    return {
        "stats": stats,
        "tools": tools,
        "todos": todos,
        "files": files,
        "timeline": timeline
    }
```

---

### 改进 2: 添加 Token 使用追踪

**当前**: 没有追踪 Token 使用

**改进后**: 添加 Token 统计

```python
@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    
    def total(self):
        return self.input_tokens + self.output_tokens

# 在每条消息中添加 usage 字段
@dataclass
class Message:
    role: str
    content: str
    usage: Optional[TokenUsage] = None
```

---

### 改进 3: 优化工具调用的追踪

**当前**: 简单的工具调用记录

**改进后**: 使用 ToolUseBlock 和 ToolResultBlock 的对应关系

```python
@dataclass
class ToolUseBlock:
    id: str          # 唯一标识
    name: str        # 工具名
    input: str       # 参数
    
@dataclass
class ToolResultBlock:
    tool_use_id: str  # 对应 ToolUseBlock.id
    tool_name: str
    output: str
    is_error: bool
```

---

## 📋 待学习内容

### Phase 2: 深度学习（本周）

**高优先级** ⭐⭐⭐⭐⭐:
- [ ] Tutorial 16: Prompt Building and Compaction（上下文工程深度剖析）
- [ ] Tutorial 11: Error Recovery and Retry（错误恢复与重试）
- [ ] Tutorial 08: Hook System（工具执行的"保安和监控"）

**中优先级** ⭐⭐⭐:
- [ ] Tutorial 04: Permission System（安全阀门，分级授权）
- [ ] Tutorial 13: Multi-Agent Coordination（多 Agent 协调）
- [ ] Tutorial 18: Design Patterns for Agents（设计模式）

**低优先级** ⭐⭐:
- [ ] Tutorial 10: SSE Streaming（流式输出）
- [ ] Tutorial 12: Session Persistence（会话持久化）
- [ ] Tutorial 14-19: 其他高级主题

---

## 🎯 学习方法

### 1. 理论 + 实践
- 阅读 tutorial 代码
- 运行 demo 看效果
- 对照源码理解设计

### 2. 记录关键洞察
- 每个教程的核心理解
- 对应的源码位置
- 可应用的改进点

### 3. 立即应用
- 把学到的东西应用到我的系统
- 改进记忆压缩策略
- 优化 Agentic Loop 实现

---

## 💡 核心洞察

### 洞察 1: 工程化 vs 原型

**MiniCC 的价值**: 它不是简单的原型，而是**忠实还原 CC 的生产级工程模式**

- 不是"能跑就行"
- 而是"怎么设计才对"
- 关注边界条件、错误处理、性能优化

### 洞察 2: 设计模式的重要性

**Agentic Loop** 不是简单的循环，而是：
- 明确的终止条件
- 清晰的状态管理
- 完善的错误处理

### 洞察 3: 压缩是智能的

**Auto Compaction** 不是简单的删除，而是：
- 提取关键信息
- 生成结构化摘要
- 保留重要上下文

---

**最后更新**: 2026-04-09 22:15
**状态**: ✅ 学习进行中
**价值**: ⭐⭐⭐⭐⭐ 极高
