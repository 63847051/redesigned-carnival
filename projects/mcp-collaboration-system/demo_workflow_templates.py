#!/usr/bin/env python3
"""
工作流模板库 - 常用工作流模板集合
"""

import asyncio
import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from mcp_workflow import create_simple_workflow, Task, WorkflowConfig


# ============================================================================
# 模板 1: 数据处理流水线
# ============================================================================

def data_processing_pipeline():
    """数据处理流水线模板"""

    tasks = [
        Task("collect", "数据采集", "opencode"),
        Task("clean", "数据清洗", "opencode", dependencies=["collect"]),
        Task("validate", "数据验证", "opencode", dependencies=["clean"]),
        Task("transform", "数据转换", "opencode", dependencies=["validate"]),
        Task("load", "数据加载", "opencode", dependencies=["transform"]),
        Task("analyze", "数据分析", "opencode", dependencies=["load"]),
        Task("report", "生成报告", "opencode", dependencies=["analyze"]),
    ]

    config = WorkflowConfig(
        workflow_id="data_pipeline",
        name="数据处理流水线",
        description="完整的 ETL 流程：采集、清洗、验证、转换、加载、分析、报告",
        max_parallel_tasks=2,
        enable_quality_gate=True,
        min_quality_score=70.0,
        timeout_seconds=600
    )

    return create_simple_workflow("data_pipeline", "数据处理流水线", tasks), config


# ============================================================================
# 模板 2: CI/CD 流水线
# ============================================================================

def cicd_pipeline():
    """CI/CD 流水线模板"""

    tasks = [
        Task("checkout", "检出代码", "opencode"),
        Task("install", "安装依赖", "opencode", dependencies=["checkout"]),
        Task("lint", "代码检查", "opencode", dependencies=["install"]),
        Task("unit_test", "单元测试", "opencode", dependencies=["install"]),
        Task("build", "构建项目", "opencode",
             dependencies=["lint", "unit_test"]),
        Task("integration_test", "集成测试", "opencode",
             dependencies=["build"]),
        Task("deploy_staging", "部署到预发布", "opencode",
             dependencies=["integration_test"]),
        Task("e2e_test", "端到端测试", "opencode",
             dependencies=["deploy_staging"]),
        Task("deploy_prod", "部署到生产", "opencode",
             dependencies=["e2e_test"]),
    ]

    config = WorkflowConfig(
        workflow_id="cicd_pipeline",
        name="CI/CD 流水线",
        description="完整的 CI/CD 流程：从代码检出到生产部署",
        max_parallel_tasks=3,
        enable_quality_gate=True,
        min_quality_score=80.0,
        timeout_seconds=900
    )

    return create_simple_workflow("cicd_pipeline", "CI/CD 流水线", tasks), config


# ============================================================================
# 模板 3: 机器学习流水线
# ============================================================================

def ml_pipeline():
    """机器学习流水线模板"""

    tasks = [
        Task("collect_data", "收集数据", "opencode"),
        Task("preprocess", "数据预处理", "opencode",
             dependencies=["collect_data"]),
        Task("feature_engineering", "特征工程", "opencode",
             dependencies=["preprocess"]),
        Task("split_data", "数据分割", "opencode",
             dependencies=["feature_engineering"]),
        Task("train_model", "训练模型", "opencode",
             dependencies=["split_data"]),
        Task("evaluate_model", "评估模型", "opencode",
             dependencies=["train_model"]),
        Task("tune_hyperparameters", "超参数调优", "opencode",
             dependencies=["evaluate_model"]),
        Task("validate_model", "验证模型", "opencode",
             dependencies=["tune_hyperparameters"]),
        Task("deploy_model", "部署模型", "opencode",
             dependencies=["validate_model"]),
        Task("monitor_model", "监控模型", "opencode",
             dependencies=["deploy_model"]),
    ]

    config = WorkflowConfig(
        workflow_id="ml_pipeline",
        name="机器学习流水线",
        description="完整的 ML 流程：从数据收集到模型部署和监控",
        max_parallel_tasks=2,
        enable_quality_gate=True,
        min_quality_score=75.0,
        timeout_seconds=1200
    )

    return create_simple_workflow("ml_pipeline", "机器学习流水线", tasks), config


# ============================================================================
# 模板 4: 文档生成流水线
# ============================================================================

def documentation_pipeline():
    """文档生成流水线模板"""

    tasks = [
        Task("research", "研究主题", "opencode"),
        Task("outline", "创建大纲", "opencode", dependencies=["research"]),
        Task("draft_content", "起草内容", "opencode",
             dependencies=["outline"]),
        Task("add_examples", "添加示例", "opencode",
             dependencies=["draft_content"]),
        Task("review_content", "审查内容", "opencode",
             dependencies=["add_examples"]),
        Task("format_document", "格式化文档", "opencode",
             dependencies=["review_content"]),
        Task("generate_pdf", "生成 PDF", "opencode",
             dependencies=["format_document"]),
        Task("publish", "发布文档", "opencode",
             dependencies=["generate_pdf"]),
    ]

    config = WorkflowConfig(
        workflow_id="doc_pipeline",
        name="文档生成流水线",
        description="完整的文档流程：从研究到发布",
        max_parallel_tasks=2,
        enable_quality_gate=False,
        timeout_seconds=600
    )

    return create_simple_workflow("doc_pipeline", "文档生成流水线", tasks), config


# ============================================================================
# 模板 5: 系统监控流水线
# ============================================================================

def monitoring_pipeline():
    """系统监控流水线模板"""

    tasks = [
        Task("check_services", "检查服务状态", "opencode"),
        Task("collect_metrics", "收集指标", "opencode",
             dependencies=["check_services"]),
        Task("analyze_logs", "分析日志", "opencode",
             dependencies=["check_services"]),
        Task("check_alerts", "检查告警", "opencode",
             dependencies=["collect_metrics", "analyze_logs"]),
        Task("generate_report", "生成报告", "opencode",
             dependencies=["check_alerts"]),
        Task("send_notification", "发送通知", "opencode",
             dependencies=["generate_report"]),
    ]

    config = WorkflowConfig(
        workflow_id="monitoring_pipeline",
        name="系统监控流水线",
        description="系统健康检查和监控报告",
        max_parallel_tasks=3,
        enable_quality_gate=False,
        timeout_seconds=180
    )

    return create_simple_workflow("monitoring_pipeline", "系统监控流水线", tasks), config


# ============================================================================
# 主函数
# ============================================================================

async def demo_workflow_templates():
    """演示所有工作流模板"""

    print("=" * 70)
    print("🎨 MCP-S 工作流模板库")
    print("=" * 70)
    print()

    templates = [
        ("数据处理流水线", data_processing_pipeline),
        ("CI/CD 流水线", cicd_pipeline),
        ("机器学习流水线", ml_pipeline),
        ("文档生成流水线", documentation_pipeline),
        ("系统监控流水线", monitoring_pipeline),
    ]

    results = []

    for i, (name, template_func) in enumerate(templates, 1):
        print("=" * 70)
        print(f"📋 模板 {i}/{len(templates)}: {name}")
        print("=" * 70)
        print()

        # 创建工作流
        workflow, config = template_func()
        workflow.config = config

        # 显示配置
        print(f"工作流 ID: {config.workflow_id}")
        print(f"描述: {config.description}")
        print(f"任务数: {len(workflow.scheduler.get_all_tasks())}")
        print(f"最大并行: {config.max_parallel_tasks}")
        print(f"质量门禁: {'启用' if config.enable_quality_gate else '禁用'}")
        if config.enable_quality_gate:
            print(f"最低分数: {config.min_quality_score}")
        print()

        # 显示任务结构
        tasks = workflow.scheduler.get_all_tasks()
        print("任务结构:")
        for j, task in enumerate(tasks, 1):
            deps = f" → {', '.join(task.dependencies)}" if task.dependencies else ""
            print(f"  {j}. {task.id}: {task.name}{deps}")
        print()

        # 执行工作流
        print("▶️  执行工作流...")
        result = await workflow.execute()

        print(f"\n结果:")
        print(f"  状态: {result.status.value}")
        print(f"  完成: {result.tasks_completed}")
        print(f"  耗时: {result.total_execution_time:.2f} 秒")
        print()

        results.append({
            "name": name,
            "status": result.status.value,
            "completed": result.tasks_completed,
            "time": result.total_execution_time,
        })

        await asyncio.sleep(0.5)

    # 总结
    print("=" * 70)
    print("📊 工作流模板总结")
    print("=" * 70)
    print()

    print(f"{'模板名称':<20} {'状态':<12} {'完成任务':<10} {'执行时间'}")
    print("-" * 70)

    for r in results:
        print(f"{r['name']:<20} {r['status']:<12} {r['completed']:<10} {r['time']:.2f}秒")

    print()
    print("=" * 70)
    print("✅ 所有工作流模板演示完成！")
    print("=" * 70)


async def save_workflow_templates():
    """保存工作流模板到文件"""

    templates_code = '''#!/usr/bin/env python3
"""
MCP-S 工作流模板库
包含 5 个常用工作流模板
"""

import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from workflow_templates import (
    data_processing_pipeline,
    cicd_pipeline,
    ml_pipeline,
    documentation_pipeline,
    monitoring_pipeline,
)

# 使用示例
async def main():
    # 选择模板
    workflow, config = data_processing_pipeline()

    # 配置工作流
    workflow.config = config

    # 执行工作流
    result = await workflow.execute()

    print(f"状态: {result.status.value}")
    print(f"完成: {result.tasks_completed}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

    with open('/root/.openclaw/workspace/projects/mcp-collaboration-system/workflow_templates.py', 'w') as f:
        f.write(templates_code)

    print("✅ 工作流模板库已保存到: workflow_templates.py")


async def main():
    """主函数"""

    # 演示所有模板
    await demo_workflow_templates()

    # 保存模板库
    await save_workflow_templates()

    print()
    print("🎯 下一步:")
    print("  1. 查看模板库: cat workflow_templates.py")
    print("  2. 使用模板创建工作流")
    print("  3. 根据需求修改模板")
    print()


if __name__ == "__main__":
    asyncio.run(main())
