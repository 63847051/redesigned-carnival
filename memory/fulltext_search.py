"""
全文检索模块

提供基于关键词的全文搜索功能
支持布尔查询、TF-IDF 相关性评分和模糊匹配
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import Counter
import math

from .context_engine import MemoryEntry, MemoryType, ImportanceLevel

logger = logging.getLogger(__name__)


class FullTextSearchError(Exception):
    """全文检索基础异常"""

    pass


@dataclass
class FullTextResult:
    """全文检索结果"""

    entry: MemoryEntry
    score: float
    matched_terms: List[str]
    rank: int


class TFIDFIndex:
    """
    TF-IDF 索引

    构建文本的 TF-IDF 向量用于相关性排序
    """

    def __init__(self):
        """初始化 TF-IDF 索引"""
        self._documents: List[str] = []
        self._entries: List[MemoryEntry] = []
        self._term_doc_freq: Counter = Counter()
        self._doc_term_freq: List[Counter] = []
        self._num_docs = 0
        self._idf_cache: Dict[str, float] = {}

    def add_document(self, entry: MemoryEntry) -> None:
        """
        添加文档

        参数:
            entry: 记忆条目
        """
        text = self._preprocess(entry.content)
        tokens = text.split()

        self._documents.append(text)
        self._entries.append(entry)
        self._doc_term_freq.append(Counter(tokens))

        for token in set(tokens):
            self._term_doc_freq[token] += 1

        self._num_docs += 1
        self._idf_cache.clear()

    def add_documents(self, entries: List[MemoryEntry]) -> int:
        """
        批量添加文档

        参数:
            entries: 记忆条目列表

        返回:
            int: 添加的文档数量
        """
        for entry in entries:
            self.add_document(entry)
        return len(entries)

    def _preprocess(self, text: str) -> str:
        """文本预处理"""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _compute_idf(self, term: str) -> float:
        """计算 IDF"""
        if term in self._idf_cache:
            return self._idf_cache[term]

        if term not in self._term_doc_freq:
            return 0.0

        df = self._term_doc_freq[term]
        idf = math.log((self._num_docs + 1) / (df + 1)) + 1
        self._idf_cache[term] = idf
        return idf

    def get_tfidf_score(self, doc_idx: int, query_terms: List[str]) -> float:
        """
        计算查询的 TF-IDF 得分

        参数:
            doc_idx: 文档索引
            query_terms: 查询词列表

        返回:
            float: TF-IDF 得分
        """
        if doc_idx >= len(self._doc_term_freq):
            return 0.0

        doc_freq = self._doc_term_freq[doc_idx]
        score = 0.0

        for term in query_terms:
            tf = doc_freq.get(term, 0)
            idf = self._compute_idf(term)
            score += tf * idf

        return score

    def clear(self) -> None:
        """清空索引"""
        self._documents.clear()
        self._entries.clear()
        self._term_doc_freq.clear()
        self._doc_term_freq.clear()
        self._idf_cache.clear()
        self._num_docs = 0


class BooleanQueryParser:
    """
    布尔查询解析器

    支持 AND、OR、NOT 运算符
    """

    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    def __init__(self):
        """初始化解析器"""
        self._operator_pattern = re.compile(
            r"\b(AND|OR|NOT)\b",
            re.IGNORECASE,
        )

    def parse(self, query: str) -> Dict[str, Any]:
        """
        解析查询

        参数:
            query: 查询字符串

        返回:
            Dict: 解析后的查询结构
        """
        query = query.strip()

        if self._operator_pattern.search(query):
            return self._parse_boolean(query)

        return self._parse_simple(query)

    def _parse_simple(self, query: str) -> Dict[str, Any]:
        """解析简单查询"""
        terms = self._preprocess(query)
        return {
            "type": "simple",
            "terms": terms,
            "required": terms,
            "optional": [],
            "excluded": [],
        }

    def _parse_boolean(self, query: str) -> Dict[str, Any]:
        """解析布尔查询"""
        tokens = self._tokenize(query)

        required: List[str] = []
        optional: List[str] = []
        excluded: List[str] = []

        i = 0
        current_op = self.AND

        while i < len(tokens):
            token = tokens[i]

            if token.upper() in (self.AND, self.OR):
                current_op = token.upper()
                i += 1
                continue

            if token.upper() == self.NOT:
                if i + 1 < len(tokens):
                    excluded.append(tokens[i + 1])
                    i += 2
                continue

            if current_op == self.AND:
                required.append(token)
            elif current_op == self.OR:
                optional.append(token)

            i += 1

        return {
            "type": "boolean",
            "required": required,
            "optional": optional,
            "excluded": excluded,
        }

    def _tokenize(self, query: str) -> List[str]:
        """分词"""
        tokens = []
        current = []

        for char in query:
            if char.isspace():
                if current:
                    tokens.append("".join(current))
                    current = []
            elif char in "()":
                if current:
                    tokens.append("".join(current))
                    current = []
                tokens.append(char)
            else:
                current.append(char)

        if current:
            tokens.append("".join(current))

        return tokens

    def _preprocess(self, text: str) -> List[str]:
        """预处理"""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return text.split()


class FuzzyMatcher:
    """
    模糊匹配器

    基于编辑距离的模糊匹配
    """

    def __init__(self, max_distance: int = 2):
        """
        初始化模糊匹配器

        参数:
            max_distance: 最大编辑距离
        """
        self.max_distance = max_distance

    def is_fuzzy_match(self, term: str, text: str) -> bool:
        """
        检查是否有模糊匹配

        参数:
            term: 查询词
            text: 文本

        返回:
            bool: 是否有匹配
        """
        words = text.lower().split()

        for word in words:
            if self._edit_distance(term.lower(), word) <= self.max_distance:
                return True

        return False

    def _edit_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        prev = list(range(len(s2) + 1))

        for i, c1 in enumerate(s1):
            curr = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev[j + 1] + 1
                deletions = curr[j] + 1
                substitutions = prev[j] + (c1 != c2)
                curr.append(min(insertions, deletions, substitutions))
            prev = curr

        return prev[-1]


class FullTextSearcher:
    """
    全文搜索引擎

    整合布尔查询、TF-IDF 评分和模糊匹配
    """

    def __init__(
        self,
        enable_fuzzy: bool = True,
        fuzzy_max_distance: int = 2,
    ):
        """
        初始化全文搜索引擎

        参数:
            enable_fuzzy: 是否启用模糊匹配
            fuzzy_max_distance: 模糊匹配最大距离
        """
        self._index = TFIDFIndex()
        self._query_parser = BooleanQueryParser()
        self._fuzzy_matcher = FuzzyMatcher(fuzzy_max_distance) if enable_fuzzy else None

    def index_entries(self, entries: List[MemoryEntry]) -> int:
        """
        索引记忆条目

        参数:
            entries: 记忆条目列表

        返回:
            int: 索引的条目数量
        """
        count = self._index.add_documents(entries)
        logger.info(f"Indexed {count} entries for full-text search")
        return count

    def add_entry(self, entry: MemoryEntry) -> None:
        """添加单个条目"""
        self._index.add_document(entry)

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[FullTextResult]:
        """
        全文搜索

        参数:
            query: 查询字符串
            top_k: 返回结果数量
            filters: 过滤条件

        返回:
            List[FullTextResult]: 搜索结果
        """
        parsed = self._query_parser.parse(query)

        results: List[FullTextResult] = []

        for idx, entry in enumerate(self._index._entries):
            if filters and not self._matches_filters(entry, filters):
                continue

            matched, score, matched_terms = self._evaluate_match(entry, parsed, idx)

            if matched:
                results.append(
                    FullTextResult(
                        entry=entry,
                        score=score,
                        matched_terms=matched_terms,
                        rank=len(results) + 1,
                    )
                )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _evaluate_match(
        self,
        entry: MemoryEntry,
        parsed: Dict[str, Any],
        doc_idx: int,
    ) -> Tuple[bool, float, List[str]]:
        """评估文档匹配"""
        text = entry.content.lower()
        matched_terms: List[str] = []

        required = parsed.get("required", [])
        optional = parsed.get("optional", [])
        excluded = parsed.get("excluded", [])

        for term in excluded:
            if term.lower() in text:
                return False, 0.0, []

        all_terms = required + optional
        required_matches = 0

        for term in all_terms:
            term_lower = term.lower()

            if term_lower in text:
                matched_terms.append(term)
                required_matches += 1
            elif self._fuzzy_matcher:
                if self._fuzzy_matcher.is_fuzzy_match(term, entry.content):
                    matched_terms.append(term)
                    required_matches += 1

        if required and required_matches < len(required):
            return False, 0.0, []

        if required and required_matches == len(required):
            tfidf_score = self._index.get_tfidf_score(doc_idx, all_terms)
            bonus = 0.5 * len(matched_terms) / len(all_terms)
            score = tfidf_score + bonus
        else:
            tfidf_score = self._index.get_tfidf_score(doc_idx, matched_terms)
            score = tfidf_score * 0.8

        return True, score, matched_terms

    def _matches_filters(
        self,
        entry: MemoryEntry,
        filters: Dict[str, Any],
    ) -> bool:
        """检查过滤条件"""
        if "memory_type" in filters:
            if entry.memory_type != filters["memory_type"]:
                return False

        if "min_importance" in filters:
            if entry.importance.value < filters["min_importance"].value:
                return False

        if "tags" in filters:
            if not any(tag in entry.tags for tag in filters["tags"]):
                return False

        return True

    def delete_entry(self, entry_id: str) -> bool:
        """删除条目（需要重建索引）"""
        logger.warning("Full-text index does not support individual deletion")
        return False

    def rebuild_index(self, entries: List[MemoryEntry]) -> int:
        """
        重建索引

        参数:
            entries: 记忆条目列表

        返回:
            int: 索引的条目数量
        """
        self._index.clear()
        return self.index_entries(entries)

    @property
    def count(self) -> int:
        """索引的条目数量"""
        return self._index._num_docs


def create_fulltext_searcher(
    enable_fuzzy: bool = True,
    fuzzy_max_distance: int = 2,
) -> FullTextSearcher:
    """
    创建全文搜索引擎

    参数:
        enable_fuzzy: 是否启用模糊匹配
        fuzzy_max_distance: 模糊匹配最大距离

    返回:
        FullTextSearcher: 全文搜索引擎
    """
    return FullTextSearcher(
        enable_fuzzy=enable_fuzzy,
        fuzzy_max_distance=fuzzy_max_distance,
    )


__all__ = [
    "FullTextSearchError",
    "FullTextResult",
    "TFIDFIndex",
    "BooleanQueryParser",
    "FuzzyMatcher",
    "FullTextSearcher",
    "create_fulltext_searcher",
]
