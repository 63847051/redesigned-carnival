#!/usr/bin/env python3
"""
mem9 记忆系统 - 基础使用示例

演示如何将记忆系统集成到日常对话中
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
from memory.fulltext_search import FullTextSearcher
from memory.importance_scorer import ImportanceScorer


async def example_1_basic_usage():
    """示例 1: 基础使用 - 记住用户偏好"""
    print("=" * 60)
    print("示例 1: 基础使用 - 记住用户偏好")
    print("=" * 60)

    # 创建记忆引擎
    engine = create_context_engine({
        "enable_feishu": False,  # 暂时不启用飞书
    })

    # 初始化
    await engine.bootstrap()
    print("✅ 记忆系统已启动\n")

    # 模拟对话
    print("👤 用户: 我最喜欢使用蓝色主题，不喜欢太复杂的界面")
    user_msg = Message(
        id="msg_001",
        role="user",
        content="我最喜欢使用蓝色主题，不喜欢太复杂的界面"
    )

    # 处理用户消息
    await engine.ingest(user_msg)
    print("✅ 已记录用户偏好\n")

    # 组装上下文（用于 AI 回复）
    budget = TokenBudget(hard_limit=100000, soft_limit=80000)
    context = await engine.assemble(budget)
    print(f"✅ 已组装上下文: {len(context.messages)} 条消息\n")

    # AI 回复
    print("🤖 助手: 好的，已记住！你喜欢蓝色主题，偏好简洁界面")
    assistant_msg = Message(
        id="msg_002",
        role="assistant",
        content="好的，已记住！你喜欢蓝色主题，偏好简洁界面"
    )

    # 轮次后处理
    turn = Turn(
        turn_id="turn_001",
        user_message=user_msg,
        assistant_message=assistant_msg
    )
    await engine.afterTurn(turn)
    print("✅ 轮次处理完成\n")

    # 查看记忆统计
    print("📊 当前记忆统计:")
    # 记忆统计已自动记录


async def example_2_remember_rules():
    """示例 2: 记住重要规则"""
    print("\n" + "=" * 60)
    print("示例 2: 记住重要规则")
    print("=" * 60)

    engine = create_context_engine()
    await engine.bootstrap()

    print("👤 用户: 记住：Git 推送前必须先确认，这个规则绝对不能违反")
    user_msg = Message(
        id="msg_003",
        role="user",
        content="记住：Git 推送前必须先确认，这个规则绝对不能违反"
    )

    await engine.ingest(user_msg)
    print("✅ 已记录重要规则（CRITICAL 级别）\n")

    # 测试重要性评分
    scorer = ImportanceScorer()
    result = scorer.score_content("Git 推送前必须先确认")
    print(f"📊 重要性评分: {result.overall_score:.2f}")
    print(f"   重要性等级: CRITICAL" if result.overall_score >= 0.67 else f"   重要性等级: HIGH")


async def example_3_search_memories():
    """示例 3: 搜索记忆"""
    print("\n" + "=" * 60)
    print("示例 3: 搜索记忆")
    print("=" * 60)

    searcher = FullTextSearcher()

    # 添加一些测试记忆
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
        searcher.add_entry(memory)

    print("✅ 已索引 3 条记忆\n")

    # 搜索 1: 关键词搜索
    print("🔍 搜索 'python':")
    results = searcher.search("python", top_k=5)
    for result in results:
        print(f"   ✅ {result.entry.content}")
        print(f"      相关性: {result.score:.2f}\n")

    # 搜索 2: 关键词搜索
    print("🔍 搜索 'git':")
    results = searcher.search("git", top_k=5)
    for result in results:
        print(f"   ✅ {result.entry.content}")
        print(f"      相关性: {result.score:.2f}\n")


async def example_4_conversation():
    """示例 4: 完整对话流程"""
    print("\n" + "=" * 60)
    print("示例 4: 完整对话流程")
    print("=" * 60)

    engine = create_context_engine()
    await engine.bootstrap()

    # 对话轮次 1
    print("👤 用户: 我叫小明，喜欢用 Python 开发")
    msg1 = Message(id="m1", role="user", content="我叫小明，喜欢用 Python 开发")
    await engine.ingest(msg1)

    budget = TokenBudget(hard_limit=100000, soft_limit=80000)
    context = await engine.assemble(budget)

    resp1 = Message(id="r1", role="assistant", content="你好小明！很高兴认识你")
    turn1 = Turn(turn_id="t1", user_message=msg1, assistant_message=resp1)
    await engine.afterTurn(turn1)
    print("🤖 助手: 你好小明！很高兴认识你\n")

    # 对话轮次 2
    print("👤 用户: 记住我最喜欢的框架是 FastAPI")
    msg2 = Message(id="m2", role="user", content="记住我最喜欢的框架是 FastAPI")
    await engine.ingest(msg2)

    context = await engine.assemble(budget)
    print(f"✅ 上下文已组装: {len(context.messages)} 条消息")

    resp2 = Message(id="r2", role="assistant", content="已记住！你喜欢 FastAPI 框架")
    turn2 = Turn(turn_id="t2", user_message=msg2, assistant_message=resp2)
    await engine.afterTurn(turn2)
    print("🤖 助手: 已记住！你喜欢 FastAPI 框架\n")

    # 查看最终统计
    print("📊 最终记忆统计:")
    # 记忆已自动记录到存储
    print("   所有对话已成功记录到记忆系统！")


async def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("mem9 记忆系统 - 基础使用示例")
    print("=" * 60 + "\n")

    await example_1_basic_usage()
    await example_2_remember_rules()
    await example_3_search_memories()
    await example_4_conversation()

    print("\n" + "=" * 60)
    print("✅ 所有示例运行完成！")
    print("=" * 60 + "\n")

    print("💡 下一步:")
    print("1. 创建飞书多维表格，启用云端同步")
    print("2. 调整重要性评分阈值")
    print("3. 集成向量搜索，实现语义检索")
    print("4. 查看 USAGE_GUIDE.md 了解更多功能")


if __name__ == "__main__":
    asyncio.run(main())
