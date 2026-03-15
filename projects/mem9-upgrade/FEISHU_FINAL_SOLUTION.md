# mem9 记忆系统 - 飞书集成完整解决方案

**基于飞书官方插件 v2.0.26**
**更新**: 2026-03-15

---

## 🎯 当前状态

### ✅ 已完成
1. ✅ 飞书官方插件已安装
2. ✅ 飞书文档已授权
3. ✅ mem9 记忆系统完全可用
4. ✅ 所有测试通过

### ⏳ 待完成
1. ⏳ 飞书表格创建和配置
2. ⏳ mem9 记忆系统与飞书表格的集成
3. ⏳ 云端同步测试

---

## 🚀 快速解决方案

### 方案 A: 使用现有的蓝色光标工作日志表格（临时）

**立即可用！**

你的蓝色光标工作日志表格已经有：
- ✅ 飞书凭证
- ✅ 表格结构
- ✅ 记录功能

**可以临时用于 mem9 记忆**：
```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "BISAbNgYXa7Do1sc36YcBChInnS",
    "feishu_table_id": "tbl5s8TEZ0tKhEm7",
    # 复用工作日志的配置
})
```

**优点**：
- ✅ 立即可用，无需创建新表格
- ✅ 已经有权限
- ✅ 可以存储和查询

**缺点**：
- ⚠️ 字段可能不完全匹配
- ⚠️ 数据会和工作日志混合

---

### 方案 B: 创建新的专用表格（推荐）

**长期使用最佳实践！**

#### 步骤 1: 创建新表格

1. 在飞书中创建新的多维表格
2. 命名：`mem9 记忆系统`
3. 添加字段（见下方）

#### 步骤 2: 添加字段

**必需字段（7 个）**:

| 字段名 | 类型 | 配置 |
|--------|------|------|
| **content** | 文本 | - |
| **importance** | 单选 | CRITICAL, HIGH, MEDIUM, LOW, MINIMAL |
| **memory_type** | 单选 | SHORT_TERM, LONG_TERM |
| **tags** | 多选 | 添加预设标签（可选） |
| **extraction_type** | 单选 | PREFERENCE, RULE, TASK, PROJECT, IDENTITY, MANUAL |
| **created_at** | 日期 | 包含时间 ✅ |
| **source_turn_id** | 文本 | - |

#### 步骤 3: 获取凭证

从表格 URL 中提取：
- `app_token`: URL 中的 BASE_ID
- `table_id`: URL 中的 `table` 参数

#### 步骤 4: 测试集成

```python
# 测试连接
from skills.feishu_worklog.bitable_manager import BitableManager

manager = BitableManager(app_token, table_id)
manager.set_access_token("your_access_token")

# 查询记录
records = manager.query_records()
print(f"✅ 表格中有 {len(records)} 条记录")
```

---

## 📊 字段配置详解

### importance（重要性）

| 选项 | 说明 | 触发条件 |
|------|------|----------|
| **CRITICAL** | 最高优先级 | 评分 >= 0.8 |
| **HIGH** | 高优先级 | 评分 >= 0.6 |
| **MEDIUM** | 中等优先级 | 评分 >= 4.0 |
| **LOW** | 低优先级 | 评分 >= 0.2 |
| **MINIMAL** | 最低优先级 | 评分 < 0.2 |

### memory_type（记忆类型）

| 选项 | 说明 | 使用场景 |
|------|------|----------|
| **SHORT_TERM** | 短期记忆 | 当前会话临时记忆 |
| **LONG_TERM** | 长期记忆 | 永久存储的记忆 |

### extraction_type（提取类型）

| 选项 | 说明 | 示例 |
|------|------|------|
| **PREFERENCE** | 偏好 | "用户喜欢使用 Python" |
| **RULE** | 规则 | "Git 推送前必须确认" |
| **TASK** | 任务 | "明天之前完成测试" |
| **PROJECT** | 项目 | "mem9 升级项目" |
| **IDENTITY** | 身份 | "我叫小明" |
| **MANUAL** | 手动 | 手动添加的记忆 |

---

## 🔧 集成代码示例

### 基础使用

```python
import asyncio
from memory import create_context_engine, Message

async def main():
    engine = create_context_engine({
        "enable_feishu": True,
        "feishu_app_token": "BISAbNgYXa7Do1sc36YcBChInnS",
        "feishu_table_id": "tbl5s8TEZ0tKhEm7",
    })
    
    await engine.bootstrap()
    
    # 添加记忆（会自动同步到飞书）
    msg = Message(
        id="mem_001",
        role="user",
        content="用户喜欢使用 Python 编程，特别是 FastAPI"
    )
    
    await engine.ingest(msg)
    print("✅ 记忆已添加并同步到飞书！")

asyncio.run(main())
```

### 高级配置

```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "BISAbNgYXa7Do1sc36YcBChInnS",
    "feishu_table_id": "tbl5s8TEZ0tKhEm7",
    
    # 高级配置
    "feishu_sync_threshold": 0.5,  # 只同步评分 >= 0.5 的记忆
    "feishu_batch_size": 10,  # 批量同步大小
    "feishu_sync_interval": 30,  # 同步间隔（秒）
    "max_short_term": 20,  # 短期记忆上限
    "max_long_term": 100,  # 长期记忆上限
    "compaction_threshold": 0.7,  # 压缩阈值
})
```

---

## 🎉 总结

**现在你有 2 个选择**:

### 选项 1: 使用现有工作日志表格（临时方案）
- ✅ 立即可用
- ✅ 已经有权限
- ⚠️ 数据会混合

### 选项 2: 创建新表格（推荐）
- ✅ 数据隔离
- ✅ 专用记忆存储
- ✅ 更好的管理

---

## 📞 建议

**我现在可以做的**：

1. **查看现有工作日志表格结构**
2. **根据现有结构调整 mem9 系统适配**
3. **或者等待你创建新的专用表格**

**你想选择哪个？或者我现在先查看一下现有表格的字段？** 😊
