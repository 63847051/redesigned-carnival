#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步批量写入记忆系统 v2
- 简化设计，更可靠
- 真正的批量写入
- 不阻塞对话
"""

import json
import os
import time
import atexit
from datetime import datetime
from pathlib import Path
from threading import Thread, Lock
from typing import Dict, List

# 配置
MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
BUFFER_FILE = MEMORY_DIR / ".write_buffer.json"
BATCH_SIZE = 10  # 批量写入大小
FLUSH_INTERVAL = 30  # 自动刷新间隔（秒）

class AsyncMemoryWriter:
    """异步批量写入记忆系统"""

    def __init__(self):
        self.lock = Lock()
        self.buffer: List[Dict] = []
        self.running = False
        self.writer_thread: Thread = None

        # 注册退出时刷新
        atexit.register(self._on_exit)

    def start(self):
        """启动异步写入器"""
        if self.running:
            print("[AsyncMemoryWriter] 已经在运行")
            return

        self.running = True
        self.writer_thread = Thread(target=self._write_loop, daemon=True)
        self.writer_thread.start()
        print(f"[AsyncMemoryWriter] 已启动 (批量大小: {BATCH_SIZE}, 刷新间隔: {FLUSH_INTERVAL}s)")

    def stop(self):
        """停止异步写入器"""
        if not self.running:
            return

        print("[AsyncMemoryWriter] 正在停止...")
        self.running = False

        # 等待线程结束
        if self.writer_thread:
            self.writer_thread.join(timeout=5)

        # 刷新剩余消息
        self._flush()

        print("[AsyncMemoryWriter] 已停止")

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
            self.buffer.append({
                "type": message.get("type", "conversation"),
                "timestamp": message.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "content": message.get("content", ""),
                "metadata": message.get("metadata", {})
            })

            # 达到批量大小，立即触发写入
            if len(self.buffer) >= BATCH_SIZE:
                print(f"[AsyncMemoryWriter] 缓冲区已满 ({len(self.buffer)}/{BATCH_SIZE})，触发写入")
                # 在后台线程中写入，避免阻塞
                Thread(target=self._flush, daemon=True).start()

    def _write_loop(self):
        """写入循环（后台线程）"""
        last_flush = time.time()

        while self.running:
            time.sleep(1)  # 每秒检查一次

            # 定时刷新
            if time.time() - last_flush >= FLUSH_INTERVAL:
                with self.lock:
                    if self.buffer:
                        print(f"[AsyncMemoryWriter] 定时刷新 ({len(self.buffer)} 条消息)")
                        Thread(target=self._flush, daemon=True).start()
                last_flush = time.time()

    def _flush(self):
        """刷新缓冲区到磁盘"""
        with self.lock:
            if not self.buffer:
                return

            # 复制缓冲区并清空
            messages = self.buffer.copy()
            self.buffer.clear()

        # 写入消息（不持有锁，避免阻塞）
        try:
            self._write_messages(messages)
            print(f"[AsyncMemoryWriter] ✓ 成功写入 {len(messages)} 条消息")
        except Exception as e:
            print(f"[AsyncMemoryWriter] ✗ 写入失败: {e}")
            # 失败的消息保存到文件
            self._save_to_buffer_file(messages)

    def _write_messages(self, messages: List[Dict]):
        """批量写入消息到磁盘"""
        # 按类型分组
        by_type = {}
        for msg in messages:
            msg_type = msg["type"]
            if msg_type not in by_type:
                by_type[msg_type] = []
            by_type[msg_type].append(msg)

        # 写入每种类型
        for msg_type, type_messages in by_type.items():
            if msg_type == "conversation":
                self._write_conversations(type_messages)
            elif msg_type == "system":
                self._write_system_log(type_messages)
            elif msg_type == "event":
                self._write_events(type_messages)

    def _write_conversations(self, messages: List[Dict]):
        """写入对话消息到每日记忆文件"""
        # 按日期分组
        by_date = {}
        for msg in messages:
            # 从时间戳提取日期
            timestamp = msg["timestamp"]
            date_str = timestamp.split()[0]  # "2026-03-29"

            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(msg)

        # 写入每个日期的文件
        for date_str, date_messages in by_date.items():
            target_file = MEMORY_DIR / f"{date_str}.md"

            # 格式化内容
            lines = []
            for msg in date_messages:
                timestamp = msg["timestamp"]
                content = msg["content"]
                lines.append(f"\n## {timestamp}\n{content}\n")

            # 追加写入
            with open(target_file, "a", encoding="utf-8") as f:
                f.writelines(lines)

    def _write_system_log(self, messages: List[Dict]):
        """写入系统日志"""
        target_file = MEMORY_DIR / ".system.log"

        lines = []
        for msg in messages:
            timestamp = msg["timestamp"]
            content = msg["content"]
            lines.append(f"[{timestamp}] {content}\n")

        with open(target_file, "a", encoding="utf-8") as f:
            f.writelines(lines)

    def _write_events(self, messages: List[Dict]):
        """写入事件日志"""
        target_file = MEMORY_DIR / ".events.log"

        lines = []
        for msg in messages:
            event_data = {
                "timestamp": msg["timestamp"],
                "event": msg["content"],
                "metadata": msg.get("metadata", {})
            }
            lines.append(json.dumps(event_data, ensure_ascii=False) + "\n")

        with open(target_file, "a", encoding="utf-8") as f:
            f.writelines(lines)

    def _save_to_buffer_file(self, messages: List[Dict]):
        """保存失败的消息到缓冲文件"""
        try:
            with open(BUFFER_FILE, "a", encoding="utf-8") as f:
                for msg in messages:
                    f.write(json.dumps(msg, ensure_ascii=False) + "\n")
            print(f"[AsyncMemoryWriter] 失败的消息已保存到 {BUFFER_FILE}")
        except Exception as e:
            print(f"[AsyncMemoryWriter] ✗ 保存失败消息出错: {e}")

    def _on_exit(self):
        """退出时刷新"""
        print("[AsyncMemoryWriter] 退出时刷新缓冲区...")
        self._flush()

    def status(self) -> Dict:
        """获取状态"""
        with self.lock:
            return {
                "running": self.running,
                "buffer_size": len(self.buffer),
                "batch_size": BATCH_SIZE,
                "flush_interval": FLUSH_INTERVAL,
            }

# 全局实例
_writer: AsyncMemoryWriter = None

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
    writer._flush()

def status() -> Dict:
    """获取状态"""
    writer = get_writer()
    return writer.status()

# CLI 接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="异步批量写入记忆系统 v2")
    parser.add_argument("action", choices=["start", "stop", "flush", "status", "test"],
                       help="操作: start(启动), stop(停止), flush(刷新), status(状态), test(测试)")
    parser.add_argument("--type", default="conversation",
                       help="消息类型: conversation, system, event")
    parser.add_argument("--content", help="消息内容（测试用）")
    parser.add_argument("--count", type=int, default=1,
                       help="测试消息数量（默认: 1）")

    args = parser.parse_args()

    writer = get_writer()

    if args.action == "start":
        writer.start()

    elif args.action == "stop":
        writer.stop()

    elif args.action == "flush":
        writer._flush()

    elif args.action == "status":
        print(json.dumps(writer.status(), indent=2, ensure_ascii=False))

    elif args.action == "test":
        # 测试写入
        for i in range(args.count):
            test_message = {
                "type": args.type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": f"{args.content or '测试消息'} #{i+1}",
                "metadata": {"test": True, "index": i+1}
            }

            add_message(test_message)

        print(f"✓ 已添加 {args.count} 条测试消息")
        print(json.dumps(writer.status(), indent=2, ensure_ascii=False))
