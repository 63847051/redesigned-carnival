"""
自动记忆系统测试

测试重要性评分、自动提取和自动标签功能
"""

import logging
import unittest
from datetime import datetime
from typing import List
from unittest.mock import Mock, patch

from memory.context_engine import (
    ImportanceLevel,
    MemoryEntry,
    MemoryType,
    Message,
)
from memory.importance_scorer import (
    BatchScorer,
    ImportanceScorer,
    ScoringConfig,
    ScoringDimension,
    ScoringResult,
)
from memory.auto_extractor import (
    AutoExtractor,
    ExtractionType,
    ExtractedInfo,
    ExtractionResult,
    EntityExtractor,
    InfoClassifier,
    SummaryExtractor,
)
from memory.auto_tagger import (
    AutoTagger,
    TagCluster,
    TagManager,
    TagRecommendation,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestImportanceScorer(unittest.TestCase):
    """测试重要性评分器"""

    def setUp(self):
        """测试前准备"""
        self.scorer = ImportanceScorer()

    def test_critical_content(self):
        """测试关键内容评分"""
        content = "请记住我的API密钥是 abc123xyz，永远不要告诉别人"
        result = self.scorer.score_content(content)

        self.assertGreater(result.overall_score, 0.6)
        self.assertIn(
            result.importance_level, [ImportanceLevel.CRITICAL, ImportanceLevel.HIGH]
        )
        logger.info(
            f"Critical content score: {result.overall_score}, level: {result.importance_level}"
        )

    def test_preference_content(self):
        """测试偏好内容评分"""
        content = "我最喜欢使用蓝色主题，不喜欢太复杂的界面"
        result = self.scorer.score_content(content)

        self.assertGreater(result.overall_score, 0.4)
        self.assertTrue(len(result.reasons) > 0)
        logger.info(
            f"Preference content score: {result.overall_score}, reasons: {result.reasons}"
        )

    def test_temporal_context(self):
        """测试时间上下文评分"""
        content = "每次开会都要记得记录会议纪要"
        result = self.scorer.score_content(content)

        self.assertGreater(
            result.dimension_scores.get(ScoringDimension.TEMPORAL_CONTEXT, 0), 0.5
        )
        logger.info(
            f"Temporal context dimension: {result.dimension_scores.get(ScoringDimension.TEMPORAL_CONTEXT)}"
        )

    def test_low_importance_content(self):
        """测试低重要性内容"""
        content = "今天天气不错"
        result = self.scorer.score_content(content)

        self.assertLess(result.overall_score, 0.5)
        logger.info(f"Low importance score: {result.overall_score}")

    def test_empty_content(self):
        """测试空内容"""
        result = self.scorer.score_content("")

        self.assertEqual(result.overall_score, 0.0)
        self.assertEqual(result.importance_level, ImportanceLevel.MINIMAL)
        self.assertEqual(result.confidence, 0.0)

    def test_message_scoring(self):
        """测试消息评分"""
        message = Message(
            id="test_msg_1",
            role="user",
            content="请记住我喜欢喝绿茶，不喜欢咖啡",
            timestamp=datetime.now(),
        )

        result = self.scorer.score_message(message)

        self.assertGreater(result.overall_score, 0.3)
        self.assertIsNotNone(result.dimension_scores)
        logger.info(f"Message scoring result: {result.overall_score}")

    def test_confidence_calculation(self):
        """测试置信度计算"""
        content = "记住我最重要的偏好是喜欢简洁的设计"
        result = self.scorer.score_content(content)

        self.assertGreater(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        logger.info(f"Confidence: {result.confidence}")


class TestBatchScorer(unittest.TestCase):
    """测试批量评分器"""

    def setUp(self):
        """测试前准备"""
        self.batch_scorer = BatchScorer()

    def test_batch_scoring(self):
        """测试批量评分"""
        contents = [
            "请记住我的密码是123456",
            "今天天气怎么样",
            "我讨厌吃胡萝卜",
        ]

        results = self.batch_scorer.score_contents(contents)

        self.assertEqual(len(results), 3)
        self.assertGreater(results[0].overall_score, results[1].overall_score)
        logger.info(f"Batch scores: {[r.overall_score for r in results]}")

    def test_get_top_memories(self):
        """测试获取最重要记忆"""
        memories = [
            MemoryEntry(
                id="1",
                content="普通内容",
                memory_type=MemoryType.SHORT_TERM,
                importance=ImportanceLevel.LOW,
                tags=[],
            ),
            MemoryEntry(
                id="2",
                content="请记住我的重要偏好",
                memory_type=MemoryType.LONG_TERM,
                importance=ImportanceLevel.HIGH,
                tags=[],
            ),
            MemoryEntry(
                id="3",
                content="关键规则不要忘记",
                memory_type=MemoryType.LONG_TERM,
                importance=ImportanceLevel.CRITICAL,
                tags=[],
            ),
        ]

        top_memories = self.batch_scorer.get_top_memories(memories, top_n=2)

        self.assertEqual(len(top_memories), 2)
        self.assertIn(top_memories[0].id, ["2", "3"])
        logger.info(f"Top memories: {[m.id for m in top_memories]}")

    def test_filter_by_threshold(self):
        """测试阈值过滤"""
        memories = [
            MemoryEntry(
                id="1",
                content="低重要性",
                memory_type=MemoryType.SHORT_TERM,
                importance=ImportanceLevel.LOW,
                tags=[],
            ),
            MemoryEntry(
                id="2",
                content="高重要性内容",
                memory_type=MemoryType.LONG_TERM,
                importance=ImportanceLevel.HIGH,
                tags=[],
            ),
        ]

        filtered = self.batch_scorer.filter_by_threshold(memories, 0.1)

        self.assertGreaterEqual(len(filtered), 1)


class TestEntityExtractor(unittest.TestCase):
    """测试实体提取器"""

    def setUp(self):
        """测试前准备"""
        self.extractor = EntityExtractor()

    def test_extract_email(self):
        """测试邮箱提取"""
        text = "请联系我的邮箱 test@example.com"
        entities = self.extractor.extract_entities(text)

        self.assertIn("email", entities)
        self.assertIn("test@example.com", entities["email"])
        logger.info(f"Extracted emails: {entities.get('email')}")

    def test_extract_url(self):
        """测试URL提取"""
        text = "查看 https://example.com/docs 获取更多信息"
        entities = self.extractor.extract_entities(text)

        self.assertIn("url", entities)
        logger.info(f"Extracted URLs: {entities.get('url')}")

    def test_extract_date(self):
        """测试日期提取"""
        text = "会议安排在 2024-01-15"
        entities = self.extractor.extract_entities(text)

        self.assertIn("date", entities)
        logger.info(f"Extracted dates: {entities.get('date')}")


class TestInfoClassifier(unittest.TestCase):
    """测试信息分类器"""

    def setUp(self):
        """测试前准备"""
        self.classifier = InfoClassifier()

    def test_classify_preference(self):
        """测试偏好分类"""
        content = "我喜欢蓝色，讨厌红色"
        ex_type, confidence, reasons = self.classifier.classify(content)

        self.assertEqual(ex_type, ExtractionType.PREFERENCE)
        self.assertGreater(confidence, 0.5)
        logger.info(
            f"Preference classification: type={ex_type.value}, confidence={confidence}"
        )

    def test_classify_rule(self):
        """测试规则分类"""
        content = "必须遵守的规则：不要在工作时间聊私事"
        ex_type, confidence, reasons = self.classifier.classify(content)

        self.assertEqual(ex_type, ExtractionType.RULE)
        self.assertGreater(confidence, 0.6)
        logger.info(
            f"Rule classification: type={ex_type.value}, confidence={confidence}"
        )

    def test_classify_task(self):
        """测试任务分类"""
        content = "帮我完成这个任务：整理文档"
        ex_type, confidence, reasons = self.classifier.classify(content)

        self.assertEqual(ex_type, ExtractionType.TASK)
        logger.info(f"Task classification: type={ex_type.value}")

    def test_classify_identity(self):
        """测试身份分类"""
        content = "我叫张三，是一名工程师"
        ex_type, confidence, reasons = self.classifier.classify(content)

        self.assertEqual(ex_type, ExtractionType.IDENTITY)
        logger.info(f"Identity classification: type={ex_type.value}")


class TestSummaryExtractor(unittest.TestCase):
    """测试摘要提取器"""

    def setUp(self):
        """测试前准备"""
        self.extractor = SummaryExtractor(max_summary_length=50)

    def test_short_content(self):
        """测试短内容"""
        content = "这是短内容"
        summary = self.extractor.extract_summary(content)

        self.assertEqual(summary, content)

    def test_long_content(self):
        """测试长内容摘要"""
        content = (
            "这是一个重要的话题。我最喜欢的事情是编程。记住每天要运动。最后记得喝水。"
        )
        summary = self.extractor.extract_summary(content)

        self.assertLessEqual(len(summary), 60)
        self.assertIn("重要", summary)
        logger.info(f"Summary: {summary}")


class TestAutoExtractor(unittest.TestCase):
    """测试自动提取器"""

    def setUp(self):
        """测试前准备"""
        self.extractor = AutoExtractor()

    def test_extract_from_message(self):
        """测试从消息提取"""
        message = Message(
            id="test_msg",
            role="user",
            content="请记住我的偏好：我最喜欢喝绿茶，最讨厌喝咖啡",
            timestamp=datetime.now(),
        )

        result = self.extractor.extract_from_message(message)

        self.assertGreater(result.total_extracted, 0)
        self.assertGreater(result.high_priority_count, 0)
        self.assertEqual(len(result.memory_entries), 1)

        entry = result.memory_entries[0]
        self.assertEqual(entry.memory_type, MemoryType.LONG_TERM)
        logger.info(f"Extracted entry importance: {entry.importance}")

    def test_extract_batch(self):
        """测试批量提取"""
        contents = [
            "记住我喜欢蓝色",
            "今天天气不错",
            "重要规则：不要迟到",
        ]

        result = self.extractor.extract_batch(contents)

        self.assertGreaterEqual(result.total_extracted, 1)
        self.assertGreater(result.high_priority_count, 0)
        logger.info(
            f"Batch extraction: {result.total_extracted} extracted, {result.high_priority_count} high priority"
        )

    def test_extract_with_low_importance(self):
        """测试低重要性内容不提取"""
        result = self.extractor.extract_from_content("你好")

        self.assertEqual(result.total_extracted, 0)


class TestAutoTagger(unittest.TestCase):
    """测试智能标签器"""

    def setUp(self):
        """测试前准备"""
        self.tagger = AutoTagger()

    def test_generate_tags_preference(self):
        """测试生成偏好标签"""
        content = "我最喜欢蓝色主题"

        recommendation = self.tagger.generate_tags(content)

        self.assertIn("偏好", recommendation.tags)
        logger.info(f"Generated tags: {recommendation.tags}")

    def test_generate_tags_with_existing(self):
        """测试带已有标签生成"""
        content = "这是一个技术项目"

        recommendation = self.tagger.generate_tags(content, existing_tags=["tech"])

        self.assertIn("技术", recommendation.tags)
        logger.info(f"Tags with existing: {recommendation.tags}")

    def test_recommend_similar_tags(self):
        """测试推荐相似标签"""
        memories = [
            MemoryEntry(
                id="1",
                content="我喜欢蓝色",
                memory_type=MemoryType.LONG_TERM,
                importance=ImportanceLevel.HIGH,
                tags=["偏好", "颜色"],
            ),
            MemoryEntry(
                id="2",
                content="我喜欢红色",
                memory_type=MemoryType.LONG_TERM,
                importance=ImportanceLevel.HIGH,
                tags=["偏好", "颜色"],
            ),
        ]

        similar = self.tagger.recommend_similar_tags("偏好", memories)

        self.assertIn("颜色", similar)
        logger.info(f"Similar tags: {similar}")

    def test_tag_scores(self):
        """测试标签评分"""
        content = "记住我讨厌咖啡，喜欢绿茶"

        recommendation = self.tagger.generate_tags(content)

        for tag in recommendation.tags:
            self.assertIn(tag, recommendation.scores)
            self.assertGreater(recommendation.scores[tag], 0.0)
            self.assertIn(tag, recommendation.reasons)


class TestTagManager(unittest.TestCase):
    """测试标签管理器"""

    def setUp(self):
        """测试前准备"""
        self.manager = TagManager()

    def test_process_memory(self):
        """测试处理记忆"""
        memory = MemoryEntry(
            id="test_memory",
            content="我最喜欢的项目是OpenClaw",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.HIGH,
            tags=[],
        )

        final_tags = self.manager.process_memory(memory)

        self.assertGreater(len(final_tags), 0)
        logger.info(f"Final tags: {final_tags}")

    def test_suggest_tags_for_memories(self):
        """测试为记忆建议标签"""
        memories = [
            MemoryEntry(
                id="1",
                content="重要规则",
                memory_type=MemoryType.LONG_TERM,
                importance=ImportanceLevel.HIGH,
                tags=[],
            ),
            MemoryEntry(
                id="2",
                content="我喜欢蓝色",
                memory_type=MemoryType.LONG_TERM,
                importance=ImportanceLevel.MEDIUM,
                tags=[],
            ),
        ]

        suggestions = self.manager.suggest_tags_for_memories(memories)

        self.assertEqual(len(suggestions), 2)
        for memory_id, tags in suggestions.items():
            self.assertGreater(len(tags), 0)

        logger.info(f"Tag suggestions: {suggestions}")


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_pipeline(self):
        """测试完整流程"""
        # 1. 评分
        scorer = ImportanceScorer()
        content = "请记住我的重要偏好：我最喜欢简洁的设计风格"

        scoring_result = scorer.score_content(content)
        logger.info(f"Step 1 - Scoring: {scoring_result.overall_score}")

        # 2. 提取
        extractor = AutoExtractor(scorer=scorer)
        extraction_result = extractor.extract_from_content(content)
        logger.info(f"Step 2 - Extraction: {extraction_result.total_extracted} items")

        # 3. 标签
        tagger = AutoTagger()

        for entry in extraction_result.memory_entries:
            tag_recommendation = tagger.generate_tags(
                entry.content, entry.tags, {"importance": entry.importance}
            )
            logger.info(
                f"Step 3 - Tags for entry {entry.id}: {tag_recommendation.tags}"
            )

        # 验证流程
        self.assertGreater(scoring_result.overall_score, 0.3)
        self.assertGreater(extraction_result.total_extracted, 0)

    def test_memory_entry_creation(self):
        """测试记忆条目创建"""
        # 创建记忆
        memory = MemoryEntry(
            id="integration_test",
            content="记住我讨厌咖啡",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.HIGH,
            tags=[],
            source_turn_id="test_turn",
        )

        # 处理标签
        manager = TagManager()
        final_tags = manager.process_memory(memory)

        # 更新记忆
        memory.tags = final_tags

        # 验证
        self.assertGreater(len(memory.tags), 0)
        self.assertIn("偏好", memory.tags)

        logger.info(f"Final memory tags: {memory.tags}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
