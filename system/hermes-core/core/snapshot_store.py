"""
Hermes 核心存储系统 - 快照冻结 + 原子写入

快照冻结：加载时捕获知识状态，会话期间不刷新
原子写入：tempfile + os.replace() 确保写入安全
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import threading


class SnapshotStore:
    """
    快照冻结存储系统

    核心特性：
    - 加载时捕获知识状态（快照）
    - 会话期间不刷新（冻结）
    - 原子写入保证数据安全
    """

    def __init__(self, base_path: str = None):
        self.base_path = (
            Path(base_path) if base_path else Path.home() / ".hermes" / "hermes-core"
        )
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._snapshots: Dict[str, Dict] = {}
        self._frozen: bool = False

    def capture_snapshot(self, key: str, data: Dict[str, Any]) -> None:
        """捕获快照 - 在加载时调用，会话期间不刷新"""
        with self._lock:
            self._snapshots[key] = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "frozen": False,
            }

    def freeze(self, key: str) -> None:
        """冻结指定快照 - 会话期间不再更新"""
        with self._lock:
            if key in self._snapshots:
                self._snapshots[key]["frozen"] = True
                self._frozen = True

    def unfreeze(self, key: str) -> None:
        """解冻快照 - 允许更新"""
        with self._lock:
            if key in self._snapshots:
                self._snapshots[key]["frozen"] = False

    def get_snapshot(self, key: str) -> Optional[Dict[str, Any]]:
        """获取快照 - 返回冻结时的数据"""
        with self._lock:
            if key in self._snapshots:
                return self._snapshots[key].copy()
            return None

    def update_snapshot(self, key: str, data: Dict[str, Any]) -> bool:
        """更新快照 - 仅当未冻结时有效"""
        with self._lock:
            if key in self._snapshots and not self._snapshots[key]["frozen"]:
                self._snapshots[key]["data"] = data
                self._snapshots[key]["timestamp"] = datetime.now().isoformat()
                return True
            return False

    def is_frozen(self, key: str) -> bool:
        """检查快照是否冻结"""
        with self._lock:
            return self._snapshots.get(key, {}).get("frozen", False)

    def save_to_disk(self, key: str, filename: str = None) -> Path:
        """原子写入快照到磁盘"""
        with self._lock:
            if key not in self._snapshots:
                raise ValueError(f"Snapshot {key} not found")

            if filename is None:
                filename = f"{key}.json"

            filepath = self.base_path / filename
            temp_fd, temp_path = tempfile.mkstemp(
                dir=self.base_path, prefix=".tmp_", suffix=".json"
            )

            try:
                with os.fdopen(temp_fd, "w") as f:
                    json.dump(self._snapshots[key], f, indent=2, ensure_ascii=False)

                os.replace(temp_path, filepath)
                return filepath
            except Exception:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise

    def load_from_disk(self, key: str, filename: str = None) -> Dict:
        """从磁盘加载快照"""
        if filename is None:
            filename = f"{key}.json"

        filepath = self.base_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Snapshot file not found: {filepath}")

        with self._lock:
            with open(filepath, "r") as f:
                data = json.load(f)

            self._snapshots[key] = data
            return data

    def list_snapshots(self) -> list:
        """列出所有快照"""
        with self._lock:
            return [
                {
                    "key": key,
                    "timestamp": val.get("timestamp"),
                    "frozen": val.get("frozen", False),
                }
                for key, val in self._snapshots.items()
            ]

    def clear(self) -> None:
        """清除所有快照"""
        with self._lock:
            self._snapshots.clear()
            self._frozen = False


class AtomicWriter:
    """
    原子写入工具

    使用 tempfile + os.replace() 确保写入安全
    适用于任何需要安全写入的场景
    """

    def __init__(self, base_path: str = None):
        self.base_path = (
            Path(base_path) if base_path else Path.home() / ".hermes" / "hermes-core"
        )
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write_json(self, filepath: str, data: Any, indent: int = 2) -> Path:
        """原子写入 JSON 文件"""
        filepath = (
            self.base_path / filepath
            if not Path(filepath).is_absolute()
            else Path(filepath)
        )
        filepath.parent.mkdir(parents=True, exist_ok=True)

        temp_fd, temp_path = tempfile.mkstemp(
            dir=filepath.parent, prefix=".tmp_", suffix=".json"
        )

        try:
            with os.fdopen(temp_fd, "w") as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)

            os.replace(temp_path, filepath)
            return filepath
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def write_text(self, filepath: str, content: str, encoding: str = "utf-8") -> Path:
        """原子写入文本文件"""
        filepath = (
            self.base_path / filepath
            if not Path(filepath).is_absolute()
            else Path(filepath)
        )
        filepath.parent.mkdir(parents=True, exist_ok=True)

        temp_fd, temp_path = tempfile.mkstemp(
            dir=filepath.parent, prefix=".tmp_", suffix=".txt"
        )

        try:
            with os.fdopen(temp_fd, "w", encoding=encoding) as f:
                f.write(content)

            os.replace(temp_path, filepath)
            return filepath
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def write_bytes(self, filepath: str, data: bytes) -> Path:
        """原子写入二进制文件"""
        filepath = (
            self.base_path / filepath
            if not Path(filepath).is_absolute()
            else Path(filepath)
        )
        filepath.parent.mkdir(parents=True, exist_ok=True)

        temp_fd, temp_path = tempfile.mkstemp(
            dir=filepath.parent, prefix=".tmp_", suffix=".bin"
        )

        try:
            with os.fdopen(temp_fd, "wb") as f:
                f.write(data)

            os.replace(temp_path, filepath)
            return filepath
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def append_atomic(
        self, filepath: str, content: str, encoding: str = "utf-8"
    ) -> Path:
        """原子追加写入（先读后写）"""
        filepath = (
            self.base_path / filepath
            if not Path(filepath).is_absolute()
            else Path(filepath)
        )

        existing = ""
        if filepath.exists():
            existing = filepath.read_text(encoding=encoding)

        return self.write_text(str(filepath), existing + content, encoding)

    def read_json(self, filepath: str) -> Any:
        """读取 JSON 文件"""
        filepath = (
            self.base_path / filepath
            if not Path(filepath).is_absolute()
            else Path(filepath)
        )
        with open(filepath, "r") as f:
            return json.load(f)

    def read_text(self, filepath: str, encoding: str = "utf-8") -> str:
        """读取文本文件"""
        filepath = (
            self.base_path / filepath
            if not Path(filepath).is_absolute()
            else Path(filepath)
        )
        return filepath.read_text(encoding=encoding)

    def delete(self, filepath: str) -> bool:
        """安全删除文件"""
        filepath = (
            self.base_path / filepath
            if not Path(filepath).is_absolute()
            else Path(filepath)
        )
        if filepath.exists():
            filepath.unlink()
            return True
        return False


def get_snapshot_store() -> SnapshotStore:
    """获取全局快照存储实例"""
    global _snapshot_store
    if _snapshot_store is None:
        _snapshot_store = SnapshotStore()
    return _snapshot_store


def get_atomic_writer() -> AtomicWriter:
    """获取全局原子写入器实例"""
    global _atomic_writer
    if _atomic_writer is None:
        _atomic_writer = AtomicWriter()
    return _atomic_writer


_snapshot_store: Optional[SnapshotStore] = None
_atomic_writer: Optional[AtomicWriter] = None
