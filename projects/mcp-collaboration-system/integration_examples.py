#!/usr/bin/env python3
"""
MCP-S 实用集成示例
展示如何将 MCP-S 集成到日常工作中
"""

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from mcp_workflow import create_simple_workflow, Task, WorkflowConfig


# ============================================================================
# 案例 1: 每日工作报告
# ============================================================================

async def daily_report_workflow():
    """生成每日工作报告"""

    print("=" * 60)
    print("📅 每日工作报告工作流")
    print("=" * 60)
    print()

    tasks = [
        Task("collect_tasks", "收集今日任务", "opencode"),
        Task("summarize", "总结进度", "opencode",
             dependencies=["collect_tasks"]),
        Task("generate_report", "生成报告", "opencode",
             dependencies=["summarize"]),
        Task("send_to_feishu", "发送到飞书", "opencode",
             dependencies=["generate_report"]),
    ]

    workflow = create_simple_workflow("daily_report", "每日报告", tasks)
    result = await workflow.execute()

    print(f"✅ 报告生成完成")
    print(f"   完成任务: {result.tasks_completed}")
    print(f"   耗时: {result.total_execution_time:.2f} 秒")
    print()

    return result


# ============================================================================
# 案例 2: 系统维护工作流
# ============================================================================

async def system_maintenance_workflow():
    """系统维护工作流"""

    print("=" * 60)
    print("🔧 系统维护工作流")
    print("=" * 60)
    print()

    tasks = [
        Task("backup", "备份数据", "opencode"),
        Task("update", "更新系统", "opencode",
             dependencies=["backup"]),
        Task("test", "测试功能", "opencode",
             dependencies=["update"]),
        Task("monitor", "监控状态", "opencode",
             dependencies=["test"]),
        Task("report", "生成报告", "opencode",
             dependencies=["monitor"]),
    ]

    workflow = create_simple_workflow("maintenance", "系统维护", tasks)
    result = await workflow.execute()

    print(f"✅ 系统维护完成")
    print(f"   完成任务: {result.tasks_completed}")
    print(f"   耗时: {result.total_execution_time:.2f} 秒")
    print()

    return result


# ============================================================================
# 案例 3: 代码审查工作流
# ============================================================================

async def code_review_workflow(pr_url: str):
    """代码审查工作流"""

    print("=" * 60)
    print("🔍 代码审查工作流")
    print("=" * 60)
    print()

    tasks = [
        Task("fetch", "获取 PR 代码", "opencode",
             metadata={"url": pr_url}),
        Task("review", "审查代码", "opencode",
             dependencies=["fetch"]),
        Task("comment", "添加评论", "opencode",
             dependencies=["review"]),
    ]

    config = WorkflowConfig(
        workflow_id="code_review",
        name="代码审查",
        description="自动化代码审查流程",
        enable_quality_gate=True,
        min_quality_score=75.0
    )

    workflow = create_simple_workflow("code_review", "代码审查", tasks)
    workflow.config = config

    result = await workflow.execute()

    print(f"✅ 代码审查完成")
    print(f"   完成任务: {result.tasks_completed}")
    print(f"   耗时: {result.total_execution_time:.2f} 秒")
    print()

    return result


# ============================================================================
# 主函数 - 运行所有示例
# ============================================================================

async def main():
    """运行所有集成示例"""

    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "MCP-S 集成示例" + " " * 27 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # 案例 1: 每日报告
    await daily_report_workflow()

    # 等待一下
    await asyncio.sleep(1)

    # 案例 2: 系统维护
    await system_maintenance_workflow()

    # 等待一下
    await asyncio.sleep(1)

    # 案例 3: 代码审查
    await code_review_workflow("https://github.com/example/pull/123")

    print("=" * 60)
    print("🎉 所有集成示例执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
