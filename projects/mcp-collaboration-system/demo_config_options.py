#!/usr/bin/env python3
"""
配置选项演示 - 展示不同配置的效果
"""

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from mcp_workflow import create_simple_workflow, Task, WorkflowConfig


async def demo_configuration_options():
    """演示不同的配置选项"""

    print("=" * 70)
    print("⚙️  MCP-S 配置选项演示")
    print("=" * 70)
    print()

    # 基础任务
    tasks = [
        Task("t1", "任务1", "opencode"),
        Task("t2", "任务2", "opencode"),
        Task("t3", "任务3", "opencode"),
    ]

    # ============================================================================
    # 配置 1: 快速执行模式
    # ============================================================================
    print("📋 配置 1/4: 快速执行模式")
    print("-" * 70)

    config1 = WorkflowConfig(
        workflow_id="fast_mode",
        name="快速执行模式",
        description="禁用质量门禁，最大化执行速度",
        max_parallel_tasks=5,
        enable_quality_gate=False,  # 禁用质量门禁
        timeout_seconds=120
    )

    print(f"工作流 ID: {config1.workflow_id}")
    print(f"最大并行任务: {config1.max_parallel_tasks}")
    print(f"质量门禁: {'启用' if config1.enable_quality_gate else '禁用'}")
    print(f"超时时间: {config1.timeout_seconds} 秒")
    print()

    # ============================================================================
    # 配置 2: 高质量模式
    # ============================================================================
    print("📋 配置 2/4: 高质量模式")
    print("-" * 70)

    config2 = WorkflowConfig(
        workflow_id="high_quality",
        name="高质量模式",
        description="启用严格的质量检查",
        max_parallel_tasks=1,  # 串行执行，确保质量
        enable_quality_gate=True,
        min_quality_score=90.0,  # 严格要求
        timeout_seconds=600
    )

    print(f"工作流 ID: {config2.workflow_id}")
    print(f"最大并行任务: {config2.max_parallel_tasks}")
    print(f"质量门禁: {'启用' if config2.enable_quality_gate else '禁用'}")
    print(f"最低质量分数: {config2.min_quality_score}")
    print(f"超时时间: {config2.timeout_seconds} 秒")
    print()

    # ============================================================================
    # 配置 3: 平衡模式
    # ============================================================================
    print("📋 配置 3/4: 平衡模式")
    print("-" * 70)

    config3 = WorkflowConfig(
        workflow_id="balanced",
        name="平衡模式",
        description="在速度和质量之间取得平衡",
        max_parallel_tasks=3,
        enable_quality_gate=True,
        min_quality_score=70.0,  # 适中要求
        timeout_seconds=300
    )

    print(f"工作流 ID: {config3.workflow_id}")
    print(f"最大并行任务: {config3.max_parallel_tasks}")
    print(f"质量门禁: {'启用' if config3.enable_quality_gate else '禁用'}")
    print(f"最低质量分数: {config3.min_quality_score}")
    print(f"超时时间: {config3.timeout_seconds} 秒")
    print()

    # ============================================================================
    # 配置 4: 性能优化模式
    # ============================================================================
    print("📋 配置 4/4: 性能优化模式")
    print("-" * 70)

    config4 = WorkflowConfig(
        workflow_id="performance",
        name="性能优化模式",
        description="最大化并行执行，适合独立任务",
        max_parallel_tasks=10,  # 高度并行
        enable_quality_gate=False,
        timeout_seconds=180
    )

    print(f"工作流 ID: {config4.workflow_id}")
    print(f"最大并行任务: {config4.max_parallel_tasks}")
    print(f"质量门禁: {'启用' if config4.enable_quality_gate else '禁用'}")
    print(f"超时时间: {config4.timeout_seconds} 秒")
    print()

    # ============================================================================
    # 对比测试
    # ============================================================================
    print("=" * 70)
    print("🧪 配置对比测试")
    print("=" * 70)
    print()

    configs = [
        ("快速执行模式", config1),
        ("平衡模式", config3),
    ]

    results = []

    for name, config in configs:
        print(f"▶️  执行: {name}")
        print("-" * 70)

        workflow = create_simple_workflow(config.workflow_id, config.name, tasks)
        workflow.config = config

        result = await workflow.execute()

        results.append({
            "name": name,
            "status": result.status.value,
            "completed": result.tasks_completed,
            "time": result.total_execution_time,
        })

        print(f"状态: {result.status.value}")
        print(f"完成任务: {result.tasks_completed}")
        print(f"执行时间: {result.total_execution_time:.2f} 秒")
        print()

    # ============================================================================
    # 对比总结
    # ============================================================================
    print("=" * 70)
    print("📊 配置对比总结")
    print("=" * 70)
    print()

    print(f"{'配置模式':<20} {'状态':<12} {'完成任务':<10} {'执行时间'}")
    print("-" * 70)

    for r in results:
        print(f"{r['name']:<20} {r['status']:<12} {r['completed']:<10} {r['time']:.2f}秒")

    print()
    print("💡 建议:")
    print("  - 快速执行模式: 适合原型开发和测试")
    print("  - 高质量模式: 适合生产环境和关键任务")
    print("  - 平衡模式: 适合日常开发工作")
    print("  - 性能优化模式: 适合大批量独立任务")

    print()
    print("=" * 70)
    print("✅ 配置选项演示完成！")
    print("=" * 70)


async def create_config_examples():
    """创建配置示例文件"""

    examples = {
        "config_fast.py": '''# 快速执行模式配置
from mcp_workflow import WorkflowConfig

config = WorkflowConfig(
    workflow_id="fast_mode",
    name="快速执行模式",
    description="禁用质量门禁，最大化执行速度",
    max_parallel_tasks=5,
    enable_quality_gate=False,
    timeout_seconds=120
)
''',
        "config_high_quality.py": '''# 高质量模式配置
from mcp_workflow import WorkflowConfig

config = WorkflowConfig(
    workflow_id="high_quality",
    name="高质量模式",
    description="启用严格的质量检查",
    max_parallel_tasks=1,
    enable_quality_gate=True,
    min_quality_score=90.0,
    timeout_seconds=600
)
''',
        "config_balanced.py": '''# 平衡模式配置
from mcp_workflow import WorkflowConfig

config = WorkflowConfig(
    workflow_id="balanced",
    name="平衡模式",
    description="在速度和质量之间取得平衡",
    max_parallel_tasks=3,
    enable_quality_gate=True,
    min_quality_score=70.0,
    timeout_seconds=300
)
''',
    }

    import os
    config_dir = "/root/.openclaw/workspace/projects/mcp-collaboration-system/config_examples"
    os.makedirs(config_dir, exist_ok=True)

    for filename, content in examples.items():
        filepath = os.path.join(config_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)

    print(f"✅ 配置示例已保存到: {config_dir}/")


async def main():
    """主函数"""

    # 运行配置演示
    await demo_configuration_options()

    # 创建配置示例
    await create_config_examples()

    print()
    print("🎯 下一步:")
    print("  1. 查看配置示例: ls config_examples/")
    print("  2. 使用配置创建工作流")
    print("  3. 根据需求调整参数")
    print()


if __name__ == "__main__":
    asyncio.run(main())
