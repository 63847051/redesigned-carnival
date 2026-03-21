#!/usr/bin/env python3
"""
Phase 3.1: 性能测试
测试大量书籍处理性能、内存使用、响应时间
"""

import asyncio
import sys
import time
import tracemalloc
import psutil
import gc

sys.path.append("/root/.openclaw/workspace/projects/mcp-collaboration-system")

from mcp_workflow import MCPWorkflow, create_simple_workflow, WorkflowConfig
from dag_scheduler import Task, TaskStatus
from role_pool import RolePool, RoleConfig


class PerformanceMetrics:
    """性能指标收集器"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.peak_memory = None
        self.cpu_percent_start = None
        self.cpu_percent_end = None
        self.task_times = {}
        self.throughput_data = []

    def start(self):
        """开始计时和内存跟踪"""
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        self.cpu_percent_start = psutil.cpu_percent(interval=0.1)
        tracemalloc.start()

    def stop(self):
        """停止计时和内存跟踪"""
        self.end_time = time.time()
        self.end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        self.cpu_percent_end = psutil.cpu_percent(interval=0.1)
        current, peak = tracemalloc.get_traced_memory()
        self.peak_memory = peak / 1024 / 1024
        tracemalloc.stop()

    def record_task_time(self, task_id: str, duration: float):
        """记录单个任务执行时间"""
        self.task_times[task_id] = duration

    def add_throughput(self, count: int, duration: float):
        """记录吞吐量数据"""
        self.throughput_data.append(
            {
                "count": count,
                "duration": duration,
                "tps": count / duration if duration > 0 else 0,
            }
        )

    def get_report(self) -> dict:
        """生成性能报告"""
        execution_time = (self.end_time or 0) - (self.start_time or 0)
        memory_delta = (self.end_memory or 0) - (self.start_memory or 0)

        avg_task_time = (
            sum(self.task_times.values()) / len(self.task_times)
            if self.task_times
            else 0
        )
        max_task_time = max(self.task_times.values()) if self.task_times else 0
        min_task_time = min(self.task_times.values()) if self.task_times else 0

        avg_throughput = (
            sum(d["tps"] for d in self.throughput_data) / len(self.throughput_data)
            if self.throughput_data
            else 0
        )

        return {
            "execution_time_seconds": execution_time,
            "memory_start_mb": self.start_memory,
            "memory_end_mb": self.end_memory,
            "memory_delta_mb": memory_delta,
            "peak_memory_mb": self.peak_memory,
            "cpu_start_percent": self.cpu_percent_start,
            "cpu_end_percent": self.cpu_percent_end,
            "task_count": len(self.task_times),
            "avg_task_time_seconds": avg_task_time,
            "max_task_time_seconds": max_task_time,
            "min_task_time_seconds": min_task_time,
            "avg_throughput_tps": avg_throughput,
        }


async def test_large_book_processing(num_books: int = 50) -> dict:
    """测试大量书籍处理性能"""
    print(f"\n{'=' * 60}")
    print(f"测试: 大量书籍处理 ({num_books} 本)")
    print(f"{'=' * 60}")

    metrics = PerformanceMetrics()
    metrics.start()

    tasks = []
    for i in range(num_books):
        task_id = f"book_{i + 1}"
        task = Task(
            id=task_id,
            name=f"处理书籍 {i + 1}",
            agent_id="reader",
            dependencies=[f"book_{i}"] if i > 0 else [],
        )
        tasks.append(task)

    config = WorkflowConfig(
        workflow_id="perf_large_scale",
        name="大量书籍处理",
        description="测试50本书的处理性能",
        enable_quality_gate=False,
        max_parallel_tasks=10,
    )

    workflow = MCPWorkflow(config)
    for task in tasks:
        workflow.add_task(task)

    result = await workflow.execute()

    metrics.stop()

    report = metrics.get_report()
    report["books_processed"] = result.tasks_completed
    report["books_failed"] = result.tasks_failed

    print(f"✓ 处理完成: {result.tasks_completed} 本")
    print(f"✗ 失败: {result.tasks_failed} 本")
    print(f"⏱ 执行时间: {report['execution_time_seconds']:.2f}秒")
    print(f"📊 内存增长: {report['memory_delta_mb']:.2f} MB")
    print(f"💾 峰值内存: {report['peak_memory_mb']:.2f} MB")

    return report


async def test_memory_usage() -> dict:
    """测试内存使用"""
    print(f"\n{'=' * 60}")
    print("测试: 内存使用分析")
    print(f"{'=' * 60}")

    gc.collect()
    metrics = PerformanceMetrics()
    metrics.start()

    workflows = []
    for i in range(5):
        tasks = [
            Task(f"t{i}_1", f"任务1-{i}", agent_id="agent_a"),
            Task(f"t{i}_2", f"任务2-{i}", agent_id="agent_b", dependencies=[f"t{i}_1"]),
            Task(f"t{i}_3", f"任务3-{i}", agent_id="agent_c", dependencies=[f"t{i}_2"]),
            Task(f"t{i}_4", f"任务4-{i}", agent_id="agent_d", dependencies=[f"t{i}_3"]),
        ]
        config = WorkflowConfig(
            workflow_id=f"mem_wf_{i}",
            name=f"内存测试工作流 {i}",
            description="内存使用测试",
            enable_quality_gate=True,
        )
        workflow = MCPWorkflow(config)
        for task in tasks:
            workflow.add_task(task)
        workflows.append(workflow)

    results = []
    for wf in workflows:
        result = await wf.execute()
        results.append(result)

    metrics.stop()
    gc.collect()

    report = metrics.get_report()
    report["workflows_executed"] = len(workflows)

    print(f"✓ 执行工作流数: {len(workflows)}")
    print(f"⏱ 执行时间: {report['execution_time_seconds']:.2f}秒")
    print(f"📊 内存增长: {report['memory_delta_mb']:.2f} MB")
    print(f"💾 峰值内存: {report['peak_memory_mb']:.2f} MB")
    print(f"🔄 平均吞吐量: {report['avg_throughput_tps']:.2f} 任务/秒")

    return report


async def test_response_time() -> dict:
    """测试响应时间"""
    print(f"\n{'=' * 60}")
    print("测试: 响应时间分析")
    print(f"{'=' * 60}")

    response_times = []
    task_counts = [1, 5, 10, 20, 30]

    for count in task_counts:
        tasks = [
            Task(f"rt_t{i}", f"响应时间任务 {i}", agent_id="agent")
            for i in range(count)
        ]
        config = WorkflowConfig(
            workflow_id=f"response_time_{count}",
            name=f"响应时间测试 ({count}任务)",
            description="响应时间性能测试",
            enable_quality_gate=False,
        )

        workflow = MCPWorkflow(config)
        for task in tasks:
            workflow.add_task(task)

        start = time.time()
        result = await workflow.execute()
        duration = time.time() - start

        response_times.append(
            {
                "task_count": count,
                "total_time": duration,
                "avg_per_task": duration / count if count > 0 else 0,
                "tasks_completed": result.tasks_completed,
            }
        )

        print(
            f"  {count:2d} 任务: {duration:.3f}秒 (平均 {duration / count:.3f}秒/任务)"
        )

    report = {
        "response_times": response_times,
        "linearity_score": _calculate_linearity(response_times),
        "avg_response_time": sum(r["total_time"] for r in response_times)
        / len(response_times),
    }

    print(f"\n📈 线性度评分: {report['linearity_score']:.2f}/100")
    print(f"⏱ 平均响应时间: {report['avg_response_time']:.3f}秒")

    return report


async def test_concurrent_execution() -> dict:
    """测试并发执行性能"""
    print(f"\n{'=' * 60}")
    print("测试: 并发执行性能")
    print(f"{'=' * 60}")

    concurrency_levels = [1, 2, 5, 10]
    results = []

    for level in concurrency_levels:
        tasks = [
            Task(f"concurrent_t{i}", f"并发任务 {i}", agent_id="agent")
            for i in range(level)
        ]
        config = WorkflowConfig(
            workflow_id=f"concurrent_{level}",
            name=f"并发测试 (level={level})",
            description="并发执行性能测试",
            enable_quality_gate=False,
            max_parallel_tasks=level,
        )

        workflow = MCPWorkflow(config)
        for task in tasks:
            workflow.add_task(task)

        start = time.time()
        result = await workflow.execute()
        duration = time.time() - start

        results.append(
            {
                "concurrency_level": level,
                "duration": duration,
                "throughput": result.tasks_completed / duration if duration > 0 else 0,
                "efficiency": (result.tasks_completed / duration) / level
                if duration > 0
                else 0,
            }
        )

        print(
            f"  并发度 {level:2d}: {duration:.3f}秒, 吞吐量 {result.tasks_completed / duration:.2f} 任务/秒"
        )

    report = {
        "concurrent_results": results,
        "max_throughput": max(r["throughput"] for r in results),
        "best_concurrency": results[
            max(range(len(results)), key=lambda i: results[i]["throughput"])
        ]["concurrency_level"],
    }

    print(f"\n🚀 最大吞吐量: {report['max_throughput']:.2f} 任务/秒")
    print(f"⚡ 最佳并发度: {report['best_concurrency']}")

    return report


async def test_role_pool_efficiency() -> dict:
    """测试角色池效率"""
    print(f"\n{'=' * 60}")
    print("测试: 角色池效率")
    print(f"{'=' * 60}")

    pool = RolePool(max_pool_size=10)

    role_configs = [RoleConfig(f"role_{i}", f"角色 {i}", "agent") for i in range(5)]

    for config in role_configs:
        await pool.create_role(config)

    tasks = [Task(f"pool_t{i}", f"池测试任务 {i}", agent_id="agent") for i in range(20)]

    start = time.time()
    acquired_count = 0
    reused_count = 0
    acquired_roles = set()

    for task in tasks:
        role_id = await pool.acquire_role(task.id, "agent")
        if role_id:
            acquired_count += 1
            if role_id in acquired_roles:
                reused_count += 1
            acquired_roles.add(role_id)

            await asyncio.sleep(0.01)
            await pool.release_role(task.id)

    duration = time.time() - start
    pool_stats = pool.get_pool_stats()

    report = {
        "total_tasks": len(tasks),
        "acquired_count": acquired_count,
        "reused_count": reused_count,
        "reuse_rate": reused_count / acquired_count if acquired_count > 0 else 0,
        "duration": duration,
        "pool_stats": pool_stats,
    }

    print(f"✓ 任务数: {len(tasks)}")
    print(f"✓ 获取次数: {acquired_count}")
    print(f"🔄 复用次数: {reused_count}")
    print(f"📊 复用率: {report['reuse_rate'] * 100:.1f}%")
    print(f"⏱ 总耗时: {duration:.3f}秒")

    return report


async def test_quality_gate_overhead() -> dict:
    """测试质量门禁开销"""
    print(f"\n{'=' * 60}")
    print("测试: 质量门禁开销")
    print(f"{'=' * 60}")

    tasks = [
        Task(f"quality_t{i}", f"质量测试 {i}", agent_id="agent") for i in range(10)
    ]

    print("  禁用质量门禁...")
    config_no_gate = WorkflowConfig(
        workflow_id="no_gate",
        name="无质量门禁",
        description="质量门禁开销测试-无门禁",
        enable_quality_gate=False,
    )
    workflow_no_gate = MCPWorkflow(config_no_gate)
    for task in tasks:
        workflow_no_gate.add_task(task)

    start = time.time()
    result_no_gate = await workflow_no_gate.execute()
    time_no_gate = time.time() - start

    print("  启用质量门禁...")
    config_with_gate = WorkflowConfig(
        workflow_id="with_gate",
        name="有质量门禁",
        description="质量门禁开销测试-有门禁",
        enable_quality_gate=True,
        min_quality_score=50.0,
    )
    workflow_with_gate = MCPWorkflow(config_with_gate)
    for task in tasks:
        workflow_with_gate.add_task(task)

    start = time.time()
    result_with_gate = await workflow_with_gate.execute()
    time_with_gate = time.time() - start

    overhead = time_with_gate - time_no_gate
    overhead_percent = (overhead / time_no_gate * 100) if time_no_gate > 0 else 0

    report = {
        "time_no_gate": time_no_gate,
        "time_with_gate": time_with_gate,
        "overhead_seconds": overhead,
        "overhead_percent": overhead_percent,
    }

    print(f"  无质量门禁: {time_no_gate:.3f}秒")
    print(f"  有质量门禁: {time_with_gate:.3f}秒")
    print(f"  开销: {overhead:.3f}秒 ({overhead_percent:.1f}%)")

    return report


def _calculate_linearity(response_times: list) -> float:
    """计算响应时间的线性度"""
    if len(response_times) < 2:
        return 100.0

    x = [r["task_count"] for r in response_times]
    y = [r["total_time"] for r in response_times]

    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(xi**2 for xi in x)

    if n * sum_x2 - sum_x**2 == 0:
        return 100.0

    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)

    y_pred = [slope * xi for xi in x]
    ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((yi - sum_y / n) ** 2 for yi in y)

    if ss_tot == 0:
        return 100.0

    r_squared = 1 - ss_res / ss_tot
    return max(0, min(100, r_squared * 100))


async def run_performance_tests():
    """运行所有性能测试"""
    print("\n" + "=" * 60)
    print("Phase 3.1: 性能测试")
    print("=" * 60)

    reports = {}

    reports["large_scale"] = await test_large_book_processing(50)
    reports["memory"] = await test_memory_usage()
    reports["response_time"] = await test_response_time()
    reports["concurrent"] = await test_concurrent_execution()
    reports["role_pool"] = await test_role_pool_efficiency()
    reports["quality_gate"] = await test_quality_gate_overhead()

    print("\n" + "=" * 60)
    print("性能测试报告摘要")
    print("=" * 60)
    print(
        f"📊 大量处理: 50本书, {reports['large_scale']['execution_time_seconds']:.2f}秒"
    )
    print(
        f"💾 内存测试: 峰值 {reports['memory']['peak_memory_mb']:.2f} MB, 增长 {reports['memory']['memory_delta_mb']:.2f} MB"
    )
    print(
        f"⏱ 响应时间: 平均 {reports['response_time']['avg_response_time']:.3f}秒, 线性度 {reports['response_time']['linearity_score']:.1f}%"
    )
    print(
        f"🚀 并发性能: 最大吞吐量 {reports['concurrent']['max_throughput']:.2f} 任务/秒"
    )
    print(f"🔄 角色池复用率: {reports['role_pool']['reuse_rate'] * 100:.1f}%")
    print(f"⚖️ 质量门禁开销: {reports['quality_gate']['overhead_percent']:.1f}%")

    return reports


if __name__ == "__main__":
    reports = asyncio.run(run_performance_tests())
