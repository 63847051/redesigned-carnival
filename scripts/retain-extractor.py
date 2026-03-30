#!/usr/bin/env python3
"""
Retain 格式生成器
从用户消息中提取结构化记忆

使用方法:
    python3 retain-extractor.py "用户消息"

标签类型:
- W (World Fact) - 世界事实，客观持久
- B (Behavior) - 我们做了什么
- O (Opinion) - 观点/偏好，带信心度 (0.0-1.0)
"""

import sys
import re
from datetime import datetime

def extract_retain(message):
    """提取 Retain 格式的记忆"""

    retains = []

    # 提取世界事实 (W)
    # 关键词: 是、有、在、支持、不支持、API、配置
    fact_patterns = [
        r'不支持?\s+[\u4e00-\u9fa5A-Za-z0-9_]+',
        r'API[:：]\s*[\u4e00-\u9fa5A-Za-z0-9_]+',
        r'配置[:：]\s*[\u4e00-\u9fa5A-Za-z0-9_]+',
    ]

    for pattern in fact_patterns:
        matches = re.findall(pattern, message)
        for match in matches:
            retains.append({
                "type": "W",
                "content": match.strip(),
                "context": "用户告知"
            })

    # 提取行为 (B)
    # 关键词: 完成、发布、更新、删除、创建
    behavior_patterns = [
        r'(?:完成|发布|更新|删除|创建)[了]?\s*[\u4e00-\u9fa5A-Za-z0-9_]+',
    ]

    for pattern in behavior_patterns:
        matches = re.findall(pattern, message)
        for match in matches:
            retains.append({
                "type": "B",
                "content": match.strip(),
                "context": "已完成任务"
            })

    # 提取观点/偏好 (O)
    # 关键词: 觉得、认为、喜欢、不喜欢、应该、最好
    opinion_patterns = [
        r'(?:觉得|认为|喜欢|不喜欢|应该|最好)[^\n。]*',
    ]

    for pattern in opinion_patterns:
        matches = re.findall(pattern, message)
        for match in matches:
            retains.append({
                "type": "O",
                "content": match.strip(),
                "confidence": 0.8,  # 默认信心度
                "context": "用户偏好"
            })

    return retains


def format_retain(retains):
    """格式化 Retain 输出"""

    if not retains:
        return "## Retain\n（未提取到结构化记忆）"

    output = "## Retain\n"

    for retain in retains:
        r_type = retain["type"]
        content = retain["content"]

        if r_type == "O":
            confidence = retain.get("confidence", 0.8)
            output += f"- {r_type}(c={confidence}) @{retain['context']}: {content}\n"
        else:
            output += f"- {r_type} @{retain['context']}: {content}\n"

    return output


def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 retain-extractor.py \"用户消息\"")
        sys.exit(1)

    message = sys.argv[1]

    # 提取 Retain
    retains = extract_retain(message)

    # 格式化输出
    output = format_retain(retains)
    print(output)

    # 追加到今日日志
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = f"/root/.openclaw/workspace/memory/{today}.md"

    try:
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(f"\n{output}\n")
        print(f"\n✅ 已追加到 {memory_file}")
    except Exception as e:
        print(f"\n❌ 写入失败: {e}")


if __name__ == "__main__":
    main()
