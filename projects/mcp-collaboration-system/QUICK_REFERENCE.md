# MCP-S 快速参考指南

## 🚀 快速开始

### 运行第一个工作流
```bash
cd /root/.openclaw/workspace/projects/mcp-collaboration-system
python3 my_first_workflow.py
```

### 运行集成示例
```bash
python3 integration_examples.py
```

### 使用 CLI 工具
```bash
./mcp-s-cli.sh
```

---

## 📋 常用工作流模板

### 1. 数据处理流水线
```python
tasks = [
    Task("collect", "数据采集", "opencode"),
    Task("clean", "数据清洗", "opencode", dependencies=["collect"]),
    Task("analyze", "数据分析", "opencode", dependencies=["clean"]),
    Task("report", "生成报告", "opencode", dependencies=["analyze"]),
]
```

### 2. 代码审查流程
```python
tasks = [
    Task("write", "编写代码", "developer"),
    Task("review", "代码审查", "reviewer", dependencies=["write"]),
    Task("fix", "修复问题", "developer", dependencies=["review"]),
    Task("approve", "最终批准", "reviewer", dependencies=["fix"]),
]
```

### 3. 文档生成流程
```python
tasks = [
    Task("research", "研究主题", "researcher"),
    Task("draft", "起草文档", "writer", dependencies=["research"]),
    Task("review", "审查文档", "editor", dependencies=["draft"]),
    Task("publish", "发布文档", "publisher", dependencies=["review"]),
]
```

### 4. 系统维护流程
```python
tasks = [
    Task("backup", "备份数据", "opencode"),
    Task("update", "更新系统", "opencode", dependencies=["backup"]),
    Task("test", "测试功能", "opencode", dependencies=["update"]),
    Task("monitor", "监控状态", "opencode", dependencies=["test"]),
]
```

---

## ⚙️ 配置选项

### 工作流配置
```python
config = WorkflowConfig(
    workflow_id="my_workflow",
    name="我的工作流",
    description="工作流描述",
    max_parallel_tasks=3,          # 最大并行任务数
    enable_quality_gate=True,       # 启用质量门禁
    min_quality_score=70.0,         # 最低质量分数
    timeout_seconds=600             # 超时时间
)
```

### 角色配置
```python
role_config = RoleConfig(
    role_id="analyst",
    role_name="数据分析师",
    agent_id="opencode",
    model="glmcode/glm-4.5-air",
    max_concurrent_tasks=1,
    warm_up=True,                   # 启用预热
    timeout_seconds=300
)
```

---

## 🎯 质量检查

### 启用内置检查器
```python
from quality_gate import QualityCheck, CheckType, BuiltInCheckers

workflow.quality_gate.register_check(QualityCheck(
    "syntax", "语法检查", CheckType.SYNTAX,
    "检查代码语法", BuiltInCheckers.check_code_syntax
))
```

### 自定义检查器
```python
async def my_checker(content: str, metadata: Dict) -> CheckResult:
    issues = []
    score = 100

    if "TODO" in content:
        issues.append("包含未完成的 TODO")
        score -= 10

    return CheckResult(
        passed=score >= 70,
        score=score,
        message=f"检查完成",
        suggestions=issues
    )
```

---

## 📝 Prompt 模板

### 使用内置模板
```python
from prompt_template import BuiltInTemplates

workflow.register_template(BuiltInTemplates.coding_task_template())
```

### 自定义模板
```python
from prompt_template import PromptTemplate, TemplateType

template = PromptTemplate(
    template_id="my_template",
    name="我的模板",
    template_type=TemplateType.TASK,
    content="请帮我{{action}}，主题是{{topic}}"
)

workflow.register_template(template)
```

### 在任务中使用模板
```python
task = Task(
    "t1", "编写文档", "opencode",
    metadata={
        "template_id": "my_template",
        "template_vars": {
            "action": "编写教程",
            "topic": "Python 异步编程"
        }
    }
)
```

---

## 🔍 调试技巧

### 查看工作流状态
```python
print(workflow.visualize_workflow())
```

### 查看执行摘要
```python
summary = workflow.get_execution_summary()
print(f"完成率: {summary['tasks']['completion_rate']:.1%}")
print(f"角色池利用率: {summary['role_pool']['utilization_rate']:.1%}")
```

### 查看任务状态
```python
task = workflow.scheduler.get_task("task_id")
print(f"状态: {task.status.value}")
```

---

## 📊 性能优化

### 1. 增加并行度
```python
config.max_parallel_tasks = 5
```

### 2. 启用角色预热
```python
role_config = RoleConfig(..., warm_up=True)
```

### 3. 调整质量检查
```python
# 只在关键任务启用
task.metadata["quality_blocking"] = False
```

### 4. 禁用不必要的检查
```python
config.enable_quality_gate = False  # 快速执行
```

---

## 🛠️ 常见问题

### Q: 任务执行失败怎么办？
**A**:
1. 检查任务依赖是否正确
2. 查看日志了解失败原因
3. 检查角色池是否有可用角色
4. 验证质量门禁配置

### Q: 如何提高性能？
**A**:
1. 增加 `max_parallel_tasks` 参数
2. 启用角色预热 (`warm_up=True`)
3. 优化质量检查器性能
4. 考虑禁用不必要的质量检查

### Q: 质量检查总是失败？
**A**:
1. 调整 `min_quality_score` 参数
2. 检查质量检查器配置
3. 查看质量报告了解具体问题
4. 修改任务内容以符合质量标准

---

## 📚 更多资源

- **完整文档**: README.md
- **用户指南**: USER_GUIDE.md
- **集成指南**: INTEGRATION_GUIDE.md
- **交付报告**: PROJECT_DELIVERY_REPORT.md
- **测试套件**: test_mcp_workflow.py

---

## 🎯 下一步

1. ✅ 运行 `my_first_workflow.py` 体验第一个工作流
2. ✅ 运行 `integration_examples.py` 查看集成示例
3. ✅ 阅读 USER_GUIDE.md 了解高级功能
4. ✅ 参考 INTEGRATION_GUIDE.md 集成到现有系统
5. ✅ 使用 `mcp-s-cli.sh` 创建自定义工作流

---

**🎉 开始使用 MCP-S，提升多 Agent 协作效率！**
