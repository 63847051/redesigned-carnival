"""
智能记忆压缩系统 v1.0 - 使用示例
"""

import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.dirname(__file__))

from token_estimator import estimate_messages_tokens
from rule_extractor import extract_todos, extract_decisions, extract_links, extract_stats
from summary_generator import generate_summary
from compactor import compact_memory


def create_test_messages(count=50):
    """创建测试消息"""
    messages = []
    for i in range(count):
        role = "user" if i % 2 == 0 else "assistant"
        content = f"消息 {i}: TODO: 待办事项 {i}" if i % 3 == 0 else f"消息 {i}: 普通内容"
        messages.append({
            "role": role,
            "content": content,
            "timestamp": f"2026-04-09T{10+i//60:02d}:{i%60:02d}:00"
        })
    return messages


def main():
    print("=" * 60)
    print("智能记忆压缩系统 v1.0 - 使用示例")
    print("=" * 60)
    print()

    # 1. 创建测试消息
    print("步骤 1: 创建测试消息")
    messages = create_test_messages(50)
    print(f"✅ 创建了 {len(messages)} 条消息")
    print()

    # 2. 估算 Token 数量
    print("步骤 2: 估算 Token 数量")
    tokens = estimate_messages_tokens(messages)
    print(f"✅ 总 Token 数: {tokens}")
    print()

    # 3. 提取关键信息
    print("步骤 3: 提取关键信息")
    todos = extract_todos(messages)
    decisions = extract_decisions(messages)
    links = extract_links(messages)
    stats = extract_stats(messages)

    print(f"✅ 待办事项: {len(todos)} 个")
    print(f"✅ 关键决策: {len(decisions)} 个")
    print(f"✅ 重要链接: {len(links)} 个")
    print(f"✅ 统计信息: {stats['total_messages']} 条消息")
    print()

    # 4. 生成摘要
    print("步骤 4: 生成摘要")
    summary = generate_summary(messages[:20])
    print(f"✅ 摘要预览（前 500 字符）:")
    print(summary[:500])
    print("...")
    print()

    # 5. 执行压缩
    print("步骤 5: 执行压缩")
    config = {
        "preserve_recent": 10,
        "max_tokens": 100,
        "min_messages": 20,
        "include_timeline": True,
        "max_timeline_items": 5
    }
    result = compact_memory(messages, config)

    print(f"✅ 压缩完成!")
    print(f"   - 原始消息数: {len(messages)}")
    print(f"   - 压缩后消息数: {len(result['compressed'])}")
    print(f"   - 压缩掉: {result['removed_count']} 条")
    print(f"   - 原始 Token: {result['original_tokens']}")
    print(f"   - 压缩后 Token: {result['compressed_tokens']}")
    print(f"   - 节省: {result['tokens_saved']} tokens ({result['compression_ratio']})")
    print()

    # 6. 查看压缩后的消息
    print("步骤 6: 查看压缩后的消息")
    print(f"✅ 第一条消息（摘要）:")
    print(result['compressed'][0]['content'][:300])
    print("...")
    print()

    print("=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
