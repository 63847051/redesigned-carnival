---
name: feishu-worklog
description: 蓝色光标工作日志智能助手。支持自然语言记录、查询、修改、删除工作日志，自动推断意图和参数，无需手动指定字段。
---

# 飞书工作日志智能助手

一个基于飞书多维表格的智能工作日志管理 skill，支持自然语言处理和智能意图识别。

## 触发条件

当用户提到以下内容时触发：
- "工作日志"、"日志"、"记一下"、"记录"
- "小蓝"（语音助手式触发）
- 查询任务、统计、查看进度

## 核心功能

- **自然语言记录** - 用日常语言描述工作内容
- **智能意图识别** - 自动识别操作类型（记录/查询/更新/删除）
- **参数自动推断** - 自动判断项目类型、优先级、状态
- **统计报表** - 实时获取工作统计和今日摘要

## 快速开始

### 初始化

```python
from worklog_assistant import WorklogAssistant

app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
table_id = "tbl5s8TEZ0tKhEm7"

assistant = WorklogAssistant(app_token, table_id)
assistant.set_access_token("your_access_token")
```

### 处理用户输入

```python
result = assistant.process("记录一下：完成了3F会议室平面图设计")
print(result)
```

## 工作流程

### Step 1: 意图分析

用户输入自然语言后，系统首先进行意图分析：

```python
from intent_analyzer import IntentAnalyzer

analyzer = IntentAnalyzer()
result = analyzer.analyze("紧急任务，完成设计图")

# 返回结果
# IntentResult(
#     intent='record',
#     content='完成设计图',
#     project_type='室内设计',
#     priority='高',
#     status='待确认',
#     note='',
#     confidence=0.9
# )
```

### Step 2: 参数提取

系统自动提取以下参数：

| 参数 | 来源 | 默认值 |
|------|------|--------|
| content | 用户输入内容 | - |
| project_type | 关键词匹配 | 技术开发 |
| priority | 关键词匹配 | 中 |
| status | 关键词匹配 | 待确认 |
| note | 括号内容 | "" |

### Step 3: 执行操作

根据意图类型调用相应接口：

- **record** → `bitable_manager.add_record()`
- **query** → `bitable_manager.query_records()`
- **update** → `bitable_manager.update_status()`
- **delete** → `bitable_manager.delete_record()`

## 意图识别

### 1. 记录意图 (record)

**触发词**: 记录、添加、新建、创建、写下、提交、录入

**示例**:
```
输入: "记录一下：完成了3F会议室平面图设计"
输出: intent=record, content=完成了3F会议室平面图设计, 
      project_type=室内设计, priority=中, status=已完成
```

### 2. 查询意图 (query)

**触发词**: 查询、查看、显示、统计、多少、看看、有哪些

**示例**:
```
输入: "今天完成了多少任务？"
输出: intent=query, filters={status: 已完成, date: 今天}
```

### 3. 更新意图 (update)

**触发词**: 更新、修改、标记、完成、改成

**示例**:
```
输入: "把ID=rec123任务标记为完成"
输出: intent=update, record_id=rec123, status=已完成
```

### 4. 删除意图 (delete)

**触发词**: 删除、移除、去掉、清掉

**示例**:
```
输入: "删除ID=rec123这条记录"
输出: intent=delete, record_id=rec123
```

## 智能推断规则

### 项目类型识别

| 关键词 | 类型 |
|--------|------|
| 设计、图纸、平面图、立面图、天花、排砖、效果图、CAD、施工图 | 室内设计 |
| 代码、开发、爬虫、API、脚本、前端、后端、bug、修复 | 技术开发 |
| 文档、手册、说明、报告、方案、总结 | 文档编写 |
| 现场、工地、施工、验收、巡查 | 现场 |
| 机电、电气、弱电、智能化 | 机电 |

### 优先级识别

| 关键词 | 优先级 |
|--------|--------|
| 紧急、重要、优先、高、急、加急、马上、立即 | 高 |
| 普通、中、正常、常规、日常 | 中 |
| 低、不急、稍后、有空、后面 | 低 |

### 状态识别

| 关键词 | 状态 |
|--------|------|
| 完成、done、做好了、结束、完结 | 已完成 |
| 进行中、doing、正在、做、处理中 | 进行中 |
| 待确认、待办、todo、未开始、待处理 | 待确认 |

## 代码示例

### 基本使用

```python
from worklog_assistant import WorklogAssistant

assistant = WorklogAssistant(
    app_token="BISAbNgYXa7Do1sc36YcBChInnS",
    table_id="tbl5s8TEZ0tKhEm7"
)
assistant.set_access_token("your_token")

# 记录任务
result = assistant.process("记录紧急任务：完成API开发")
print(result)

# 查询任务
result = assistant.process("查询今天已完成的任务")
print(result)

# 获取统计
result = assistant.get_statistics()
print(result)
```

### 直接使用 BitableManager

```python
from bitable_manager import BitableManager

manager = BitableManager(
    app_token="BISAbNgYXa7Do1sc36YcBChInnS",
    table_id="tbl5s8TEZ0tKhEm7"
)
manager.set_access_token("your_token")

# 添加记录
result = manager.add_record(
    content="完成设计方案",
    project_type="室内设计",
    priority="高",
    status="已完成"
)

# 查询记录
records = manager.query_records(filters={"status": "已完成"})

# 更新状态
manager.update_status("rec123", "已完成")

# 获取统计
stats = manager.get_statistics()
```

### 直接使用 IntentAnalyzer

```python
from intent_analyzer import IntentAnalyzer

analyzer = IntentAnalyzer()
result = analyzer.analyze("记录重要任务：完成项目方案")

print(f"意图: {result.intent}")
print(f"内容: {result.content}")
print(f"类型: {result.project_type}")
print(f"优先级: {result.priority}")
print(f"状态: {result.status}")
print(f"可信度: {result.confidence}")

# 验证参数
is_valid, error = analyzer.validate_params({
    "project_type": result.project_type,
    "priority": result.priority,
    "status": result.status
})
```

## 错误处理

```python
from bitable_manager import (
    BitableManagerError,
    BitableValidationError,
    BitableAPIError
)
from intent_analyzer import IntentAnalyzerError
from worklog_assistant import WorklogAssistantError

try:
    result = assistant.process("记录任务")
except WorklogAssistantError as e:
    print(f"处理失败: {e}")
except BitableValidationError as e:
    print(f"验证失败: {e}")
except BitableAPIError as e:
    print(f"API错误: {e}")
```

## 测试

```bash
# 运行单元测试
python3 -m unittest tests.test_feishu_worklog

# 运行特定测试类
python3 -m unittest tests.test_feishu_worklog.TestBitableManager
python3 -m unittest tests.test_feishu_worklog.TestIntentAnalyzer
python3 -m unittest tests.test_feishu_worklog.TestWorklogAssistant
```

## 项目结构

```
feishu-worklog/
├── bitable_manager.py    # 飞书多维表格管理器
├── intent_analyzer.py    # 意图分析器
├── worklog_assistant.py # 主控制器
├── REQUIREMENTS.md       # 需求文档
├── SKILL.md             # Skill 说明文档
├── README.md            # 项目说明
├── tests/
│   └── test_feishu_worklog.py  # 单元测试
└── examples/
    └── quick_start.py   # 快速开始示例
```

## 依赖

- Python 3.6+
- requests

## 注意事项

1. 使用前需设置有效的飞书 access_token
2. 删除操作需要先确认再执行
3. 默认参数会在无法识别时自动填充
4. 日期范围支持"今天"、"昨天"、"本周"、"本月"
