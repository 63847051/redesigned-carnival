#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步写入优化系统
- 动态批量大小
- 智能刷新策略
- 写入队列管理
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from queue import Queue, Empty

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
QUEUE_FILE = WORKSPACE / ".cache" / "write-queue.json"


class DynamicBatchWriter:
    """动态批量写入系统"""
    
    def __init__(
        self,
        min_batch_size: int = 5,
        max_batch_size: int = 20,
        max_wait_time: float = 30.0
    ):
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        
        self.queue = Queue()
        self.buffer: List[Dict] = []
        self.last_flush = time.time()
        self.is_running = False
        
        # 统计
        self.stats = {
            "total_writes": 0,
            "total_batches": 0,
            "avg_batch_size": 0,
            "total_time": 0
        }
    
    def _calculate_dynamic_batch_size(self) -> int:
        """
        动态计算批量大小
        
        策略：
        - 如果写入频繁，增加批量大小
        - 如果写入稀疏，减少批量大小
        """
        if not self.stats["total_batches"]:
            return self.min_batch_size
        
        avg_size = self.stats["avg_batch_size"]
        time_since_flush = time.time() - self.last_flush
        
        # 如果距离上次刷新很久，减少批量大小
        if time_since_flush > self.max_wait_time * 2:
            return max(self.min_batch_size, int(avg_size * 0.7))
        
        # 如果写入频繁，增加批量大小
        if avg_size >= self.min_batch_size * 1.5:
            return min(self.max_batch_size, int(avg_size * 1.2))
        
        return int(avg_size) if avg_size > 0 else self.min_batch_size
    
    def _flush(self):
        """刷新缓冲区到磁盘"""
        if not self.buffer:
            return
        
        start_time = time.time()
        
        # 写入所有文件
        for item in self.buffer:
            try:
                file_path = Path(item["path"])
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(item["content"])
                
                self.stats["total_writes"] += 1
                
            except Exception as e:
                print(f"写入失败: {item['path']}, 错误: {e}")
        
        # 更新统计
        batch_size = len(self.buffer)
        self.stats["total_batches"] += 1
        self.stats["avg_batch_size"] = (
            (self.stats["avg_batch_size"] * (self.stats["total_batches"] - 1) + batch_size) /
            self.stats["total_batches"]
        )
        self.stats["total_time"] += time.time() - start_time
        
        # 清空缓冲区
        self.buffer.clear()
        self.last_flush = time.time()
    
    def _worker(self):
        """工作线程"""
        self.is_running = True
        
        while self.is_running:
            try:
                # 检查队列
                try:
                    item = self.queue.get(timeout=1.0)
                    self.buffer.append(item)
                except Empty:
                    item = None
                
                # 检查是否需要刷新
                should_flush = False
                
                # 条件 1: 缓冲区满了
                batch_size = self._calculate_dynamic_batch_size()
                if len(self.buffer) >= batch_size:
                    should_flush = True
                
                # 条件 2: 超时
                elif self.buffer and (time.time() - self.last_flush) >= self.max_wait_time:
                    should_flush = True
                
                if should_flush:
                    self._flush()
                
            except Exception as e:
                print(f"工作线程错误: {e}")
        
        # 停止前刷新剩余数据
        if self.buffer:
            self._flush()
    
    def write(self, file_path: str, content: str):
        """
        异步写入
        
        Args:
            file_path: 文件路径
            content: 写入内容
        """
        self.queue.put({
            "path": file_path,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def start(self):
        """启动写入线程"""
        if not self.is_running:
            self.thread = threading.Thread(target=self._worker, daemon=True)
            self.thread.start()
    
    def stop(self, wait: bool = True):
        """
        停止写入线程
        
        Args:
            wait: 是否等待缓冲区刷新完成
        """
        self.is_running = False
        
        if wait and self.buffer:
            self._flush()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "buffer_size": len(self.buffer),
            "is_running": self.is_running,
            "dynamic_batch_size": self._calculate_dynamic_batch_size()
        }


# 全局写入器实例
_writer = None

def get_writer() -> DynamicBatchWriter:
    """获取全局写入器实例"""
    global _writer
    if _writer is None:
        _writer = DynamicBatchWriter()
        _writer.start()
    return _writer


def async_write(file_path: str, content: str):
    """
    异步写入（简化接口）
    
    Args:
        file_path: 文件路径
        content: 写入内容
    """
    writer = get_writer()
    writer.write(file_path, content)


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    import random
    
    print("="*60)
    print("异步写入优化系统测试")
    print("="*60)
    
    # 创建测试写入器
    writer = DynamicBatchWriter(
        min_batch_size=3,
        max_batch_size=10,
        max_wait_time=5.0
    )
    writer.start()
    
    # 测试写入
    print("\n测试动态批量写入:")
    
    test_file = MEMORY_DIR / "test-dynamic-batch.md"
    
    # 写入测试数据
    for i in range(15):
        content = f"\n## 测试条目 {i}\n\n时间: {datetime.now()}\n"
        writer.write(str(test_file), content)
        
        # 模拟随机间隔
        time.sleep(random.uniform(0.1, 0.3))
    
    # 等待写入完成
    time.sleep(1)
    
    # 获取统计
    stats = writer.get_stats()
    print(f"\n📊 写入统计:")
    print(f"   总写入数: {stats['total_writes']}")
    print(f"   总批次数: {stats['total_batches']}")
    print(f"   平均批量: {stats['avg_batch_size']:.1f}")
    print(f"   缓冲区大小: {stats['buffer_size']}")
    print(f"   动态批量大小: {stats['dynamic_batch_size']}")
    print(f"   总耗时: {stats['total_time']:.3f}s")
    
    # 停止写入器
    writer.stop()
    
    # 清理测试文件
    if test_file.exists():
        test_file.unlink()
    
    print("\n✅ 测试完成！")
