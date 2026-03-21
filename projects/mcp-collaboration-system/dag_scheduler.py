#!/usr/bin/env python3
"""
DAG 调度器 - Phase 1
实现任务依赖调度和拓扑排序
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    agent_id: str
    dependencies: List[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    metadata: Dict = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


class DAGScheduler:
    """DAG 调度器 - 管理任务依赖和执行顺序"""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.execution_order: List[str] = []

    def add_task(self, task: Task) -> bool:
        """
        添加任务

        参数:
            task: 任务对象

        返回:
            是否添加成功
        """
        # 检查任务是否已存在
        if task.id in self.tasks:
            return False

        # 检查依赖是否存在
        for dep_id in task.dependencies:
            if dep_id not in self.tasks and dep_id not in self.tasks:
                raise ValueError(f"依赖任务 {dep_id} 不存在")

        # 添加任务
        self.tasks[task.id] = task

        # 构建依赖图
        for dep_id in task.dependencies:
            self.adjacency[dep_id].add(task.id)
            self.reverse_adjacency[task.id].add(dep_id)

        return True

    def detect_cycle(self) -> Optional[List[str]]:
        """
        检测循环依赖

        返回:
            如果存在循环，返回循环路径；否则返回 None
        """
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.adjacency[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # 找到循环
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(node)
            return False

        for task_id in self.tasks:
            if task_id not in visited:
                if dfs(task_id):
                    return path[path.index(path[-1]):] + [path[-1]]

        return None

    def topological_sort(self) -> List[str]:
        """
        拓扑排序 - 确定任务执行顺序

        返回:
            任务 ID 列表（按执行顺序）
        """
        # 计算入度
        in_degree = {task_id: 0 for task_id in self.tasks}
        for task_id in self.tasks:
            for dep_id in self.tasks[task_id].dependencies:
                in_degree[task_id] += 1

        # 使用队列进行拓扑排序
        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            task_id = queue.popleft()
            result.append(task_id)

            # 减少依赖此任务的邻居的入度
            for neighbor in self.adjacency[task_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 检查是否所有任务都已排序
        if len(result) != len(self.tasks):
            raise ValueError("存在循环依赖，无法进行拓扑排序")

        self.execution_order = result
        return result

    def get_ready_tasks(self) -> List[Task]:
        """
        获取可以执行的任务

        返回:
            可执行任务列表
        """
        ready_tasks = []

        for task_id, task in self.tasks.items():
            if task.status != TaskStatus.PENDING:
                continue

            # 检查所有依赖是否已完成
            dependencies_met = all(
                self.tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
                if dep_id in self.tasks
            )

            if dependencies_met:
                ready_tasks.append(task)

        # 按优先级排序
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        return ready_tasks

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        更新任务状态

        参数:
            task_id: 任务 ID
            status: 新状态

        返回:
            是否更新成功
        """
        if task_id not in self.tasks:
            return False

        self.tasks[task_id].status = status
        return True

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return list(self.tasks.values())

    def get_execution_summary(self) -> Dict:
        """
        获取执行摘要

        返回:
            执行统计信息
        """
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
            "completion_rate": completed / total if total > 0 else 0,
        }

    def visualize_dag(self) -> str:
        """
        可视化 DAG（文本格式）

        返回:
            DAG 的文本表示
        """
        lines = ["DAG 结构:", "=" * 50]

        for task_id in self.execution_order or self.topological_sort():
            task = self.tasks[task_id]
            deps = ", ".join(task.dependencies) if task.dependencies else "无"
            lines.append(f"{task_id} ({task.name})")
            lines.append(f"  依赖: {deps}")
            lines.append(f"  状态: {task.status.value}")
            lines.append(f"  Agent: {task.agent_id}")
            lines.append("")

        return "\n".join(lines)


if __name__ == "__main__":
    # 测试 DAG 调度器
    scheduler = DAGScheduler()

    # 添加任务
    scheduler.add_task(Task("t1", "数据采集", "agent_a"))
    scheduler.add_task(Task("t2", "数据清洗", "agent_b", dependencies=["t1"]))
    scheduler.add_task(Task("t3", "数据分析", "agent_c", dependencies=["t2"]))
    scheduler.add_task(Task("t4", "生成报告", "agent_d", dependencies=["t3"]))

    # 拓扑排序
    order = scheduler.topological_sort()
    print("执行顺序:", order)

    # 可视化
    print(scheduler.visualize_dag())
