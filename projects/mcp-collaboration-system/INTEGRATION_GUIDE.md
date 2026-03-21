# MCP-S 集成到日常工作指南

## 概述

本指南将帮助你将 MCP-S（多智能体协作系统）集成到日常工作中，实现自动化任务管理和多 Agent 协作。

## 第一步：环境准备

### 1.1 安装依赖

MCP-S 已经包含所有必需的代码，无需额外安装。确保你的环境满足以下要求：

- Python 3.9+
- asyncio 支持
- 网络连接（如果需要远程 Agent）

### 1.2 配置文件

MCP-S 包含三个配置文件：

1. **mcp-s-config.json** - 系统配置
2. **quality-standards.json** - 质量标准
3. **prompt-templates.json** - Prompt 模板

根据你的需求修改这些文件。

## 第二步：创建日常工作流

### 2.1 数据处理工作流

```python
#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('/root/.openclaw/workspace/projects/mcp-collaboration-system')

from mcp_workflow import create_simple_workflow, Task, WorkflowConfig

async def daily_data_processing():
    """每日数据处理工作流"""

    # 创建任务
    tasks = [
        Task("collect", "采集数据", "opencode"),
        Task("clean", "清洗数据", "opencode", dependencies=["collect"]),
        Task("analyze", "分析数据", "opencode", dependencies=["clean"]),
        Task("report", "生成报告", "opencode", dependencies=["analyze"]),
    ]

    # 创建工作流
    config = WorkflowConfig(
        workflow_id="daily_data",
        name="每日数据处理",
        description="自动化数据处理流水线",
        enable_quality_gate=False,  # 快速执行
        max_parallel_tasks=2
    )

    workflow = create_simple_workflow("daily_data", "每日数据处理", tasks)

    # 执行
    result = await workflow.execute()

    print(f"✅ 完成 {result.tasks_completed} 个任务")
    print(f"⏱️ 耗时 {result.total_execution_time:.2f} 秒")

    return result.status.value == "completed"

if __name__ == "__main__":
    success = asyncio.run(daily_data_processing())
    sys.exit(0 if success else 1)
```

### 2.2 代码审查工作流

```python
async def code_review_workflow(pr_url: str):
    """代码审查工作流"""

    tasks = [
        Task("fetch", "获取 PR 代码", "opencode",
             metadata={"url": pr_url}),
        Task("review", "审查代码", "opencode",
             dependencies=["fetch"],
             metadata={
                 "template_id": "code_review",
                 "template_vars": {
                     "language": "python",
                     "code": "从 PR 获取"
                 }
             }),
        Task("comment", "添加评论", "opencode",
             dependencies=["review"]),
    ]

    workflow = create_simple_workflow("code_review", "代码审查", tasks)

    # 启用质量门禁
    workflow.config.enable_quality_gate = True
    workflow.config.min_quality_score = 75.0

    result = await workflow.execute()
    return result
```

### 2.3 文档生成工作流

```python
async def documentation_workflow(topic: str):
    """文档生成工作流"""

    tasks = [
        Task("research", "研究主题", "opencode",
             metadata={"topic": topic}),
        Task("outline", "创建大纲", "opencode",
             dependencies=["research"]),
        Task("draft", "起草内容", "opencode",
             dependencies=["outline"]),
        Task("review", "审查文档", "opencode",
             dependencies=["draft"]),
        Task("format", "格式化", "opencode",
             dependencies=["review"]),
    ]

    workflow = create_simple_workflow("doc_gen", "文档生成", tasks)
    result = await workflow.execute()

    return result
```

## 第三步：集成到现有系统

### 3.1 与飞书集成

```python
from feishu_bitable import FeishuBitableClient

async def sync_workflow_results_to_feishu(workflow_result, table_id):
    """将工作流结果同步到飞书表格"""

    client = FeishuBitableClient()

    # 创建记录
    record = {
        "工作流ID": workflow_result.workflow_id,
        "状态": workflow_result.status.value,
        "完成任务数": workflow_result.tasks_completed,
        "失败任务数": workflow_result.tasks_failed,
        "执行时间": workflow_result.total_execution_time,
    }

    await client.create_record(table_id, record)
```

### 3.2 定时任务

使用 cron 或 systemd timer 定期执行工作流：

```bash
# /etc/cron.daily/daily-workflow
#!/bin/bash
cd /root/.openclaw/workspace/projects/mcp-collaboration-system
python3 daily_data_processing.py
```

### 3.3 Webhook 触发

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/webhook/workflow")
async def trigger_workflow(payload: dict):
    """通过 Webhook 触发工作流"""

    workflow_type = payload.get("type")

    if workflow_type == "data_processing":
        result = await daily_data_processing()
    elif workflow_type == "code_review":
        result = await code_review_workflow(payload.get("pr_url"))
    else:
        return {"error": "Unknown workflow type"}

    return {"status": result.status.value}
```

## 第四步：监控和优化

### 4.1 监控脚本

```python
async def monitor_workflows():
    """监控所有工作流"""

    # 获取统计信息
    summary = workflow.get_execution_summary()

    print(f"工作流状态: {summary['status']}")
    print(f"任务完成率: {summary['tasks']['completion_rate']:.1%}")
    print(f"角色池利用率: {summary['role_pool']['utilization_rate']:.1%}")
    print(f"质量检查通过率: {summary['quality']['pass_rate']:.1%}")

    # 检查是否需要优化
    if summary['role_pool']['utilization_rate'] > 0.8:
        print("⚠️ 角色池利用率高，考虑增加池大小")

    if summary['quality']['pass_rate'] < 0.9:
        print("⚠️ 质量检查通过率低，调整质量标准")
```

### 4.2 性能优化

1. **增加并行度**
   ```python
   config.max_parallel_tasks = 5  # 增加到 5
   ```

2. **启用角色预热**
   ```python
   role_config = RoleConfig(
       role_id="analyst",
       role_name="分析师",
       agent_id="opencode",
       warm_up=True  # 启用预热
   )
   ```

3. **调整质量检查**
   ```python
   # 只在关键任务启用
   task.metadata["quality_blocking"] = False
   ```

## 第五步：创建自定义工作流

### 5.1 分析任务

1. **识别任务类型** - 编码、分析、审查等
2. **确定依赖关系** - 哪些任务依赖其他任务
3. **选择合适的 Agent** - 根据任务类型选择
4. **定义质量标准** - 设置质量检查规则

### 5.2 创建工作流模板

```python
def create_custom_workflow(name: str, tasks_config: list) -> MCPWorkflow:
    """创建自定义工作流"""

    tasks = []
    for i, config in enumerate(tasks_config):
        task = Task(
            f"task_{i}",
            config["name"],
            config["agent"],
            dependencies=config.get("dependencies", []),
            metadata=config.get("metadata", {})
        )
        tasks.append(task)

    workflow = create_simple_workflow(
        workflow_id=name.lower().replace(" ", "_"),
        name=name,
        tasks=tasks
    )

    return workflow
```

## 实际案例

### 案例 1: 每日工作报告

```python
async def daily_report_workflow():
    """生成每日工作报告"""

    # 1. 收集今日任务
    tasks = [
        Task("collect_tasks", "收集任务", "opencode"),
        Task("summarize", "总结进度", "opencode",
             dependencies=["collect_tasks"]),
        Task("generate_report", "生成报告", "opencode",
             dependencies=["summarize"]),
        Task("send_to_feishu", "发送到飞书", "opencode",
             dependencies=["generate_report"]),
    ]

    workflow = create_simple_workflow("daily_report", "每日报告", tasks)
    result = await workflow.execute()

    return result
```

### 案例 2: 系统维护工作流

```python
async def system_maintenance_workflow():
    """系统维护工作流"""

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

    return result
```

## 常见问题

### Q: 如何调试工作流？

A: 使用 `visualize_workflow()` 方法查看工作流状态：

```python
print(workflow.visualize_workflow())
```

### Q: 如何处理失败的任务？

A: 检查任务状态并重新执行：

```python
task = workflow.scheduler.get_task("task_id")
if task.status == TaskStatus.FAILED:
    # 重试
    await workflow._execute_task(task)
```

### Q: 如何优化性能？

A: 1) 增加并行任务数 2) 启用角色预热 3) 调整质量检查规则

## 下一步

1. **创建更多工作流** - 根据实际需求创建
2. **优化性能** - 调整参数和配置
3. **集成监控** - 添加日志和告警
4. **扩展功能** - 添加自定义检查器和模板

## 获取帮助

- 查看完整文档：`USER_GUIDE.md`
- 查看架构文档：`MCP-S_ARCHITECTURE.md`
- 查看测试报告：`MCP-S_TESTING_REPORT.md`
