import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import hashlib


class ResultOffloader:
    """中间结果卸载模块，将中间结果保存到文件系统以减少上下文占用"""

    def __init__(
        self,
        storage_dir: str = "/root/.openclaw/workspace/context-optimization/results",
    ):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """加载索引文件"""
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"entries": {}}

    def _save_index(self):
        """保存索引文件"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def _generate_id(self, data: Dict[str, Any]) -> str:
        """生成唯一ID"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def save_result(
        self,
        session_id: str,
        key: str,
        result: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """保存中间结果"""
        result_id = self._generate_result_id(session_id, key)

        data = {
            "id": result_id,
            "session_id": session_id,
            "key": key,
            "result": result,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }

        filepath = self.storage_dir / f"{result_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.index["entries"][result_id] = {
            "key": key,
            "session_id": session_id,
            "filepath": str(filepath),
            "timestamp": data["timestamp"],
        }
        self._save_index()

        return result_id

    def _generate_result_id(self, session_id: str, key: str) -> str:
        """生成结果文件ID"""
        content = f"{session_id}:{key}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def load_result(self, session_id: str, key: str) -> Optional[Any]:
        """加载中间结果"""
        result_id = self._generate_result_id(session_id, key)

        for entry_id, entry in self.index["entries"].items():
            if entry_id == result_id:
                filepath = Path(entry["filepath"])
                if filepath.exists():
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return data.get("result")
        return None

    def list_results(self, session_id: str) -> List[Dict[str, Any]]:
        """列出指定会话的所有结果"""
        results = []
        for entry_id, entry in self.index["entries"].items():
            if entry.get("session_id") == session_id:
                results.append(
                    {
                        "id": entry_id,
                        "key": entry.get("key"),
                        "timestamp": entry.get("timestamp"),
                    }
                )
        return results

    def delete_result(self, session_id: str, key: str) -> bool:
        """删除中间结果"""
        result_id = self._generate_result_id(session_id, key)

        for entry_id in list(self.index["entries"].keys()):
            entry = self.index["entries"][entry_id]
            if entry.get("session_id") == session_id and entry.get("key") == key:
                filepath = Path(entry["filepath"])
                if filepath.exists():
                    filepath.unlink()
                del self.index["entries"][entry_id]
                self._save_index()
                return True
        return False

    def cleanup_session(self, session_id: str) -> int:
        """清理指定会话的所有结果"""
        count = 0
        for entry_id in list(self.index["entries"].keys()):
            entry = self.index["entries"][entry_id]
            if entry.get("session_id") == session_id:
                filepath = Path(entry["filepath"])
                if filepath.exists():
                    filepath.unlink()
                del self.index["entries"][entry_id]
                count += 1
        self._save_index()
        return count

    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        total_size = 0
        file_count = 0

        for entry in self.index["entries"].values():
            filepath = Path(entry.get("filepath", ""))
            if filepath.exists():
                total_size += filepath.stat().st_size
                file_count += 1

        return {
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
