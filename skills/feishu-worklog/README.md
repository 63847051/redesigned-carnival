# 飞书工作日志智能助手

基于飞书多维表格的智能工作日志管理工具，支持自然语言处理和意图识别。

## 功能特性

- 自然语言记录工作日志
- 智能意图识别（记录/查询/更新/删除）
- 自动推断项目类型、优先级、状态
- 实时统计和报表
- 今日工作摘要

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 基本使用

```python
from worklog_assistant import WorklogAssistant

# 初始化
app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
table_id = "tbl5s8TEZ0tKhEm7"
assistant = WorklogAssistant(app_token, table_id)
assistant.set_access_token("your_access_token")

# 记录任务
result = assistant.process("记录一下：完成了3F会议室平面图设计")
print(result)

# 查询任务
result = assistant.process("查询今天已完成的任务")

# 获取统计
result = assistant.get_statistics()
```

## 项目结构

```
feishu-worklog/
├── bitable_manager.py    # 飞书多维表格管理器
├── intent_analyzer.py    # 意图分析器
├── worklog_assistant.py # 主控制器
├── tests/
│   └── test_feishu_worklog.py  # 单元测试
├── examples/
│   └── quick_start.py   # 快速开始示例
├── SKILL.md            # Skill 说明文档
└── README.md           # 本文件
```

## 模块说明

### BitableManager

飞书多维表格 API 管理器，提供增删改查功能：

```python
from bitable_manager import BitableManager

manager = BitableManager(app_token, table_id)
manager.set_access_token(token)

# 添加记录
manager.add_record(
    content="任务内容",
    project_type="技术开发",
    priority="高",
    status="进行中"
)

# 查询记录
records = manager.query_records(filters={"status": "已完成"})

# 更新状态
manager.update_status("record_id", "已完成")

# 获取统计
stats = manager.get_statistics()
```

### IntentAnalyzer

意图分析器，识别用户输入的意图和参数：

```python
from intent_analyzer import IntentAnalyzer

analyzer = IntentAnalyzer()
result = analyzer.analyze("紧急任务，完成设计图")

# result.intent       # 'record'
# result.content      # '完成设计图'
# result.project_type # '室内设计'
# result.priority    # '高'
# result.status      # '待确认'
# result.confidence  # 0.9
```

### WorklogAssistant

整合意图分析和 Bitable 管理的主控制器：

```python
from worklog_assistant import WorklogAssistant

assistant = WorklogAssistant(app_token, table_id)
result = assistant.process("记录任务：完成API开发")
```

## 示例场景

### 场景 1: 记录工作

```
输入: "记录一下：完成了3F会议室平面图设计"
输出: ✅ 记录创建成功
      📝 内容: 完成了3F会议室平面图设计
      📁 类型: 室内设计
      ⭐ 优先级: 中
      📌 状态: 已完成
```

### 场景 2: 查询任务

```
输入: "查询今天已完成的任务"
输出: 🔍 查询结果 (共 X 条)
      [1] 任务内容 - 技术开发 - 已完成
```

### 场景 3: 获取统计

```
输入: (调用 get_statistics)
输出: 📊 工作日志统计
      📈 总任务数: 10
      ✅ 已完成: 5
      🔄 进行中: 3
      ⏳ 待确认: 2
      📊 完成率: 50.0%
```

## 运行测试

```bash
python3 -m unittest tests.test_feishu_worklog
```

## 配置说明

### 飞书 Bitable 配置

- **app_token**: `BISAbNgYXa7Do1sc36YcBChInnS`
- **table_id**: `tbl5s8TEZ0tKhEm7`

### 字段映射

| 字段 | 类型 | 说明 |
|------|------|------|
| 内容 | Text | 工作描述 |
| 项目类型 | SingleSelect | 室内设计/技术开发/文档编写/现场/机电 |
| 优先级别 | SingleSelect | 高/中/低 |
| 项目状态 | SingleSelect | 待确认/进行中/已完成 |
| 备注 | Text | 补充说明 |
| 创建日期 | DateTime | 创建时间 |
| 完成时间 | DateTime | 完成时间 |

## 依赖

- Python 3.6+
- requests

## 许可证

MIT License
