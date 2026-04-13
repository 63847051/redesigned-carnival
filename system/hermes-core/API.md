# Hermes Core API 文档

## 模块导入

```python
from hermes_core import (
    # Core
    SnapshotStore, AtomicWriter, get_snapshot_store, get_atomic_writer,
    FuzzyPatcher, PatchResult, fuzzy_match, calculate_similarity, find_closest_match,
    
    # Learning
    AutoSkillCreator, TaskContext, create_skill_from_task,
    AutoSkillImprover, UsageContext, ImprovementSuggestion, improve_skill,
    SelfGuidance, get_self_guidance, should_inject_guidance,
    
    # Search
    SessionSearch, get_session_search, search_sessions, index_session,
    LLMSummarizer, SummaryResult, get_llm_summarizer, summarize_search_results,
    
    # Modeling
    HonchoLite, UserProfile, UserConclusion, get_honcho,
    get_user_profile, search_user_history, reason_about_user, save_user_conclusion,
)
```

---

## Core 模块

### SnapshotStore

快照冻结存储系统。

```python
store = SnapshotStore(base_path: str = None)
```

**方法**:

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| `capture_snapshot` | `key: str`, `data: Dict` | `None` | 捕获快照 |
| `freeze` | `key: str` | `None` | 冻结快照 |
| `unfreeze` | `key: str` | `None` | 解冻快照 |
| `get_snapshot` | `key: str` | `Dict \| None` | 获取快照 |
| `update_snapshot` | `key: str`, `data: Dict` | `bool` | 更新快照 |
| `is_frozen` | `key: str` | `bool` | 检查是否冻结 |
| `save_to_disk` | `key: str`, `filename: str = None` | `Path` | 原子写入 |
| `load_from_disk` | `key: str`, `filename: str = None` | `Dict` | 从磁盘加载 |
| `list_snapshots` | - | `List` | 列出快照 |
| `clear` | - | `None` | 清除所有 |

### AtomicWriter

原子写入工具。

```python
writer = AtomicWriter(base_path: str = None)
```

**方法**:

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| `write_json` | `filepath: str`, `data: Any`, `indent: int = 2` | `Path` | 原子写 JSON |
| `write_text` | `filepath: str`, `content: str` | `Path` | 原子写文本 |
| `write_bytes` | `filepath: str`, `data: bytes` | `Path` | 原子写二进制 |
| `read_json` | `filepath: str` | `Any` | 读 JSON |
| `read_text` | `filepath: str` | `str` | 读文本 |
| `delete` | `filepath: str` | `bool` | 删除文件 |

### FuzzyPatcher

Fuzzy Patch 引擎。

```python
patcher = FuzzyPatcher(normalize_whitespace: bool = True)
```

**方法**:

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| `normalize` | `text: str` | `str` | 规范化空白符 |
| `compute_diff` | `original: str`, `patched: str` | `str` | 计算 diff |
| `apply_patch` | `original: str`, `patch: str` | `PatchResult` | 应用补丁 |
| `smart_merge` | `base: str`, `theirs: str`, `ours: str` | `str` | 三方合并 |

### 工具函数

```python
fuzzy_match(pattern: str, text: str, threshold: float = 0.8) -> bool
calculate_similarity(a: str, b: str) -> float
find_closest_match(target: str, candidates: List[str]) -> Tuple[Optional[str], float]
```

---

## Learning 模块

### TaskContext

任务上下文数据类。

```python
@dataclass
class TaskContext:
    tool_calls: List[Dict[str, Any]]      # 工具调用列表
    errors: List[str]                      # 错误列表
    user_corrections: List[str]           # 用户纠正列表
    success: bool                          # 是否成功
    duration: float                        # 持续时间
```

### AutoSkillCreator

技能自动创建器。

```python
creator = AutoSkillCreator(skills_dir: str = None)
```

**方法**:

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| `analyze_context` | `context: TaskContext` | `Dict` | 分析上下文 |
| `create_skill` | `context: TaskContext`, `force: bool = False` | `str \| None` | 创建技能 |
| `should_create_skill` | `tool_calls: int`, `errors: int`, `corrections: int`, `success: bool` | `bool` | 快速检查 |

### UsageContext

技能使用上下文。

```python
@dataclass
class UsageContext:
    skill_name: str                       # 技能名称
    user_request: str                     # 用户请求
    execution_result: str                 # 执行结果
    success: bool                         # 是否成功
    error: Optional[str] = None           # 错误信息
    partial_match: bool = False           # 部分匹配
    missing_context: List[str] = []      # 缺失上下文
```

### AutoSkillImprover

技能自动改进器。

```python
improver = AutoSkillImprover(skills_dir: str = None)
```

**方法**:

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| `analyze_usage` | `context: UsageContext` | `ImprovementSuggestion \| None` | 分析使用 |
| `apply_improvement` | `suggestion: ImprovementSuggestion`, `auto_apply: bool = False` | `bool` | 应用改进 |
| `get_usage_stats` | `skill_name: str` | `Dict` | 使用统计 |
| `suggest_skills_for_improvement` | - | `List[Tuple[str, float]]` | 建议改进 |

### SelfGuidance

自我引导系统。

```python
guidance = SelfGuidance()
```

**方法**:

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| `register_trigger` | `trigger: GuidanceTrigger` | `None` | 注册触发器 |
| `evaluate_triggers` | `context: Dict` | `List[str]` | 评估触发器 |
| `inject_guidance` | `prompts: List[str]`, `existing: List[str]` | `List[str]` | 注入引导 |
| `get_guidance_history` | `limit: int = 10` | `List[Dict]` | 引导历史 |

---

## Search 模块

### SessionSearch

FTS5 会话搜索引擎。

```python
search = SessionSearch(db_path: str = None)
```

**方法**:

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| `index_session` | `session_id: str`, `title: str`, `messages: List[Dict]`, `metadata: Dict = None` | `None` | 索引会话 |
| `search` | `query: str`, `limit: int = 10`, `session_id: str = None` | `List[Dict]` | 搜索会话 |
| `get_session_messages` | `session_id: str`, `limit: int = 100` | `List[Dict]` | 获取消息 |
| `get_recent_sessions` | `limit: int = 10` | `List[Dict]` | 最近会话 |
| `delete_session` | `session_id: str` | `bool` | 删除会话 |
| `get_stats` | - | `Dict` | 统计信息 |

### LLMSummarizer

LLM 摘要生成器。

```python
summarizer = LLMSummarizer(api_key: str = None, model: str = None)
```

**方法**:

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| `summarize` | `query: str`, `sessions: List[Dict]`, `force: bool = False` | `SummaryResult` | 生成摘要 |
| `summarize_conversation` | `messages: List[Dict]` | `str` | 总结对话 |
| `extract_insights` | `sessions: List[Dict]` | `List[str]` | 提取洞察 |

### SummaryResult

摘要结果数据类。

```python
@dataclass
class SummaryResult:
    summary: str                          # 摘要
    key_topics: List[str]                 # 主题
    relevant_sessions: List[Dict]         # 相关会话
    confidence: float                     # 置信度
    generated_at: str                    # 生成时间
```

---

## Modeling 模块

### HonchoLite

Honcho 用户建模简化版。

```python
honcho = HonchoLite(db_path: str = None)
```

**方法**:

| 方法 | 参数 | 返回 | 描述 |
|------|------|------|------|
| `profile` | `user_id: str`, `name: str = None` | `UserProfile` | 获取用户卡片 |
| `search` | `user_id: str`, `query: str`, `limit: int = 10` | `List[Dict]` | 语义搜索 |
| `context` | `user_id: str`, `question: str` | `Dict` | 辩证推理 |
| `conclude` | `user_id: str`, `statement: str`, `confidence: float`, `evidence: List[str] = None` | `UserConclusion` | 持久化结论 |
| `record_interaction` | `user_id: str`, `content: str`, `metadata: Dict = None` | `None` | 记录交互 |
| `update_traits` | `user_id: str`, `traits: List[str]` | `None` | 更新特征 |
| `get_all_users` | - | `List[UserProfile]` | 所有用户 |

### UserProfile

用户档案数据类。

```python
@dataclass
class UserProfile:
    user_id: str                          # 用户 ID
    name: str                             # 用户名
    traits: List[str]                     # 特征
    preferences: Dict[str, Any]           # 偏好
    interaction_count: int                # 交互次数
    last_seen: str                        # 最后活跃
    created_at: str                      # 创建时间
```

### UserConclusion

用户结论数据类。

```python
@dataclass
class UserConclusion:
    conclusion_id: str                    # 结论 ID
    user_id: str                          # 用户 ID
    statement: str                        # 结论陈述
    confidence: float                     # 置信度
    evidence: List[str]                  # 证据
    created_at: str                      # 创建时间
```

---

## 全局实例

所有模块提供便捷函数获取全局单例:

```python
get_snapshot_store() -> SnapshotStore
get_atomic_writer() -> AtomicWriter
get_session_search() -> SessionSearch
get_llm_summarizer() -> LLMSummarizer
get_honcho() -> HonchoLite
get_self_guidance() -> SelfGuidance
```

---

## 数据类型

### PatchResult

```python
@dataclass
class PatchResult:
    success: bool                         # 是否成功
    original: str                         # 原始文本
    patched: str                          # 修补后文本
    diff: str                             # diff 内容
    confidence: float                     # 置信度
```

### ImprovementSuggestion

```python
@dataclass
class ImprovementSuggestion:
    skill_name: str                       # 技能名称
    patch_content: str                     # 补丁内容
    confidence: float                     # 置信度
    reason: str                            # 原因
    priority: str                          # 优先级 (high/medium/low)
```