#!/usr/bin/env python3
"""
Agent Diary - 专业 Agent 独立记忆系统
每个专业 Agent 维护自己的日记，跨会话持久化
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DIARY_DIR = Path("/root/.openclaw/memory-tdai/agents")


class AgentDiary:
    """Agent 日记管理器"""

    def __init__(self):
        self.diary_dir = DIARY_DIR
        self.diary_dir.mkdir(parents=True, exist_ok=True)

    def write(self, agent_id: str, entry: str, rating: Optional[int] = None):
        """写日记"""
        diary_path = self.diary_dir / f"{agent_id}_diary.md"

        # 准备日记条目
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rating_str = f" {'⭐' * rating if rating else ''}" if rating else ""

        entry_text = f"""
## {timestamp}{rating_str}

{entry}
---

"""

        # 追加到日记文件
        with open(diary_path, "a", encoding="utf-8") as f:
            f.write(entry_text)

        print(f"✅ {agent_id} 日记已写入")

    def read(self, agent_id: str, last_n: int = 10) -> List[Dict]:
        """读最近 N 条日记"""
        diary_path = self.diary_dir / f"{agent_id}_diary.md"

        if not diary_path.exists():
            return []

        with open(diary_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析日记条目
        entries = []
        for entry_block in content.split("## ")[1:]:  # 跳过第一个空块
            lines = entry_block.strip().split("\n")
            if not lines:
                continue

            # 提取时间戳和内容
            timestamp_line = lines[0]
            content_lines = lines[1:-1]  # 排除时间戳和分隔符
            content_text = "\n".join(content_lines).strip()

            entries.append({
                "timestamp": timestamp_line,
                "content": content_text
            })

        # 返回最近 N 条
        return entries[-last_n:] if len(entries) > last_n else entries

    def get_summary(self, agent_id: str) -> Dict:
        """获取 Agent 日记摘要"""
        entries = self.read(agent_id, last_n=100)

        total = len(entries)
        if total == 0:
            return {"total": 0}

        return {
            "agent_id": agent_id,
            "total": total,
            "total_entries": total,
            "last_entry": entries[-1]["timestamp"] if entries else None
        }


def demo():
    """演示 Agent Diary 功能"""
    print("=" * 50)
    print("📔 Agent Diary 演示")
    print("=" * 50)

    diary = AgentDiary()

    # 写入示例日记
    print("\n📝 写入示例日记...")

    diary.write("xiaoxin",
        "完成了 FinanceDatabase 集成项目\n"
        "- 健康度监控系统：70/100 分\n"
        "- 高级筛选器：多维度搜索\n"
        "- 报告生成器：CSV/JSON 导出\n"
        "- 用时：1.5 小时",
        rating=5
    )

    diary.write("xiaoxin",
        "完成了 Golutra 并行执行增强\n"
        "- 并行执行编排器：3.5x 加速\n"
        "- 任务优先级队列：5 级优先级\n"
        "- 11 个测试全部通过\n"
        "- 用时：1 小时",
        rating=5
    )

    diary.write("xiaolan",
        "记录了今日的工作日志\n"
        "- 三个项目全部完成\n"
        "- 健康分数：80 分\n"
        "- 磁盘空间改善：98% → 88%",
        rating=4
    )

    # 读取日记
    print("\n📖 小新的日记（最近 3 条）:")
    xiaoxin_entries = diary.read("xiaoxin", last_n=3)
    for entry in xiaoxin_entries:
        print(f"\n  📅 {entry['timestamp']}")
        print(f"  {entry['content']}")

    # 摘要
    print("\n📊 Agent 日记摘要:")
    for agent_id in ["xiaoxin", "xiaolan", "designer"]:
        summary = diary.get_summary(agent_id)
        if summary["total"] > 0:
            print(f"  - {agent_id}: {summary['total_entries']} 条日记")
        else:
            print(f"  - {agent_id}: 0 条日记")

    print("\n✅ Agent Diary 演示完成！")
    print(f"📁 日记目录: {DIARY_DIR}")


if __name__ == "__main__":
    demo()
