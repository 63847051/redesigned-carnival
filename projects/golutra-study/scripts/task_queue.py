#!/usr/bin/env python3
"""
任务优先级队列
支持多级队列和优先级管理
"""

import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import PriorityQueue, Empty
from typing import Any, Dict, List, Optional, Callable


class PriorityLevel(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class TaskState(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class QueuedTask:
    priority: int
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    state: TaskState = TaskState.QUEUED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.created_at < other.created_at
        return self.priority < other.priority


class TaskQueue:
    """多级任务优先级队列"""

    def __init__(self, max_size: int = 0):
        self._queue = PriorityQueue(maxsize=max_size)
        self._tasks: Dict[str, QueuedTask] = {}
        self._lock = threading.RLock()
        self._callbacks: Dict[str, List[Callable]] = {
            "on_enqueue": [],
            "on_dequeue": [],
            "on_complete": [],
            "on_fail": [],
        }

    def enqueue(self, task: QueuedTask) -> str:
        """入队任务"""
        with self._lock:
            self._tasks[task.task_id] = task
            self._queue.put(task)
            self._trigger_callbacks("on_enqueue", task)
        return task.task_id

    def dequeue(self, timeout: Optional[float] = None) -> Optional[QueuedTask]:
        """出队任务"""
        try:
            task = self._queue.get(timeout=timeout)
            with self._lock:
                if task.task_id in self._tasks:
                    self._tasks[task.task_id].state = TaskState.RUNNING
                    self._tasks[task.task_id].started_at = datetime.now()
            self._trigger_callbacks("on_dequeue", task)
            return task
        except Empty:
            return None

    def get_task(self, task_id: str) -> Optional[QueuedTask]:
        """获取任务详情"""
        with self._lock:
            return self._tasks.get(task_id)

    def update_task_state(self, task_id: str, state: TaskState) -> bool:
        """更新任务状态"""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.state = state
                if state == TaskState.COMPLETED:
                    task.completed_at = datetime.now()
                    self._trigger_callbacks("on_complete", task)
                elif state == TaskState.FAILED:
                    self._trigger_callbacks("on_fail", task)
                return True
        return False

    def retry_task(self, task_id: str) -> bool:
        """重试失败任务"""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.state = TaskState.QUEUED
                    self._queue.put(task)
                    return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        return self.update_task_state(task_id, TaskState.CANCELLED)

    def get_pending_tasks(self) -> List[QueuedTask]:
        """获取待处理任务列表"""
        with self._lock:
            return [t for t in self._tasks.values() if t.state == TaskState.QUEUED]

    def get_running_tasks(self) -> List[QueuedTask]:
        """获取运行中任务列表"""
        with self._lock:
            return [t for t in self._tasks.values() if t.state == TaskState.RUNNING]

    def get_completed_tasks(self) -> List[QueuedTask]:
        """获取已完成任务列表"""
        with self._lock:
            return [t for t in self._tasks.values() if t.state == TaskState.COMPLETED]

    def size(self) -> int:
        """队列大小"""
        return self._queue.qsize()

    def is_empty(self) -> bool:
        """队列是否为空"""
        return self._queue.empty()

    def register_callback(self, event: str, callback: Callable):
        """注册回调"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _trigger_callbacks(self, event: str, task: QueuedTask):
        """触发回调"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(task)
            except Exception:
                pass


class MultiLevelQueue:
    """多级队列管理器"""

    def __init__(self):
        self.queues: Dict[PriorityLevel, TaskQueue] = {
            level: TaskQueue() for level in PriorityLevel
        }

    def enqueue(
        self, task: QueuedTask, priority: PriorityLevel = PriorityLevel.NORMAL
    ) -> str:
        """入队任务到指定优先级队列"""
        task.priority = priority.value
        return self.queues[priority].enqueue(task)

    def dequeue(self) -> Optional[QueuedTask]:
        """从最高优先级队列获取任务"""
        for level in PriorityLevel:
            task = self.queues[level].dequeue(timeout=0.001)
            if task:
                return task
        return None

    def get_queue_size(self, priority: Optional[PriorityLevel] = None) -> int:
        """获取队列大小"""
        if priority:
            return self.queues[priority].size()
        return sum(q.size() for q in self.queues.values())

    def get_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        stats = {}
        for level in PriorityLevel:
            queue = self.queues[level]
            stats[level.name] = {
                "size": queue.size(),
                "pending": len(queue.get_pending_tasks()),
                "running": len(queue.get_running_tasks()),
                "completed": len(queue.get_completed_tasks()),
            }
        return stats


class TaskScheduler:
    """任务调度器"""

    def __init__(self, max_workers: int = 5):
        self.multi_queue = MultiLevelQueue()
        self.max_workers = max_workers
        self.active_workers = 0
        self._lock = threading.Lock()
        self._running = False

    def submit(
        self,
        name: str,
        payload: Dict[str, Any],
        priority: PriorityLevel = PriorityLevel.NORMAL,
        max_retries: int = 3,
    ) -> str:
        """提交任务"""
        task = QueuedTask(
            priority=priority.value, name=name, payload=payload, max_retries=max_retries
        )
        return self.multi_queue.enqueue(task, priority)

    def start(self):
        """启动调度器"""
        self._running = True

    def stop(self):
        """停止调度器"""
        self._running = False

    def get_stats(self) -> Dict[str, Any]:
        """获取调度器统计"""
        return {
            "max_workers": self.max_workers,
            "active_workers": self.active_workers,
            "queue_stats": self.multi_queue.get_stats(),
        }


def main():
    """测试入口"""
    scheduler = TaskScheduler(max_workers=5)

    print("=" * 50)
    print("任务优先级队列测试")
    print("=" * 50)

    task_ids = [
        scheduler.submit("代码任务 1", {"type": "tech"}, PriorityLevel.HIGH),
        scheduler.submit("日志任务 1", {"type": "log"}, PriorityLevel.NORMAL),
        scheduler.submit("设计任务 1", {"type": "design"}, PriorityLevel.LOW),
        scheduler.submit("紧急任务", {"type": "urgent"}, PriorityLevel.CRITICAL),
        scheduler.submit("后台任务", {"type": "background"}, PriorityLevel.BACKGROUND),
    ]

    print(f"\n提交了 {len(task_ids)} 个任务:")
    for tid in task_ids:
        print(f"  - {tid}")

    print("\n队列统计:")
    print(scheduler.get_stats())

    print("\n多级队列统计:")
    print(scheduler.multi_queue.get_stats())


if __name__ == "__main__":
    main()
