# mem9 记忆系统 - 使用指南

**版本**: 1.2.0  
**更新**: 2026-03-15

---

## 📋 快速开始

### 1. 基础使用（5 分钟）

创建一个简单的对话记忆系统：

```python
import asyncio
from memory import create_context_engine, Message, TokenBudget, Turn

async def main():
    # 创建记忆引擎
    engine = create_context_engine({
        "enable_feishu": False,  # 暂时不启用飞书
    })
    
    # 初始化
    await engine.bootstrap()
    print("✅ 记忆系统已启动")
    
    # 模拟对话
    user_msg = Message(
        id="msg_001",
        role="user",
        content="记住我喜欢使用蓝色主题，不喜欢太复杂的界面"
    )
    
    # 处理用户消息
    await engine.ingest(user_msg)
    print("✅ 已记录用户偏好")
    
    # 组装上下文（用于 AI 回复）
    budget = TokenBudget(hard_limit=100000, soft_limit=80000)
    context = await engine.assemble(budget)
    print(f"✅ 已组装上下文: {len(context.messages)} 条消息")
    
    # AI 回复
    assistant_msg = Message(
        id="msg_002",
        role="assistant",
        content="好的，已记住！你喜欢蓝色主题，偏好简洁界面"
    )
    
    # 轮次后处理
    turn = Turn(
        turn_id="turn_001",
        user_message=user_msg,
        assistant_message=assistant_msg
    )
    await engine.afterTurn(turn)
    print("✅ 轮次处理完成")

asyncio.run(main())
```

---

## 🎯 使用场景

### 场景 1: 记住用户偏好

```python
# 记住偏好
user_msg = Message(
    id="msg_001",
    role="user",
    content="我最喜欢使用 Python 编程，特别是用 FastAPI 搭建后端"
)
await engine.ingest(user_msg)
```

**自动识别**:
- 重要性: HIGH (0.50+)
- 类型: PREFERENCE (偏好)
- 标签: ["python", "fastapi", "后端", "编程", "偏好"]

---

### 场景 2: 记住重要规则

```python
# 记住规则
user_msg = Message(
    id="msg_002",
    role="user",
    content="记住：Git 推送前必须先确认，这个规则绝对不能违反"
)
await engine.ingest(user_msg)
```

**自动识别**:
- 重要性: CRITICAL (0.67+)
- 类型: RULE (规则)
- 标签: ["git", "推送", "确认", "规则", "重要"]

---

### 场景 3: 记住任务

```python
# 记住任务
user_msg = Message(
    id="msg_003",
    role="user",
    content="明天之前完成 mem9 升级的 Phase 4 测试"
)
await engine.ingest(user_msg)
```

**自动识别**:
- 重要性: HIGH (0.50+)
- 类型: TASK (任务)
- 标签: ["mem9", "升级", "测试", "任务", "明天"]

---

## 🔍 智能检索

### 1. 全文检索

```python
from memory.fulltext_search import FullTextSearcher
from memory import MemoryEntry, MemoryType, ImportanceLevel

searcher = FullTextSearcher()

# 添加记忆
entry = MemoryEntry(
    id="001",
    content="用户喜欢使用 Python 编程",
    memory_type=MemoryType.LONG_TERM,
    importance=ImportanceLevel.HIGH
)
searcher.add_entry(entry)

# 搜索
results = searcher.search("python 编程", top_k=5)
for result in results:
    print(f"✅ {result.entry.content}")
    print(f"   相关性: {result.score:.2f}")
```

---

### 2. 向量搜索（语义搜索）

```python
from memory.vector_search import VectorSearcher
from memory import MemoryEntry, MemoryType, ImportanceLevel

searcher = VectorSearcher()

# 添加记忆
entry = MemoryEntry(
    id="001",
    content="用户喜欢使用 Python 编程，特别是 FastAPI",
    memory_type=MemoryType.LONG_TERM,
    importance=ImportanceLevel.HIGH
)
searcher.add_entry(entry)

# 语义搜索（即使没有完全匹配的关键词）
results = searcher.search("用户擅长的技术栈", top_k=5)
for result in results:
    print(f"✅ {result.entry.content}")
    print(f"   相似度: {result.score:.2f}")
```

---

### 3. 混合召回（最佳结果）

```python
from memory.hybrid_retriever import HybridRetriever
from memory import MemoryEntry, MemoryType, ImportanceLevel

retriever = HybridRetriever()

# 添加记忆
entry = MemoryEntry(
    id="001",
    content="用户喜欢使用 Python 编程",
    memory_type=MemoryType.LONG_TERM,
    importance=ImportanceLevel.HIGH
)
retriever.add_entry(entry)

# 混合搜索（向量 + 全文）
results = retriever.search(
    query="python",
    vector_weight=0.6,
    fulltext_weight=0.4,
    top_k=5
)
for result in results:
    print(f"✅ {result.entry.content}")
    print(f"   向量: {result.vector_score:.2f} | 全文: {result.fulltext_score:.2f}")
```

---

## 📊 记忆统计

```python
from scripts.optimize_memory import stats

# 查看记忆统计
stats()
```

**输出示例**:
```
==================================================
Memory Statistics
==================================================
Short-term memories: 1
Long-term memories: 7

Long-term by importance:
  CRITICAL: 1
  HIGH: 3
  MEDIUM: 3
  LOW: 0
  MINIMAL: 0
==================================================
```

---

## 🚀 高级功能

### 1. 飞书集成（云端同步）

```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_app_token",
    "feishu_table_id": "your_table_id",
})
```

**好处**:
- 云端永久存储
- 跨设备同步
- 可视化查看

---

### 2. 自动重要性评分

```python
from memory.importance_scorer import ImportanceScorer

scorer = ImportanceScorer()
result = scorer.score_content("记住：API Key 是 xxx")

print(f"重要性: {result.importance}")  # CRITICAL
print(f"评分: {result.overall_score:.2f}")  # 0.67+
print(f"理由: {result.reasons}")  # ['包含关键关键词', '包含重要关键词']
```

---

### 3. 自动提取

```python
from memory.auto_extractor import AutoExtractor

extractor = AutoExtractor()
result = extractor.extract_from_content(
    "我最喜欢使用 Python 编程",
    "msg_001"
)

print(f"类型: {result.info_list[0].type}")  # PREFERENCE
print(f"标签: {result.info_list[0].tags}")  # ['python', '编程', '偏好']
print(f"实体: {result.info_list[0].entities}")  # {}
```

---

## 💡 最佳实践

### 1. 定期压缩记忆

```bash
python3 scripts/optimize-memory.py compress
```

### 2. 查看记忆统计

```bash
python3 scripts/optimize-memory.py stats
```

### 3. 搜索记忆

```python
from memory import MemoryManager

manager = MemoryManager()
memories = manager.search_memories(
    keywords=["python"],
    importance_min=ImportanceLevel.HIGH
)
```

---

## 🎉 总结

**核心功能**:
- ✅ 自动记忆管理
- ✅ 智能重要性评分
- ✅ 自动提取和分类
- ✅ 多种检索方式
- ✅ 飞书云端同步

**开始使用**: 只需 3 行代码！

```python
from memory import create_context_engine
engine = create_context_engine()
await engine.bootstrap()
```

---

**完整示例**: `examples/basic_usage.py`
