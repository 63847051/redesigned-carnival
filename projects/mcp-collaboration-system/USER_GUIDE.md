# MCP-S 用户指南

## 快速开始

### 1. 基本工作流

```python
from mcp_workflow import create_simple_workflow, Task
from prompt_template import BuiltInTemplates

# 创建任务
tasks = [
    Task("t1", "数据采集", "agent_a"),
    Task("t2", "数据清洗", "agent_b", dependencies=["t1"]),
    Task("t3", "数据分析", "agent_c", dependencies=["t2"]),
]

# 创建工作流
workflow = create_simple_workflow(
    workflow_id="data_pipeline",
    name="数据处理流水线",
    tasks=tasks
)

# 注册模板
workflow.register_template(BuiltInTemplates.coding_task_template())

# 执行工作流
result = await workflow.execute()

# 查看结果
print(f"完成: {result.tasks_completed}")
print(f"失败: {result.tasks_failed}")
print(f"耗时: {result.total_execution_time:.2f}秒")
```

### 2. 使用角色池

```python
from role_pool import RoleConfig

# 添加角色配置
role_config = RoleConfig(
    role_id="analyst",
    role_name="数据分析师",
    agent_id="opencode",
    model="glmcode/glm-4.5-air",
    warm_up=True
)

workflow.add_role_config(role_config)
```

### 3. 使用 Prompt 模板

```python
from prompt_template import PromptTemplate, TemplateType

# 自定义模板
template = PromptTemplate(
    template_id="my_template",
    name="我的模板",
    template_type=TemplateType.TASK,
    content="请帮我{{action}}，主题是{{topic}}"
)

workflow.register_template(template)

# 在任务中使用模板
task = Task(
    "t1", "编写文档", "agent_a",
    metadata={
        "template_id": "my_template",
        "template_vars": {
            "action": "编写教程",
            "topic": "Python 异步编程"
        }
    }
)
```

### 4. 质量门禁

```python
from quality_gate import QualityCheck, CheckType, BuiltInCheckers

# 注册质量检查
workflow.quality_gate.register_check(QualityCheck(
    "my_check", "我的检查", CheckType.SYNTAX,
    "检查代码语法", BuiltInCheckers.check_code_syntax
))

# 配置质量门禁
config = WorkflowConfig(
    workflow_id="wf1",
    name="高质量工作流",
    description="启用质量门禁",
    enable_quality_gate=True,
    min_quality_score=80.0
)
```

## 高级用法

### 自定义质量检查器

```python
async def my_checker(content: str, metadata: Dict) -> CheckResult:
    # 实现你的检查逻辑
    issues = []
    score = 100

    # 检查内容
    if "TODO" in content:
        issues.append("包含未完成的 TODO")
        score -= 10

    return CheckResult(
        passed=score >= 70,
        score=score,
        message=f"检查完成，得分: {score}",
        suggestions=issues
    )

# 注册自定义检查器
workflow.quality_gate.register_check(QualityCheck(
    "custom", "自定义检查", CheckType.CUSTOM,
    "我的自定义检查", my_checker
))
```

### 并行执行

```python
# 配置并行任务数
config = WorkflowConfig(
    workflow_id="parallel_wf",
    name="并行工作流",
    max_parallel_tasks=5,  # 最多 5 个任务并行
    enable_quality_gate=False
)

# 创建并行任务（无依赖关系）
tasks = [
    Task("t1", "任务1", "agent_a"),
    Task("t2", "任务2", "agent_b"),
    Task("t3", "任务3", "agent_c"),
]
```

## 实际应用场景

### 场景 1: 数据处理流水线

```python
tasks = [
    Task("collect", "数据采集", "agent_a"),
    Task("clean", "数据清洗", "agent_b", dependencies=["collect"]),
    Task("analyze", "数据分析", "agent_c", dependencies=["clean"]),
    Task("report", "生成报告", "agent_d", dependencies=["analyze"]),
]
```

### 场景 2: 代码审查流程

```python
tasks = [
    Task("write", "编写代码", "developer"),
    Task("review", "代码审查", "reviewer", dependencies=["write"]),
    Task("fix", "修复问题", "developer", dependencies=["review"]),
    Task("approve", "最终批准", "reviewer", dependencies=["fix"]),
]
```

### 场景 3: 文档生成

```python
tasks = [
    Task("research", "研究主题", "researcher"),
    Task("draft", "起草文档", "writer", dependencies=["research"]),
    Task("review", "审查文档", "editor", dependencies=["draft"]),
    Task("publish", "发布文档", "publisher", dependencies=["review"]),
]
```

## 最佳实践

1. **合理设计任务依赖** - 避免过度依赖，保持 DAG 简洁
2. **使用角色复用** - 相同类型的任务复用同一个角色
3. **配置质量门禁** - 确保输出质量符合要求
4. **使用 Prompt 模板** - 标准化任务输入，提高一致性
5. **监控执行状态** - 定期检查工作流状态和统计信息

## 故障排查

### 问题：任务执行失败

**解决方案**：
1. 检查任务依赖是否正确
2. 查看日志了解失败原因
3. 检查角色池是否有可用角色
4. 验证质量门禁配置

### 问题：性能不佳

**解决方案**：
1. 增加 `max_parallel_tasks` 参数
2. 启用角色预热 (`warm_up=True`)
3. 优化质量检查器性能
4. 考虑禁用不必要的质量检查

### 问题：质量检查失败

**解决方案**：
1. 调整 `min_quality_score` 参数
2. 检查质量检查器配置
3. 查看质量报告了解具体问题
4. 修改任务内容以符合质量标准
