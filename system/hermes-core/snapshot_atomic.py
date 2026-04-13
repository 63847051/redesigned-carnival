"""
Snapshot & Atomic Write System - 快照冻结 + 原子写入系统

基于 Hermes Agent 的状态管理机制实现
"""

import os
import fcntl
import json
import hashlib
import shutil
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class SnapshotMetadata:
    """快照元数据"""
    snapshot_id: str
    timestamp: str
    checksum: str
    size: int
    description: str
    tags: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AtomicFileWriter:
    """原子文件写入器"""
    
    def __init__(self, file_path: str):
        """初始化"""
        self.file_path = file_path
        self.temp_path = f"{file_path}.tmp.{os.getpid()}"
        
    def write(self, content: str, mode: str = "w") -> bool:
        """原子写入"""
        try:
            # 写入临时文件
            with open(self.temp_path, mode) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            
            # 原子重命名
            os.replace(self.temp_path, self.file_path)
            return True
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(self.temp_path):
                os.remove(self.temp_path)
            print(f"❌ 原子写入失败: {e}")
            return False
    
    def write_json(self, data: Dict[str, Any], indent: int = 2) -> bool:
        """原子写入 JSON"""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return self.write(content)
        except Exception as e:
            print(f"❌ JSON 写入失败: {e}")
            return False


class SnapshotManager:
    """快照管理器"""
    
    def __init__(self, snapshot_dir: str = "/root/.openclaw/workspace/data/snapshots"):
        """初始化"""
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.snapshot_dir / "index.json"
        self._load_index()
        
    def _load_index(self):
        """加载快照索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}
            
    def _save_index(self):
        """保存快照索引"""
        writer = AtomicFileWriter(str(self.index_file))
        writer.write_json(self.index)
        
    def _calculate_checksum(self, file_path: str) -> str:
        """计算文件校验和"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def create_snapshot(self, source_path: str, description: str = "", 
                       tags: List[str] = None) -> Optional[SnapshotMetadata]:
        """创建快照"""
        try:
            source = Path(source_path)
            if not source.exists():
                print(f"❌ 源文件不存在: {source_path}")
                return None
            
            # 生成快照 ID
            snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
            snapshot_path = self.snapshot_dir / f"{snapshot_id}.dat"
            
            # 复制文件
            shutil.copy2(source, snapshot_path)
            
            # 计算元数据
            checksum = self._calculate_checksum(str(snapshot_path))
            size = snapshot_path.stat().st_size
            
            metadata = SnapshotMetadata(
                snapshot_id=snapshot_id,
                timestamp=datetime.now().isoformat(),
                checksum=checksum,
                size=size,
                description=description,
                tags=tags or []
            )
            
            # 更新索引
            self.index[snapshot_id] = metadata.to_dict()
            self._save_index()
            
            return metadata
            
        except Exception as e:
            print(f"❌ 创建快照失败: {e}")
            return None
    
    def restore_snapshot(self, snapshot_id: str, target_path: str) -> bool:
        """恢复快照"""
        try:
            if snapshot_id not in self.index:
                print(f"❌ 快照不存在: {snapshot_id}")
                return False
            
            snapshot_path = self.snapshot_dir / f"{snapshot_id}.dat"
            if not snapshot_path.exists():
                print(f"❌ 快照文件不存在: {snapshot_path}")
                return False
            
            # 验证校验和
            current_checksum = self._calculate_checksum(str(snapshot_path))
            stored_checksum = self.index[snapshot_id]["checksum"]
            
            if current_checksum != stored_checksum:
                print(f"❌ 快照校验和不匹配")
                return False
            
            # 原子恢复
            target = Path(target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            
            temp_path = f"{target_path}.tmp.restore"
            shutil.copy2(snapshot_path, temp_path)
            os.replace(temp_path, target_path)
            
            return True
            
        except Exception as e:
            print(f"❌ 恢复快照失败: {e}")
            return False
    
    def list_snapshots(self, tag: str = None) -> List[SnapshotMetadata]:
        """列出快照"""
        snapshots = []
        
        for snapshot_id, data in self.index.items():
            if tag and tag not in data.get("tags", []):
                continue
                
            snapshots.append(SnapshotMetadata(**data))
        
        # 按时间倒序
        snapshots.sort(key=lambda x: x.timestamp, reverse=True)
        return snapshots
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """删除快照"""
        try:
            if snapshot_id not in self.index:
                return False
            
            snapshot_path = self.snapshot_dir / f"{snapshot_id}.dat"
            if snapshot_path.exists():
                snapshot_path.unlink()
            
            del self.index[snapshot_id]
            self._save_index()
            
            return True
            
        except Exception as e:
            print(f"❌ 删除快照失败: {e}")
            return False
    
    def cleanup_old_snapshots(self, keep_count: int = 10) -> int:
        """清理旧快照"""
        try:
            snapshots = self.list_snapshots()
            
            if len(snapshots) <= keep_count:
                return 0
            
            # 删除最旧的快照
            deleted_count = 0
            for snapshot in snapshots[keep_count:]:
                if self.delete_snapshot(snapshot.snapshot_id):
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ 清理快照失败: {e}")
            return 0


class StateLock:
    """状态锁（防止并发修改）"""
    
    def __init__(self, lock_file: str = "/tmp/openclaw_state.lock"):
        """初始化"""
        self.lock_file = lock_file
        self.lock_fd = None
        
    def acquire(self, timeout: int = 10) -> bool:
        """获取锁"""
        try:
            self.lock_fd = open(self.lock_file, 'w')
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            return False
            
    def release(self):
        """释放锁"""
        if self.lock_fd:
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
            self.lock_fd.close()
            self.lock_fd = None
            
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
    
    def __enter__(self):
        """上下文管理器入口"""
        self.acquire()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.release()


class SnapshotAtomicSystem:
    """快照 + 原子写入系统（主接口）"""
    
    def __init__(self, snapshot_dir: str = "/root/.openclaw/workspace/data/snapshots"):
        """初始化系统"""
        self.snapshot_manager = SnapshotManager(snapshot_dir)
        self.lock = StateLock()
        
    def save_state(self, file_path: str, content: str, 
                   create_snapshot: bool = True,
                   description: str = "") -> bool:
        """保存状态（可选创建快照）"""
        with self.lock:
            # 创建快照
            if create_snapshot and os.path.exists(file_path):
                self.snapshot_manager.create_snapshot(
                    file_path, 
                    description=description or f"Auto snapshot before {datetime.now().isoformat()}"
                )
            
            # 原子写入
            writer = AtomicFileWriter(file_path)
            return writer.write(content)
    
    def restore_state(self, file_path: str, snapshot_id: str) -> bool:
        """恢复状态"""
        with self.lock:
            return self.snapshot_manager.restore_snapshot(snapshot_id, file_path)
    
    def list_states(self) -> List[Dict]:
        """列出所有状态快照"""
        snapshots = self.snapshot_manager.list_snapshots()
        return [s.to_dict() for s in snapshots]
    
    def rollback(self, file_path: str, steps: int = 1) -> bool:
        """回滚到之前的快照"""
        snapshots = self.snapshot_manager.list_snapshots()
        
        if len(snapshots) < steps:
            print(f"❌ 没有足够的快照进行回滚")
            return False
        
        target_snapshot = snapshots[steps - 1]
        return self.restore_state(file_path, target_snapshot.snapshot_id)


if __name__ == "__main__":
    system = SnapshotAtomicSystem()
    
    # 测试
    test_file = "/tmp/test_state.txt"
    system.save_state(test_file, "Hello, OpenClaw!", create_snapshot=True, description="Initial state")
    print("✅ 快照 + 原子写入系统测试成功")
