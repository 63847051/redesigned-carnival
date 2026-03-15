"""
混合召回策略模块

结合向量搜索和全文检索
支持结果融合、加权、重排序和多样性优化
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

import numpy as np

from .context_engine import MemoryEntry, MemoryType, ImportanceLevel
from .vector_search import VectorSearcher, SearchResult as VectorResult
from .fulltext_search import FullTextSearcher, FullTextResult

logger = logging.getLogger(__name__)


class HybridRetrieverError(Exception):
    """混合检索基础异常"""

    pass


@dataclass
class RetrievedEntry:
    """检索到的记忆条目"""

    entry: MemoryEntry
    vector_score: float
    fulltext_score: float
    combined_score: float
    sources: List[str]
    rank: int


class ScoreNormalizer:
    """分数归一化器"""

    @staticmethod
    def min_max_normalize(scores: List[float]) -> List[float]:
        """Min-Max 归一化"""
        if not scores:
            return []
        min_score = min(scores)
        max_score = max(scores)
        if max_score == min_score:
            return [1.0] * len(scores)
        return [(s - min_score) / (max_score - min_score) for s in scores]

    @staticmethod
    def percentile_normalize(scores: List[float]) -> List[float]:
        """百分位归一化"""
        if not scores:
            return []
        sorted_scores = sorted(scores)
        return [
            sorted_scores.index(s) / len(sorted_scores) if s in sorted_scores else 1.0
            for s in scores
        ]


class ResultFusion:
    """结果融合器"""

    @staticmethod
    def weighted_fusion(
        vector_results: List[VectorResult],
        fulltext_results: List[FullTextResult],
        vector_weight: float = 0.5,
    ) -> Dict[str, RetrievedEntry]:
        """
        加权融合

        参数:
            vector_results: 向量搜索结果
            fulltext_results: 全文搜索结果
            vector_weight: 向量搜索权重 (0-1)

        返回:
            Dict[str, RetrievedEntry]: 融合后的结果
        """
        fulltext_weight = 1.0 - vector_weight

        vector_max = max((r.score for r in vector_results), default=1.0)
        fulltext_max = max((r.score for r in fulltext_results), default=1.0)

        fused: Dict[str, RetrievedEntry] = {}

        for result in vector_results:
            entry_id = result.entry.id
            normalized_score = result.score / vector_max if vector_max > 0 else 0
            fused[entry_id] = RetrievedEntry(
                entry=result.entry,
                vector_score=normalized_score,
                fulltext_score=0.0,
                combined_score=normalized_score * vector_weight,
                sources=["vector"],
                rank=result.rank,
            )

        for result in fulltext_results:
            entry_id = result.entry.id
            normalized_score = result.score / fulltext_max if fulltext_max > 0 else 0

            if entry_id in fused:
                fused[entry_id].fulltext_score = normalized_score
                fused[entry_id].combined_score += normalized_score * fulltext_weight
                fused[entry_id].sources.append("fulltext")
            else:
                fused[entry_id] = RetrievedEntry(
                    entry=result.entry,
                    vector_score=0.0,
                    fulltext_score=normalized_score,
                    combined_score=normalized_score * fulltext_weight,
                    sources=["fulltext"],
                    rank=result.rank,
                )

        return fused

    @staticmethod
    def rrf_fusion(
        vector_results: List[VectorResult],
        fulltext_results: List[FullTextResult],
        k: float = 60.0,
    ) -> Dict[str, RetrievedEntry]:
        """
        RRF (Reciprocal Rank Fusion) 融合

        参数:
            vector_results: 向量搜索结果
            fulltext_results: 全文搜索结果
            k: RRF 参数

        返回:
            Dict[str, RetrievedEntry]: 融合后的结果
        """
        fused: Dict[str, RetrievedEntry] = {}

        for rank, result in enumerate(vector_results, 1):
            entry_id = result.entry.id
            rrf_score = 1.0 / (k + rank)
            fused[entry_id] = RetrievedEntry(
                entry=result.entry,
                vector_score=result.score,
                fulltext_score=0.0,
                combined_score=rrf_score,
                sources=["vector"],
                rank=rank,
            )

        for rank, result in enumerate(fulltext_results, 1):
            entry_id = result.entry.id
            rrf_score = 1.0 / (k + rank)

            if entry_id in fused:
                fused[entry_id].fulltext_score = result.score
                fused[entry_id].combined_score += rrf_score
                fused[entry_id].sources.append("fulltext")
            else:
                fused[entry_id] = RetrievedEntry(
                    entry=result.entry,
                    vector_score=0.0,
                    fulltext_score=result.score,
                    combined_score=rrf_score,
                    sources=["fulltext"],
                    rank=rank,
                )

        return fused


class ResultReranker:
    """结果重排序器"""

    def __init__(self, importance_boost: float = 0.1):
        """
        初始化重排序器

        参数:
            importance_boost: 重要性提升系数
        """
        self.importance_boost = importance_boost

    def rerank(
        self,
        results: Dict[str, RetrievedEntry],
        boost_importance: bool = True,
        boost_recency: bool = True,
    ) -> List[RetrievedEntry]:
        """
        重排序

        参数:
            results: 融合后的结果
            boost_importance: 是否提升高重要性结果
            boost_recency: 是否提升近期结果

        返回:
            List[RetrievedEntry]: 重排序后的结果
        """
        reranked = []

        for entry_id, retrieved in results.items():
            entry = retrieved.entry
            score = retrieved.combined_score

            if boost_importance:
                importance_boost = (
                    (entry.importance.value - 1) / 4 * self.importance_boost
                )
                score += importance_boost

            if boost_recency:
                from datetime import datetime, timedelta

                days_old = (datetime.now() - entry.last_accessed).days
                recency_boost = max(0, 1 - days_old / 365) * 0.1
                score += recency_boost

            retrieved.combined_score = score
            reranked.append(retrieved)

        reranked.sort(key=lambda x: x.combined_score, reverse=True)

        for rank, item in enumerate(reranked, 1):
            item.rank = rank

        return reranked


class DiversityOptimizer:
    """多样性优化器"""

    def __init__(self, max_similar: int = 2):
        """
        初始化多样性优化器

        参数:
            max_similar: 允许的最大相似结果数
        """
        self.max_similar = max_similar

    def optimize(
        self,
        results: List[RetrievedEntry],
    ) -> List[RetrievedEntry]:
        """
        优化结果多样性

        参数:
            results: 排序后的结果

        返回:
            List[RetrievedEntry]: 多样化后的结果
        """
        if len(results) <= self.max_similar:
            return results

        optimized: List[RetrievedEntry] = []
        seen_content: Set[str] = set()

        for result in results:
            content_lower = result.entry.content.lower()

            similar_count = sum(
                1
                for seen in seen_content
                if self._calculate_similarity(content_lower, seen) > 0.8
            )

            if similar_count < self.max_similar:
                optimized.append(result)
                seen_content.add(content_lower)

            if len(optimized) >= len(results):
                break

        return optimized

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """计算文本相似度"""
        words1 = set(s1.split())
        words2 = set(s2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)


class HybridRetriever:
    """
    混合检索器

    整合向量搜索和全文检索
    """

    def __init__(
        self,
        vector_weight: float = 0.5,
        fusion_method: str = "weighted",
        enable_rerank: bool = True,
        enable_diversity: bool = True,
    ):
        """
        初始化混合检索器

        参数:
            vector_weight: 向量搜索权重 (0-1)
            fusion_method: 融合方法 (weighted, rrf)
            enable_rerank: 是否启用重排序
            enable_diversity: 是否启用多样性优化
        """
        self.vector_weight = vector_weight
        self.fusion_method = fusion_method
        self.enable_rerank = enable_rerank
        self.enable_diversity = enable_diversity

        self._vector_searcher: Optional[VectorSearcher] = None
        self._fulltext_searcher: Optional[FullTextSearcher] = None
        self._reranker = ResultReranker()
        self._diversity_optimizer = DiversityOptimizer()

    def set_vector_searcher(self, searcher: VectorSearcher) -> None:
        """设置向量搜索器"""
        self._vector_searcher = searcher

    def set_fulltext_searcher(self, searcher: FullTextSearcher) -> None:
        """设置全文搜索器"""
        self._fulltext_searcher = searcher

    def index_entries(self, entries: List[MemoryEntry]) -> int:
        """
        索引记忆条目

        参数:
            entries: 记忆条目列表

        返回:
            int: 索引的条目数量
        """
        indexed = 0

        if self._vector_searcher:
            indexed += self._vector_searcher.index_entries(entries)

        if self._fulltext_searcher:
            self._fulltext_searcher.rebuild_index(entries)
            indexed += len(entries)

        logger.info(f"Hybrid retriever indexed {indexed} entries")
        return indexed

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedEntry]:
        """
        混合搜索

        参数:
            query: 查询字符串
            top_k: 返回结果数量
            filters: 过滤条件

        返回:
            List[RetrievedEntry]: 检索结果
        """
        vector_results: List[VectorResult] = []
        fulltext_results: List[FullTextResult] = []

        if self._vector_searcher:
            try:
                vector_results = self._vector_searcher.search(query, top_k * 2, filters)
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")

        if self._fulltext_searcher:
            try:
                fulltext_results = self._fulltext_searcher.search(
                    query, top_k * 2, filters
                )
            except Exception as e:
                logger.warning(f"Full-text search failed: {e}")

        if not vector_results and not fulltext_results:
            return []

        if self.fusion_method == "rrf":
            fused = ResultFusion.rrf_fusion(vector_results, fulltext_results)
        else:
            fused = ResultFusion.weighted_fusion(
                vector_results, fulltext_results, self.vector_weight
            )

        results = list(fused.values())

        if self.enable_rerank:
            results = self._reranker.rerank({r.entry.id: r for r in results})

        if self.enable_diversity:
            results = self._diversity_optimizer.optimize(results)

        results = self._deduplicate(results)

        return results[:top_k]

    def _deduplicate(
        self,
        results: List[RetrievedEntry],
    ) -> List[RetrievedEntry]:
        """去重"""
        seen_ids: Set[str] = set()
        deduplicated: List[RetrievedEntry] = []

        for result in results:
            if result.entry.id not in seen_ids:
                seen_ids.add(result.entry.id)
                deduplicated.append(result)

        return deduplicated

    def search_by_vector(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedEntry]:
        """
        仅向量搜索

        参数:
            query_embedding: 查询向量
            top_k: 返回数量
            filters: 过滤条件

        返回:
            List[RetrievedEntry]: 检索结果
        """
        if not self._vector_searcher:
            return []

        results = self._vector_searcher._store.search(query_embedding, top_k, filters)

        return [
            RetrievedEntry(
                entry=r.entry,
                vector_score=r.score,
                fulltext_score=0.0,
                combined_score=r.score,
                sources=["vector"],
                rank=r.rank,
            )
            for r in results
        ]

    def search_by_keyword(
        self,
        keyword: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedEntry]:
        """
        仅全文搜索

        参数:
            keyword: 关键词
            top_k: 返回数量
            filters: 过滤条件

        返回:
            List[RetrievedEntry]: 检索结果
        """
        if not self._fulltext_searcher:
            return []

        results = self._fulltext_searcher.search(keyword, top_k, filters)

        return [
            RetrievedEntry(
                entry=r.entry,
                vector_score=0.0,
                fulltext_score=r.score,
                combined_score=r.score,
                sources=["fulltext"],
                rank=r.rank,
            )
            for r in results
        ]

    @property
    def indexed_count(self) -> int:
        """索引的条目数量"""
        if self._vector_searcher:
            return self._vector_searcher.count
        return 0


def create_hybrid_retriever(
    vector_weight: float = 0.5,
    fusion_method: str = "weighted",
    enable_rerank: bool = True,
    enable_diversity: bool = True,
) -> HybridRetriever:
    """
    创建混合检索器

    参数:
        vector_weight: 向量搜索权重
        fusion_method: 融合方法
        enable_rerank: 是否启用重排序
        enable_diversity: 是否启用多样性优化

    返回:
        HybridRetriever: 混合检索器
    """
    return HybridRetriever(
        vector_weight=vector_weight,
        fusion_method=fusion_method,
        enable_rerank=enable_rerank,
        enable_diversity=enable_diversity,
    )


__all__ = [
    "HybridRetrieverError",
    "RetrievedEntry",
    "ScoreNormalizer",
    "ResultFusion",
    "ResultReranker",
    "DiversityOptimizer",
    "HybridRetriever",
    "create_hybrid_retriever",
]
