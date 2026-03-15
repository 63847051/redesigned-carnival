"""
重要性评分器模块

提供多维度的重要性评分算法，用于评估内容的重要性
"""

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .context_engine import ImportanceLevel, MemoryEntry, Message

logger = logging.getLogger(__name__)


class ScoringDimension(Enum):
    """评分维度"""

    EXPLICIT_KEYWORD = "explicit_keyword"  # 显式关键词
    IMPLICIT_INTENT = "implicit_intent"  # 隐含意图
    EMOTIONAL_SIGNAL = "emotional_signal"  # 情感信号
    TEMPORAL_CONTEXT = "temporal_context"  # 时间上下文
    ENTITY_REFERENCE = "entity_reference"  # 实体引用
    ACTIONABILITY = "actionability"  # 可操作性
    UNIQUENESS = "uniqueness"  # 唯一性
    REPETITION = "repetition"  # 重复度


@dataclass
class ScoringResult:
    """评分结果"""

    overall_score: float  # 综合评分 0-1
    dimension_scores: Dict[ScoringDimension, float]  # 各维度评分
    importance_level: ImportanceLevel  # 重要性级别
    reasons: List[str] = field(default_factory=list)  # 评分原因
    confidence: float = 1.0  # 置信度 0-1


def _default_dimension_weights() -> Dict[ScoringDimension, float]:
    return {
        ScoringDimension.EXPLICIT_KEYWORD: 0.25,
        ScoringDimension.IMPLICIT_INTENT: 0.20,
        ScoringDimension.EMOTIONAL_SIGNAL: 0.15,
        ScoringDimension.TEMPORAL_CONTEXT: 0.10,
        ScoringDimension.ENTITY_REFERENCE: 0.15,
        ScoringDimension.ACTIONABILITY: 0.10,
        ScoringDimension.UNIQUENESS: 0.025,
        ScoringDimension.REPETITION: 0.025,
    }


def _default_thresholds() -> Dict[ImportanceLevel, float]:
    return {
        ImportanceLevel.CRITICAL: 0.8,
        ImportanceLevel.HIGH: 0.6,
        ImportanceLevel.MEDIUM: 0.4,
        ImportanceLevel.LOW: 0.2,
        ImportanceLevel.MINIMAL: 0.0,
    }


@dataclass
class ScoringConfig:
    """评分配置"""

    dimension_weights: Dict[ScoringDimension, float] = field(
        default_factory=_default_dimension_weights
    )
    thresholds: Dict[ImportanceLevel, float] = field(
        default_factory=_default_thresholds
    )


class ImportanceScorer:
    """
    重要性评分器

    使用多维度评分算法评估内容重要性
    """

    CRITICAL_KEYWORDS: Set[str] = {
        "确认",
        "确认执行",
        "critical",
        "必须",
        "一定要",
        "记住",
        "不要忘记",
        "never forget",
        "always remember",
        "密码",
        "密钥",
        "api key",
        "token",
        "凭证",
        "紧急",
        "urgent",
        "立刻",
        "immediately",
    }

    HIGH_KEYWORDS: Set[str] = {
        "重要",
        "important",
        "偏好",
        "喜欢",
        "讨厌",
        "决定",
        "decision",
        "选择",
        "项目",
        "任务",
        "规则",
        "policy",
        "配置",
        "设置",
        "custom",
        "下次",
        "以后",
        "将来",
        "后续",
    }

    MEDIUM_KEYWORDS: Set[str] = {
        "关于",
        "关于我",
        "我的",
        "我是",
        "工作",
        "生活",
        "学习",
        "请问",
        "可以帮我",
        "能不能",
    }

    EMOTIONAL_SIGNALS: Set[str] = {
        "喜欢",
        "讨厌",
        "爱",
        "恨",
        "想要",
        "需要",
        "感谢",
        "谢谢",
        "抱歉",
        "对不起",
        "不好意思",
        "太好了",
        "太好了",
        "开心",
        "难过",
        "担心",
        "love",
        "hate",
        "like",
        "dislike",
        "want",
        "need",
        "thanks",
        "thank you",
        "sorry",
        "great",
        "awesome",
    }

    TEMPORAL_KEYWORDS: Set[str] = {
        "每次",
        "总是",
        "永远",
        "一直",
        "经常",
        "下次",
        "以后",
        "将来",
        "以后",
        "今天",
        "明天",
        "昨天",
        "上周",
        "下周",
        "always",
        "every",
        "never",
        "usually",
        "sometimes",
    }

    ACTION_VERBS: Set[str] = {
        "做",
        "执行",
        "运行",
        "创建",
        "删除",
        "修改",
        "更新",
        "发送",
        "处理",
        "管理",
        "调用",
        "do",
        "run",
        "execute",
        "create",
        "delete",
        "update",
        "send",
        "process",
        "manage",
        "call",
    }

    def __init__(self, config: Optional[ScoringConfig] = None):
        """
        初始化评分器

        参数:
            config: 评分配置
        """
        self._config = config or ScoringConfig()
        self._history: List[MemoryEntry] = []
        self._scored_cache: Dict[str, float] = {}
        logger.info("ImportanceScorer initialized")

    def update_history(self, entries: List[MemoryEntry]) -> None:
        """
        更新历史记忆用于重复度计算

        参数:
            entries: 记忆条目列表
        """
        self._history = entries
        self._scored_cache.clear()
        logger.debug(f"Updated history with {len(entries)} entries")

    def score_content(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> ScoringResult:
        """
        评分内容重要性

        参数:
            content: 待评分内容
            context: 额外上下文信息

        返回:
            ScoringResult: 评分结果
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for scoring")
            return ScoringResult(
                overall_score=0.0,
                dimension_scores={},
                importance_level=ImportanceLevel.MINIMAL,
                reasons=["Empty content"],
                confidence=0.0,
            )

        try:
            content_lower = content.lower()
            dimension_scores: Dict[ScoringDimension, float] = {}

            # 各维度评分
            dimension_scores[ScoringDimension.EXPLICIT_KEYWORD] = (
                self._score_explicit_keyword(content_lower)
            )
            dimension_scores[ScoringDimension.IMPLICIT_INTENT] = (
                self._score_implicit_intent(content, content_lower)
            )
            dimension_scores[ScoringDimension.EMOTIONAL_SIGNAL] = (
                self._score_emotional_signal(content_lower)
            )
            dimension_scores[ScoringDimension.TEMPORAL_CONTEXT] = (
                self._score_temporal_context(content_lower)
            )
            dimension_scores[ScoringDimension.ENTITY_REFERENCE] = (
                self._score_entity_reference(content, content_lower)
            )
            dimension_scores[ScoringDimension.ACTIONABILITY] = (
                self._score_actionability(content_lower)
            )
            dimension_scores[ScoringDimension.UNIQUENESS] = self._score_uniqueness(
                content
            )
            dimension_scores[ScoringDimension.REPETITION] = self._score_repetition(
                content, context
            )

            # 计算加权总分
            overall_score = self._calculate_weighted_score(dimension_scores)

            # 确定重要性级别
            importance_level = self._score_to_level(overall_score)

            # 生成评分原因
            reasons = self._generate_reasons(dimension_scores, content_lower)

            # 计算置信度
            confidence = self._calculate_confidence(dimension_scores)

            result = ScoringResult(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                importance_level=importance_level,
                reasons=reasons,
                confidence=confidence,
            )

            logger.debug(
                f"Scored content: overall={overall_score:.2f}, level={importance_level.name}"
            )
            return result

        except Exception as e:
            logger.error(f"Error scoring content: {e}")
            return ScoringResult(
                overall_score=0.3,
                dimension_scores={},
                importance_level=ImportanceLevel.MEDIUM,
                reasons=[f"Scoring error: {str(e)}"],
                confidence=0.0,
            )

    def _score_explicit_keyword(self, content: str) -> float:
        """评分显式关键词"""
        score = 0.0

        # 检查关键关键词
        for keyword in self.CRITICAL_KEYWORDS:
            if keyword in content:
                score = 1.0
                break

        if score == 0.0:
            for keyword in self.HIGH_KEYWORDS:
                if keyword in content:
                    score = 0.8
                    break

        if score == 0.0:
            for keyword in self.MEDIUM_KEYWORDS:
                if keyword in content:
                    score = 0.5
                    break

        return score

    def _score_implicit_intent(self, content: str, content_lower: str) -> float:
        """评分隐含意图"""
        score = 0.0

        # 记忆类意图
        if any(
            kw in content_lower
            for kw in ["记住", "记住这", "帮我记", "别忘了", "提醒我"]
        ):
            score = max(score, 0.9)

        # 偏好表达
        if any(
            kw in content_lower
            for kw in ["我喜欢", "我讨厌", "我想要", "我不想要", "偏好"]
        ):
            score = max(score, 0.8)

        # 决策/结论
        if any(kw in content_lower for kw in ["决定了", "选择", "就这个", "这样吧"]):
            score = max(score, 0.7)

        # 问题解决
        if any(kw in content_lower for kw in ["怎么", "如何", "怎么办", "帮帮我"]):
            score = max(score, 0.4)

        return score

    def _score_emotional_signal(self, content: str) -> float:
        """评分情感信号"""
        emotional_count = sum(
            1 for signal in self.EMOTIONAL_SIGNALS if signal in content
        )

        if emotional_count >= 3:
            return 0.9
        elif emotional_count == 2:
            return 0.7
        elif emotional_count == 1:
            return 0.5

        return 0.2

    def _score_temporal_context(self, content: str) -> float:
        """评分时间上下文"""
        if any(kw in content for kw in ["每次", "总是", "永远", "一直"]):
            return 0.9
        if any(kw in content for kw in ["经常", "时常", "常常"]):
            return 0.7
        if any(kw in content for kw in ["下次", "以后", "将来", "后续"]):
            return 0.6

        return 0.2

    def _score_entity_reference(self, content: str, content_lower: str) -> float:
        """评分实体引用"""
        score = 0.0

        # 专有名词（首字母大写的词）
        proper_nouns = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", content)
        if len(proper_nouns) >= 2:
            score = max(score, 0.7)

        # 代词/引用
        if any(
            pro in content_lower
            for pro in ["他", "她", "它", "你", "我", "我们", "这个", "那个"]
        ):
            score = max(score, 0.5)

        # 数字引用
        if re.search(r"\d+", content):
            score = max(score, 0.4)

        return score

    def _score_actionability(self, content: str) -> float:
        """评分可操作性"""
        action_count = sum(1 for verb in self.ACTION_VERBS if verb in content)

        if action_count >= 3:
            return 0.9
        elif action_count == 2:
            return 0.6
        elif action_count == 1:
            return 0.4

        return 0.2

    def _score_uniqueness(self, content: str) -> float:
        """评分唯一性"""
        if not self._history:
            return 0.5

        # 检查内容与历史记忆的相似度
        content_words = set(content.lower().split())

        max_similarity = 0.0
        for entry in self._history:
            entry_words = set(entry.content.lower().split())
            if entry_words:
                similarity = len(content_words & entry_words) / len(
                    content_words | entry_words
                )
                max_similarity = max(max_similarity, similarity)

        # 越不相似越重要
        return 1.0 - max_similarity

    def _score_repetition(
        self, content: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """评分重复度"""
        if not context:
            return 0.5

        # 检查是否是重复内容
        is_repeated = context.get("is_repeated", False)
        repeat_count = context.get("repeat_count", 0)

        if is_repeated or repeat_count > 2:
            return 0.1

        return 0.5

    def _calculate_weighted_score(
        self, dimension_scores: Dict[ScoringDimension, float]
    ) -> float:
        """计算加权总分"""
        weights = self._config.dimension_weights

        total_weight = 0.0
        weighted_sum = 0.0

        for dimension, score in dimension_scores.items():
            weight = weights.get(dimension, 0.0)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight

        return 0.0

    def _score_to_level(self, score: float) -> ImportanceLevel:
        """将分数转换为重要性级别"""
        thresholds = self._config.thresholds

        if score >= thresholds[ImportanceLevel.CRITICAL]:
            return ImportanceLevel.CRITICAL
        elif score >= thresholds[ImportanceLevel.HIGH]:
            return ImportanceLevel.HIGH
        elif score >= thresholds[ImportanceLevel.MEDIUM]:
            return ImportanceLevel.MEDIUM
        elif score >= thresholds[ImportanceLevel.LOW]:
            return ImportanceLevel.LOW

        return ImportanceLevel.MINIMAL

    def _generate_reasons(
        self, dimension_scores: Dict[ScoringDimension, float], content: str
    ) -> List[str]:
        """生成评分原因"""
        reasons = []

        if dimension_scores.get(ScoringDimension.EXPLICIT_KEYWORD, 0) >= 0.8:
            reasons.append("包含重要关键词")
        if dimension_scores.get(ScoringDimension.IMPLICIT_INTENT, 0) >= 0.7:
            reasons.append("包含明确的记忆或偏好表达")
        if dimension_scores.get(ScoringDimension.EMOTIONAL_SIGNAL, 0) >= 0.5:
            reasons.append("包含情感信号")
        if dimension_scores.get(ScoringDimension.TEMPORAL_CONTEXT, 0) >= 0.6:
            reasons.append("包含时间上下文")
        if dimension_scores.get(ScoringDimension.ACTIONABILITY, 0) >= 0.6:
            reasons.append("包含可执行的动作")
        if dimension_scores.get(ScoringDimension.UNIQUENESS, 0) >= 0.7:
            reasons.append("内容具有独特性")

        return reasons

    def _calculate_confidence(
        self, dimension_scores: Dict[ScoringDimension, float]
    ) -> float:
        """计算置信度"""
        # 维度得分分布越均匀，置信度越高
        if not dimension_scores:
            return 0.0

        scores = list(dimension_scores.values())
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)

        # 方差越小，置信度越高
        confidence = max(0.0, 1.0 - (variance**0.5))
        return confidence

    def score_message(self, message: Message) -> ScoringResult:
        """
        评分消息重要性

        参数:
            message: 消息对象

        返回:
            ScoringResult: 评分结果
        """
        context = {
            "role": message.role,
            "timestamp": message.timestamp,
            "metadata": message.metadata,
        }

        return self.score_content(message.content, context)

    def score_memory_entry(self, entry: MemoryEntry) -> ScoringResult:
        """
        评分记忆条目重要性

        参数:
            entry: 记忆条目

        返回:
            ScoringResult: 评分结果
        """
        context = {
            "access_count": entry.access_count,
            "created_at": entry.created_at,
            "tags": entry.tags,
        }

        return self.score_content(entry.content, context)


class BatchScorer:
    """
    批量评分器

    用于批量评估多个内容的重要性
    """

    def __init__(self, scorer: Optional[ImportanceScorer] = None):
        """
        初始化批量评分器

        参数:
            scorer: 重要性评分器实例
        """
        self._scorer = scorer or ImportanceScorer()
        logger.info("BatchScorer initialized")

    def score_contents(self, contents: List[str]) -> List[ScoringResult]:
        """
        批量评分内容

        参数:
            contents: 内容列表

        返回:
            List[ScoringResult]: 评分结果列表
        """
        results = []
        for content in contents:
            result = self._scorer.score_content(content)
            results.append(result)

        logger.debug(f"Batch scored {len(contents)} contents")
        return results

    def get_top_memories(
        self, entries: List[MemoryEntry], top_n: int = 10
    ) -> List[MemoryEntry]:
        """
        获取最重要的记忆条目

        参数:
            entries: 记忆条目列表
            top_n: 返回数量

        返回:
            List[MemoryEntry]: 排序后的记忆条目
        """
        scored = []
        for entry in entries:
            result = self._scorer.score_memory_entry(entry)
            scored.append((entry, result.overall_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in scored[:top_n]]

    def filter_by_threshold(
        self, entries: List[MemoryEntry], threshold: float
    ) -> List[MemoryEntry]:
        """
        按阈值过滤记忆条目

        参数:
            entries: 记忆条目列表
            threshold: 阈值

        返回:
            List[MemoryEntry]: 过滤后的记忆条目
        """
        filtered = []
        for entry in entries:
            result = self._scorer.score_memory_entry(entry)
            if result.overall_score >= threshold:
                filtered.append(entry)

        return filtered


# 导出
__all__ = [
    "ImportanceScorer",
    "BatchScorer",
    "ScoringResult",
    "ScoringConfig",
    "ScoringDimension",
]
