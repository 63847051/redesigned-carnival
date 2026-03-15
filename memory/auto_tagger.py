"""
智能标签器模块

自动生成和管理记忆标签
"""

import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from .context_engine import ImportanceLevel, MemoryEntry, MemoryType

logger = logging.getLogger(__name__)


@dataclass
class TagInfo:
    """标签信息"""

    name: str
    count: int = 0
    weight: float = 1.0
    category: str = "general"
    related_tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class TagCluster:
    """标签聚类"""

    cluster_id: str
    name: str
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    memory_count: int = 0


@dataclass
class TagRecommendation:
    """标签推荐"""

    tags: List[str] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)
    reasons: Dict[str, str] = field(default_factory=dict)


def _default_category_keywords() -> Dict[str, List[str]]:
    return {
        "技术": [
            "代码",
            "开发",
            "技术",
            "编程",
            "api",
            "sdk",
            "技术栈",
            "tech",
            "code",
            "programming",
        ],
        "项目": ["项目", "project", "产品", "功能", "需求"],
        "规则": ["规则", "policy", "规范", "原则", "rule", "guideline"],
        "偏好": [
            "喜欢",
            "讨厌",
            "偏好",
            "爱",
            "不爱",
            "想要",
            "love",
            "hate",
            "like",
            "dislike",
            "prefer",
        ],
        "人物": [
            "人",
            "朋友",
            "家人",
            "同事",
            "老板",
            "friend",
            "family",
            "colleague",
            "team",
        ],
        "地点": [
            "地方",
            "位置",
            "城市",
            "国家",
            "office",
            "location",
            "city",
            "country",
        ],
        "时间": ["时间", "时候", "日期", "day", "time", "date", "when"],
        "任务": ["任务", "待办", "todo", "task", "要做", "完成"],
        "学习": ["学习", "学", "课程", "书籍", "learn", "study", "course", "book"],
        "生活": ["生活", "日常", "习惯", "life", "daily", "habit"],
        "工作": ["工作", "job", "公司", "职业", "career", "business"],
        "沟通": ["说", "告诉", "通知", "消息", "message", "tell", "notify", "say"],
    }


def _default_tags() -> Set[str]:
    return {
        "important",
        "preference",
        "rule",
        "task",
        "project",
        "identity",
        "relationship",
        "fact",
        "procedure",
        "decision",
        "work",
        "life",
        "learning",
        "technical",
        "personal",
    }


class TagVocabulary:
    """
    标签词汇表

    管理预定义的标签及其关系
    """

    CATEGORY_KEYWORDS: Dict[str, List[str]] = _default_category_keywords()
    DEFAULT_TAGS: Set[str] = _default_tags()

    def __init__(self):
        """初始化标签词汇表"""
        self._tags: Dict[str, TagInfo] = {}
        self._categories: Dict[str, List[str]] = defaultdict(list)

        # 初始化默认标签
        for tag in self.DEFAULT_TAGS:
            self._tags[tag] = TagInfo(name=tag, category="general")

        # 初始化分类
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                self._categories[keyword].append(category)

        logger.debug(f"TagVocabulary initialized with {len(self._tags)} default tags")

    def add_tag(self, tag: str, category: str = "general") -> None:
        """
        添加标签

        参数:
            tag: 标签名
            category: 分类
        """
        if tag not in self._tags:
            self._tags[tag] = TagInfo(name=tag, category=category)
            logger.debug(f"Added new tag: {tag} (category: {category})")

    def get_category(self, keyword: str) -> Optional[str]:
        """
        获取关键词对应的分类

        参数:
            keyword: 关键词

        Returns:
            Optional[str]: 分类名
        """
        for kw, category in self._categories.items():
            if kw in keyword.lower():
                return category[0] if category else None
        return None


class TagClusterer:
    """
    标签聚类器

    将相关标签聚类分组
    """

    def __init__(self, vocabulary: Optional[TagVocabulary] = None):
        """
        初始化标签聚类器

        参数:
            vocabulary: 标签词汇表
        """
        self._vocabulary = vocabulary or TagVocabulary()
        logger.debug("TagClusterer initialized")

    def cluster_tags(
        self, tags: List[str], memories: List[MemoryEntry]
    ) -> List[TagCluster]:
        """
        聚类标签

        参数:
            tags: 标签列表
            memories: 记忆条目列表

        Returns:
            List[TagCluster]: 标签聚类列表
        """
        # 基于标签共现构建聚类
        tag_cooccurrence: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for memory in memories:
            memory_tags = set(memory.tags)
            for tag1 in memory_tags:
                for tag2 in memory_tags:
                    if tag1 != tag2:
                        tag_cooccurrence[tag1][tag2] += 1

        # 构建聚类
        clusters: List[TagCluster] = []
        used_tags: Set[str] = set()

        # 优先聚类高频共现标签
        sorted_tags = sorted(
            tag_cooccurrence.items(),
            key=lambda x: sum(x[1].values()),
            reverse=True,
        )

        for tag, cotags in sorted_tags:
            if tag in used_tags:
                continue

            # 创建新聚类
            cluster_tags = [tag]
            related_keywords = []

            # 合并高度相关的标签
            for cotag, count in sorted(
                cotags.items(), key=lambda x: x[1], reverse=True
            ):
                if count >= 2 and len(cluster_tags) < 5:
                    cluster_tags.append(cotag)
                    used_tags.add(cotag)

            used_tags.add(tag)

            # 确定聚类名称
            cluster_name = self._get_cluster_name(cluster_tags)

            # 获取关键词
            for t in cluster_tags:
                category = self._vocabulary.get_category(t)
                if category:
                    related_keywords.append(category)

            cluster = TagCluster(
                cluster_id=f"cluster_{len(clusters)}",
                name=cluster_name,
                tags=cluster_tags,
                keywords=list(set(related_keywords)),
                memory_count=sum(
                    1 for m in memories if any(t in m.tags for t in cluster_tags)
                ),
            )
            clusters.append(cluster)

        # 添加未聚类的标签
        remaining_tags = [t for t in tags if t not in used_tags]
        if remaining_tags:
            clusters.append(
                TagCluster(
                    cluster_id="cluster_other",
                    name="其他",
                    tags=remaining_tags,
                    keywords=[],
                    memory_count=0,
                )
            )

        logger.debug(f"Created {len(clusters)} tag clusters")
        return clusters

    def _get_cluster_name(self, tags: List[str]) -> str:
        """获取聚类名称"""
        # 基于最常见的类别命名
        categories = []
        for tag in tags:
            category = self._vocabulary.get_category(tag)
            if category:
                categories.append(category)

        if categories:
            return Counter(categories).most_common(1)[0][0]

        return "综合"


class AutoTagger:
    """
    智能标签器

    自动生成和管理标签
    """

    def __init__(self, vocabulary: Optional[TagVocabulary] = None):
        """
        初始化智能标签器

        参数:
            vocabulary: 标签词汇表
        """
        self._vocabulary = vocabulary or TagVocabulary()
        self._clusterer = TagClusterer(self._vocabulary)
        self._tag_history: List[Dict[str, Any]] = []

        logger.info("AutoTagger initialized")

    def generate_tags(
        self,
        content: str,
        existing_tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TagRecommendation:
        """
        生成标签

        参数:
            content: 内容文本
            existing_tags: 已有标签
            metadata: 额外元数据

        Returns:
            TagRecommendation: 标签推荐
        """
        recommendation = TagRecommendation()

        try:
            content_lower = content.lower()
            existing_tags = existing_tags or []

            # 基于内容生成标签
            content_tags = self._extract_content_tags(content_lower)

            # 基于元数据生成标签
            metadata_tags = self._extract_metadata_tags(metadata or {})

            # 基于上下文生成标签
            context_tags = self._extract_context_tags(content, existing_tags)

            # 合并所有标签
            all_tags = set(content_tags + metadata_tags + context_tags)

            # 评分标签
            for tag in all_tags:
                score = 0.5
                reasons = []

                # 内容匹配得分
                if tag in content_tags:
                    score += 0.3
                    reasons.append("内容匹配")

                # 元数据得分
                if tag in metadata_tags:
                    score += 0.2
                    reasons.append("元数据匹配")

                # 上下文得分
                if tag in context_tags:
                    score += 0.1
                    reasons.append("上下文相关")

                # 已有标签权重
                if tag in existing_tags:
                    score += 0.2
                    reasons.append("已存在标签")

                recommendation.tags.append(tag)
                recommendation.scores[tag] = min(1.0, score)
                recommendation.reasons[tag] = "; ".join(reasons[:2])

            # 按分数排序
            recommendation.tags.sort(
                key=lambda t: recommendation.scores.get(t, 0), reverse=True
            )

            logger.debug(f"Generated {len(recommendation.tags)} tags for content")

        except Exception as e:
            logger.error(f"Error generating tags: {e}")

        return recommendation

    def _extract_content_tags(self, content: str) -> List[str]:
        """从内容中提取标签"""
        tags = []

        # 类别关键词匹配
        for category, keywords in self._vocabulary.CATEGORY_KEYWORDS.items():
            if any(kw in content for kw in keywords):
                tags.append(category)

        # 提取特殊模式
        # 项目标签
        if re.search(r"项目[:：]?\s*\S+", content):
            tags.append("project")

        # 任务标签
        if re.search(r"(待办|todo|task|任务)[:：]?\s*\S+", content):
            tags.append("task")

        # 规则标签
        if re.search(r"(规则|policy|规范)[:：]?", content):
            tags.append("rule")

        # 重要标签
        if any(
            kw in content for kw in ["重要", "关键", "记住", "important", "remember"]
        ):
            tags.append("important")

        # 偏好标签
        if any(
            kw in content for kw in ["喜欢", "讨厌", "偏好", "love", "hate", "prefer"]
        ):
            tags.append("preference")

        return list(set(tags))

    def _extract_metadata_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """从元数据中提取标签"""
        tags = []

        # 基于角色
        role = metadata.get("role")
        if role:
            role_tags = {
                "user": ["user-input"],
                "assistant": ["assistant-response"],
                "system": ["system"],
                "tool": ["tool-result"],
            }
            tags.extend(role_tags.get(role, []))

        # 基于记忆类型
        memory_type = metadata.get("memory_type")
        if memory_type:
            tags.append(
                memory_type.value if hasattr(memory_type, "value") else str(memory_type)
            )

        # 基于重要性
        importance = metadata.get("importance")
        if importance:
            if isinstance(importance, ImportanceLevel):
                if importance.value >= ImportanceLevel.HIGH.value:
                    tags.append("high-priority")
            elif isinstance(importance, (int, float)):
                if importance >= 0.7:
                    tags.append("high-priority")

        return tags

    def _extract_context_tags(
        self, content: str, existing_tags: List[str]
    ) -> List[str]:
        """从上下文提取标签"""
        tags = []

        # 基于历史标签
        recent_tags = [h.get("tags", []) for h in self._tag_history[-5:]]
        tag_counter = Counter([t for tags in recent_tags for t in tags])

        # 添加高频标签
        for tag, count in tag_counter.most_common(3):
            if count >= 2 and tag not in existing_tags:
                tags.append(tag)

        return tags

    def recommend_similar_tags(
        self, tag: str, memories: List[MemoryEntry], top_n: int = 5
    ) -> List[str]:
        """
        推荐相似标签

        参数:
            tag: 目标标签
            memories: 记忆条目列表
            top_n: 返回数量

        Returns:
            List[str]: 相似标签列表
        """
        # 找到使用该标签的记忆
        related_memories = [m for m in memories if tag in m.tags]

        if not related_memories:
            return []

        # 统计相关标签
        tag_counter = Counter()
        for memory in related_memories:
            for t in memory.tags:
                if t != tag:
                    tag_counter[t] += 1

        # 返回最相关的标签
        return [t for t, _ in tag_counter.most_common(top_n)]

    def get_tag_clusters(self, memories: List[MemoryEntry]) -> List[TagCluster]:
        """
        获取标签聚类

        参数:
            memories: 记忆条目列表

        Returns:
            List[TagCluster]: 标签聚类列表
        """
        # 收集所有标签
        all_tags = set()
        for memory in memories:
            all_tags.update(memory.tags)

        return self._clusterer.cluster_tags(list(all_tags), memories)

    def update_tag_usage(
        self, tags: List[str], metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        更新标签使用记录

        参数:
            tags: 标签列表
            metadata: 元数据
        """
        self._tag_history.append(
            {
                "tags": tags,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
            }
        )

        # 保持历史记录有限长度
        if len(self._tag_history) > 100:
            self._tag_history = self._tag_history[-100:]


class TagManager:
    """
    标签管理器

    管理和维护标签系统
    """

    def __init__(self, tagger: Optional[AutoTagger] = None):
        """
        初始化标签管理器

        参数:
            tagger: 智能标签器
        """
        self._tagger = tagger or AutoTagger()
        self._vocabulary = self._tagger._vocabulary
        logger.info("TagManager initialized")

    def process_memory(self, memory: MemoryEntry) -> List[str]:
        """
        处理记忆条目，生成最终标签

        参数:
            memory: 记忆条目

        Returns:
            List[str]: 最终标签列表
        """
        # 生成标签推荐
        recommendation = self._tagger.generate_tags(
            content=memory.content,
            existing_tags=memory.tags,
            metadata={
                "memory_type": memory.memory_type,
                "importance": memory.importance,
                "access_count": memory.access_count,
            },
        )

        # 合并已有标签
        final_tags = list(set(memory.tags + recommendation.tags[:5]))

        # 更新使用记录
        self._tagger.update_tag_usage(
            final_tags,
            {
                "memory_id": memory.id,
                "importance": memory.importance.value,
            },
        )

        return final_tags

    def suggest_tags_for_memories(
        self, memories: List[MemoryEntry], top_n: int = 3
    ) -> Dict[str, List[str]]:
        """
        为记忆列表建议标签

        参数:
            memories: 记忆列表
            top_n: 每个记忆的建议标签数

        Returns:
            Dict[str, List[str]]: 记忆ID到标签列表的映射
        """
        suggestions = {}

        for memory in memories:
            recommendation = self._tagger.generate_tags(
                memory.content,
                memory.tags,
                {"importance": memory.importance},
            )
            suggestions[memory.id] = recommendation.tags[:top_n]

        return suggestions


# 导出
__all__ = [
    "AutoTagger",
    "TagManager",
    "TagClusterer",
    "TagVocabulary",
    "TagInfo",
    "TagCluster",
    "TagRecommendation",
]
