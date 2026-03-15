# 飞书云端同步 - 配置指南

**版本**: 1.0.0  
**更新**: 2026-03-15

---

## 📋 前置准备

### 1. 飞书多维表格字段配置

在飞书中创建新的多维表格，添加以下字段：

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| **content** | **文本** | 记忆内容 | "用户喜欢使用蓝色主题" |
| **importance** | **单选** | 重要性等级 | CRITICAL / HIGH / MEDIUM / LOW / MINIMAL |
| **memory_type** | **单选** | 记忆类型 | SHORT_TERM / LONG_TERM |
| **tags** | **多选** | 标签 | ["偏好", "蓝色", "主题"] |
| **extraction_type** | **单选** | 提取类型 | PREFERENCE / RULE / TASK / PROJECT / IDENTITY / DECISION / PROCEDURE / RELATIONSHIP |
| **created_at** | **日期** | 创建时间 | 2026-03-15 |
| **source_turn_id** | **文本** | 来源对话ID | turn_001 |

### 2. 获取凭证

从 `skills/feishu-worklog/bitable_manager.py` 获取：

```python
app_token = "BISAbNgYXa7Do1sc36YcBChInnS"  # 你的 app_token
table_id = "tbl5s8TEZ0tKhEm7"  # 你的 table_id
```

---

## 🚀 配置步骤

### 步骤 1: 创建飞书多维表格

1. 打开飞书
2. 点击 **+** → **多维表格**
3. 添加上述字段
4. 记下 **app_token** 和 **table_id**

### 步骤 2: 启用飞书同步

修改记忆系统配置：

```python
from memory import create_context_engine

engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_app_token",
    "feishu_table_id": "your_table_id",
})
```

### 步骤 3: 测试同步

```python
import asyncio
from memory import create_context_engine, Message, TokenBudget, Turn

async def test_feishu_sync():
    engine = create_context_engine({
        "enable_feishu": True,
        "feishu_app_token": "BISAbNgYXa7Do1sc36YcBChInnS",
        "feishu_table_id": "tbl5s8TEZ0tKhEm7",
    })
    
    await engine.bootstrap()
    print("✅ 飞书同步已启用")
    
    # 添加一条测试记忆
    msg = Message(
        id="test_feishu",
        role="user",
        content="测试飞书同步：这条记录应该出现在飞书表格中"
    )
    await engine.ingest(msg)
    print("✅ 测试记忆已添加")
    
    # 检查飞书表格
    print("📱 请检查飞书多维表格，应该能看到新记录")

asyncio.run(test_feishu_sync())
```

---

## 📊 同步规则

### 自动同步触发条件

记忆会自动同步到飞书，如果满足以下条件：

1. **重要性 >= HIGH**
   - CRITICAL: 总是同步
   - HIGH: 自动同步
   - MEDIUM: 根据配置
   - LOW/MINIMAL: 不同步

2. **提取类型在白名单**
   - PREFERENCE (偏好)
   - RULE (规则)
   - TASK (任务)
   - PROJECT (项目)
   - IDENTITY (身份)
   - DECISION (决策)

### 不同步的内容

- 临时对话
- 低重要性信息
- 重复内容

---

## 🔍 查看同步的记忆

### 方法 1: 飞书多维表格

直接在飞书中查看：
- 打开多维表格
- 筛选重要性 >= HIGH
- 按创建时间排序

### 方法 2: 代码查询

```python
from memory import MemoryManager

manager = MemoryManager()
memories = manager.get_all_memories()

for memory in memories:
    if memory.importance.value >= 3:  # HIGH 或 CRITICAL
        print(f"✅ {memory.content}")
        print(f"   重要性: {memory.importance.value}")
        print(f"   标签: {memory.tags}")
```

---

## ⚙️ 高级配置

### 自定义同步阈值

```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_app_token",
    "feishu_table_id": "your_table_id",
    "feishu_sync_threshold": 0.5,  # 只同步评分 >= 0.5 的记忆
})
```

### 自定义同步间隔

```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_app_token",
    "feishu_table_id": "your_table_id",
    "persistence_interval": 60,  # 每 60 秒同步一次
})
```

---

## 🎯 使用场景

### 场景 1: 同步用户偏好

```python
msg = Message(
    id="pref_001",
    role="user",
    content="我最喜欢使用 Python 编程，特别是 FastAPI"
)
await engine.ingest(msg)
# ✅ 自动同步到飞书（重要性 HIGH，类型 PREFERENCE）
```

### 场景 2: 同步重要规则

```python
msg = Message(
    id="rule_001",
    role="user",
    content="记住：Git 推送前必须先确认，这个规则绝对不能违反"
)
await engine.ingest(msg)
# ✅ 自动同步到飞书（重要性 CRITICAL，类型 RULE）
```

### 场景 3: 不同步临时对话

```python
msg = Message(
    id="temp_001",
    role="user",
    content="今天天气很好"
)
await engine.ingest(msg)
# ❌ 不同步到飞书（重要性 LOW）
```

---

## 📝 飞书表格示例

| content | importance | memory_type | tags | extraction_type | created_at | source_turn_id |
|---------|------------|-------------|------|-----------------|------------|----------------|
| 用户喜欢使用蓝色主题 | HIGH | LONG_TERM | ["偏好", "蓝色", "主题"] | PREFERENCE | 2026-03-15 | turn_001 |
| Git 推送前必须先确认 | CRITICAL | LONG_TERM | ["git", "推送", "确认", "规则"] | RULE | 2026-03-15 | turn_002 |
| 用户喜欢 Python 编程 | HIGH | LONG_TERM | ["python", "编程", "偏好"] | PREFERENCE | 2026-03-15 | turn_003 |
| 明天之前完成测试 | HIGH | LONG_TERM | ["测试", "任务", "明天"] | TASK | 2026-03-15 | turn_004 |

---

## 🔧 故障排查

### 问题 1: 记忆没有同步到飞书

**检查**:
1. `enable_feishu` 是否为 `True`
2. `app_token` 和 `table_id` 是否正确
3. 记忆的重要性是否 >= HIGH
4. 飞书表格字段是否正确

**解决**:
```python
# 检查配置
print(f"飞书同步: {engine._config.enable_feishu}")
print(f"App Token: {engine._config.app_token}")
print(f"Table ID: {engine._config.table_id}")
```

### 问题 2: 飞书 API 错误

**常见错误**:
- `invalid_token`: app_token 不正确
- `invalid_table_id`: table_id 不正确
- `permission_denied`: 没有权限

**解决**:
1. 检查凭证
2. 确保有权限访问表格
3. 检查网络连接

---

## 🎉 总结

**飞书云端同步的好处**:
- ✅ 永久存储
- ✅ 跨设备同步
- ✅ 可视化查看
- ✅ 多人协作
- ✅ 数据备份

**开始使用**: 只需修改 3 行配置！

```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_token",
    "feishu_table_id": "your_table_id",
})
```

---

**完整示例**: `examples/feishu_sync.py`
