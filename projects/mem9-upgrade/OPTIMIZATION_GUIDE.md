# mem9 记忆系统 - 参数配置和优化指南

**版本**: 1.0.0  
**更新**: 2026-03-15

---

## 📋 可配置参数

### 1. 重要性评分参数

控制记忆重要性的评分算法：

```python
from memory.importance_scorer import ScoringConfig

config = ScoringConfig(
    # 内容长度权重（0.0 - 1.0）
    length_weight=0.15,
    
    # 关键词密度权重（0.0 - 1.0）
    keyword_weight=0.50,
    
    # 时效性权重（0.0 - 1.0）
    temporal_weight=0.20,
    
    # 情感信号权重（0.0 - 1.0）
    emotion_weight=0.15,
    
    # 重要性阈值
    critical_threshold=0.67,
    high_threshold=0.50,
    medium_threshold=0.35,
    low_threshold=0.20,
)
```

**建议配置**：

**场景 1: 严格模式**（只记住真正重要的）
```python
config = ScoringConfig(
    keyword_weight=0.60,  # 提高关键词权重
    critical_threshold=0.70,  # 提高 CRITICAL 阈值
    high_threshold=0.55,  # 提高 HIGH 阈值
)
```

**场景 2: 宽松模式**（记住更多内容）
```python
config = ScoringConfig(
    keyword_weight=0.40,  # 降低关键词权重
    critical_threshold=0.60,  # 降低 CRITICAL 阈值
    high_threshold=0.40,  # 降低 HIGH 阈值
)
```

---

### 2. 记忆管理参数

控制记忆的存储和检索：

```python
engine = create_context_engine({
    # 最大短期记忆数量
    "max_short_term": 50,
    
    # 最大长期记忆数量
    "max_long_term": 1000,
    
    # 压缩阈值（当记忆超过此数量时触发压缩）
    "compaction_threshold": 0.8,
    
    # 持久化间隔（秒）
    "persistence_interval": 60,
})
```

**建议配置**：

**轻量级使用**（个人助手）
```python
engine = create_context_engine({
    "max_short_term": 20,
    "max_long_term": 100,
    "compaction_threshold": 0.7,
})
```

**中等级别**（团队协作）
```python
engine = create_context_engine({
    "max_short_term": 50,
    "max_long_term": 500,
    "compaction_threshold": 0.8,
})
```

**重量级使用**（企业级）
```python
engine = create_context_engine({
    "max_short_term": 100,
    "max_long_term": 2000,
    "compaction_threshold": 0.9,
})
```

---

### 3. 飞书同步参数

控制云端同步行为：

```python
engine = create_context_engine({
    # 启用飞书同步
    "enable_feishu": True,
    
    # 飞书应用凭证
    "feishu_app_token": "your_app_token",
    "feishu_table_id": "your_table_id",
    
    # 同步阈值（只同步评分 >= 此值的记忆）
    "feishu_sync_threshold": 0.5,
    
    # 同步批次大小
    "feishu_batch_size": 10,
    
    # 同步间隔（秒）
    "feishu_sync_interval": 30,
})
```

**建议配置**：

**即时同步**（重要记忆立即同步）
```python
engine = create_context_engine({
    "feishu_sync_threshold": 0.5,  # HIGH 及以上
    "feishu_sync_interval": 10,  # 每 10 秒同步
})
```

**定期同步**（节省 API 调用）
```python
engine = create_context_engine({
    "feishu_sync_threshold": 0.67,  # 只同步 CRITICAL
    "feishu_sync_interval": 60,  # 每 60 秒同步
})
```

---

### 4. 检索参数

控制搜索和检索行为：

```python
from memory.hybrid_retriever import HybridRetriever

retriever = HybridRetriever()

# 混合检索参数
results = retriever.search(
    query="python 编程",
    vector_weight=0.6,      # 向量搜索权重（0.0 - 1.0）
    fulltext_weight=0.4,    # 全文检索权重（0.0 - 1.0）
    top_k=10,               # 返回结果数量
    diversity_threshold=0.7, # 多样性阈值（0.0 - 1.0）
)
```

**建议配置**：

**语义优先**（适合模糊查询）
```python
results = retriever.search(
    query="用户擅长的技术",
    vector_weight=0.7,      # 优先向量搜索
    fulltext_weight=0.3,
)
```

**关键词优先**（适合精确查询）
```python
results = retriever.search(
    query="python",
    vector_weight=0.3,      # 优先全文检索
    fulltext_weight=0.7,
)
```

**均衡模式**（推荐）
```python
results = retriever.search(
    query="python 编程",
    vector_weight=0.5,
    fulltext_weight=0.5,
)
```

---

## 🎯 优化场景

### 场景 1: 个人助手（轻量级）

**特点**: 记住用户偏好，快速响应

```python
from memory import create_context_engine

engine = create_context_engine({
    # 记忆限制
    "max_short_term": 20,
    "max_long_term": 100,
    
    # 压缩策略
    "compaction_threshold": 0.7,
    
    # 飞书同步（可选）
    "enable_feishu": True,
    "feishu_sync_threshold": 0.5,
})
```

**优化建议**:
- ✅ 降低记忆数量限制
- ✅ 提高压缩频率
- ✅ 只同步重要记忆

---

### 场景 2: 团队协作（中等级别）

**特点**: 多人共享记忆，需要云端同步

```python
engine = create_context_engine({
    # 记忆限制
    "max_short_term": 50,
    "max_long_term": 500,
    
    # 压缩策略
    "compaction_threshold": 0.8,
    
    # 飞书同步（必须）
    "enable_feishu": True,
    "feishu_app_token": "your_token",
    "feishu_table_id": "your_table_id",
    "feishu_sync_threshold": 0.4,  # 同步更多记忆
    "feishu_sync_interval": 30,
})
```

**优化建议**:
- ✅ 提高记忆数量限制
- ✅ 启用飞书同步
- ✅ 定期同步

---

### 场景 3: 企业级（重量级）

**特点**: 大量记忆，需要高性能

```python
engine = create_context_engine({
    # 记忆限制
    "max_short_term": 100,
    "max_long_term": 2000,
    
    # 压缩策略
    "compaction_threshold": 0.9,
    
    # 飞书同步（必须）
    "enable_feishu": True,
    "feishu_app_token": "your_token",
    "feishu_table_id": "your_table_id",
    "feishu_sync_threshold": 0.3,  # 同步几乎所有记忆
    "feishu_batch_size": 20,  # 批量同步
    "feishu_sync_interval": 60,
})
```

**优化建议**:
- ✅ 最大化记忆数量
- ✅ 批量同步
- ✅ 降低同步阈值

---

## 🔧 性能优化

### 1. 向量搜索优化

**启用 FAISS 加速**（需要安装 `faiss-cpu`）:

```python
from memory.vector_search import VectorSearcher, FAISSVectorStore

searcher = VectorSearcher(
    vector_store=FAISSVectorStore()  # 使用 FAISS 加速
)
```

**安装 FAISS**:
```bash
pip3 install faiss-cpu
```

**性能提升**:
- 小规模（< 1000 条）: 无明显提升
- 中规模（1000-10000 条）: 2-3 倍提升
- 大规模（> 10000 条）: 5-10 倍提升

---

### 2. 缓存优化

**启用向量缓存**:

```python
from memory.vector_search import EmbeddingModel

model = EmbeddingModel(
    cache_embeddings=True,  # 启用缓存
    cache_size=1000,  # 缓存 1000 个向量
)
```

**性能提升**:
- 重复查询: 10-100 倍提升
- 内存占用: +50-100MB

---

### 3. 批量操作

**批量添加记忆**:

```python
from memory.fulltext_search import FullTextSearcher

searcher = FullTextSearcher()

# 批量添加（更快）
searcher.index_entries(memories)

# 而不是逐个添加
for memory in memories:
    searcher.add_entry(memory)
```

**性能提升**:
- 10 条: 1.5 倍
- 100 条: 3 倍
- 1000 条: 5 倍

---

## 📊 监控和调试

### 1. 查看记忆统计

```bash
python3 scripts/optimize-memory.py stats
```

**输出示例**:
```
==================================================
Memory Statistics
==================================================
Short-term memories: 15
Long-term memories: 85

Long-term by importance:
  CRITICAL: 5
  HIGH: 30
  MEDIUM: 35
  LOW: 10
  MINIMAL: 5
==================================================
```

### 2. 压缩记忆

```bash
python3 scripts/optimize-memory.py compress
```

**功能**:
- 删除低价值记忆
- 合并相似记忆
- 优化存储结构

### 3. 搜索记忆

```python
from memory import MemoryManager

manager = MemoryManager()

# 按关键词搜索
memories = manager.search_memories(
    keywords=["python", "编程"],
    importance_min=ImportanceLevel.HIGH
)

for memory in memories:
    print(f"{memory.content}")
    print(f"  重要性: {memory.importance}")
    print(f"  标签: {memory.tags}")
```

---

## 💡 最佳实践

### 1. 定期压缩记忆

```bash
# 每周压缩一次
python3 scripts/optimize-memory.py compress
```

### 2. 监控记忆数量

```bash
# 每天检查一次
python3 scripts/optimize-memory.py stats
```

### 3. 调整评分阈值

```python
# 如果记忆太多，提高阈值
config = ScoringConfig(
    high_threshold=0.60,  # 从 0.50 提高到 0.60
)

# 如果记忆太少，降低阈值
config = ScoringConfig(
    high_threshold=0.40,  # 从 0.50 降低到 0.40
)
```

### 4. 优化同步策略

```python
# 如果 API 调用太多，降低同步频率
engine = create_context_engine({
    "feishu_sync_interval": 120,  # 从 60 秒改为 120 秒
    "feishu_sync_threshold": 0.67,  # 只同步 CRITICAL
})
```

---

## 🎉 总结

**核心参数**:
- ✅ 重要性评分权重
- ✅ 记忆数量限制
- ✅ 压缩阈值
- ✅ 同步策略
- ✅ 检索权重

**优化方向**:
- 🎯 根据使用场景调整参数
- 🎯 定期监控和优化
- 🎯 平衡性能和功能

**开始优化**: 根据你的需求选择合适的配置！

---

**完整示例**: `examples/optimization.py`
**配置文件**: `config/memory_config.py`
