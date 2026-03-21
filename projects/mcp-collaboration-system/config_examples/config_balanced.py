# 平衡模式配置
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
