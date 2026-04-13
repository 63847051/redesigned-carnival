"""
Hermes Core 完整测试
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path


class TestSnapshotStore(unittest.TestCase):
    """测试快照存储"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        from core.snapshot_store import SnapshotStore

        self.store = SnapshotStore(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_capture_and_get_snapshot(self):
        data = {"key": "value", "list": [1, 2, 3]}
        self.store.capture_snapshot("test", data)

        result = self.store.get_snapshot("test")
        self.assertIsNotNone(result)
        self.assertEqual(result["data"], data)

    def test_freeze_unfreeze(self):
        self.store.capture_snapshot("test", {"data": "value"})
        self.store.freeze("test")

        self.assertTrue(self.store.is_frozen("test"))

        self.store.unfreeze("test")
        self.assertFalse(self.store.is_frozen("test"))

    def test_update_frozen_snapshot_fails(self):
        self.store.capture_snapshot("test", {"data": "original"})
        self.store.freeze("test")

        result = self.store.update_snapshot("test", {"data": "updated"})
        self.assertFalse(result)

    def test_save_load_disk(self):
        data = {"test": "data"}
        self.store.capture_snapshot("test", data)

        filepath = self.store.save_to_disk("test")
        self.assertTrue(filepath.exists())

        self.store.clear()
        loaded = self.store.load_from_disk("test")
        self.assertEqual(loaded["data"], data)


class TestAtomicWriter(unittest.TestCase):
    """测试原子写入"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        from core.snapshot_store import AtomicWriter

        self.writer = AtomicWriter(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_write_json(self):
        data = {"key": "value", "num": 123}
        filepath = self.writer.write_json("test.json", data)

        self.assertTrue(filepath.exists())

        loaded = self.writer.read_json("test.json")
        self.assertEqual(loaded, data)

    def test_write_text(self):
        content = "Hello World"
        filepath = self.writer.write_text("test.txt", content)

        self.assertTrue(filepath.exists())

        loaded = self.writer.read_text("test.txt")
        self.assertEqual(loaded, content)


class TestFuzzyPatcher(unittest.TestCase):
    """测试 Fuzzy Patch"""

    def setUp(self):
        from core.fuzzy_patch import FuzzyPatcher

        self.patcher = FuzzyPatcher()

    def test_normalize(self):
        text = "  line1  \n\n  line2  \n"
        normalized = self.patcher.normalize(text)

        self.assertIn("line1", normalized)
        self.assertIn("line2", normalized)

    def test_compute_diff(self):
        original = "line1\nline2\nline3"
        patched = "line1\nmodified\nline3"

        diff = self.patcher.compute_diff(original, patched)
        self.assertIn("modified", diff)

    def test_calculate_similarity(self):
        from core.fuzzy_patch import calculate_similarity

        a = "hello world"
        b = "hello world"
        c = "different text"

        self.assertGreater(calculate_similarity(a, b), 0.9)
        self.assertLess(calculate_similarity(a, c), 0.5)


class TestAutoSkillCreator(unittest.TestCase):
    """测试技能自动创建"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        from learning.auto_skill_creator import AutoSkillCreator

        self.creator = AutoSkillCreator(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_analyze_context_should_create(self):
        from learning.auto_skill_creator import TaskContext

        context = TaskContext(
            tool_calls=[{"name": f"tool_{i}"} for i in range(6)],
            errors=["error1"],
            user_corrections=["correction1"],
            success=True,
        )

        analysis = self.creator.analyze_context(context)
        self.assertTrue(analysis["should_create"])

    def test_analyze_context_should_not_create(self):
        from learning.auto_skill_creator import TaskContext

        context = TaskContext(
            tool_calls=[{"name": "tool_1"}],
            errors=[],
            user_corrections=[],
            success=True,
        )

        analysis = self.creator.analyze_context(context)
        self.assertFalse(analysis["should_create"])

    def test_quick_check(self):
        result = self.creator.should_create_skill(
            tool_calls=6, errors=1, corrections=1, success=True
        )
        self.assertTrue(result)


class TestAutoSkillImprover(unittest.TestCase):
    """测试技能自动改进"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        from learning.auto_skill_improver import AutoSkillImprover

        self.improver = AutoSkillImprover(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_analyze_failure(self):
        from learning.auto_skill_improver import UsageContext

        context = UsageContext(
            skill_name="test_skill",
            user_request="test request",
            execution_result="failed",
            success=False,
            error="File not found",
        )

        suggestion = self.improver.analyze_usage(context)
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.priority, "high")

    def test_get_usage_stats(self):
        from learning.auto_skill_improver import UsageContext

        context = UsageContext(
            skill_name="test_skill",
            user_request="test",
            execution_result="success",
            success=True,
        )

        self.improver.analyze_usage(context)

        stats = self.improver.get_usage_stats("test_skill")
        self.assertEqual(stats["total_uses"], 1)


class TestSelfGuidance(unittest.TestCase):
    """测试自我引导"""

    def setUp(self):
        from learning.self_guidance import SelfGuidance

        self.guidance = SelfGuidance()

    def test_evaluate_triggers_repeated_error(self):
        context = {
            "consecutive_errors": 3,
            "tool_call_count": 0,
            "confidence": 1.0,
            "tool_failed": False,
        }

        prompts = self.guidance.evaluate_triggers(context)
        self.assertTrue(any("错误" in p for p in prompts))

    def test_evaluate_triggers_complex_task(self):
        context = {
            "consecutive_errors": 0,
            "tool_call_count": 10,
            "confidence": 1.0,
            "tool_failed": False,
        }

        prompts = self.guidance.evaluate_triggers(context)
        self.assertTrue(any("复杂" in p or "分解" in p for p in prompts))


class TestSessionSearch(unittest.TestCase):
    """测试 FTS5 会话搜索"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        from search.fts5_search import SessionSearch

        self.search = SessionSearch(self.temp_dir + "/test.db")

    def tearDown(self):
        self.search.close()
        shutil.rmtree(self.temp_dir)

    def test_index_and_search(self):
        session_id = "test_session_1"
        messages = [
            {"role": "user", "content": "Hello world"},
            {"role": "assistant", "content": "Hi there"},
        ]

        self.search.index_session(session_id, "Test Session", messages)

        results = self.search.search("hello", limit=5)
        self.assertTrue(len(results) > 0)

    def test_get_recent_sessions(self):
        session_id = "test_session_2"
        messages = [{"role": "user", "content": "test"}]

        self.search.index_session(session_id, "Recent", messages)

        recent = self.search.get_recent_sessions(limit=5)
        self.assertTrue(len(recent) > 0)


class TestLLMSummarizer(unittest.TestCase):
    """测试 LLM 摘要"""

    def setUp(self):
        from search.llm_summarizer import LLMSummarizer

        self.summarizer = LLMSummarizer()

    def test_summarize_empty(self):
        result = self.summarizer.summarize("test", [])

        self.assertEqual(result.summary, "没有找到相关会话")

    def test_summarize_few_results(self):
        sessions = [
            {"title": "Session 1", "snippet": "content about python"},
            {"title": "Session 2", "snippet": "more python content"},
        ]

        result = self.summarizer.summarize("python", sessions)

        self.assertIn("2", result.summary)
        self.assertTrue(len(result.key_topics) > 0)


class TestHonchoLite(unittest.TestCase):
    """测试 Honcho 用户建模"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        from modeling.honcho_lite import HonchoLite

        self.honcho = HonchoLite(self.temp_dir + "/users.db")

    def tearDown(self):
        self.honcho.close()
        shutil.rmtree(self.temp_dir)

    def test_profile_create(self):
        profile = self.honcho.profile("user_123", "Test User")

        self.assertEqual(profile.user_id, "user_123")
        self.assertEqual(profile.name, "Test User")
        self.assertEqual(profile.interaction_count, 0)

    def test_record_interaction(self):
        self.honcho.record_interaction("user_123", "Hello world")

        profile = self.honcho.profile("user_123")
        self.assertEqual(profile.interaction_count, 1)

    def test_search_interactions(self):
        self.honcho.record_interaction("user_123", "I love Python programming")

        results = self.honcho.search("user_123", "Python")
        self.assertTrue(len(results) > 0)

    def test_conclude(self):
        conclusion = self.honcho.conclude(
            "user_123", "用户偏好 Python 开发", 0.8, ["多次提到 Python"]
        )

        self.assertIsNotNone(conclusion.conclusion_id)
        self.assertEqual(conclusion.confidence, 0.8)

    def test_context(self):
        self.honcho.record_interaction("user_123", "I prefer dark mode")
        self.honcho.record_interaction("user_123", "I like Python")

        reasoning = self.honcho.context("user_123", "用户的技术偏好是什么？")

        self.assertIn("question", reasoning)
        self.assertIn("reasoning", reasoning)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_workflow(self):
        from core.snapshot_store import SnapshotStore, AtomicWriter
        from learning.auto_skill_creator import AutoSkillCreator, TaskContext
        from core.fuzzy_patch import calculate_similarity

        temp_dir = tempfile.mkdtemp()

        try:
            store = SnapshotStore(temp_dir)
            store.capture_snapshot("knowledge", {"skills": []})
            store.freeze("knowledge")

            writer = AtomicWriter(temp_dir)
            writer.write_json("config.json", {"setting": "value"})

            creator = AutoSkillCreator(temp_dir)
            context = TaskContext(
                tool_calls=[{"name": f"tool_{i}"} for i in range(7)],
                errors=["error1"],
                user_corrections=["correction1"],
                success=True,
            )
            skill_path = creator.create_skill(context)

            self.assertIsNotNone(skill_path)

            sim = calculate_similarity("hello world", "hello world")
            self.assertGreater(sim, 0.9)

        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    unittest.main(verbosity=2)
