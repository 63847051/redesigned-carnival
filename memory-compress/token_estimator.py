"""
Token 估算器
粗略估算文本的 token 数量

参考：Claude Code compact.rs:326-338 (estimate_message_tokens)
"""

def estimate_tokens(text: str) -> int:
    """
    粗略估算 token 数量

    规则：约每 4 个字符 = 1 个 token
    英文：1 个单词 ≈ 1 个 token
    中文：1 个汉字 ≈ 1-2 个 token

    参数:
        text: 要估算的文本

    返回:
        估算的 token 数量
    """
    if not text:
        return 0

    # 简单估算：每 4 个字符 = 1 个 token
    return len(text) // 4 + 1


def estimate_message_tokens(message: dict) -> int:
    """
    估算一条消息的 token 数量

    参数:
        message: 消息字典，包含 role 和 content

    返回:
        估算的 token 数量
    """
    content = message.get("content", "")

    # 如果 content 是字符串，直接估算
    if isinstance(content, str):
        return estimate_tokens(content)

    # 如果 content 是列表（ContentBlock），遍历估算
    if isinstance(content, list):
        total = 0
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    total += estimate_tokens(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    total += estimate_tokens(block.get("name", "")) + estimate_tokens(block.get("input", ""))
                elif block.get("type") == "tool_result":
                    total += estimate_tokens(block.get("tool_name", "")) + estimate_tokens(block.get("output", ""))
        return total

    return 0


def estimate_messages_tokens(messages: list) -> int:
    """
    估算多条消息的总 token 数量

    参数:
        messages: 消息列表

    返回:
        总 token 数量
    """
    return sum(estimate_message_tokens(msg) for msg in messages)


# 测试
if __name__ == "__main__":
    # 测试 1: 简单文本
    assert estimate_tokens("hello") == 2  # 5 chars // 4 + 1
    assert estimate_tokens("hello world") == 3  # 11 chars // 4 + 1

    # 测试 2: 空字符串
    assert estimate_tokens("") == 0
    assert estimate_tokens("   ") == 1

    # 测试 3: 中文
    assert estimate_tokens("你好") == 1  # 2 chars // 4 + 1
    assert estimate_tokens("你好世界") == 2  # 4 chars // 4 + 1
    assert estimate_tokens("你好世界你好") == 2  # 6 chars // 4 + 1

    # 测试 4: 消息估算
    msg = {
        "role": "user",
        "content": "hello world"
    }
    assert estimate_message_tokens(msg) == 3

    # 测试 5: ContentBlock 消息
    msg_blocks = {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "let me check"},
            {"type": "tool_use", "name": "bash", "input": "ls"}
        ]
    }
    tokens = estimate_message_tokens(msg_blocks)
    print(f"ContentBlock 消息 token 数: {tokens}")

    # 测试 6: 多条消息
    messages = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi there"},
        {"role": "user", "content": "how are you?"}
    ]
    total = estimate_messages_tokens(messages)
    print(f"多条消息总 token 数: {total}")

    print("✅ 所有测试通过！")
