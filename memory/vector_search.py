"""
向量搜索模块

提供基于 sentence-transformers 的文本向量化功能
支持余弦相似度计算和批量向量化
可选集成 FAISS 本地向量存储
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .context_engine import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)


class VectorSearchError(Exception):
    """向量搜索基础异常"""

    pass


class ModelLoadError(VectorSearchError):
    """模型加载异常"""

    pass


class VectorStoreError(VectorSearchError):
    """向量存储异常"""

    pass


@dataclass
class SearchResult:
    """搜索结果"""

    entry: MemoryEntry
    score: float
    rank: int


class EmbeddingModel:
    """
    文本向量化模型

    使用 sentence-transformers 生成文本向量
    支持批量处理和缓存
    """

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ):
        """
        初始化向量化模型

        参数:
            model_name: 模型名称，默认为 all-MiniLM-L6-v2
            device: 计算设备，优先使用 GPU
            cache_dir: 模型缓存目录
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.device = device or self._get_default_device()
        self.cache_dir = cache_dir or self._get_default_cache_dir()
        self._model = None
        self._embedding_dim: Optional[int] = None

    def _get_default_device(self) -> str:
        """获取默认设备"""
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def _get_default_cache_dir(self) -> str:
        """获取默认缓存目录"""
        cache_home = os.path.expanduser("~/.cache")
        return os.path.join(cache_home, "sentence-transformers")

    @property
    def embedding_dim(self) -> int:
        """获取向量维度"""
        if self._embedding_dim is None:
            self._load_model()
        return self._embedding_dim

    def _load_model(self) -> None:
        """加载模型"""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=self.cache_dir,
            )
            self._embedding_dim = self._model.get_sentence_embedding_dimension()
            logger.info(
                f"Embedding model loaded: {self.model_name}, "
                f"device={self.device}, dim={self._embedding_dim}"
            )
        except ImportError:
            logger.warning(
                "sentence-transformers not installed, "
                "falling back to TF-IDF vectorization"
            )
            self._model = None
        except Exception as e:
            raise ModelLoadError(f"Failed to load model {self.model_name}: {e}")

    def encode(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        将文本编码为向量

        参数:
            texts: 文本列表
            batch_size: 批量大小
            normalize: 是否归一化向量
            show_progress: 是否显示进度

        返回:
            np.ndarray: 向量数组，形状为 (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])

        self._load_model()

        if self._model is None:
            return self._tfidf_encode(texts)

        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )

        return embeddings

    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        编码单个文本

        参数:
            text: 文本
            normalize: 是否归一化

        返回:
            np.ndarray: 向量
        """
        return self.encode([text], normalize=normalize)[0]

    def _tfidf_encode(self, texts: List[str]) -> np.ndarray:
        """
        TF-IDF 回退实现

        当 sentence-transformers 不可用时使用
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            vectorizer = TfidfVectorizer(
                max_features=384,
                ngram_range=(1, 2),
                stop_words="english",
            )
            embeddings = vectorizer.fit_transform(texts).toarray()
            return embeddings
        except ImportError:
            logger.error("Neither sentence-transformers nor sklearn available")
            raise ModelLoadError("No vectorization library available")


class InMemoryVectorStore:
    """
    内存向量存储

    轻量级向量存储实现，支持基本的增删改查
    """

    def __init__(self, embedding_dim: int = 384):
        """
        初始化向量存储

        参数:
            embedding_dim: 向量维度
        """
        self.embedding_dim = embedding_dim
        self._vectors: List[np.ndarray] = []
        self._entries: List[MemoryEntry] = []
        self._entry_id_to_idx: Dict[str, int] = {}

    def add(self, entry: MemoryEntry, embedding: np.ndarray) -> None:
        """
        添加向量

        参数:
            entry: 记忆条目
            embedding: 对应的向量
        """
        if embedding.shape[0] != self.embedding_dim:
            raise VectorStoreError(
                f"Embedding dimension mismatch: "
                f"expected {self.embedding_dim}, got {embedding.shape[0]}"
            )

        idx = len(self._vectors)
        self._vectors.append(embedding)
        self._entries.append(entry)
        self._entry_id_to_idx[entry.id] = idx

    def add_batch(
        self,
        entries: List[MemoryEntry],
        embeddings: np.ndarray,
    ) -> None:
        """
        批量添加向量

        参数:
            entries: 记忆条目列表
            embeddings: 对应的向量数组
        """
        if len(entries) != embeddings.shape[0]:
            raise VectorStoreError("Entries and embeddings count mismatch")

        for entry, embedding in zip(entries, embeddings):
            self.add(entry, embedding)

    def get(self, entry_id: str) -> Optional[Tuple[MemoryEntry, np.ndarray]]:
        """
        获取向量

        参数:
            entry_id: 条目 ID

        返回:
            Optional[Tuple[MemoryEntry, np.ndarray]]: (条目, 向量)
        """
        idx = self._entry_id_to_idx.get(entry_id)
        if idx is None:
            return None
        return self._entries[idx], self._vectors[idx]

    def delete(self, entry_id: str) -> bool:
        """
        删除向量

        参数:
            entry_id: 条目 ID

        返回:
            bool: 是否成功
        """
        idx = self._entry_id_to_idx.get(entry_id)
        if idx is None:
            return False

        del self._vectors[idx]
        del self._entries[idx]

        del self._entry_id_to_idx[entry_id]
        for id_, i in list(self._entry_id_to_idx.items()):
            if i > idx:
                self._entry_id_to_idx[id_] = i - 1

        return True

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        搜索向量

        参数:
            query_embedding: 查询向量
            top_k: 返回结果数量
            filters: 过滤条件

        返回:
            List[SearchResult]: 搜索结果列表
        """
        if not self._vectors:
            return []

        query_embedding = query_embedding.reshape(1, -1)
        all_embeddings = np.vstack(self._vectors)

        similarities = cosine_similarity(query_embedding, all_embeddings)[0]

        results = []
        for idx, sim in enumerate(similarities):
            entry = self._entries[idx]

            if filters:
                if not self._matches_filters(entry, filters):
                    continue

            results.append(
                SearchResult(
                    entry=entry,
                    score=float(sim),
                    rank=len(results) + 1,
                )
            )

            if len(results) >= top_k:
                break

        return results

    def _matches_filters(self, entry: MemoryEntry, filters: Dict[str, Any]) -> bool:
        """检查条目是否匹配过滤条件"""
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

    def __len__(self) -> int:
        return len(self._vectors)

    def clear(self) -> None:
        """清空存储"""
        self._vectors.clear()
        self._entries.clear()
        self._entry_id_to_idx.clear()


class FAISSVectorStore:
    """
    FAISS 向量存储

    使用 Facebook AI Similarity Search 进行高效的向量检索
    需要安装 faiss-cpu 或 faiss-gpu
    """

    def __init__(self, embedding_dim: int = 384, metric: str = "l2"):
        """
        初始化 FAISS 存储

        参数:
            embedding_dim: 向量维度
            metric: 距离度量，l2 或 ip (内积/余弦)
        """
        self.embedding_dim = embedding_dim
        self.metric = metric
        self._index = None
        self._entries: List[MemoryEntry] = []
        self._entry_id_to_idx: Dict[str, int] = {}
        self._init_index()

    def _init_index(self) -> None:
        """初始化 FAISS 索引"""
        try:
            import faiss

            if self.metric == "l2":
                self._index = faiss.IndexFlatL2(self.embedding_dim)
            else:
                self._index = faiss.IndexFlatIP(self.embedding_dim)

            logger.info(
                f"FAISS index initialized: dim={self.embedding_dim}, "
                f"metric={self.metric}"
            )
        except ImportError:
            logger.warning("faiss not installed, using InMemoryVectorStore")
            raise VectorStoreError("FAISS not available")

    def add(self, entry: MemoryEntry, embedding: np.ndarray) -> None:
        """添加向量"""
        embedding = embedding.reshape(1, -1).astype("float32")

        if self.metric == "ip":
            faiss.normalize_L2(embedding)

        self._index.add(embedding)
        self._entries.append(entry)
        self._entry_id_to_idx[entry.id] = len(self._entries) - 1

    def add_batch(self, entries: List[MemoryEntry], embeddings: np.ndarray) -> None:
        """批量添加"""
        embeddings = embeddings.astype("float32")

        if self.metric == "ip":
            faiss.normalize_L2(embeddings)

        self._index.add(embeddings)

        for entry in entries:
            self._entries.append(entry)
            self._entry_id_to_idx[entry.id] = len(self._entries) - 1

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """搜索"""
        if self._index.ntotal == 0:
            return []

        query = query_embedding.reshape(1, -1).astype("float32")

        if self.metric == "ip":
            faiss.normalize_L2(query)

        distances, indices = self._index.search(
            query, min(top_k * 2, self._index.ntotal)
        )

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0:
                continue

            entry = self._entries[idx]

            if filters:
                if not self._matches_filters(entry, filters):
                    continue

            if self.metric == "l2":
                score = 1.0 / (1.0 + dist)
            else:
                score = float(dist)

            results.append(
                SearchResult(
                    entry=entry,
                    score=score,
                    rank=len(results) + 1,
                )
            )

            if len(results) >= top_k:
                break

        return results

    def _matches_filters(self, entry: MemoryEntry, filters: Dict[str, Any]) -> bool:
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

    def __len__(self) -> int:
        return self._index.ntotal if self._index else 0


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    计算余弦相似度

    参数:
        a: 向量 a，形状为 (n, d)
        b: 向量 b，形状为 (m, d)

    返回:
        np.ndarray: 相似度矩阵，形状为 (n, m)
    """
    a = a / np.linalg.norm(a, axis=1, keepdims=True)
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(a, b.T)


class VectorSearcher:
    """
    向量搜索引擎

    整合向量化模型和向量存储
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        use_faiss: bool = False,
        embedding_dim: int = 384,
    ):
        """
        初始化向量搜索引擎

        参数:
            model_name: 向量化模型名称
            use_faiss: 是否使用 FAISS
            embedding_dim: 向量维度
        """
        self._model = EmbeddingModel(model_name)
        self._embedding_dim = embedding_dim

        if use_faiss:
            try:
                self._store = FAISSVectorStore(embedding_dim)
                logger.info("Using FAISS vector store")
            except VectorStoreError:
                self._store = InMemoryVectorStore(embedding_dim)
                logger.info("Falling back to in-memory store")
        else:
            self._store = InMemoryVectorStore(embedding_dim)
            logger.info("Using in-memory vector store")

    def index_entries(self, entries: List[MemoryEntry]) -> int:
        """
        索引记忆条目

        参数:
            entries: 记忆条目列表

        返回:
            int: 索引的条目数量
        """
        if not entries:
            return 0

        texts = [entry.content for entry in entries]
        embeddings = self._model.encode(texts)

        self._store.add_batch(entries, embeddings)

        logger.info(f"Indexed {len(entries)} entries")
        return len(entries)

    def add_entry(self, entry: MemoryEntry) -> None:
        """添加单个条目"""
        embedding = self._model.encode_single(entry.content)
        self._store.add(entry, embedding)

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        向量搜索

        参数:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件

        返回:
            List[SearchResult]: 搜索结果
        """
        query_embedding = self._model.encode_single(query)
        return self._store.search(query_embedding, top_k, filters)

    def delete_entry(self, entry_id: str) -> bool:
        """删除条目"""
        return self._store.delete(entry_id)

    @property
    def count(self) -> int:
        """索引的条目数量"""
        return len(self._store)


def create_vector_searcher(
    model_name: Optional[str] = None,
    use_faiss: bool = False,
) -> VectorSearcher:
    """
    创建向量搜索引擎

    参数:
        model_name: 向量化模型名称
        use_faiss: 是否使用 FAISS

    返回:
        VectorSearcher: 向量搜索引擎
    """
    return VectorSearcher(model_name=model_name, use_faiss=use_faiss)


__all__ = [
    "VectorSearchError",
    "ModelLoadError",
    "VectorStoreError",
    "SearchResult",
    "EmbeddingModel",
    "InMemoryVectorStore",
    "FAISSVectorStore",
    "VectorSearcher",
    "cosine_similarity",
    "create_vector_searcher",
]
