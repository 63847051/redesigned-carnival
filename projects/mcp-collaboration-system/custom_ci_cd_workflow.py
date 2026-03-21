#!/usr/bin/env python3
"""
自定义 CI/CD 工作流
自动化测试、构建和部署流程
"""

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from mcp_workflow import create_simple_workflow, Task, WorkflowConfig

async def main():
    # 创建任务
    tasks = [
        Task("unit_test", "运行单元测试", "opencode"),
        Task("quality_check", "代码质量检查", "opencode",
             dependencies=["unit_test"]),
        Task("build", "构建项目", "opencode",
             dependencies=["quality_check"]),
        Task("deploy_test", "部署到测试环境", "opencode",
             dependencies=["build"]),
        Task("integration_test", "运行集成测试", "opencode",
             dependencies=["deploy_test"]),
        Task("deploy_prod", "部署到生产环境", "opencode",
             dependencies=["integration_test"]),
    ]

    # 配置工作流
    config = WorkflowConfig(
        workflow_id="automated_ci_cd",
        name="我的自动化测试流程",
        description="自动化测试、构建和部署流程",
        max_parallel_tasks=3,
        enable_quality_gate=True,
        min_quality_score=75.0,
        timeout_seconds=600
    )

    # 创建工作流
    workflow = create_simple_workflow("automated_ci_cd", "我的自动化测试流程", tasks)
    workflow.config = config

    # 执行工作流
    result = await workflow.execute()

    # 显示结果
    print(f"状态: {result.status.value}")
    print(f"完成任务: {result.tasks_completed}")
    print(f"执行时间: {result.total_execution_time:.2f} 秒")

    return result

if __name__ == "__main__":
    asyncio.run(main())
