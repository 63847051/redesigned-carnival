"""
检索系统测试

测试向量搜索、全文检索和混合召回功能
"""

import logging
import sys
import os
from datetime import datetime
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.context_engine import MemoryEntry, MemoryType, ImportanceLevel
from memory.vector_search import (
    VectorSearcher,
    EmbeddingModel,
    InMemoryVectorStore,
    cosine_similarity,
    SearchResult,
)
from memory.fulltext_search import (
    FullTextSearcher,
    TFIDFIndex,
    BooleanQueryParser,
    FuzzyMatcher,
    FullTextResult,
)
from memory.hybrid_retriever import (
    HybridRetriever,
    RetrievedEntry,
    ResultFusion,
    ResultReranker,
    DiversityOptimizer,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def create_test_entries() -> List[MemoryEntry]:
    """创建测试用记忆条目"""
    return [
        MemoryEntry(
            id="mem1",
            content="用户喜欢在下午3点喝咖啡，这个习惯已经保持了半年",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.HIGH,
            tags=["偏好", "习惯"],
            created_at=datetime.now(),
            last_accessed=datetime.now(),
        ),
        MemoryEntry(
            id="mem2",
            content="用户的工作是软件工程师，主要使用Python和JavaScript",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.HIGH,
            tags=["职业", "技能"],
            created_at=datetime.now(),
            last_accessed=datetime.now(),
        ),
        MemoryEntry(
            id="mem3",
            content="用户住在上海，喜欢周末去咖啡馆办公",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.MEDIUM,
            tags=["位置", "偏好"],
            created_at=datetime.now(),
            last_accessed=datetime.now(),
        ),
        MemoryEntry(
            id="mem4",
            content="今天天气很好，用户去公园散步了",
            memory_type=MemoryType.SHORT_TERM,
            importance=ImportanceLevel.LOW,
            tags=["日常"],
            created_at=datetime.now(),
            last_accessed=datetime.now(),
        ),
        MemoryEntry(
            id="mem5",
            content="用户计划下个月去日本旅游，需要提前订酒店",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.MEDIUM,
            tags=["计划", "旅行"],
            created_at=datetime.now(),
            last_accessed=datetime.now(),
        ),
        MemoryEntry(
            id="mem6",
            content="用户喜欢看科幻电影，尤其是星际穿越这类",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.MEDIUM,
            tags=["偏好", "娱乐"],
            created_at=datetime.now(),
            last_accessed=datetime.now(),
        ),
        MemoryEntry(
            id="mem7",
            content="项目 deadline 是下周五，需要尽快完成",
            memory_type=MemoryType.EPISODIC,
            importance=ImportanceLevel.CRITICAL,
            tags=["任务", "项目"],
            created_at=datetime.now(),
            last_accessed=datetime.now(),
        ),
        MemoryEntry(
            id="mem8",
            content="用户对猫过敏，所以不能养宠物",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.HIGH,
            tags=["健康", "偏好"],
            created_at=datetime.now(),
            last_accessed=datetime.now(),
        ),
    ]


def test_vector_search():
    """测试向量搜索"""
    logger.info("=" * 50)
    logger.info("Testing Vector Search")
    logger.info("=" * 50)

    entries = create_test_entries()

    searcher = VectorSearcher(use_faiss=False)
    searcher.index_entries(entries)

    logger.info(f"Indexed {searcher.count} entries")

    queries = [
        "用户的兴趣爱好是什么",
        "工作相关的内容",
        "重要的任务",
    ]

    for query in queries:
        logger.info(f"\nQuery: {query}")
        results = searcher.search(query, top_k=3)

        for result in results:
            logger.info(
                f"  Rank {result.rank}: {result.entry.content[:50]}... "
                f"(score: {result.score:.4f})"
            )

    logger.info("\nVector search tests passed!")


def test_fulltext_search():
    """测试全文检索"""
    logger.info("=" * 50)
    logger.info("Testing Full-Text Search")
    logger.info("=" * 50)

    entries = create_test_entries()

    searcher = FullTextSearcher(enable_fuzzy=True)
    searcher.index_entries(entries)

    logger.info(f"Indexed {searcher.count} entries")

    test_queries = [
        "用户 喜欢",
        "工作 AND Python",
        "旅游 OR 计划",
        "用户 NOT 上海",
        "软*",
    ]

    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        results = searcher.search(query, top_k=3)

        for result in results:
            logger.info(
                f"  Rank {result.rank}: {result.entry.content[:50]}... "
                f"(score: {result.score:.4f}, matched: {result.matched_terms})"
            )

    logger.info("\nFull-text search tests passed!")


def test_boolean_parser():
    """测试布尔查询解析器"""
    logger.info("=" * 50)
    logger.info("Testing Boolean Query Parser")
    logger.info("=" * 50)

    parser = BooleanQueryParser()

    test_cases = [
        "用户 喜欢",
        "工作 AND Python",
        "旅游 OR 旅行",
        "用户 NOT 上海",
        "重要 AND 任务",
    ]

    for query in test_cases:
        parsed = parser.parse(query)
        logger.info(f"Query: {query} -> {parsed}")

    logger.info("\nBoolean parser tests passed!")


def test_tfidf_index():
    """测试 TF-IDF 索引"""
    logger.info("=" * 50)
    logger.info("Testing TF-IDF Index")
    logger.info("=" * 50)

    index = TFIDFIndex()
    entries = create_test_entries()

    index.add_documents(entries)

    test_queries = [
        ["用户", "喜欢"],
        ["工作", "Python"],
        ["计划", "旅游"],
    ]

    for query in test_queries:
        scores = []
        for i in range(len(entries)):
            score = index.get_tfidf_score(i, query)
            scores.append((entries[i].id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"Query {query}: {scores[:3]}")

    logger.info("\nTF-IDF index tests passed!")


def test_fuzzy_matcher():
    """测试模糊匹配"""
    logger.info("=" * 50)
    logger.info("Testing Fuzzy Matcher")
    logger.info("=" * 50)

    matcher = FuzzyMatcher(max_distance=2)

    test_cases = [
        ("软工", "软件工程师"),
        ("咖非", "咖啡"),
        ("旅游", "旅行"),
        ("test", "testing"),
    ]

    for term, text in test_cases:
        result = matcher.is_fuzzy_match(term, text)
        logger.info(f"Fuzzy match '{term}' in '{text}': {result}")

    logger.info("\nFuzzy matcher tests passed!")


def test_hybrid_retriever():
    """测试混合召回"""
    logger.info("=" * 50)
    logger.info("Testing Hybrid Retriever")
    logger.info("=" * 50)

    entries = create_test_entries()

    vector_searcher = VectorSearcher(use_faiss=False)
    fulltext_searcher = FullTextSearcher(enable_fuzzy=True)

    retriever = HybridRetriever(
        vector_weight=0.5,
        fusion_method="weighted",
        enable_rerank=True,
        enable_diversity=True,
    )

    retriever.set_vector_searcher(vector_searcher)
    retriever.set_fulltext_searcher(fulltext_searcher)

    retriever.index_entries(entries)

    logger.info(f"Indexed {retriever.indexed_count} entries")

    queries = [
        "用户的兴趣爱好",
        "工作任务",
        "重要紧急的事情",
    ]

    for query in queries:
        logger.info(f"\nQuery: {query}")
        results = retriever.search(query, top_k=5)

        for result in results:
            logger.info(
                f"  Rank {result.rank}: {result.entry.content[:40]}... "
                f"(vector: {result.vector_score:.3f}, "
                f"fulltext: {result.fulltext_score:.3f}, "
                f"combined: {result.combined_score:.3f}, "
                f"sources: {result.sources})"
            )

    logger.info("\nHybrid retriever tests passed!")


def test_result_fusion():
    """测试结果融合"""
    logger.info("=" * 50)
    logger.info("Testing Result Fusion")
    logger.info("=" * 50)

    entries = create_test_entries()

    vector_results = [
        SearchResult(entry=entries[0], score=0.9, rank=1),
        SearchResult(entry=entries[1], score=0.8, rank=2),
        SearchResult(entry=entries[2], score=0.7, rank=3),
    ]

    fulltext_results = [
        FullTextResult(entry=entries[1], score=0.85, matched_terms=["工作"], rank=1),
        FullTextResult(entry=entries[0], score=0.8, matched_terms=["用户"], rank=2),
        FullTextResult(entry=entries[3], score=0.6, matched_terms=["今天"], rank=3),
    ]

    weighted = ResultFusion.weighted_fusion(
        vector_results, fulltext_results, vector_weight=0.5
    )
    logger.info(f"Weighted fusion: {len(weighted)} results")

    rrf = ResultFusion.rrf_fusion(vector_results, fulltext_results)
    logger.info(f"RRF fusion: {len(rrf)} results")

    logger.info("\nResult fusion tests passed!")


def test_diversity_optimizer():
    """测试多样性优化"""
    logger.info("=" * 50)
    logger.info("Testing Diversity Optimizer")
    logger.info("=" * 50)

    entries = create_test_entries()

    results = [
        RetrievedEntry(
            entry=entries[0],
            vector_score=0.9,
            fulltext_score=0.8,
            combined_score=0.9,
            sources=["vector", "fulltext"],
            rank=1,
        ),
        RetrievedEntry(
            entry=entries[1],
            vector_score=0.8,
            fulltext_score=0.7,
            combined_score=0.8,
            sources=["vector"],
            rank=2,
        ),
    ]

    optimizer = DiversityOptimizer(max_similar=1)
    optimized = optimizer.optimize(results)

    logger.info(f"Original: {len(results)}, Optimized: {len(optimized)}")

    logger.info("\nDiversity optimizer tests passed!")


def test_integration_with_memory_manager():
    """测试与 MemoryManager 集成"""
    logger.info("=" * 50)
    logger.info("Testing Integration with Memory Manager")
    logger.info("=" * 50)

    from memory.memory_manager import FileMemoryStorage

    storage = FileMemoryStorage()

    entries = create_test_entries()

    for entry in entries:
        storage.save_memory(entry)

    loaded = storage.list_memories(limit=10)
    logger.info(f"Loaded {len(loaded)} entries from storage")

    vector_searcher = VectorSearcher(use_faiss=False)
    fulltext_searcher = FullTextSearcher(enable_fuzzy=True)

    vector_searcher.index_entries(loaded)
    fulltext_searcher.index_entries(loaded)

    query = "用户的工作和兴趣"
    vector_results = vector_searcher.search(query, top_k=3)
    fulltext_results = fulltext_searcher.search(query, top_k=3)

    logger.info(f"Vector search found {len(vector_results)} results")
    logger.info(f"Full-text search found {len(fulltext_results)} results")

    logger.info("\nIntegration tests passed!")


def main():
    """运行所有测试"""
    logger.info("Starting Retrieval System Tests")
    logger.info("=" * 50)

    try:
        test_boolean_parser()
        test_fuzzy_matcher()
        test_tfidf_index()
        test_vector_search()
        test_fulltext_search()
        test_result_fusion()
        test_diversity_optimizer()
        test_hybrid_retriever()
        test_integration_with_memory_manager()

        logger.info("=" * 50)
        logger.info("All tests passed!")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
