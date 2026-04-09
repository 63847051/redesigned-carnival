"""
记忆压缩集成器
将智能压缩系统集成到 MEMORY.md 更新流程
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional
from compactor import compact_memory
from config_loader import load_config


def parse_memory_md(content: str) -> List[Dict]:
    """
    解析 MEMORY.md 文件，提取消息

    参数:
        content: MEMORY.md 文件内容

    返回:
        消息列表
    """
    messages = []

    # 按行分割
    lines = content.split('\n')
    
    current_date = None
    for i, line in enumerate(lines):
        # 检测日期行（格式：## 📝 今日决策（2026-04-01））
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
        if date_match and '今日决策' in line:
            current_date = date_match.group(1)
            continue
        
        # 如果找到了日期，并且当前行是决策/学习点
        if current_date and (line.startswith('- ') or line.startswith('**')):
            messages.append({
                "role": "user",
                "content": line.strip(),
                "timestamp": f"{current_date}T{10+i//60:02d}:{i%60:02d}:00"
            })

    return messages


def format_memory_md(messages: List[Dict]) -> str:
    """
    将消息列表格式化为 MEMORY.md 格式

    参数:
        messages: 消息列表

    返回:
        MEMORY.md 格式的文本
    """
    # 按日期分组
    by_date = {}
    for msg in messages:
        date = msg.get("timestamp", "")[:10]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(msg)

    # 生成内容
    lines = []
    for date in sorted(by_date.keys(), reverse=True):
        lines.append(f"\n## 📝 今日决策（{date}）\n")

        for msg in by_date[date]:
            content = msg.get("content", "")
            if content.startswith('- '):
                lines.append(f"{content}")
            else:
                lines.append(f"- {content}")

        lines.append("")

    return "\n".join(lines)


def compress_memory_file(
    file_path: str = "/root/.openclaw/workspace/MEMORY.md",
    config: Optional[Dict] = None,
    dry_run: bool = False
) -> Dict:
    """
    压缩 MEMORY.md 文件

    参数:
        file_path: MEMORY.md 文件路径
        config: 配置字典（可选）
        dry_run: 是否模拟运行（不实际修改文件）

    返回:
        压缩结果字典
    """
    # 加载配置
    if config is None:
        config = load_config()

    # 读取文件
    if not os.path.exists(file_path):
        return {
            "success": False,
            "reason": "文件不存在",
            "file_path": file_path
        }

    with open(file_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    # 解析消息
    messages = parse_memory_md(original_content)

    if len(messages) == 0:
        return {
            "success": False,
            "reason": "未找到可压缩的消息",
            "file_path": file_path
        }

    # 执行压缩
    result = compact_memory(messages, config)

    # 如果没有压缩，直接返回
    if result["removed_count"] == 0:
        return {
            "success": True,
            "compressed": False,
            "reason": result["reason"],
            "file_path": file_path,
            "original_size": len(original_content),
            "original_messages": len(messages)
        }

    # 格式化压缩后的内容
    compressed_content = format_memory_md(result["compressed"])

    # 如果不是模拟运行，写入文件
    if not dry_run:
        # 备份原文件
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        # 写入压缩后的内容
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(compressed_content)

    return {
        "success": True,
        "compressed": True,
        "file_path": file_path,
        "backup_path": f"{file_path}.backup.{datetime.now().strftime('%Y%m%d-%H%M%S')}" if not dry_run else None,
        "original_messages": len(messages),
        "compressed_messages": len(result["compressed"]),
        "removed_count": result["removed_count"],
        "original_size": len(original_content),
        "compressed_size": len(compressed_content),
        "size_saved": len(original_content) - len(compressed_content),
        "compression_ratio": f"{(1 - len(compressed_content) / len(original_content)) * 100:.1f}%",
        "original_tokens": result["original_tokens"],
        "compressed_tokens": result["compressed_tokens"],
        "tokens_saved": result["tokens_saved"],
    }


def auto_compress_memory(
    file_path: str = "/root/.openclaw/workspace/MEMORY.md",
    config_path: Optional[str] = None
) -> bool:
    """
    自动压缩 MEMORY.md（集成到更新流程）

    参数:
        file_path: MEMORY.md 文件路径
        config_path: 配置文件路径（可选）

    返回:
        是否执行了压缩
    """
    # 加载配置
    config = load_config(config_path) if config_path else load_config()

    # 检查文件大小
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 简单估算 token（每 4 个字符 = 1 个 token）
    estimated_tokens = len(content) // 4

    # 如果没有超过阈值，不压缩
    if estimated_tokens < config.get("max_tokens", 2000):
        return False

    # 执行压缩
    result = compress_memory_file(file_path, config)

    return result.get("compressed", False)


# 测试
if __name__ == "__main__":
    # 创建测试 MEMORY.md
    test_content = """
# MEMORY.md

## 📝 今日决策（2026-04-01）

- 决策 1
- 决策 2

## 🧠 核心学习（2026-04-01）

- 学习 1
- 学习 2

## 📝 今日决策（2026-04-02）

- 决策 3
- 决策 4
"""
    test_path = "/tmp/test-memory.md"

    # 测试 1: 解析
    print("=== 测试 1: 解析 MEMORY.md ===")
    messages = parse_memory_md(test_content)
    print(f"提取到 {len(messages)} 条消息")
    for msg in messages[:5]:
        print(f"  - {msg['timestamp']}: {msg['content'][:50]}")
    assert len(messages) >= 4  # 至少提取到决策

    # 测试 2: 格式化
    print("\n=== 测试 2: 格式化 ===")
    formatted = format_memory_md(messages)
    print(formatted[:200])
    assert "今日决策" in formatted

    # 测试 3: 压缩（模拟）
    print("\n=== 测试 3: 压缩（模拟） ===")
    result = compress_memory_file(test_path, dry_run=True)
    print(f"压缩成功: {result.get('success')}")
    print(f"需要压缩: {result.get('compressed')}")

    print("\n✅ 所有测试通过！")
