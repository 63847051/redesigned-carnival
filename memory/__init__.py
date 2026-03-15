"""
Memory 模块

基于 OpenClaw 3.7+ ContextEngine 接口的记忆管理系统

主要组件:
- context_engine.py: ContextEngine 接口定义和实现
- memory_manager.py: 记忆管理器，整合多种存储

使用示例:

```python
from memory import create_context_engine

# 创建增强型 ContextEngine
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_token",
    "feishu_table_id": "your_table_id",
})

# Bootstrap
await engine.bootstrap()

# 处理消息
message = Message(
    id="msg_001",
    role="user",
    content="记住我喜欢高效直接的工作方式"
)
await engine.ingest(message)

# 组装上下文
budget = TokenBudget(hard_limit=100000, soft_limit=80000)
context = await engine.assemble(budget)

# 轮次后处理
turn = Turn(
    turn_id="turn_001",
    user_message=message,
    assistant_message=Message(id="resp_001", role="assistant", content="好的，已记住")
)
await engine.afterTurn(turn)
```
"""

from .context_engine import (
    ContextEngine,
    ImportanceLevel,
    LegacyContextEngine,
    MemoryEntry,
    MemoryType,
    Message,
    TokenBudget,
    Turn,
)
from .memory_manager import (
    EnhancedContextEngine,
    FeishuMemoryBitable,
    FileMemoryStorage,
    MemoryManager,
    create_context_engine,
)
from .importance_scorer import (
    ImportanceScorer,
    BatchScorer,
    ScoringResult,
    ScoringConfig,
)
from .auto_extractor import (
    AutoExtractor,
    ExtractionResult,
    ExtractedInfo,
    ExtractionType,
)
from .auto_tagger import (
    AutoTagger,
    TagManager,
    TagRecommendation,
)
from .vector_search import (
    VectorSearcher,
    EmbeddingModel,
    InMemoryVectorStore,
)
from .fulltext_search import (
    FullTextSearcher,
    BooleanQueryParser,
    TFIDFIndex,
)
from .hybrid_retriever import (
    HybridRetriever,
    ResultFusion,
)

__version__ = "1.2.0"

__all__ = [
    # Context Engine
    "ContextEngine",
    "LegacyContextEngine",
    "EnhancedContextEngine",
    "create_context_engine",
    # Data Classes
    "MemoryEntry",
    "MemoryType",
    "ImportanceLevel",
    "Message",
    "Turn",
    "TokenBudget",
    # Storage
    "MemoryManager",
    "FileMemoryStorage",
    "FeishuMemoryBitable",
    # Importance Scorer
    "ImportanceScorer",
    "BatchScorer",
    "ScoringResult",
    "ScoringConfig",
    # Auto Extractor
    "AutoExtractor",
    "ExtractionResult",
    "ExtractedInfo",
    "ExtractionType",
    # Auto Tagger
    "AutoTagger",
    "TagManager",
    "TagRecommendation",
    # Vector Search
    "VectorSearcher",
    "EmbeddingModel",
    "InMemoryVectorStore",
    # Full-text Search
    "FullTextSearcher",
    "BooleanQueryParser",
    "TFIDFIndex",
    # Hybrid Retrieval
    "HybridRetriever",
    "ResultFusion",
]
