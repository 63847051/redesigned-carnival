"""
摘要生成器
组装结构化摘要

参考：Claude Code compact.rs:113-198 (summarize_messages)
"""

from typing import List, Dict
from datetime import datetime
from rule_extractor import extract_todos, extract_decisions, extract_links, extract_stats, extract_tools


def generate_summary(messages: list, config: dict = None) -> str:
    """
    生成结构化摘要

    参数:
        messages: 要压缩的消息列表
        config: 配置字典

    返回:
        Markdown 格式的摘要文本
    """
    if config is None:
        config = {
            "include_timeline": True,
            "max_timeline_items": 10,
            "summary_format": "markdown"
        }

    # 提取结构化信息
    stats = extract_stats(messages)
    todos = extract_todos(messages)
    decisions = extract_decisions(messages)
    links = extract_links(messages)
    tools = extract_tools(messages)

    # 组装摘要
    lines = ["<summary>", ""]

    # 1. 统计信息
    lines.append("## 📊 统计信息")
    lines.append("")
    lines.append(f"- **总消息数**: {stats['total_messages']}")
    lines.append(f"- **用户消息**: {stats['user_messages']}")
    lines.append(f"- **助手消息**: {stats['assistant_messages']}")
    lines.append(f"- **工具消息**: {stats['tool_messages']}")

    if stats.get("time_range"):
        lines.append(f"- **时间范围**: {stats['time_range']['start']} ~ {stats['time_range']['end']}")

    lines.append("")

    # 2. 使用的工具
    if tools:
        lines.append("## 🔧 使用的工具")
        lines.append("")
        lines.append(f"- {', '.join(sorted(tools))}")
        lines.append("")

    # 3. 待办事项
    if todos:
        lines.append("## ✅ 待办事项")
        lines.append("")
        for todo in todos[:10]:  # 最多显示 10 个
            text = todo["text"]
            # 截断过长的文本
            if len(text) > 100:
                text = text[:97] + "..."
            lines.append(f"- [ ] {text}")
        lines.append("")

    # 4. 关键决策
    if decisions:
        lines.append("## 🎯 关键决策")
        lines.append("")
        for decision in decisions[:10]:  # 最多显示 10 个
            text = decision["text"]
            # 截断过长的文本
            if len(text) > 100:
                text = text[:97] + "..."
            timestamp = decision.get("timestamp", "")[:10]  # 只显示日期
            lines.append(f"- **{timestamp}**: {text}")
        lines.append("")

    # 5. 重要链接
    if links:
        lines.append("## 🔗 重要链接")
        lines.append("")
        for link in links[:10]:  # 最多显示 10 个
            lines.append(f"- {link}")
        lines.append("")

    # 6. 时间线（简化版）
    if config.get("include_timeline", True):
        lines.append("## 📅 时间线")
        lines.append("")

        max_items = config.get("max_timeline_items", 10)
        timeline_messages = messages[-max_items:] if len(messages) > max_items else messages

        for i, msg in enumerate(timeline_messages):
            role = msg.get("role", "unknown").upper()

            # 提取消息文本（更短的预览）
            content = _extract_text_preview(msg, max_length=40)

            lines.append(f"{i+1}. **{role}**: {content}")

        lines.append("")

    lines.append("</summary>")

    return "\n".join(lines)


def _extract_text_preview(msg: dict, max_length: int = 80) -> str:
    """
    从消息中提取文本预览

    参数:
        msg: 消息字典
        max_length: 最大长度

    返回:
        文本预览
    """
    content = msg.get("content", "")

    # 如果是字符串
    if isinstance(content, str):
        text = content.replace("\n", " ")
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        return text

    # 如果是列表（ContentBlock）
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    text = block.get("text", "").replace("\n", " ")
                    if len(text) > 40:
                        text = text[:37] + "..."
                    parts.append(text)
                elif block.get("type") == "tool_use":
                    parts.append(f"[tool: {block.get('name', '')}]")
                elif block.get("type") == "tool_result":
                    parts.append(f"[result: {block.get('tool_name', '')}]")

        result = " | ".join(parts)
        if len(result) > max_length:
            result = result[:max_length-3] + "..."
        return result

    return ""


def generate_summary_as_dict(messages: list, config: dict = None) -> dict:
    """
    生成结构化摘要（字典格式）

    参数:
        messages: 要压缩的消息列表
        config: 配置字典

    返回:
        摘要字典
    """
    if config is None:
        config = {}

    # 提取结构化信息
    stats = extract_stats(messages)
    todos = extract_todos(messages)
    decisions = extract_decisions(messages)
    links = extract_links(messages)
    tools = extract_tools(messages)

    return {
        "stats": stats,
        "tools": tools,
        "todos": todos,
        "decisions": decisions,
        "links": links,
        "message_count": len(messages),
        "generated_at": datetime.now().isoformat()
    }


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
        }
    ]

    # 测试 1: 生成 Markdown 摘要
    summary = generate_summary(messages)
    print("=== Markdown 摘要 ===")
    print(summary)
    print("\n")

    # 测试 2: 生成字典摘要
    summary_dict = generate_summary_as_dict(messages)
    print("=== 字典摘要 ===")
    print(f"统计: {summary_dict['stats']}")
    print(f"待办: {len(summary_dict['todos'])}")
    print(f"决策: {len(summary_dict['decisions'])}")
    print(f"链接: {len(summary_dict['links'])}")

    print("\n✅ 所有测试通过！")
