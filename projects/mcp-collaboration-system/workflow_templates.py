#!/usr/bin/env python3
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
