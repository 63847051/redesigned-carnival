"""
单元测试
测试所有核心组件
"""

import unittest
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.dirname(__file__))

from token_estimator import estimate_tokens, estimate_messages_tokens
from rule_extractor import extract_todos, extract_decisions, extract_links, extract_stats
from summary_generator import generate_summary
from compactor import compact_memory, should_compact


class TestTokenEstimator(unittest.TestCase):
    """测试 Token 估算器"""

    def test_simple_text(self):
        self.assertEqual(estimate_tokens("hello"), 2)
        self.assertEqual(estimate_tokens("hello world"), 3)

    def test_empty_text(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens("   "), 1)

    def test_chinese_text(self):
        self.assertEqual(estimate_tokens("你好"), 1)
        self.assertEqual(estimate_tokens("你好世界"), 2)

    def test_messages(self):
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi there"}
        ]
        tokens = estimate_messages_tokens(messages)
        self.assertEqual(tokens, 5)  # 2 + 3 = 5


class TestRuleExtractor(unittest.TestCase):
    """测试规则提取器"""

    def setUp(self):
        self.messages = [
            {
                "role": "user",
                "content": "TODO: 实现压缩功能",
                "timestamp": "2026-04-09T10:00:00"
            },
            {
                "role": "assistant",
                "content": "Next: 添加测试用例",
                "timestamp": "2026-04-09T10:05:00"
            },
            {
                "role": "user",
                "content": "我们决定采用基于规则的压缩方案",
                "timestamp": "2026-04-09T10:10:00"
            },
            {
                "role": "assistant",
                "content": "访问 https://github.com/Louisym/MiniCC 了解更多",
                "timestamp": "2026-04-09T10:15:00"
            }
        ]

    def test_extract_todos(self):
        todos = extract_todos(self.messages)
        self.assertEqual(len(todos), 2)

    def test_extract_decisions(self):
        decisions = extract_decisions(self.messages)
        self.assertEqual(len(decisions), 1)

    def test_extract_links(self):
        links = extract_links(self.messages)
        self.assertEqual(len(links), 1)

    def test_extract_stats(self):
        stats = extract_stats(self.messages)
        self.assertEqual(stats["total_messages"], 4)
        self.assertEqual(stats["user_messages"], 2)


class TestSummaryGenerator(unittest.TestCase):
    """测试摘要生成器"""

    def setUp(self):
        self.messages = [
            {
                "role": "user",
                "content": "TODO: 实现压缩功能",
                "timestamp": "2026-04-09T10:00:00"
            },
            {
                "role": "assistant",
                "content": "Next: 添加测试用例",
                "timestamp": "2026-04-09T10:05:00"
            }
        ]

    def test_generate_summary(self):
        summary = generate_summary(self.messages)
        self.assertIn("<summary>", summary)
        self.assertIn("统计信息", summary)
        self.assertIn("待办事项", summary)

    def test_summary_length(self):
        summary = generate_summary(self.messages)
        self.assertGreater(len(summary), 100)


class TestCompactor(unittest.TestCase):
    """测试压缩执行器"""

    def setUp(self):
        def create_messages(count):
            messages = []
            for i in range(count):
                role = "user" if i % 2 == 0 else "assistant"
                content = f"消息 {i}"
                messages.append({
                    "role": role,
                    "content": content,
                    "timestamp": f"2026-04-09T{10+i//60:02d}:{i%60:02d}:00"
                })
            return messages

        self.small_messages = create_messages(5)
        self.large_messages = create_messages(50)

    def test_should_not_compact_small(self):
        config = {"preserve_recent": 2, "max_tokens": 100, "min_messages": 10}
        should = should_compact(self.small_messages, config)
        self.assertFalse(should)

    def test_should_compact_large(self):
        config = {"preserve_recent": 10, "max_tokens": 100, "min_messages": 20}
        should = should_compact(self.large_messages, config)
        self.assertTrue(should)

    def test_compact_results(self):
        config = {"preserve_recent": 10, "max_tokens": 100, "min_messages": 20}
        result = compact_memory(self.large_messages, config)

        self.assertGreater(result["removed_count"], 0)
        self.assertEqual(len(result["compressed"]), 11)  # 10 保留 + 1 摘要
        self.assertIn("summary", result)


if __name__ == "__main__":
    # 运行测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTokenEstimator))
    suite.addTests(loader.loadTestsFromTestCase(TestRuleExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestSummaryGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestCompactor))

    # 运行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    # 退出码
    sys.exit(0 if result.wasSuccessful() else 1)
