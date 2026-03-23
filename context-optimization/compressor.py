import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ContextCompressor:
    """上下文压缩模块，保留最近消息，压缩旧消息"""

    def __init__(
        self,
        storage_dir: str = "/root/.openclaw/workspace/context-optimization/compressed",
    ):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.compression_history: List[Dict[str, Any]] = []

    def compress_context(
        self, messages: List[Dict[str, Any]], keep_recent: int = 10
    ) -> List[Dict[str, Any]]:
        """压缩上下文，保留最近的keep_recent条消息"""
        if len(messages) <= keep_recent:
            return messages

        recent = messages[-keep_recent:]
        older = messages[:-keep_recent]

        compressed_older = self._compress_messages(older)

        summary_msg = {
            "role": "system",
            "content": f"[已压缩 {len(older)} 条早期消息，保留摘要]",
            "timestamp": datetime.now().isoformat(),
            "compressed": True,
        }

        result = [summary_msg] + compressed_older + recent
        return result

    def _compress_messages(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """压缩旧消息列表"""
        if not messages:
            return []

        contents = []
        for msg in messages:
            content = msg.get("content", "")
            if content:
                contents.append(content[:200])

        summary = "; ".join(contents[:5])
        if len(contents) > 5:
            summary += f" ... (+{len(contents) - 5} more)"

        return [
            {
                "role": "system",
                "content": f"[消息摘要] {summary}",
                "timestamp": messages[0].get("timestamp", ""),
                "compressed": True,
            }
        ]

    def compress_by_token_budget(
        self, messages: List[Dict[str, Any]], max_tokens: int = 4000
    ) -> List[Dict[str, Any]]:
        """根据token预算压缩消息"""
        estimated_tokens = sum(len(m.get("content", "")) // 4 for m in messages)

        if estimated_tokens <= max_tokens:
            return messages

        keep_recent = max(5, len(messages) // 4)
        return self.compress_context(messages, keep_recent=keep_recent)

    def extract_key_info(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """从消息中提取关键信息"""
        key_info = {"topics": set(), "actions": set(), "entities": set()}

        for msg in messages:
            content = msg.get("content", "")

            if "task" in content.lower():
                key_info["actions"].add("task_execution")
            if "file" in content.lower() or "create" in content.lower():
                key_info["actions"].add("file_operation")
            if "search" in content.lower() or "find" in content.lower():
                key_info["actions"].add("search")

        return {
            "topics": list(key_info["topics"]),
            "actions": list(key_info["actions"]),
            "entities": list(key_info["entities"]),
            "message_count": len(messages),
        }

    def save_compressed(
        self, session_id: str, compressed_messages: List[Dict[str, Any]]
    ) -> str:
        """保存压缩后的上下文"""
        filepath = self.storage_dir / f"{session_id}_compressed.json"
        data = {
            "session_id": session_id,
            "messages": compressed_messages,
            "timestamp": datetime.now().isoformat(),
            "original_count": len(compressed_messages),
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(filepath)

    def load_compressed(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """加载压缩后的上下文"""
        filepath = self.storage_dir / f"{session_id}_compressed.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("messages")
        return None

    def get_compression_stats(
        self,
        original_messages: List[Dict[str, Any]],
        compressed_messages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """获取压缩统计信息"""
        original_tokens = sum(len(m.get("content", "")) // 4 for m in original_messages)
        compressed_tokens = sum(
            len(m.get("content", "")) // 4 for m in compressed_messages
        )

        return {
            "original_count": len(original_messages),
            "compressed_count": len(compressed_messages),
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "reduction_percentage": round(
                (1 - compressed_tokens / original_tokens) * 100, 2
            )
            if original_tokens > 0
            else 0,
        }
