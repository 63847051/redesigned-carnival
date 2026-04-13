# Hermes Core 实现指南

## 概述

Hermes Core 是 Hermes Agent 的核心学习系统，实现五大核心特性：

1. **技能自动创建** - Agent 在复杂任务后自动决策创建技能
2. **技能自动改进** - Agent 在使用技能时自动决策 patch
3. **知识持久化** - 快照冻结 + 原子写入
4. **会话搜索** - FTS5 全文搜索 + LLM 摘要
5. **用户建模** - Honcho 4 层工具

## 核心模块

### core/ - 核心基础设施

#### snapshot_store.py

```python
from core.snapshot_store import SnapshotStore, AtomicWriter

# 快照存储
store = SnapshotStore("/path/to/storage")
store.capture_snapshot("knowledge", {"data": "value"})
store.freeze("knowledge")  # 冻结，会话期间不刷新

# 原子写入
writer = AtomicWriter("/path/to/storage")
writer.write_json("config.json", {"key": "value"})
```

**核心特性**:
- 快照冻结：加载时捕获，会话期间不刷新
- 原子写入：tempfile + os.replace() 确保写入安全
- 线程安全：支持并发访问

#### fuzzy_patch.py

```python
from core.fuzzy_patch import FuzzyPatcher, calculate_similarity

patcher = FuzzyPatcher()

# 规范化空白符
normalized = patcher.normalize("  line1  \n  line2  ")

# 计算相似度
similarity = calculate_similarity("hello world", "hello world")  # > 0.9

# 应用补丁
result = patcher.apply_patch(original, patched)
```

**核心特性**:
- 空白符规范化
- 缩进差异容忍
- 转义序列处理

### learning/ - 学习闭环系统

#### auto_skill_creator.py

```python
from learning.auto_skill_creator import AutoSkillCreator, TaskContext

creator = AutoSkillCreator("/path/to/skills")

# 分析上下文
context = TaskContext(
    tool_calls=[{"name": "tool1"}, {"name": "tool2"}, ...],
    errors=["error1"],
    user_corrections=["correction1"],
    success=True
)

analysis = creator.analyze_context(context)
# analysis["should_create"] - 是否应该创建技能

# 创建技能
skill_path = creator.create_skill(context)
```

**触发条件**:
- 5+ 工具调用
- 错误克服
- 用户纠正
- 置信度 >= 0.6

#### auto_skill_improver.py

```python
from learning.auto_skill_improver import AutoSkillImprover, UsageContext

improver = AutoSkillImprover("/path/to/skills")

# 分析使用情况
context = UsageContext(
    skill_name="test_skill",
    user_request="用户请求",
    execution_result="结果",
    success=False,
    error="错误信息"
)

suggestion = improver.analyze_usage(context)
# suggestion.priority - high/medium/low

# 应用改进
improver.apply_improvement(suggestion, auto_apply=True)
```

#### self_guidance.py

```python
from learning.self_guidance import get_self_guidance

guidance = get_self_guidance()

# 评估触发器
context = {
    "consecutive_errors": 3,
    "tool_call_count": 10,
    "confidence": 0.3,
    "tool_failed": True
}

prompts = guidance.evaluate_triggers(context)
# 返回需要注入的引导提示
```

### search/ - 会话搜索

#### fts5_search.py

```python
from search.fts5_search import get_session_search

search = get_session_search()

# 索引会话
search.index_session("session_1", "Test Session", [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi"}
])

# 搜索
results = search.search("hello", limit=10)

# 获取最近会话
recent = search.get_recent_sessions(limit=5)
```

#### llm_summarizer.py

```python
from search.llm_summarizer import get_llm_summarizer

summarizer = get_llm_summarizer()

# 总结搜索结果
result = summarizer.summarize("python", sessions)
# result.summary - 摘要
# result.key_topics - 主题
# result.confidence - 置信度
```

### modeling/ - 用户建模

#### honcho_lite.py

```python
from modeling.honcho_lite import get_honcho

honcho = get_honcho()

# 1. profile - 快速卡片
profile = honcho.profile("user_123", "Test User")
# profile.name, profile.traits, profile.preferences

# 2. search - 语义搜索
results = honcho.search("user_123", "python")

# 3. context - 辩证推理
reasoning = honcho.context("user_123", "用户的技术偏好是什么？")

# 4. conclude - 持久化结论
conclusion = honcho.conclude("user_123", "用户偏好 Python", 0.8)

# 记录交互
honcho.record_interaction("user_123", "I love Python")
```

## 数据流

```
用户请求
    ↓
Hermes Core
    ↓
┌─────────────────────────────────────────┐
│ 1. AutoSkillCreator - 是否创建技能？    │
│ 2. SessionSearch - 搜索相关会话         │
│ 3. Honcho - 用户画像                     │
│ 4. SelfGuidance - 是否注入引导           │
│ 5. AutoSkillImprover - 是否改进技能     │
└─────────────────────────────────────────┘
    ↓
返回结果
```

## 配置

默认数据路径: `~/.hermes/hermes-core/`

可通过构造函数指定自定义路径:

```python
store = SnapshotStore("/custom/path")
search = SessionSearch("/custom/sessions.db")
honcho = HonchoLite("/custom/users.db")
```

## 错误处理

所有模块都包含异常处理:

- 快照不存在 → 返回 None
- 搜索失败 → 返回空列表
- LLM 不可用 → 使用简单摘要
- 数据库错误 → 记录日志并返回默认值