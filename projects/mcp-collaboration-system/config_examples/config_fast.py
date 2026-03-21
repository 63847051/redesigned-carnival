# 快速执行模式配置
from mcp_workflow import WorkflowConfig

config = WorkflowConfig(
    workflow_id="fast_mode",
    name="快速执行模式",
    description="禁用质量门禁，最大化执行速度",
    max_parallel_tasks=5,
    enable_quality_gate=False,
    timeout_seconds=120
)
