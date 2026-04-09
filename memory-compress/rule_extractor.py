"""
规则提取器
从消息中提取结构化信息（待办事项、关键决策、重要链接、统计信息）

参考：Claude Code compact.rs:113-198 (summarize_messages)
"""

import re
from typing import List, Dict
from datetime import datetime


def extract_todos(messages: list) -> List[Dict]:
    """
    提取待办事项

    关键词：todo, next, pending, remaining, 待办, 计划

    参数:
        messages: 消息列表

    返回:
        待办事项列表，每项包含 {text, timestamp}
    """
    todos = []
    keywords = ["todo", "next", "pending", "remaining", "待办", "计划", "TODO", "NEXT", "PENDING"]

    for msg in messages:
        content = _extract_text_from_message(msg)
        if not content:
            continue

        # 检查是否包含关键词
        if any(keyword in content.lower() for keyword in keywords):
            # 提取待办事项文本
            todo_text = _extract_todo_text(content)
            if todo_text:
                todos.append({
                    "text": todo_text,
                    "timestamp": msg.get("timestamp", datetime.now().isoformat())
                })

    return todos


def extract_decisions(messages: list) -> List[Dict]:
    """
    提取关键决策

    关键词：决定, 选择, 采用, 方案, 规则, decision, choose, adopt

    参数:
        messages: 消息列表

    返回:
        决策列表，每项包含 {text, timestamp}
    """
    decisions = []
    keywords = ["决定", "选择", "采用", "方案"]  # 移除 "规则"，避免匹配到 "规则提取器" 等内容

    for msg in messages:
        content = _extract_text_from_message(msg)
        if not content:
            continue

        # 检查是否包含关键词（不区分大小写）
        content_lower = content.lower()
        if any(keyword.lower() in content_lower for keyword in keywords):
            # 提取决策文本
            decision_text = _extract_decision_text(content)
            if decision_text:
                decisions.append({
                    "text": decision_text,
                    "timestamp": msg.get("timestamp", datetime.now().isoformat())
                })

    return decisions


def extract_links(messages: list) -> List[str]:
    """
    提取重要链接

    匹配：http:// 或 https://

    参数:
        messages: 消息列表

    返回:
        链接列表
    """
    links = set()
    url_pattern = r'https?://[^\s<>"\'(){}]+'

    for msg in messages:
        content = _extract_text_from_message(msg)
        if not content:
            continue

        # 提取所有 URL
        urls = re.findall(url_pattern, content)
        links.update(urls)

    return list(links)


def extract_stats(messages: list) -> Dict:
    """
    提取统计信息

    统计：消息数量、类型分布、时间范围

    参数:
        messages: 消息列表

    返回:
        统计信息字典
    """
    stats = {
        "total_messages": len(messages),
        "user_messages": 0,
        "assistant_messages": 0,
        "tool_messages": 0,
        "system_messages": 0,
        "time_range": None
    }

    # 统计各类型消息数量
    for msg in messages:
        role = msg.get("role", "unknown")
        if role == "user":
            stats["user_messages"] += 1
        elif role == "assistant":
            stats["assistant_messages"] += 1
        elif role == "tool":
            stats["tool_messages"] += 1
        elif role == "system":
            stats["system_messages"] += 1

    # 提取时间范围
    timestamps = []
    for msg in messages:
        if "timestamp" in msg:
            timestamps.append(msg["timestamp"])

    if timestamps:
        stats["time_range"] = {
            "start": min(timestamps),
            "end": max(timestamps)
        }

    return stats


def extract_tools(messages: list) -> List[str]:
    """
    提取使用的工具名称

    参数:
        messages: 消息列表

    返回:
        工具名称列表
    """
    tools = set()

    for msg in messages:
        content = msg.get("content", [])

        # 如果是 ContentBlock 列表
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_name = block.get("name", "")
                    if tool_name:
                        tools.add(tool_name)

    return list(tools)


# ===== 辅助函数 =====

def _extract_text_from_message(msg: dict) -> str:
    """
    从消息中提取纯文本内容

    参数:
        msg: 消息字典

    返回:
        提取的文本
    """
    content = msg.get("content", "")

    # 如果是字符串，直接返回
    if isinstance(content, str):
        return content

    # 如果是列表（ContentBlock），提取所有 text 块
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    texts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    texts.append(f"[tool: {block.get('name', '')}({block.get('input', '')})]")
                elif block.get("type") == "tool_result":
                    texts.append(f"[result: {block.get('tool_name', '')}]")
        return " ".join(texts)

    return ""


def _extract_todo_text(text: str) -> str:
    """
    从文本中提取待办事项

    参数:
        text: 文本内容

    返回:
        提取的待办事项文本
    """
    # 简单提取：找到关键词后的第一句话
    patterns = [
        r'(?:todo|next|pending|待办|计划)[：:]\s*([^\n.]+)',
        r'(?:todo|next|pending|待办|计划)\s+([^\n.]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # 如果没有匹配到，返回包含关键词的句子
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # 找到完整的句子
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            return text[start:end].strip()

    return ""


def _extract_decision_text(text: str) -> str:
    """
    从文本中提取决策

    参数:
        text: 文本内容

    返回:
        提取的决策文本
    """
    # 如果文本本身就不长，直接返回
    if len(text) <= 100:
        return text.strip()

    # 尝试找到包含关键词的句子
    keywords = ["决定", "选择", "采用", "方案"]
    for keyword in keywords:
        if keyword in text:
            # 找到关键词的位置
            idx = text.find(keyword)
            # 提取周围的文本（前后各 50 个字符）
            start = max(0, idx - 50)
            end = min(len(text), idx + 50)
            return text[start:end].strip()

    return ""


# 测试
if __name__ == "__main__":
    # 测试消息
    messages = [
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
        },
        {
            "role": "tool",
            "content": "执行完成",
            "timestamp": "2026-04-09T10:20:00"
        }
    ]

    # 测试 1: 提取待办事项
    todos = extract_todos(messages)
    print(f"✅ 待办事项: {todos}")
    assert len(todos) == 2

    # 测试 2: 提取决策
    decisions = extract_decisions(messages)
    print(f"✅ 关键决策: {decisions}")
    assert len(decisions) == 1

    # 测试 3: 提取链接
    links = extract_links(messages)
    print(f"✅ 重要链接: {links}")
    assert len(links) == 1

    # 测试 4: 提取统计信息
    stats = extract_stats(messages)
    print(f"✅ 统计信息: {stats}")
    assert stats["total_messages"] == 5
    assert stats["user_messages"] == 2
    assert stats["assistant_messages"] == 2
    assert stats["tool_messages"] == 1

    print("\n✅ 所有测试通过！")
