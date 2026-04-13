"""
Compressed Snapshot System - 压缩快照系统

新增功能：
- 快照压缩（zlib）
- 增量快照
- 自动清理优化
"""

import os
import fcntl
import json
import hashlib
import zlib
import shutil
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# 导入原始系统
from snapshot_atomic import (
    SnapshotMetadata,
    AtomicFileWriter,
    SnapshotManager,
    StateLock,
    SnapshotAtomicSystem
)


@dataclass
class CompressedSnapshotMetadata:
    """压缩快照元数据"""
    snapshot_id: str
    timestamp: str
    checksum: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    description: str
    tags: List[str]
    is_incremental: bool
    parent_snapshot: Optional[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CompressedSnapshotManager(SnapshotManager):
    """压缩快照管理器"""
    
    def __init__(self, snapshot_dir: str = "/root/.openclaw/workspace/data/snapshots",
                 compression_level: int = 6):
        """
        初始化压缩快照管理器
        
        Args:
            snapshot_dir: 快照目录
            compression_level: 压缩级别（0-9）
        """
        super().__init__(snapshot_dir)
        self.compression_level = compression_level
        
    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        return zlib.compress(data, level=self.compression_level)
    
    def _decompress_data(self, compressed_data: bytes) -> bytes:
        """解压数据"""
        return zlib.decompress(compressed_data)
    
    def create_compressed_snapshot(self, source_path: str, description: str = "",
                                   tags: List[str] = None,
                                   parent_snapshot: str = None) -> Optional[CompressedSnapshotMetadata]:
        """创建压缩快照"""
        try:
            source = Path(source_path)
            if not source.exists():
                print(f"❌ 源文件不存在: {source_path}")
                return None
            
            # 生成快照 ID
            snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
            snapshot_path = self.snapshot_dir / f"{snapshot_id}.snap.gz"
            
            # 读取源文件
            with open(source, 'rb') as f:
                original_data = f.read()
            
            original_size = len(original_data)
            
            # 如果是增量快照，计算差异
            if parent_snapshot and parent_snapshot in self.index:
                parent_path = self.snapshot_dir / f"{parent_snapshot}.snap.gz"
                
                if parent_path.exists():
                    # 读取父快照
                    with open(parent_path, 'rb') as f:
                        compressed_parent = f.read()
                    
                    parent_data = self._decompress_data(compressed_parent)
                    
                    # 计算差异（简单版本：完整替换）
                    # TODO: 实现真正的增量差异（如 bsdiff）
                    delta_data = original_data  # 暂时存储完整数据
                    
                    is_incremental = True
                else:
                    delta_data = original_data
                    is_incremental = False
            else:
                delta_data = original_data
                is_incremental = False
            
            # 压缩数据
            compressed_data = self._compress_data(delta_data)
            compressed_size = len(compressed_data)
            
            # 计算压缩比
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            # 写入压缩快照
            with open(snapshot_path, 'wb') as f:
                f.write(compressed_data)
            
            # 计算校验和
            checksum = hashlib.sha256(compressed_data).hexdigest()
            
            # 创建元数据
            metadata = CompressedSnapshotMetadata(
                snapshot_id=snapshot_id,
                timestamp=datetime.now().isoformat(),
                checksum=checksum,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                description=description,
                tags=tags or [],
                is_incremental=is_incremental,
                parent_snapshot=parent_snapshot
            )
            
            # 更新索引
            self.index[snapshot_id] = metadata.to_dict()
            self._save_index()
            
            return metadata
            
        except Exception as e:
            print(f"❌ 创建压缩快照失败: {e}")
            return None
    
    def restore_compressed_snapshot(self, snapshot_id: str, target_path: str) -> bool:
        """恢复压缩快照"""
        try:
            if snapshot_id not in self.index:
                print(f"❌ 快照不存在: {snapshot_id}")
                return False
            
            snapshot_path = self.snapshot_dir / f"{snapshot_id}.snap.gz"
            if not snapshot_path.exists():
                print(f"❌ 快照文件不存在: {snapshot_path}")
                return False
            
            # 读取压缩数据
            with open(snapshot_path, 'rb') as f:
                compressed_data = f.read()
            
            # 验证校验和
            checksum = hashlib.sha256(compressed_data).hexdigest()
            stored_checksum = self.index[snapshot_id]["checksum"]
            
            if checksum != stored_checksum:
                print(f"❌ 快照校验和不匹配")
                return False
            
            # 解压数据
            decompressed_data = self._decompress_data(compressed_data)
            
            # 如果是增量快照，需要应用差异
            if self.index[snapshot_id]["is_incremental"]:
                parent_snapshot = self.index[snapshot_id]["parent_snapshot"]
                
                if parent_snapshot:
                    # 递归恢复父快照
                    parent_path = self.snapshot_dir / f"{parent_snapshot}.snap.gz"
                    
                    with open(parent_path, 'rb') as f:
                        compressed_parent = f.read()
                    
                    base_data = self._decompress_data(compressed_parent)
                    
                    # 应用差异（简单版本：直接使用增量数据）
                    # TODO: 实现真正的差异应用
                    final_data = decompressed_data
                else:
                    final_data = decompressed_data
            else:
                final_data = decompressed_data
            
            # 原子写入
            target = Path(target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            
            temp_path = f"{target_path}.tmp.restore"
            with open(temp_path, 'wb') as f:
                f.write(final_data)
            
            os.replace(temp_path, target_path)
            
            return True
            
        except Exception as e:
            print(f"❌ 恢复压缩快照失败: {e}")
            return False
    
    def list_snapshots(self, tag: str = None) -> List[CompressedSnapshotMetadata]:
        """列出快照"""
        snapshots = []
        
        for snapshot_id, data in self.index.items():
            if tag and tag not in data.get("tags", []):
                continue
            
            # 检查是否为压缩快照（有新字段）
            if "original_size" in data:
                # 新格式压缩快照
                snapshots.append(CompressedSnapshotMetadata(**data))
            else:
                # 旧格式快照，转换
                snapshots.append(CompressedSnapshotMetadata(
                    snapshot_id=data["snapshot_id"],
                    timestamp=data["timestamp"],
                    checksum=data["checksum"],
                    original_size=data["size"],
                    compressed_size=data["size"],  # 未压缩
                    compression_ratio=1.0,
                    description=data["description"],
                    tags=data["tags"],
                    is_incremental=False,
                    parent_snapshot=None
                ))
        
        # 按时间倒序
        snapshots.sort(key=lambda x: x.timestamp, reverse=True)
        return snapshots
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """获取压缩统计"""
        snapshots = self.list_snapshots()
        
        if not snapshots:
            return {
                "total_snapshots": 0,
                "total_original_size": 0,
                "total_compressed_size": 0,
                "average_compression_ratio": 0.0,
                "space_saved": 0,
                "incremental_count": 0
            }
        
        total_original = sum(s.original_size for s in snapshots)
        total_compressed = sum(s.compressed_size for s in snapshots)
        avg_ratio = total_compressed / total_original if total_original > 0 else 1.0
        incremental_count = sum(1 for s in snapshots if s.is_incremental)
        
        return {
            "total_snapshots": len(snapshots),
            "total_original_size": total_original,
            "total_compressed_size": total_compressed,
            "average_compression_ratio": avg_ratio,
            "space_saved": total_original - total_compressed,
            "space_saved_percentage": (1 - avg_ratio) * 100,
            "incremental_count": incremental_count
        }
    
    def optimize_storage(self, keep_count: int = 10,
                        prefer_incremental: bool = True) -> int:
        """优化存储"""
        try:
            snapshots = self.list_snapshots()
            
            if len(snapshots) <= keep_count:
                return 0
            
            # 删除策略：
            # 1. 优先删除非增量快照
            # 2. 保留最新的快照
            # 3. 保留有特殊标签的快照
            
            protected_tags = ["important", "critical", "milestone"]
            
            # 标记受保护的快照
            protected = set()
            for s in snapshots[:keep_count]:  # 最新的 N 个
                protected.add(s.snapshot_id)
            
            for s in snapshots:
                if any(tag in s.tags for tag in protected_tags):
                    protected.add(s.snapshot_id)
            
            # 删除未受保护的快照
            deleted_count = 0
            for snapshot in snapshots:
                if snapshot.snapshot_id not in protected:
                    if self.delete_snapshot(snapshot.snapshot_id):
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ 优化存储失败: {e}")
            return 0


class CompressedSnapshotAtomicSystem(SnapshotAtomicSystem):
    """压缩快照 + 原子写入系统（主接口）"""
    
    def __init__(self, snapshot_dir: str = "/root/.openclaw/workspace/data/snapshots",
                 compression_level: int = 6):
        """初始化系统"""
        # 使用压缩快照管理器
        self.snapshot_manager = CompressedSnapshotManager(snapshot_dir, compression_level)
        self.lock = StateLock()
    
    def save_state(self, file_path: str, content: str,
                   create_snapshot: bool = True,
                   description: str = "",
                   incremental: bool = True) -> bool:
        """保存状态（可选创建压缩快照）"""
        with self.lock:
            # 创建快照
            if create_snapshot and os.path.exists(file_path):
                # 查找父快照（最新的）
                snapshots = self.snapshot_manager.list_snapshots()
                parent_snapshot = snapshots[0].snapshot_id if snapshots else None
                
                self.snapshot_manager.create_compressed_snapshot(
                    file_path,
                    description=description or f"Auto snapshot before {datetime.now().isoformat()}",
                    parent_snapshot=parent_snapshot if incremental else None
                )
            
            # 原子写入
            writer = AtomicFileWriter(file_path)
            return writer.write(content)
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """获取压缩统计"""
        return self.snapshot_manager.get_compression_stats()
    
    def optimize_storage(self, keep_count: int = 10) -> int:
        """优化存储"""
        return self.snapshot_manager.optimize_storage(keep_count)


if __name__ == "__main__":
    # 测试
    system = CompressedSnapshotAtomicSystem()
    
    # 创建测试文件
    test_file = "/tmp/test_compressed.txt"
    test_content = "Hello, Compressed Snapshot! " * 1000
    
    system.save_state(test_file, test_content, create_snapshot=True, description="Test compressed snapshot")
    
    # 获取统计
    stats = system.get_compression_stats()
    print(f"✅ 压缩统计:")
    print(f"  总快照数: {stats['total_snapshots']}")
    print(f"  原始大小: {stats['total_original_size']} 字节")
    print(f"  压缩大小: {stats['total_compressed_size']} 字节")
    print(f"  压缩比: {stats['average_compression_ratio']:.2%}")
    print(f"  节省空间: {stats['space_saved']} 字节 ({stats['space_saved_percentage']:.1f}%)")
    print(f"  增量快照: {stats['incremental_count']} 个")
