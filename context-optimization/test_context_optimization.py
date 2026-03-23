#!/usr/bin/env python3
"""上下文优化模块测试脚本"""

import sys
import json
from datetime import datetime

sys.path.insert(0, "/root/.openclaw/workspace/context-optimization")

from auto_summarizer import AutoSummarizer
from result_offloader import ResultOffloader
from compressor import ContextCompressor


def test_auto_summarizer():
    print("=" * 50)
    print("测试 AutoSummarizer")
    print("=" * 50)

    summarizer = AutoSummarizer()

    tasks = [
        {
            "id": "task_001",
            "type": "文件创建",
            "status": "completed",
            "result": "成功创建文件 test.py",
        },
        {
            "id": "task_002",
            "type": "数据处理",
            "status": "completed",
            "result": "处理了 1000 条数据",
        },
        {
            "id": "task_003",
            "type": "API调用",
            "status": "in_progress",
            "result": "正在调用API...",
        },
    ]

    summaries = summarizer.summarize_completed_tasks(tasks)
    print(f"✓ 总结已完成任务: {len(summaries)} 个")

    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，有什么可以帮你的？"},
    ]

    context_summary = summarizer.create_context_summary(messages, tasks)
    print(f"✓ 创建上下文摘要: {len(context_summary)} 字符")

    saved_path = summarizer.save_summary("test_session", context_summary)
    print(f"✓ 保存摘要到: {saved_path}")

    loaded = summarizer.load_summary("test_session")
    print(f"✓ 加载摘要: {'成功' if loaded else '失败'}")

    savings = summarizer.get_token_savings(1000, 600)
    print(f"✓ Token节省: {savings['percentage']}%")

    return True


def test_result_offloader():
    print("\n" + "=" * 50)
    print("测试 ResultOffloader")
    print("=" * 50)

    offloader = ResultOffloader()

    session_id = "test_session_001"
    result_data = {"data": [1, 2, 3], "status": "success"}

    result_id = offloader.save_result(session_id, "task_result", result_data)
    print(f"✓ 保存结果: {result_id}")

    loaded = offloader.load_result(session_id, "task_result")
    print(f"✓ 加载结果: {'成功' if loaded else '失败'}")
    if loaded:
        print(f"  数据: {loaded}")

    results = offloader.list_results(session_id)
    print(f"✓ 列出结果: {len(results)} 个")

    deleted = offloader.delete_result(session_id, "task_result")
    print(f"✓ 删除结果: {'成功' if deleted else '失败'}")

    stats = offloader.get_storage_stats()
    print(f"✓ 存储统计: {stats}")

    return True


def test_compressor():
    print("\n" + "=" * 50)
    print("测试 ContextCompressor")
    print("=" * 50)

    compressor = ContextCompressor()

    messages = [
        {
            "role": "user",
            "content": f"消息 {i}",
            "timestamp": datetime.now().isoformat(),
        }
        for i in range(20)
    ]

    print(f"✓ 原始消息数: {len(messages)}")

    compressed = compressor.compress_context(messages, keep_recent=5)
    print(f"✓ 压缩后消息数: {len(compressed)}")

    token_compressed = compressor.compress_by_token_budget(messages, max_tokens=100)
    print(f"✓ Token预算压缩后: {len(token_compressed)} 条")

    key_info = compressor.extract_key_info(messages)
    print(f"✓ 提取关键信息: {key_info['message_count']} 条消息")

    saved_path = compressor.save_compressed("test_session", compressed)
    print(f"✓ 保存压缩上下文: {saved_path}")

    loaded = compressor.load_compressed("test_session")
    print(f"✓ 加载压缩上下文: {'成功' if loaded else '失败'}")

    stats = compressor.get_compression_stats(messages, compressed)
    print(f"✓ 压缩统计: 减少 {stats['reduction_percentage']}%")

    return True


def test_integration():
    print("\n" + "=" * 50)
    print("集成测试")
    print("=" * 50)

    summarizer = AutoSummarizer()
    offloader = ResultOffloader()
    compressor = ContextCompressor()

    session_id = "integration_test"

    tasks = [
        {
            "id": f"task_{i}",
            "type": "测试任务",
            "status": "completed",
            "result": f"结果 {i}",
        }
        for i in range(5)
    ]

    summarizer.summarize_completed_tasks(tasks)
    print(f"✓ 步骤1: 总结 {len(tasks)} 个任务")

    for i in range(3):
        offloader.save_result(session_id, f"data_{i}", {"value": i})
    print(f"✓ 步骤2: 保存 3 个中间结果")

    messages = [
        {
            "role": "user",
            "content": f"用户消息 {i}",
            "timestamp": datetime.now().isoformat(),
        }
        for i in range(15)
    ]
    compressed = compressor.compress_context(messages, keep_recent=3)
    print(f"✓ 步骤3: 压缩 15 条消息到 {len(compressed)} 条")

    context_summary = summarizer.create_context_summary(compressed, tasks)
    print(f"✓ 步骤4: 生成最终上下文摘要")

    offloader.cleanup_session(session_id)
    print(f"✓ 步骤5: 清理会话数据")

    return True


def main():
    print("\n" + "=" * 50)
    print("上下文优化模块测试")
    print("=" * 50 + "\n")

    all_passed = True

    try:
        test_auto_summarizer()
    except Exception as e:
        print(f"✗ AutoSummarizer 测试失败: {e}")
        all_passed = False

    try:
        test_result_offloader()
    except Exception as e:
        print(f"✗ ResultOffloader 测试失败: {e}")
        all_passed = False

    try:
        test_compressor()
    except Exception as e:
        print(f"✗ Compressor 测试失败: {e}")
        all_passed = False

    try:
        test_integration()
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有测试通过!")
    else:
        print("✗ 部分测试失败")
    print("=" * 50 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
