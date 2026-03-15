"""
自动提取器模块

自动从内容中识别和提取重要信息
"""

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .context_engine import ImportanceLevel, MemoryEntry, MemoryType, Message
from .importance_scorer import ImportanceScorer, ScoringResult

logger = logging.getLogger(__name__)


class ExtractionType(Enum):
    """提取类型"""

    PREFERENCE = "preference"  # 偏好
    FACT = "fact"  # 事实
    RULE = "rule"  # 规则
    TASK = "task"  # 任务
    RELATIONSHIP = "relationship"  # 关系
    PROCEDURE = "procedure"  # 流程
    IDENTITY = "identity"  # 身份
    PROJECT = "project"  # 项目
    DECISION = "decision"  # 决策


@dataclass
class ExtractedInfo:
    """提取的信息"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ExtractionType = ExtractionType.FACT
    content: str = ""
    summary: str = ""
    entities: List[str] = field(default_factory=list)
    relations: List[Dict[str, str]] = field(default_factory=list)
    importance: float = 0.0
    confidence: float = 0.0
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """提取结果"""

    info_list: List[ExtractedInfo] = field(default_factory=list)
    memory_entries: List[MemoryEntry] = field(default_factory=list)
    total_extracted: int = 0
    high_priority_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class EntityExtractor:
    """
    实体提取器

    从文本中提取实体信息
    """

    ENTITY_PATTERNS: Dict[str, re.Pattern] = {
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "phone": re.compile(r"\b\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"),
        "url": re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),
        "date": re.compile(r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?"),
        "time": re.compile(r"\d{1,2}:\d{2}(?::\d{2})?"),
        "number": re.compile(r"\b\d+(?:\.\d+)?(?:[万kK百万B])?\b"),
    }

    def __init__(self):
        """初始化实体提取器"""
        logger.debug("EntityExtractor initialized")

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        提取实体

        参数:
            text: 文本内容

        返回:
            Dict[str, List[str]]: 实体类型到实体列表的映射
        """
        entities: Dict[str, List[str]] = {}

        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                entities[entity_type] = matches

        # 提取人名（简单模式）
        person_pattern = re.compile(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)")
        persons = person_pattern.findall(text)
        if persons:
            entities["person"] = persons

        return entities


class InfoClassifier:
    """
    信息分类器

    将内容分类到不同的信息类型
    """

    CLASSIFICATION_RULES: Dict[ExtractionType, Dict[str, Any]] = {
        ExtractionType.PREFERENCE: {
            "keywords": [
                "喜欢",
                "讨厌",
                "偏好",
                "想要",
                "不爱",
                "最爱",
                "不喜欢",
                "love",
                "hate",
                "like",
                "dislike",
                "prefer",
            ],
            "patterns": [r"我(喜欢|讨厌|想要|不爱).+", r"(最|特别|非常)(喜欢|讨厌)"],
            "weight": 0.9,
        },
        ExtractionType.RULE: {
            "keywords": [
                "规则",
                "规范",
                "必须",
                "不要",
                "禁止",
                "policy",
                "rule",
                "must",
                "never",
            ],
            "patterns": [r"(一定|必须|要)做到", r"不要.*", r"(永远|永远不要)"],
            "weight": 0.95,
        },
        ExtractionType.TASK: {
            "keywords": ["任务", "待办", "要做", "完成", "task", "todo", "to-do"],
            "patterns": [r"(帮我|请|要)(.+)(完成|做|处理)"],
            "weight": 0.8,
        },
        ExtractionType.PROJECT: {
            "keywords": ["项目", "project", "开发", "开发中", "进行中"],
            "patterns": [r"项目[:：].+", r"在(做|开发|进行).+项目"],
            "weight": 0.75,
        },
        ExtractionType.IDENTITY: {
            "keywords": ["我是", "我叫", "我的名字", "I am", "my name is"],
            "patterns": [r"我(叫|是|名字叫).+", r"我是(.+)"],
            "weight": 0.85,
        },
        ExtractionType.DECISION: {
            "keywords": ["决定", "选择", "就这", "这样吧", "decision", "choose", "选"],
            "patterns": [r"(决定|选择).+(就|用|这个)", r"那就这么定了"],
            "weight": 0.8,
        },
        ExtractionType.RELATIONSHIP: {
            "keywords": [
                "朋友",
                "家人",
                "同事",
                "老婆",
                "老公",
                "爸爸",
                "妈妈",
                "friend",
                "family",
                "colleague",
            ],
            "patterns": [r"我的.+是.+", r"(.+)是(.+)的(.+)"],
            "weight": 0.7,
        },
        ExtractionType.PROCEDURE: {
            "keywords": [
                "步骤",
                "流程",
                "先",
                "然后",
                "最后",
                "首先",
                "step",
                "process",
                "first",
                "then",
            ],
            "patterns": [r"(\d+)(\.|、)(.+)"],
            "weight": 0.6,
        },
    }

    def __init__(self):
        """初始化信息分类器"""
        logger.debug("InfoClassifier initialized")

    def classify(self, content: str) -> Tuple[ExtractionType, float, List[str]]:
        """
        分类内容

        参数:
            content: 内容文本

        返回:
            Tuple[ExtractionType, float, List[str]]: 类型, 置信度, 匹配原因
        """
        content_lower = content.lower()
        best_type = ExtractionType.FACT
        best_confidence = 0.0
        matched_reasons = []

        for ex_type, rules in self.CLASSIFICATION_RULES.items():
            confidence = 0.0
            reasons = []

            # 检查关键词
            for keyword in rules["keywords"]:
                if keyword in content_lower:
                    confidence = max(confidence, 0.6)
                    reasons.append(f"keyword:{keyword}")

            # 检查模式
            for pattern in rules.get("patterns", []):
                if re.search(pattern, content, re.IGNORECASE):
                    confidence = max(confidence, 0.8)
                    reasons.append(f"pattern:{pattern}")

            # 考虑权重
            if confidence > 0:
                confidence = confidence * rules.get("weight", 1.0)

            if confidence > best_confidence:
                best_confidence = confidence
                best_type = ex_type
                matched_reasons = reasons

        return best_type, best_confidence, matched_reasons


class SummaryExtractor:
    """
    摘要提取器

    从长内容中提取关键摘要
    """

    def __init__(self, max_summary_length: int = 200):
        """
        初始化摘要提取器

        参数:
            max_summary_length: 最大摘要长度
        """
        self._max_summary_length = max_summary_length
        logger.debug(
            f"SummaryExtractor initialized with max_length={max_summary_length}"
        )

    def extract_summary(self, content: str) -> str:
        """
        提取摘要

        参数:
            content: 内容文本

        返回:
            str: 摘要文本
        """
        if len(content) <= self._max_summary_length:
            return content

        # 提取关键句子
        sentences = re.split(r"[。！？\n]", content)
        important_sentences = []

        # 选择包含关键词的句子
        priority_keywords = [
            "重要",
            "记住",
            "偏好",
            "决定",
            "规则",
            "喜欢",
            "讨厌",
            "project",
            "task",
        ]

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if any(kw in sentence.lower() for kw in priority_keywords):
                important_sentences.append(sentence)
            elif len(important_sentences) < 2:
                important_sentences.append(sentence)

        # 组合摘要
        summary = "。".join(important_sentences[:3])

        if len(summary) > self._max_summary_length:
            summary = summary[: self._max_summary_length] + "..."

        return summary


class AutoExtractor:
    """
    自动提取器

    自动从消息和对话中提取重要信息
    """

    def __init__(
        self,
        scorer: Optional[ImportanceScorer] = None,
        min_importance: float = 0.3,
    ):
        """
        初始化自动提取器

        参数:
            scorer: 重要性评分器
            min_importance: 最小重要性阈值
        """
        self._scorer = scorer or ImportanceScorer()
        self._entity_extractor = EntityExtractor()
        self._classifier = InfoClassifier()
        self._summary_extractor = SummaryExtractor()
        self._min_importance = min_importance

        logger.info(f"AutoExtractor initialized with min_importance={min_importance}")

    def extract_from_message(self, message: Message) -> ExtractionResult:
        """
        从消息中提取信息

        参数:
            message: 消息对象

        Returns:
            ExtractionResult: 提取结果
        """
        result = ExtractionResult()

        try:
            # 评分内容重要性
            scoring_result = self._scorer.score_message(message)

            # 如果低于阈值，跳过
            if scoring_result.overall_score < self._min_importance:
                logger.debug(
                    f"Content below importance threshold: {scoring_result.overall_score}"
                )
                return result

            # 提取实体
            entities = self._entity_extractor.extract_entities(message.content)

            # 分类信息类型
            ex_type, confidence, reasons = self._classifier.classify(message.content)

            # 提取摘要
            summary = self._summary_extractor.extract_summary(message.content)

            # 创建提取的信息
            extracted = ExtractedInfo(
                type=ex_type,
                content=message.content,
                summary=summary,
                entities=[e for entity_list in entities.values() for e in entity_list],
                importance=scoring_result.overall_score,
                confidence=confidence,
                source=message.id or "",
                metadata={
                    "role": message.role,
                    "timestamp": message.timestamp.isoformat(),
                    "scoring_reasons": scoring_result.reasons,
                    "entities": entities,
                },
            )

            result.info_list.append(extracted)
            result.total_extracted = 1

            if scoring_result.importance_level.value >= ImportanceLevel.HIGH.value:
                result.high_priority_count = 1

            # 转换为记忆条目
            memory_entry = self._create_memory_entry(extracted, scoring_result)
            result.memory_entries.append(memory_entry)

            logger.debug(
                f"Extracted info: type={ex_type.value}, importance={scoring_result.overall_score:.2f}"
            )

        except Exception as e:
            logger.error(f"Error extracting from message: {e}")

        return result

    def extract_from_content(
        self,
        content: str,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """
        从内容中提取信息

        参数:
            content: 内容文本
            source: 来源标识
            metadata: 额外元数据

        Returns:
            ExtractionResult: 提取结果
        """
        result = ExtractionResult()

        try:
            # 评分
            scoring_result = self._scorer.score_content(content, metadata or {})

            if scoring_result.overall_score < self._min_importance:
                return result

            # 提取实体
            entities = self._entity_extractor.extract_entities(content)

            # 分类
            ex_type, confidence, _ = self._classifier.classify(content)

            # 摘要
            summary = self._summary_extractor.extract_summary(content)

            # 提取的信息
            extracted = ExtractedInfo(
                type=ex_type,
                content=content,
                summary=summary,
                entities=[e for entity_list in entities.values() for e in entity_list],
                importance=scoring_result.overall_score,
                confidence=confidence,
                source=source or "",
                metadata=metadata or {},
            )

            result.info_list.append(extracted)
            result.total_extracted = 1

            if scoring_result.importance_level.value >= ImportanceLevel.HIGH.value:
                result.high_priority_count = 1

            # 转换为记忆条目
            memory_entry = self._create_memory_entry(extracted, scoring_result)
            result.memory_entries.append(memory_entry)

        except Exception as e:
            logger.error(f"Error extracting from content: {e}")

        return result

    def extract_batch(
        self, contents: List[str], sources: Optional[List[str]] = None
    ) -> ExtractionResult:
        """
        批量提取信息

        参数:
            contents: 内容列表
            sources: 来源列表

        Returns:
            ExtractionResult: 合并的提取结果
        """
        result = ExtractionResult()

        for i, content in enumerate(contents):
            source = sources[i] if sources and i < len(sources) else None
            batch_result = self._extract_from_text(content, source)

            result.info_list.extend(batch_result.info_list)
            result.memory_entries.extend(batch_result.memory_entries)
            result.total_extracted += batch_result.total_extracted
            result.high_priority_count += batch_result.high_priority_count

        logger.info(
            f"Batch extracted {result.total_extracted} items from {len(contents)} contents"
        )
        return result

    def _extract_from_text(
        self, content: str, source: Optional[str] = None
    ) -> ExtractionResult:
        """内部方法：从文本提取"""
        metadata = {"source": source} if source else {}
        return self.extract_from_content(content, source, metadata)

    def _create_memory_entry(
        self, extracted: ExtractedInfo, scoring_result: ScoringResult
    ) -> MemoryEntry:
        """创建记忆条目"""
        memory_type = self._infer_memory_type(extracted.type)

        return MemoryEntry(
            id=extracted.id,
            content=extracted.content,
            memory_type=memory_type,
            importance=scoring_result.importance_level,
            tags=self._generate_tags(extracted),
            source_turn_id=extracted.source,
            metadata={
                "summary": extracted.summary,
                "entities": extracted.entities,
                "extraction_type": extracted.type.value,
                "confidence": extracted.confidence,
            },
        )

    def _infer_memory_type(self, ex_type: ExtractionType) -> MemoryType:
        """推断记忆类型"""
        type_mapping = {
            ExtractionType.PROCEDURE: MemoryType.PROCEDURAL,
            ExtractionType.RULE: MemoryType.LONG_TERM,
            ExtractionType.IDENTITY: MemoryType.LONG_TERM,
            ExtractionType.PREFERENCE: MemoryType.LONG_TERM,
            ExtractionType.PROJECT: MemoryType.LONG_TERM,
            ExtractionType.TASK: MemoryType.SHORT_TERM,
            ExtractionType.DECISION: MemoryType.LONG_TERM,
            ExtractionType.RELATIONSHIP: MemoryType.LONG_TERM,
            ExtractionType.FACT: MemoryType.SHORT_TERM,
        }
        return type_mapping.get(ex_type, MemoryType.SHORT_TERM)

    def _generate_tags(self, extracted: ExtractedInfo) -> List[str]:
        """生成标签"""
        tags = [extracted.type.value]

        # 添加实体类型标签
        for entity_type in extracted.metadata.get("entities", {}).keys():
            tags.append(f"entity:{entity_type}")

        # 基于内容添加标签
        content_lower = extracted.content.lower()
        if any(kw in content_lower for kw in ["项目", "project"]):
            tags.append("project")
        if any(kw in content_lower for kw in ["任务", "todo", "task"]):
            tags.append("task")
        if any(kw in content_lower for kw in ["规则", "rule", "规范"]):
            tags.append("rule")

        return list(set(tags))


# 导出
__all__ = [
    "AutoExtractor",
    "EntityExtractor",
    "InfoClassifier",
    "SummaryExtractor",
    "ExtractionResult",
    "ExtractedInfo",
    "ExtractionType",
]
