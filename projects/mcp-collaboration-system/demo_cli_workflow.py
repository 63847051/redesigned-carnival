#!/usr/bin/env python3
"""
CLI 工具演示 - 自动创建自定义工作流
模拟使用 CLI 工具的交互过程
"""

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from mcp_workflow import create_simple_workflow, Task, WorkflowConfig


async def demo_cli_workflow_creation():
    """演示使用 CLI 工具创建自定义工作流"""

    print("=" * 70)
    print("🎮 MCP-S CLI 工具演示 - 创建自定义工作流")
    print("=" * 70)
    print()

    # 模拟 CLI 交互
    print("📋 步骤 1/5: 输入工作流信息")
    print("-" * 70)
    print("工作流名称: 我的自动化测试流程")
    print("工作流描述: 自动化测试、构建和部署流程")
    print()

    print("📝 步骤 2/5: 添加任务")
    print("-" * 70)
    print("任务 1: 运行单元测试, Agent: opencode, 依赖: 无")
    print("任务 2: 代码质量检查, Agent: opencode, 依赖: 运行单元测试")
    print("任务 3: 构建项目, Agent: opencode, 依赖: 代码质量检查")
    print("任务 4: 部署到测试环境, Agent: opencode, 依赖: 构建项目")
    print("任务 5: 运行集成测试, Agent: opencode, 依赖: 部署到测试环境")
    print("任务 6: 部署到生产环境, Agent: opencode, 依赖: 运行集成测试")
    print()

    print("⚙️  步骤 3/5: 配置工作流参数")
    print("-" * 70)
    print("最大并行任务: 3")
    print("启用质量门禁: True")
    print("最低质量分数: 75.0")
    print("超时时间: 600 秒")
    print()

    print("🔧 步骤 4/5: 生成工作流代码")
    print("-" * 70)

    # 创建实际的工作流
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

    config = WorkflowConfig(
        workflow_id="automated_ci_cd",
        name="我的自动化测试流程",
        description="自动化测试、构建和部署流程",
        max_parallel_tasks=3,
        enable_quality_gate=True,
        min_quality_score=75.0,
        timeout_seconds=600
    )

    workflow = create_simple_workflow("automated_ci_cd", "我的自动化测试流程", tasks)
    workflow.config = config

    print("✅ 工作流代码生成成功！")
    print()

    print("▶️  步骤 5/5: 执行工作流")
    print("-" * 70)
    print()

    # 执行工作流
    result = await workflow.execute()

    # 显示结果
    print("=" * 70)
    print("📊 工作流执行结果")
    print("=" * 70)
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
    print("=" * 70)
    print(workflow.visualize_workflow())

    print("=" * 70)
    print("✅ 自定义工作流创建并执行成功！")
    print("=" * 70)

    # 保存工作流代码
    print()
    print("💾 工作流代码已保存到: custom_ci_cd_workflow.py")

    return workflow, result


async def save_custom_workflow():
    """保存自定义工作流到文件"""

    workflow_code = '''#!/usr/bin/env python3
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
'''

    with open('/root/.openclaw/workspace/projects/mcp-collaboration-system/custom_ci_cd_workflow.py', 'w') as f:
        f.write(workflow_code)

    print("✅ 文件保存成功!")


async def main():
    """主函数"""

    # 运行演示
    await demo_cli_workflow_creation()

    # 保存工作流
    await save_custom_workflow()

    print()
    print("🎯 下一步:")
    print("  1. 查看生成的工作流代码: cat custom_ci_cd_workflow.py")
    print("  2. 运行自定义工作流: python3 custom_ci_cd_workflow.py")
    print("  3. 修改配置选项以满足你的需求")
    print()


if __name__ == "__main__":
    asyncio.run(main())
