#!/usr/bin/env python3
"""
mem9 记忆系统 - 参数优化示例

演示如何根据不同场景调整参数
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memory import (
    create_context_engine,
    Message,
    TokenBudget,
    Turn,
)
from memory.importance_scorer import ScoringConfig, ScoringDimension, ImportanceLevel
from memory.hybrid_retriever import HybridRetriever


async def example_1_strict_mode():
    """示例 1: 严格模式 - 只记住真正重要的"""
    print("=" * 60)
    print("示例 1: 严格模式 - 只记住真正重要的")
    print("=" * 60 + "\n")

    # 严格评分配置
    config = ScoringConfig(
        dimension_weights={
            ScoringDimension.EXPLICIT_KEYWORD: 0.40,  # 提高显式关键词权重
            ScoringDimension.IMPLICIT_INTENT: 0.20,
            ScoringDimension.EMOTIONAL_SIGNAL: 0.15,
            ScoringDimension.TEMPORAL_CONTEXT: 0.10,
            ScoringDimension.ENTITY_REFERENCE: 0.10,
            ScoringDimension.ACTIONABILITY: 0.05,
        },
        thresholds={
            ImportanceLevel.CRITICAL: 0.70,  # 提高 CRITICAL 阈值
            ImportanceLevel.HIGH: 0.55,  # 提高 HIGH 阈值
            ImportanceLevel.MEDIUM: 0.40,  # 提高 MEDIUM 阈值
            ImportanceLevel.LOW: 0.20,
            ImportanceLevel.MINIMAL: 0.0,
        }
    )

    print("⚙️  严格模式配置:")
    print(f"   显式关键词权重: {config.dimension_weights[ScoringDimension.EXPLICIT_KEYWORD]}")
    print(f"   CRITICAL 阈值: {config.thresholds[ImportanceLevel.CRITICAL]}")
    print(f"   HIGH 阈值: {config.thresholds[ImportanceLevel.HIGH]}")
    print(f"   MEDIUM 阈值: {config.thresholds[ImportanceLevel.MEDIUM]}")
    print()

    # 测试评分
    from memory.importance_scorer import ImportanceScorer
    scorer = ImportanceScorer(config)

    test_cases = [
        "记住：API Key 是 xxx",
        "我喜欢使用 Python 编程",
        "今天天气很好",
    ]

    for text in test_cases:
        result = scorer.score_content(text)
        print(f"📝 文本: {text}")
        print(f"   评分: {result.overall_score:.2f}")
        if result.overall_score >= config.critical_threshold:
            print(f"   等级: CRITICAL ✅")
        elif result.overall_score >= config.high_threshold:
            print(f"   等级: HIGH ✅")
        elif result.overall_score >= config.medium_threshold:
            print(f"   等级: MEDIUM ⚠️")
        else:
            print(f"   等级: LOW ❌")
        print()


async def example_2_relaxed_mode():
    """示例 2: 宽松模式 - 记住更多内容"""
    print("=" * 60)
    print("示例 2: 宽松模式 - 记住更多内容")
    print("=" * 60 + "\n")

    # 宽松评分配置
    config = ScoringConfig(
        keyword_weight=0.40,  # 降低关键词权重
        critical_threshold=0.60,  # 降低 CRITICAL 阈值
        high_threshold=0.40,  # 降低 HIGH 阈值
        medium_threshold=0.25,  # 降低 MEDIUM 阈值
    )

    print("⚙️  宽松模式配置:")
    print(f"   关键词权重: {config.keyword_weight}")
    print(f"   CRITICAL 阈值: {config.critical_threshold}")
    print(f"   HIGH 阈值: {config.high_threshold}")
    print(f"   MEDIUM 阈值: {config.medium_threshold}")
    print()

    # 测试评分
    from memory.importance_scorer import ImportanceScorer
    scorer = ImportanceScorer(config)

    test_cases = [
        "记住：API Key 是 xxx",
        "我喜欢使用 Python 编程",
        "今天天气很好",
    ]

    for text in test_cases:
        result = scorer.score_content(text)
        print(f"📝 文本: {text}")
        print(f"   评分: {result.overall_score:.2f}")
        if result.overall_score >= config.critical_threshold:
            print(f"   等级: CRITICAL ✅")
        elif result.overall_score >= config.high_threshold:
            print(f"   等级: HIGH ✅")
        elif result.overall_score >= config.medium_threshold:
            print(f"   等级: MEDIUM ✅")
        else:
            print(f"   等级: LOW ⚠️")
        print()


async def example_3_retrieval_optimization():
    """示例 3: 检索优化 - 调整搜索权重"""
    print("=" * 60)
    print("示例 3: 检索优化 - 调整搜索权重")
    print("=" * 60 + "\n")

    retriever = HybridRetriever()

    # 添加测试记忆
    from memory import MemoryEntry, MemoryType, ImportanceLevel

    memories = [
        MemoryEntry(
            id="1",
            content="用户喜欢使用 Python 编程，特别是 FastAPI",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.HIGH
        ),
        MemoryEntry(
            id="2",
            content="用户喜欢蓝色主题，偏好简洁界面",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.MEDIUM
        ),
        MemoryEntry(
            id="3",
            content="Git 推送前必须先确认",
            memory_type=MemoryType.LONG_TERM,
            importance=ImportanceLevel.CRITICAL
        ),
    ]

    for memory in memories:
        retriever.add_entry(memory)

    print("✅ 已索引 3 条记忆\n")

    # 测试不同的检索策略
    query = "python 编程"

    # 策略 1: 语义优先
    print("🔍 策略 1: 语义优先（向量 70% + 全文 30%）")
    results = retriever.search(
        query=query,
        vector_weight=0.7,
        fulltext_weight=0.3,
        top_k=3
    )
    for i, result in enumerate(results[:3], 1):
        print(f"   {i}. {result.entry.content[:50]}...")
        print(f"      向量: {result.vector_score:.2f} | 全文: {result.fulltext_score:.2f}")
    print()

    # 策略 2: 关键词优先
    print("🔍 策略 2: 关键词优先（向量 30% + 全文 70%）")
    results = retriever.search(
        query=query,
        vector_weight=0.3,
        fulltext_weight=0.7,
        top_k=3
    )
    for i, result in enumerate(results[:3], 1):
        print(f"   {i}. {result.entry.content[:50]}...")
        print(f"      向量: {result.vector_score:.2f} | 全文: {result.fulltext_score:.2f}")
    print()

    # 策略 3: 均衡模式
    print("🔍 策略 3: 均衡模式（向量 50% + 全文 50%）")
    results = retriever.search(
        query=query,
        vector_weight=0.5,
        fulltext_weight=0.5,
        top_k=3
    )
    for i, result in enumerate(results[:3], 1):
        print(f"   {i}. {result.entry.content[:50]}...")
        print(f"      向量: {result.vector_score:.2f} | 全文: {result.fulltext_score:.2f}")
    print()


async def example_4_memory_management():
    """示例 4: 记忆管理优化"""
    print("=" * 60)
    print("示例 4: 记忆管理优化")
    print("=" * 60 + "\n")

    # 不同规模配置
    configs = {
        "轻量级（个人助手）": {
            "max_short_term": 20,
            "max_long_term": 100,
            "compaction_threshold": 0.7,
        },
        "中等级别（团队协作）": {
            "max_short_term": 50,
            "max_long_term": 500,
            "compaction_threshold": 0.8,
        },
        "重量级（企业级）": {
            "max_short_term": 100,
            "max_long_term": 2000,
            "compaction_threshold": 0.9,
        },
    }

    for name, config in configs.items():
        print(f"⚙️  {name}:")
        print(f"   短期记忆: {config['max_short_term']}")
        print(f"   长期记忆: {config['max_long_term']}")
        print(f"   压缩阈值: {config['compaction_threshold']}")
        print()


async def example_5_feishu_optimization():
    """示例 5: 飞书同步优化"""
    print("=" * 60)
    print("示例 5: 飞书同步优化")
    print("=" * 60 + "\n")

    # 不同同步策略
    configs = {
        "即时同步": {
            "feishu_sync_threshold": 0.5,
            "feishu_sync_interval": 10,
            "说明": "重要记忆立即同步，API 调用多"
        },
        "定期同步": {
            "feishu_sync_threshold": 0.67,
            "feishu_sync_interval": 60,
            "说明": "只同步 CRITICAL，节省 API 调用"
        },
        "批量同步": {
            "feishu_sync_threshold": 0.4,
            "feishu_sync_interval": 120,
            "feishu_batch_size": 20,
            "说明": "同步更多记忆，批量处理"
        },
    }

    for name, config in configs.items():
        print(f"⚙️  {name}:")
        for key, value in config.items():
            if key != "说明":
                print(f"   {key}: {value}")
        if "说明" in config:
            print(f"   说明: {config['说明']}")
        print()


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("mem9 记忆系统 - 参数优化示例")
    print("=" * 60 + "\n")

    await example_1_strict_mode()
    await example_2_relaxed_mode()
    await example_3_retrieval_optimization()
    await example_4_memory_management()
    await example_5_feishu_optimization()

    print("=" * 60)
    print("✅ 所有优化示例运行完成！")
    print("=" * 60 + "\n")

    print("💡 下一步:")
    print("1. 根据使用场景选择合适的配置")
    print("2. 定期监控记忆统计")
    print("3. 根据实际情况调整参数")
    print("4. 查看 OPTIMIZATION_GUIDE.md 了解更多")


if __name__ == "__main__":
    asyncio.run(main())
