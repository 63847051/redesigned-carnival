# 高质量模式配置
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
