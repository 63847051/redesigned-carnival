"""
压缩执行器
执行压缩操作

参考：Claude Code compact.rs:75-111 (compact_session)
"""

from typing import List, Dict, Optional
from datetime import datetime
from token_estimator import estimate_messages_tokens
from summary_generator import generate_summary


def should_compact(messages: list, config: dict) -> bool:
    """
    判断是否需要压缩

    两个条件都满足时才压缩：
    1. 消息数量 > 保留数量（否则没东西可压缩）
    2. 预估 token 数 >= 阈值（还没到限制就不压缩）

    参数:
        messages: 消息列表
        config: 配置字典

    返回:
        是否需要压缩
    """
    preserve_recent = config.get("preserve_recent", 10)
    max_tokens = config.get("max_tokens", 2000)
    min_messages = config.get("min_messages", 20)

    # 条件 1: 消息数量足够
    has_enough_messages = len(messages) > preserve_recent and len(messages) >= min_messages

    # 条件 2: token 数量超过阈值
    estimated_tokens = estimate_messages_tokens(messages)
    exceeds_token_limit = estimated_tokens >= max_tokens

    return has_enough_messages and exceeds_token_limit


def compact_memory(messages: list, config: dict = None) -> dict:
    """
    执行压缩

    算法：
    1. 判断是否需要压缩 → 不需要就直接返回
    2. 把消息分成两组：旧的（要压缩的）和新的（要保留的）
    3. 旧消息 → 生成摘要
    4. 新消息列表 = [摘要消息] + [保留的消息]

    参数:
        messages: 消息列表
        config: 配置字典

    返回:
        压缩结果字典，包含：
        - compressed: 压缩后的消息列表
        - removed_count: 被压缩掉的消息数量
        - summary: 摘要文本
        - original_tokens: 压缩前的 token 数
        - compressed_tokens: 压缩后的 token 数
    """
    if config is None:
        config = {
            "preserve_recent": 10,
            "max_tokens": 2000,
            "min_messages": 20,
            "include_timeline": True,
            "max_timeline_items": 10
        }

    # 1. 判断是否需要压缩
    if not should_compact(messages, config):
        return {
            "compressed": messages,
            "removed_count": 0,
            "summary": "",
            "original_tokens": estimate_messages_tokens(messages),
            "compressed_tokens": estimate_messages_tokens(messages),
            "reason": "不满足压缩条件"
        }

    # 2. 分离旧消息和最近消息
    preserve_recent = config.get("preserve_recent", 10)
    keep_from = max(0, len(messages) - preserve_recent)

    old_messages = messages[:keep_from]
    recent_messages = messages[keep_from:]

    # 3. 生成摘要
    summary = generate_summary(old_messages, config)

    # 4. 构造摘要消息
    summary_message = {
        "role": "system",
        "content": summary,
        "timestamp": datetime.now().isoformat()
    }

    # 5. 组装新的消息列表
    compressed_messages = [summary_message] + recent_messages

    # 6. 计算统计信息
    original_tokens = estimate_messages_tokens(messages)
    compressed_tokens = estimate_messages_tokens(compressed_messages)

    return {
        "compressed": compressed_messages,
        "removed_count": len(old_messages),
        "summary": summary,
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "tokens_saved": original_tokens - compressed_tokens,
        "compression_ratio": f"{(1 - compressed_tokens / original_tokens) * 100:.1f}%",
        "reason": "压缩成功"
    }


def compact_memory_with_validation(messages: list, config: dict = None) -> dict:
    """
    执行压缩（带验证）

    在压缩后进行验证，确保：
    1. 消息数量正确
    2. token 数量确实减少
    3. 最近的消息被保留

    参数:
        messages: 消息列表
        config: 配置字典

    返回:
        压缩结果字典（包含验证信息）
    """
    result = compact_memory(messages, config)

    # 验证
    validation = {
        "messages_correct": True,
        "tokens_reduced": True,
        "recent_preserved": True,
        "errors": []
    }

    # 验证 1: 消息数量
    # 期望 = 保留的消息 + 摘要消息
    expected_length = config.get("preserve_recent", 10) + 1  # +1 是摘要消息
    if len(result["compressed"]) != expected_length:
        validation["messages_correct"] = False
        validation["errors"].append(f"消息数量不正确：期望 {expected_length}，实际 {len(result['compressed'])}")

    # 验证 2: token 减少
    if result["compressed_tokens"] >= result["original_tokens"]:
        validation["tokens_reduced"] = False
        validation["errors"].append("Token 数量没有减少")

    # 验证 3: 最近的消息被保留
    if config and "preserve_recent" in config:
        preserve_count = config["preserve_recent"]
        if len(messages) >= preserve_count:
            recent_original = messages[-preserve_count:]
            recent_compressed = result["compressed"][-preserve_count:]

            # 检查最近的消息是否相同
            for i in range(preserve_count):
                if i < len(recent_compressed) and recent_original[i] != recent_compressed[i]:
                    validation["recent_preserved"] = False
                    validation["errors"].append(f"最近的消息 {i} 没有被正确保留")
                    break

    result["validation"] = validation

    return result


# 测试
if __name__ == "__main__":
    # 创建测试消息
    def create_test_messages(count):
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

    # 测试 1: 少量消息（不触发压缩）
    print("=== 测试 1: 少量消息 ===")
    messages = create_test_messages(5)
    config = {"preserve_recent": 2, "max_tokens": 100, "min_messages": 10}
    result = compact_memory(messages, config)
    print(f"触发压缩: {result['removed_count'] > 0}")
    print(f"原因: {result['reason']}")
    assert result["removed_count"] == 0

    # 测试 2: 大量消息（触发压缩）
    print("\n=== 测试 2: 大量消息 ===")
    messages = create_test_messages(50)
    config = {"preserve_recent": 10, "max_tokens": 100, "min_messages": 20}
    result = compact_memory(messages, config)
    print(f"原始消息数: {len(messages)}")
    print(f"压缩后消息数: {len(result['compressed'])}")
    print(f"压缩掉: {result['removed_count']} 条")
    print(f"原始 tokens: {result['original_tokens']}")
    print(f"压缩后 tokens: {result['compressed_tokens']}")
    print(f"节省: {result['tokens_saved']} tokens ({result['compression_ratio']})")
    assert result["removed_count"] > 0
    assert result["compressed_tokens"] < result["original_tokens"]

    # 测试 3: 验证
    print("\n=== 测试 3: 验证 ===")
    result = compact_memory_with_validation(messages, config)
    print(f"消息正确: {result['validation']['messages_correct']}")
    print(f"Token 减少: {result['validation']['tokens_reduced']}")
    print(f"最近保留: {result['validation']['recent_preserved']}")
    if result['validation']['errors']:
        print(f"错误: {result['validation']['errors']}")
    assert result["validation"]["messages_correct"]
    assert result["validation"]["tokens_reduced"]
    assert result["validation"]["recent_preserved"]

    # 测试 4: 摘要内容
    print("\n=== 测试 4: 摘要内容 ===")
    print(result['summary'][:500])

    print("\n✅ 所有测试通过！")
