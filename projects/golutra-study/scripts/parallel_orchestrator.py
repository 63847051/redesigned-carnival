#!/usr/bin/env python3
"""
并行执行编排器
支持 5+ 个 Agent 同时运行
"""

import asyncio
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue, Empty
import uuid

WORKSPACE_DIR = Path("/root/.openclaw/workspace")


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str = ""
    description: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __lt__(self, other):
        return self.priority.value < other.priority.value


class ResultCollector:
    """结果聚合器"""

    def __init__(self):
        self.results = {}
        self._lock = threading.Lock()

    def collect(self, task_id: str, result: Dict[str, Any]):
        """收集单个结果"""
        with self._lock:
            self.results[task_id] = {**result, "timestamp": datetime.now().isoformat()}

    def aggregate(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚合所有结果"""
        successful = [r for r in results if r.get("status") == "completed"]
        failed = [r for r in results if r.get("status") == "failed"]

        total_duration = sum(r.get("duration", 0) for r in results if r.get("duration"))

        return {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "total_duration": total_duration,
            "avg_duration": total_duration / len(results) if results else 0,
            "details": results,
            "timestamp": datetime.now().isoformat(),
        }


class AgentSession:
    """Agent 会话管理"""

    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = "idle"
        self.current_task: Optional[Task] = None
        self.created_at = datetime.now()

    def __repr__(self):
        return f"AgentSession(id={self.agent_id}, type={self.agent_type}, status={self.status})"


class TaskExecutor:
    """任务执行器基类"""

    def __init__(self, agent_type: str):
        self.agent_type = agent_type

    def execute(self, task: Task) -> Dict[str, Any]:
        """执行任务，子类重写"""
        raise NotImplementedError


class TechTaskExecutor(TaskExecutor):
    """技术任务执行器"""

    def __init__(self):
        super().__init__("tech")

    def execute(self, task: Task) -> Dict[str, Any]:
        time.sleep(0.1)
        return {
            "task_id": task.id,
            "status": "completed",
            "result": f"Tech task '{task.description}' completed",
            "output": f"Executed tech task: {task.id}",
        }


class LogTaskExecutor(TaskExecutor):
    """日志任务执行器"""

    def __init__(self):
        super().__init__("log")

    def execute(self, task: Task) -> Dict[str, Any]:
        time.sleep(0.1)
        return {
            "task_id": task.id,
            "status": "completed",
            "result": f"Log task '{task.description}' completed",
            "output": f"Logged: {task.id}",
        }


class DesignTaskExecutor(TaskExecutor):
    """设计任务执行器"""

    def __init__(self):
        super().__init__("design")

    def execute(self, task: Task) -> Dict[str, Any]:
        time.sleep(0.1)
        return {
            "task_id": task.id,
            "status": "completed",
            "result": f"Design task '{task.description}' completed",
            "output": f"Designed: {task.id}",
        }


class ParallelExecutionOrchestrator:
    """并行执行编排器"""

    def __init__(self, max_agents: int = 5):
        self.max_agents = max_agents
        self.active_agents: Dict[str, AgentSession] = {}
        self.task_queue: List[Task] = []
        self.result_collector = ResultCollector()
        self.executors = {
            "tech": TechTaskExecutor(),
            "log": LogTaskExecutor(),
            "design": DesignTaskExecutor(),
        }
        self._lock = threading.Lock()
        self._semaphore = threading.Semaphore(max_agents)

    def add_task(self, task: Task):
        """添加任务到队列"""
        with self._lock:
            self.task_queue.append(task)
            self.task_queue.sort(key=lambda t: t.priority.value)

    def add_tasks(self, tasks: List[Dict[str, Any]]):
        """批量添加任务"""
        for task_data in tasks:
            priority = TaskPriority[task_data.get("priority", "NORMAL").upper()]
            task = Task(
                id=task_data.get("id", str(uuid.uuid4())[:8]),
                type=task_data.get("type", "tech"),
                description=task_data.get("description", ""),
                priority=priority,
                payload=task_data.get("payload", {}),
            )
            self.add_task(task)

    def execute_parallel(
        self, tasks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        并行执行多个任务

        参数:
            tasks: 任务列表（如果为None，则执行队列中的任务）

        返回:
            聚合结果
        """
        if tasks:
            self.add_tasks(tasks)

        if not self.task_queue:
            return {"total": 0, "successful": 0, "failed": 0, "details": []}

        results = []
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_agents) as executor:
            future_to_task = {
                executor.submit(self._execute_single_task, task): task
                for task in self.task_queue
            }

            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.result_collector.collect(task.id, result)
                except Exception as e:
                    error_result = {
                        "task_id": task.id,
                        "status": "failed",
                        "error": str(e),
                    }
                    results.append(error_result)
                    self.result_collector.collect(task.id, error_result)

        total_duration = time.time() - start_time
        aggregated = self.result_collector.aggregate(results)
        aggregated["orchestration_duration"] = total_duration

        self.task_queue.clear()
        return aggregated

    def _execute_single_task(self, task: Task) -> Dict[str, Any]:
        """执行单个任务"""
        with self._semaphore:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()

            start_time = time.time()
            agent_id = f"agent-{task.id}"

            with self._lock:
                self.active_agents[agent_id] = AgentSession(task.id, task.type)
                self.active_agents[agent_id].status = "running"
                self.active_agents[agent_id].current_task = task

            try:
                executor = self.executors.get(task.type, self.executors["tech"])
                result = executor.execute(task)

                task.status = TaskStatus.COMPLETED
                task.result = result
                result["duration"] = time.time() - start_time

                return result

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                return {
                    "task_id": task.id,
                    "status": "failed",
                    "error": str(e),
                    "duration": time.time() - start_time,
                }

            finally:
                with self._lock:
                    if agent_id in self.active_agents:
                        self.active_agents[agent_id].status = "idle"
                        self.active_agents[agent_id].current_task = None

    def get_status(self) -> Dict[str, Any]:
        """获取编排器状态"""
        return {
            "max_agents": self.max_agents,
            "active_agents": len(self.active_agents),
            "queued_tasks": len(self.task_queue),
            "agents": {
                agent_id: {
                    "type": session.agent_type,
                    "status": session.status,
                    "current_task": session.current_task.id
                    if session.current_task
                    else None,
                }
                for agent_id, session in self.active_agents.items()
            },
        }


def main():
    """测试入口"""
    orchestrator = ParallelExecutionOrchestrator(max_agents=5)

    tasks = [
        {
            "id": "task-1",
            "type": "tech",
            "description": "代码任务 1",
            "priority": "HIGH",
        },
        {
            "id": "task-2",
            "type": "log",
            "description": "日志任务 1",
            "priority": "NORMAL",
        },
        {
            "id": "task-3",
            "type": "design",
            "description": "设计任务 1",
            "priority": "NORMAL",
        },
        {
            "id": "task-4",
            "type": "tech",
            "description": "代码任务 2",
            "priority": "LOW",
        },
        {
            "id": "task-5",
            "type": "log",
            "description": "日志任务 2",
            "priority": "CRITICAL",
        },
        {
            "id": "task-6",
            "type": "design",
            "description": "设计任务 2",
            "priority": "NORMAL",
        },
        {
            "id": "task-7",
            "type": "tech",
            "description": "代码任务 3",
            "priority": "NORMAL",
        },
    ]

    print("=" * 50)
    print("并行执行编排器测试")
    print("=" * 50)

    results = orchestrator.execute_parallel(tasks)

    print("\n并行执行结果:")
    print(json.dumps(results, indent=2, ensure_ascii=False))

    print("\n编排器状态:")
    print(json.dumps(orchestrator.get_status(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
