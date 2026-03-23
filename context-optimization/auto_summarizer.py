import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class AutoSummarizer:
    """自动总结已完成任务的模块，使用快速模型压缩上下文"""

    def __init__(
        self,
        storage_dir: str = "/root/.openclaw/workspace/context-optimization/summaries",
    ):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.summary_history: List[Dict[str, Any]] = []

    def summarize_completed_tasks(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """总结已完成的任务列表"""
        completed_tasks = [t for t in tasks if t.get("status") == "completed"]

        summaries = []
        for task in completed_tasks:
            summary = self._generate_task_summary(task)
            summaries.append(summary)
            self.summary_history.append(
                {
                    "task_id": task.get("id"),
                    "summary": summary,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return summaries

    def _generate_task_summary(self, task: Dict[str, Any]) -> str:
        """生成简洁的任务总结"""
        task_id = task.get("id", "unknown")
        task_type = task.get("type", "unknown")
        result = task.get("result", "")

        summary = f"[任务 {task_id}] {task_type}: {result[:100]}"
        if len(result) > 100:
            summary += "..."

        return summary

    def create_context_summary(
        self, recent_messages: List[Dict[str, Any]], task_history: List[Dict[str, Any]]
    ) -> str:
        """创建上下文摘要，压缩历史消息"""
        lines = ["=== 上下文摘要 ==="]

        if recent_messages:
            lines.append(f"最近消息数: {len(recent_messages)}")
            lines.append(f"最后消息: {recent_messages[-1].get('content', '')[:50]}...")

        if task_history:
            completed = [t for t in task_history if t.get("status") == "completed"]
            lines.append(f"已完成任务: {len(completed)}")

            if completed:
                lines.append("已完成任务列表:")
                for task in completed[-5:]:
                    lines.append(f"  - {self._generate_task_summary(task)}")

        return "\n".join(lines)

    def save_summary(self, session_id: str, summary: str) -> str:
        """保存总结到文件"""
        filepath = self.storage_dir / f"{session_id}.json"
        data = {
            "session_id": session_id,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(filepath)

    def load_summary(self, session_id: str) -> Optional[str]:
        """加载保存的总结"""
        filepath = self.storage_dir / f"{session_id}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("summary")
        return None

    def get_token_savings(
        self, original_tokens: int, compressed_tokens: int
    ) -> Dict[str, Any]:
        """计算token节省情况"""
        savings = original_tokens - compressed_tokens
        percentage = (savings / original_tokens * 100) if original_tokens > 0 else 0
        return {
            "original": original_tokens,
            "compressed": compressed_tokens,
            "saved": savings,
            "percentage": round(percentage, 2),
        }
