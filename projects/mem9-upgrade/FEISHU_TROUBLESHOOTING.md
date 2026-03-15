# 飞书表格创建 - 快速指南

## 🚀 为什么需要创建新表格？

你当前的 `app_token` 和 `table_id` 是用于**蓝色光标工作日志**的，而 mem9 记忆系统需要一个**独立的表格**来存储记忆数据。

---

## 📋 方法 1: 手动创建飞书表格（推荐）

### 步骤 1: 创建新表格

1. 打开飞书
2. 点击 **+** → **多维表格**
3. 命名：`记忆系统 Mem9`

### 步骤 2: 添加字段

按顺序添加以下字段（**字段名必须完全一致**）：

| 字段名 | 类型 | 选项/说明 |
|--------|------|-----------|
| **content** | 文本 | 记忆内容 |
| **importance** | 单选 | CRITICAL, HIGH, MEDIUM, LOW, MINIMAL |
| **memory_type** | 单选 | SHORT_TERM, LONG_TERM |
| **tags** | 多选 | 可以留空 |
| **extraction_type** | 单选 | PREFERENCE, RULE, TASK, PROJECT, IDENTITY, DECISION, PROCEDURE, RELATIONSHIP |
| **created_at** | 日期 | 包含时间 ✅ |
| **source_turn_id** | 文本 | 来源对话 ID |

### 步骤 3: 获取凭证

1. 打开创建的表格
2. 复制 URL 中的 `app_token`
   - URL: `https://xxx.feishu.cn/base/APP_TOKEN?table=TABLE_ID`
3. 获取 `table_id`
   - URL 中的 `table=TABLE_ID`
   - 或右键表格 → 查看表格信息

### 步骤 4: 更新配置

将新的 `app_token` 和 `table_id` 更新到代码中：

```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_new_app_token",
    "feishu_table_id": "your_new_table_id",
})
```

---

## 📋 方法 2: 使用现有工作日志表格（临时）

如果不想创建新表格，可以临时使用工作日志表格。

**优点**: 快速开始，无需创建新表格
**缺点**: 字段不匹配，数据会混在一起

### 使用方法：

```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "BISAbNgYXa7Do1sc36YcBChInnS",  # 现有的
    "feishu_table_id": "tbl5s8TEZ0tKhEm7",  # 现有的
})
```

**⚠️ 注意**: 工作日志表格的字段可能与 mem9 不匹配，可能导致同步失败。

---

## 📋 方法 3: 不启用飞书同步（最简单）

如果暂时不需要云端同步，可以不启用飞书：

```python
engine = create_context_engine({
    "enable_feishu": False,  # 不启用飞书同步
})
```

**优点**: 最简单，无需配置
**缺点**: 记忆只存储在本地，无法云端同步

---

## 🔍 验证设置

### 测试脚本

```python
import asyncio
from memory import create_context_engine, Message

async def test():
    engine = create_context_engine({
        "enable_feishu": True,
        "feishu_app_token": "your_app_token",
        "feishu_table_id": "your_table_id",
    })
    
    await engine.bootstrap()
    
    msg = Message(
        id="test_001",
        role="user",
        content="测试飞书同步"
    )
    
    await engine.ingest(msg)
    print("✅ 请检查飞书表格，应该能看到测试记录")

asyncio.run(test())
```

---

## ❌ 常见问题

### 问题 1: API error: 400 Unknown error

**原因**: 字段配置不正确

**解决**:
1. 检查字段名是否完全一致（区分大小写）
2. 检查单选选项是否完全一致（大写）
3. 删除表格，重新创建

### 问题 2: 看不到表格

**原因**: app_token 或 table_id 不正确

**解决**:
1. 重新复制 URL 中的 app_token
2. 确认 table_id 是否正确
3. 检查是否有权限访问

### 问题 3: 记录没有同步

**原因**: 字段不匹配或权限问题

**解决**:
1. 检查字段配置
2. 检查飞书开放平台权限
3. 查看错误日志

---

## 🎯 推荐

**对于初次使用**：
- ✅ 推荐**方法 3**（不启用飞书同步）
- ✅ 等熟悉系统后，再创建独立的飞书表格

**对于高级用户**：
- ✅ 推荐**方法 1**（手动创建独立表格）
- ✅ 更好的数据组织和管理

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 `FEISHU_QUICK_SETUP.md`（详细设置）
2. 查看 `FEISHU_SETUP.md`（完整配置）
3. 查看飞书开放平台文档

---

**记住**: 飞书同步是**可选功能**，不影响记忆系统的核心功能！

**你现在可以**:
1. 暂时不启用飞书同步（`enable_feishu=False`）
2. 等熟悉系统后，再创建独立的飞书表格
3. 继续使用本地记忆存储
