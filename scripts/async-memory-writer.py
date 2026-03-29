#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步批量写入记忆系统
- 积累多条消息后一次性写入
- 不阻塞对话，后台处理
- 失败自动重试
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from threading import Thread, Lock
from queue import Queue
from typing import Dict, List, Optional

# 配置
MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
QUEUE_FILE = MEMORY_DIR / ".write_queue.json"
LOCK_FILE = MEMORY_DIR / ".write_queue.lock"
BATCH_SIZE = 10  # 批量写入大小
FLUSH_INTERVAL = 60  # 自动刷新间隔（秒）
MAX_RETRIES = 3  # 最大重试次数

class AsyncMemoryWriter:
    """异步批量写入记忆系统"""

    def __init__(self):
        self.queue = Queue()
        self.lock = Lock()
        self.buffer: List[Dict] = []
        self.running = False
        self.writer_thread: Optional[Thread] = None

    def start(self):
        """启动异步写入器"""
        if self.running:
            return

        self.running = True
        self.writer_thread = Thread(target=self._write_loop, daemon=True)
        self.writer_thread.start()
        print(f"[AsyncMemoryWriter] 已启动")

    def stop(self):
        """停止异步写入器"""
        if not self.running:
            return

        self.running = False
        if self.writer_thread:
            self.writer_thread.join(timeout=5)

        # 刷新剩余消息
        self.flush()

        print(f"[AsyncMemoryWriter] 已停止")

    def add(self, message: Dict):
        """
        添加消息到写入队列
        message: {
            "type": "conversation|system|event",
            "timestamp": "2026-03-29 08:34:00",
            "content": "消息内容",
            "metadata": {...}
        }
        """
        with self.lock:
            self.buffer.append(message)

            # 达到批量大小，立即写入
            if len(self.buffer) >= BATCH_SIZE:
                self._write_buffer()

    def _write_loop(self):
        """写入循环（后台线程）"""
        last_flush = time.time()

        while self.running:
            time.sleep(1)  # 每秒检查一次

            # 定时刷新
            if time.time() - last_flush >= FLUSH_INTERVAL:
                with self.lock:
                    if self.buffer:
                        self._write_buffer()
                last_flush = time.time()

    def _write_buffer(self):
        """写入缓冲区到磁盘"""
        if not self.buffer:
            return

        # 复制缓冲区并清空
        with self.lock:
            messages = self.buffer.copy()
            self.buffer.clear()

        # 写入消息
        for message in messages:
            self._write_message(message, retry=0)

    def _write_message(self, message: Dict, retry: int):
        """写入单条消息"""
        try:
            msg_type = message.get("type", "conversation")
            timestamp = message.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            content = message.get("content", "")
            metadata = message.get("metadata", {})

            # 确定目标文件
            if msg_type == "conversation":
                # 对话消息 → 每日记忆文件
                date_str = datetime.now().strftime("%Y-%m-%d")
                target_file = MEMORY_DIR / f"{date_str}.md"

                # 格式化内容
                formatted = f"\n## {timestamp}\n{content}\n"

                # 追加写入
                with open(target_file, "a", encoding="utf-8") as f:
                    f.write(formatted)

            elif msg_type == "system":
                # 系统消息 → 系统日志
                target_file = MEMORY_DIR / ".system.log"

                with open(target_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {content}\n")

            elif msg_type == "event":
                # 事件 → 事件日志
                target_file = MEMORY_DIR / ".events.log"

                event_data = {
                    "timestamp": timestamp,
                    "event": content,
                    "metadata": metadata
                }

                with open(target_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event_data, ensure_ascii=False) + "\n")

            # 成功写入
            print(f"[AsyncMemoryWriter] ✓ 写入成功: {msg_type}")

        except Exception as e:
            print(f"[AsyncMemoryWriter] ✗ 写入失败: {e}")

            # 重试
            if retry < MAX_RETRIES:
                print(f"[AsyncMemoryWriter] ↻ 重试 {retry + 1}/{MAX_RETRIES}")
                time.sleep(1)  # 等待 1 秒后重试
                self._write_message(message, retry + 1)
            else:
                print(f"[AsyncMemoryWriter] ✗ 达到最大重试次数，放弃")

                # 保存到失败队列
                self._save_to_failed_queue(message)

    def _save_to_failed_queue(self, message: Dict):
        """保存失败的消息到队列文件"""
        try:
            with open(QUEUE_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(message, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[AsyncMemoryWriter] ✗ 保存失败队列出错: {e}")

    def flush(self):
        """立即刷新缓冲区"""
        with self.lock:
            if self.buffer:
                self._write_buffer()

    def status(self) -> Dict:
        """获取状态"""
        with self.lock:
            return {
                "running": self.running,
                "buffer_size": len(self.buffer),
                "queue_file": str(QUEUE_FILE),
            }

# 全局实例
_writer: Optional[AsyncMemoryWriter] = None

def get_writer() -> AsyncMemoryWriter:
    """获取全局写入器实例"""
    global _writer
    if _writer is None:
        _writer = AsyncMemoryWriter()
        _writer.start()
    return _writer

def add_message(message: Dict):
    """添加消息到写入队列"""
    writer = get_writer()
    writer.add(message)

def flush():
    """刷新缓冲区"""
    writer = get_writer()
    writer.flush()

def status() -> Dict:
    """获取状态"""
    writer = get_writer()
    return writer.status()

# CLI 接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="异步批量写入记忆系统")
    parser.add_argument("action", choices=["start", "stop", "flush", "status", "test"],
                       help="操作: start(启动), stop(停止), flush(刷新), status(状态), test(测试)")
    parser.add_argument("--type", default="conversation",
                       help="消息类型: conversation, system, event")
    parser.add_argument("--content", help="消息内容（测试用）")

    args = parser.parse_args()

    writer = get_writer()

    if args.action == "start":
        writer.start()

    elif args.action == "stop":
        writer.stop()

    elif args.action == "flush":
        writer.flush()

    elif args.action == "status":
        print(json.dumps(writer.status(), indent=2, ensure_ascii=False))

    elif args.action == "test":
        # 测试写入
        test_message = {
            "type": args.type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": args.content or "这是一条测试消息",
            "metadata": {"test": True}
        }

        add_message(test_message)
        print(f"✓ 已添加测试消息: {test_message['content']}")
        print(f"当前缓冲区大小: {len(writer.buffer)}")
