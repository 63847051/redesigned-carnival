# mem9 记忆系统 - 飞书集成完整方案

**基于飞书官方插件 v2.0.26**
**更新**: 2026-03-15

---

## 🎯 集成方案

### 方案概述

使用飞书多维表格作为 mem9 记忆系统的云端存储后端，实现：
- ✅ 永久存储
- ✅ 跨设备同步
- ✅ 可视化管理
- ✅ 多人协作

---

## 📋 飞书表格字段配置

### 必需字段（7 个）

| 字段名 | 类型 | 选项/说明 |
|--------|------|-----------|
| **content** | 文本 | 记忆内容 |
| **importance** | 单选 | CRITICAL, HIGH, MEDIUM, LOW, MINIMAL |
| **memory_type** | 单选 | SHORT_TERM, LONG_TERM |
| **tags** | 多选 | 可以留空 |
| **extraction_type** | 单选 | PREFERENCE, RULE, TASK, PROJECT, IDENTITY, DECISION, PROCEDURE, RELATIONSHIP |
| **created_at** | 日期 | 包含时间 ✅ |
| **source_turn_id** | 文本 | 来源对话 ID |

### 字段配置说明

**importance（重要性）**：
- `CRITICAL`: 0.8+ 评分（最高）
- `HIGH`: 0.6+ 评分（高）
- `MEDIUM`: 0.4+ 评分（中）
- `LOW`: 0.2+ 评分（低）
- `MINIMAL`: < 0.2 评分（最低）

**memory_type（记忆类型）**：
- `SHORT_TERM`: 短期记忆（当前会话）
- `LONG_TERM`: 长期记忆（永久存储）

**extraction_type（提取类型）**：
- `PREFERENCE`: 偏好
- `RULE`: 规则
- `TASK`: 任务
- `PROJECT`: 项目
- `IDENTITY`: 身份
- `MANUALLY`: 手动

---

## 🚀 快速开始

### 步骤 1: 创建飞书多维表格

1. 打开飞书
2. 创建新的多维表格
3. 添加上述 7 个字段
4. 设置字段选项（单选/多选）
5. 记录 `app_token` 和 `table_id`

### 步骤 2: 获取凭证

从飞书表格 URL 中获取：
- `app_token`: URL 中的 `BASE_ID`
- `table_id`: URL 中的 `table` 参数

### 步骤 3: 配置记忆系统

```python
from memory import create_context_engine

engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_app_token",
    "feishu_table_id": "your_table_id",
})
```

---

## 📊 同步策略

### 自动同步规则

**自动同步**（重要性 >= HIGH）：
- ✅ CRITICAL: 总是同步
- ✅ HIGH: 自动同步
- ❌ MEDIUM/LOW/MINIMAL: 不同步

### 手动同步

```python
# 手动添加记忆到飞书
from memory.feishu_adapter import FeishuMemoryBitable

bitable = FeishuMemoryBitable(
    app_token="your_app_token",
    table_id="your_table_id"
)

bitable.add_memory(memory)
```

---

## 🔧 高级配置

### 同步阈值

```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_token",
    "feishu_table_id": "your_table_id",
    "feishu_sync_threshold": 0.5,  # 只同步评分 >= 0.5 的记忆
})
```

### 批量同步

```python
engine = create_context_engine({
    "enable_feishu: True,
    "feishu_app_token": "your_token",
    "feishu_table_id": "your_table_id",
    "feishu_batch_size": 10,  # 批量同步大小
})
```

---

## 🎯 使用示例

### 示例 1: 添加记忆并自动同步

```python
from memory import create_context_engine, Message

engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_app_token",
    "feishu_table_id": "your_table_id",
})

await engine.bootstrap()

# 添加记忆
msg = Message(
    id="mem_001",
    role="user",
    content="用户喜欢使用 Python 编程，特别是 FastAPI"
)

await engine.ingest(msg)
# ✅ 自动同步到飞书（HIGH 重要性）
```

### 示例 2: 查询记忆

```python
from memory.hybrid_retriever import HybridRetriever

retriever = HybridRetriever()

# 添加记忆
retriever.add_entry(memory)

# 搜索记忆
results = retriever.search("python 编程")
for result in results:
    print(f"{result.entry.content}")
    print(f"   相关性: {result.score:.2f}")
```

---

## 🔍 验证同步

### 方法 1: 飞书多维表格

直接在飞书中查看表格，应该能看到新记录。

### 方法 2: 代码验证

```python
from skills.feishu_worklog.bitable_manager import BitableManager

manager = BitableManager(app_token, table_id)
manager.set_access_token("your_access_token")

# 查询记录
records = manager.query_records()
print(f"✅ 飞书表格中有 {len(records)} 条记录")
```

---

## 🎉 总结

**飞书集成优势**：
- ✅ 永久存储
- ✅ 跨设备同步
- ✅ 可视化管理
- ✅ 多人协作
- ✅ OpenClaw 官方支持

**下一步**：
1. 创建飞书多维表格
2. 获取凭证
3. 更新配置
4. 开始使用！

---

**完整文档**: https://bytedance.larkoffice.com/docx/MFK7dDFLFoVlOGxWCv5cTXKmnMh

**版本**: 2.0.26
**状态**: ✅ 最新
