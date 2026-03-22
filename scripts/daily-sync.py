#!/usr/bin/env python3
"""
日志查缺补漏脚本 - daily-sync.py
彬子记忆系统 - 第三道防线第一部分：00:45 执行
功能：扫描24小时消息，结构化清洗，生成反思素材
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SESSIONS_DIR = WORKSPACE / ".openclaw" / "sessions"
LOG_DIR = WORKSPACE / "logs"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_DIR.mkdir(exist_ok=True)
    with open(LOG_DIR / "daily-sync.log", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")


def get_yesterday_date():
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def scan_24h_messages():
    """扫描过去24小时的session消息"""
    log("开始扫描24小时消息...")

    yesterday = get_yesterday_date()
    cutoff_time = datetime.now() - timedelta(hours=24)

    messages = []
    session_files = list(SESSIONS_DIR.glob("*.json"))

    for session_file in session_files:
        try:
            mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
            if mtime >= cutoff_time:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "messages" in data:
                        messages.extend(data["messages"])
                    elif isinstance(data, list):
                        messages.extend(data)
        except Exception as e:
            log(f"读取session错误: {session_file}: {e}")

    log(f"扫描完成: {len(messages)} 条消息")
    return messages


def clean_and_structure(messages):
    """结构化清洗消息"""
    log("开始结构化清洗...")

    insights = {
        "decisions": [],
        "completions": [],
        "problems": [],
        "lessons": [],
        "questions": [],
        "tasks": [],
    }

    keywords = {
        "decisions": ["决定", "结论", "最终方案", "采用", "选择"],
        "completions": ["完成", "已做好", "已生成", "已创建", "已写入"],
        "problems": ["问题", "错误", "失败", "无法", "bug"],
        "lessons": ["教训", "注意", "经验", "以后要", "应该"],
        "questions": ["?", "？", "怎么做", "如何"],
        "tasks": ["待做", "待办", "需要", "下一步"],
    }

    for msg in messages:
        content = ""
        if isinstance(msg, dict):
            content = msg.get("content", "")
            role = msg.get("role", "")
        else:
            content = str(msg)
            role = ""

        if not content:
            continue

        for category, words in keywords.items():
            for word in words:
                if word in content and len(content) > 20:
                    entry = {
                        "content": content[:200],
                        "role": role,
                        "category": category,
                        "time": datetime.now().isoformat(),
                    }
                    if entry not in insights[category]:
                        insights[category].append(entry)
                    break

    for category in insights:
        log(f"  {category}: {len(insights[category])} 条")

    return insights


def generate_reflection_prep(insights):
    """生成反思素材"""
    log("生成反思素材...")

    yesterday = get_yesterday_date()
    prep_file = MEMORY_DIR / f"{yesterday}-reflection-prep.md"

    MEMORY_DIR.mkdir(exist_ok=True)

    with open(prep_file, "w", encoding="utf-8") as f:
        f.write(f"# 反思素材 - {yesterday}\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        for category, items in insights.items():
            f.write(f"## {category.upper()}\n\n")
            if items:
                for i, item in enumerate(items[:10], 1):  # 最多10条
                    content = item["content"].replace("\n", " ")[:150]
                    role = item.get("role", "")
                    f.write(f"{i}. [{role}] {content}...\n")
            else:
                f.write("*无记录*\n")
            f.write("\n")

        f.write("---\n")
        f.write(f"*由 daily-sync.py 自动生成*\n")

    log(f"反思素材已写入: {prep_file}")
    return prep_file


def main():
    log("========== 日志查缺补漏开始 ==========")

    messages = scan_24h_messages()
    insights = clean_and_structure(messages)
    prep_file = generate_reflection_prep(insights)

    log("========== 日志查缺补漏完成 ==========")
    return prep_file


if __name__ == "__main__":
    main()
