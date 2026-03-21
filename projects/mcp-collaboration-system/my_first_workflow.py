#!/usr/bin/env python3
"""
我的第一个 MCP-S 工作流
示例：数据处理流水线
"""

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from mcp_workflow import create_simple_workflow, Task, WorkflowConfig

async def main():
    print("=" * 60)
    print("🚀 我的第一个 MCP-S 工作流")
    print("=" * 60)
    print()

    # 创建任务
    tasks = [
        Task("collect", "数据采集", "opencode"),
        Task("clean", "数据清洗", "opencode", dependencies=["collect"]),
        Task("analyze", "数据分析", "opencode", dependencies=["clean"]),
        Task("report", "生成报告", "opencode", dependencies=["analyze"]),
    ]

    # 创建工作流配置
    config = WorkflowConfig(
        workflow_id="my_first_workflow",
        name="我的第一个工作流",
        description="数据处理流水线示例",
        max_parallel_tasks=2,
        enable_quality_gate=False,  # 快速执行
        timeout_seconds=300
    )

    # 创建工作流
    workflow = create_simple_workflow("my_first_workflow", "我的第一个工作流", tasks)
    workflow.config = config

    print("📋 工作流配置:")
    print(f"  ID: {config.workflow_id}")
    print(f"  名称: {config.name}")
    print(f"  描述: {config.description}")
    print(f"  最大并行任务: {config.max_parallel_tasks}")
    print(f"  质量门禁: {'启用' if config.enable_quality_gate else '禁用'}")
    print()

    # 显示任务结构
    print("📝 任务结构:")
    for i, task in enumerate(tasks, 1):
        deps = f" (依赖: {', '.join(task.dependencies)})" if task.dependencies else ""
        print(f"  {i}. {task.id} - {task.name}{deps}")
    print()

    # 执行工作流
    print("▶️  开始执行工作流...")
    print()

    result = await workflow.execute()

    # 显示结果
    print("=" * 60)
    print("📊 执行结果")
    print("=" * 60)
    print()
    print(f"状态: {result.status.value}")
    print(f"完成任务: {result.tasks_completed}")
    print(f"失败任务: {result.tasks_failed}")
    print(f"执行时间: {result.total_execution_time:.2f} 秒")
    print()

    # 显示执行摘要
    summary = workflow.get_execution_summary()
    print("📈 执行摘要:")
    print(f"  完成率: {summary['tasks']['completion_rate']:.1%}")
    print(f"  角色池利用率: {summary['role_pool']['utilization_rate']:.1%}")
    print()

    # 显示工作流可视化
    print("=" * 60)
    print(workflow.visualize_workflow())

    print("=" * 60)
    print("✅ 工作流执行完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
