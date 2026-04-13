# Hermes Core 集成指南

## 概述

本文档说明如何将 Hermes Core 集成到 OpenClaw 系统中。

## 集成方式

### 1. 导入模块

在 OpenClaw 代码中添加导入:

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/system/hermes-core")

from hermes_core import (
    get_snapshot_store,
    get_atomic_writer,
    get_session_search,
    get_llm_summarizer,
    get_honcho,
    get_self_guidance,
    AutoSkillCreator,
    AutoSkillImprover,
)
```

### 2. 集成到 Agent 循环

在 `run_agent.py` 的主循环中集成学习功能:

```python
from learning.auto_skill_creator import TaskContext

class AIAgent:
    def __init__(self, ...):
        self.skill_creator = AutoSkillCreator()
        self.tool_call_count = 0
        self.errors = []
        self.corrections = []
    
    def run_conversation(self, ...):
        tool_calls = []
        
        # 在工具调用后记录
        def on_tool_call(tool_name, args, result):
            tool_calls.append({"name": tool_name, "args": args, "result": result})
            
            if "error" in result.lower():
                self.errors.append(result)
            
            # 检查是否应该创建技能
            context = TaskContext(
                tool_calls=tool_calls,
                errors=self.errors,
                user_corrections=self.corrections,
                success=True
            )
            
            analysis = self.skill_creator.analyze_context(context)
            if analysis["should_create"]:
                self.skill_creator.create_skill(context)
```

### 3. 集成会话搜索

在消息保存时索引会话:

```python
from search.fts5_search import get_session_search

def on_message_complete(messages):
    search = get_session_search()
    search.index_session(
        session_id=current_session_id,
        title=generate_title(messages),
        messages=messages
    )
```

### 4. 集成用户建模

在用户交互时记录:

```python
from modeling.honcho_lite import get_honcho

def on_user_message(user_id, content):
    honcho = get_honcho()
    honcho.record_interaction(user_id, content)
    
    # 获取用户画像
    profile = honcho.profile(user_id)
    return profile
```

### 5. 集成自我引导

在每次迭代后评估引导:

```python
from learning.self_guidance import get_self_guidance

def after_iteration(stats):
    guidance = get_self_guidance()
    context = {
        "consecutive_errors": stats.get("consecutive_errors", 0),
        "consecutive_success": stats.get("consecutive_success", 0),
        "tool_call_count": stats.get("tool_call_count", 0),
        "confidence": stats.get("confidence", 1.0),
        "tool_failed": stats.get("tool_failed", False)
    }
    
    prompts = guidance.evaluate_triggers(context)
    
    if prompts:
        # 注入到系统提示
        return inject_guidance(prompts)
    return None
```

## 配置

在 `config.yaml` 中添加:

```yaml
hermes_core:
  enabled: true
  data_path: ~/.hermes/hermes-core
  
  # 技能创建
  skill_creation:
    tool_call_threshold: 5
    error_threshold: 1
    correction_threshold: 1
  
  # 技能改进
  skill_improvement:
    auto_apply: false
    confidence_threshold: 0.7
  
  # 会话搜索
  session_search:
    enabled: true
    max_results: 10
  
  # 用户建模
  user_modeling:
    enabled: true
    save_conclusions: true
```

## 数据存储

Hermes Core 使用以下数据目录:

```
~/.hermes/hermes-core/
├── snapshot_*.json     # 快照文件
├── skills/             # 技能文件
├── sessions.db         # 会话数据库 (FTS5)
├── users.db            # 用户数据库
└── config.json         # 配置
```

## 注意事项

1. **线程安全**: 所有模块都是线程安全的，可以并发使用
2. **错误处理**: 模块内部已包含异常处理，不会中断主流程
3. **性能**: 快照操作是内存级别，数据库操作有索引优化
4. **兼容性**: 需要 Python 3.8+，无其他依赖