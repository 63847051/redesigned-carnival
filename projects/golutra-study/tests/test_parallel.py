#!/usr/bin/env python3
"""
并行执行编排器单元测试
"""

import unittest
import time
import threading
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from parallel_orchestrator import (
    ParallelExecutionOrchestrator,
    Task,
    TaskPriority,
    TaskStatus,
    ResultCollector,
    AgentSession,
)


class TestResultCollector(unittest.TestCase):
    """测试结果聚合器"""

    def test_collect(self):
        collector = ResultCollector()
        collector.collect("task-1", {"status": "completed", "result": "ok"})

        self.assertIn("task-1", collector.results)
        self.assertEqual(collector.results["task-1"]["status"], "completed")

    def test_aggregate(self):
        collector = ResultCollector()
        results = [
            {"status": "completed", "duration": 1.0},
            {"status": "completed", "duration": 2.0},
            {"status": "failed", "duration": 0.5},
        ]

        aggregated = collector.aggregate(results)

        self.assertEqual(aggregated["total"], 3)
        self.assertEqual(aggregated["successful"], 2)
        self.assertEqual(aggregated["failed"], 1)


class TestAgentSession(unittest.TestCase):
    """测试 Agent 会话"""

    def test_creation(self):
        session = AgentSession("agent-1", "tech")

        self.assertEqual(session.agent_id, "agent-1")
        self.assertEqual(session.agent_type, "tech")
        self.assertEqual(session.status, "idle")
        self.assertIsNone(session.current_task)


class TestParallelOrchestrator(unittest.TestCase):
    """测试并行执行编排器"""

    def setUp(self):
        self.orchestrator = ParallelExecutionOrchestrator(max_agents=5)

    def test_creation(self):
        self.assertEqual(self.orchestrator.max_agents, 5)
        self.assertEqual(len(self.orchestrator.active_agents), 0)

    def test_add_task(self):
        task = Task(
            id="test-1",
            type="tech",
            description="test task",
            priority=TaskPriority.HIGH,
        )
        self.orchestrator.add_task(task)

        self.assertEqual(len(self.orchestrator.task_queue), 1)
        self.assertEqual(self.orchestrator.task_queue[0].priority, TaskPriority.HIGH)

    def test_add_tasks(self):
        tasks = [
            {"id": "t1", "type": "tech", "description": "task 1"},
            {"id": "t2", "type": "log", "description": "task 2"},
            {"id": "t3", "type": "design", "description": "task 3"},
        ]
        self.orchestrator.add_tasks(tasks)

        self.assertEqual(len(self.orchestrator.task_queue), 3)

    def test_parallel_execution(self):
        tasks = [
            {"id": "p1", "type": "tech", "description": "parallel 1"},
            {"id": "p2", "type": "tech", "description": "parallel 2"},
            {"id": "p3", "type": "tech", "description": "parallel 3"},
            {"id": "p4", "type": "tech", "description": "parallel 4"},
            {"id": "p5", "type": "tech", "description": "parallel 5"},
        ]

        start_time = time.time()
        results = self.orchestrator.execute_parallel(tasks)
        duration = time.time() - start_time

        self.assertEqual(results["total"], 5)
        self.assertEqual(results["successful"], 5)
        self.assertEqual(results["failed"], 0)
        self.assertLess(duration, 1.0)

    def test_priority_ordering(self):
        tasks = [
            {"id": "low", "type": "tech", "description": "low", "priority": "LOW"},
            {"id": "high", "type": "tech", "description": "high", "priority": "HIGH"},
            {
                "id": "normal",
                "type": "tech",
                "description": "normal",
                "priority": "NORMAL",
            },
        ]
        self.orchestrator.add_tasks(tasks)

        self.assertEqual(self.orchestrator.task_queue[0].id, "high")
        self.assertEqual(self.orchestrator.task_queue[1].id, "normal")
        self.assertEqual(self.orchestrator.task_queue[2].id, "low")

    def test_get_status(self):
        status = self.orchestrator.get_status()

        self.assertIn("max_agents", status)
        self.assertIn("active_agents", status)
        self.assertIn("queued_tasks", status)


class TestPerformance(unittest.TestCase):
    """性能基准测试"""

    def test_5_agents_parallel(self):
        orchestrator = ParallelExecutionOrchestrator(max_agents=5)

        tasks = [
            {"id": f"perf-{i}", "type": "tech", "description": f"task {i}"}
            for i in range(5)
        ]

        start_time = time.time()
        results = orchestrator.execute_parallel(tasks)
        parallel_duration = time.time() - start_time

        serial_time = 0.1 * 5
        speedup = serial_time / parallel_duration

        print(f"\n[性能] 5个任务并行执行:")
        print(f"  - 串行预计: {serial_time:.3f}s")
        print(f"  - 实际并行: {parallel_duration:.3f}s")
        print(f"  - 加速比: {speedup:.2f}x")

        self.assertGreater(speedup, 2.0)

    def test_10_agents_parallel(self):
        orchestrator = ParallelExecutionOrchestrator(max_agents=5)

        tasks = [
            {"id": f"perf10-{i}", "type": "tech", "description": f"task {i}"}
            for i in range(10)
        ]

        start_time = time.time()
        results = orchestrator.execute_parallel(tasks)
        parallel_duration = time.time() - start_time

        serial_time = 0.1 * 10
        speedup = serial_time / parallel_duration

        print(f"\n[性能] 10个任务并行执行 (max_agents=5):")
        print(f"  - 串行预计: {serial_time:.3f}s")
        print(f"  - 实际并行: {parallel_duration:.3f}s")
        print(f"  - 加速比: {speedup:.2f}x")

        self.assertGreater(speedup, 1.5)
        self.assertEqual(results["total"], 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
