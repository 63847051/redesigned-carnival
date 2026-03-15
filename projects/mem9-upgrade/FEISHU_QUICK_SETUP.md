# 飞书多维表格 - 快速设置指南

## 🚀 5 分钟快速设置

### 步骤 1: 创建新的多维表格

1. 打开飞书
2. 点击 **+** → **多维表格**
3. 命名：`记忆系统 Mem9`

### 步骤 2: 添加字段（按顺序）

按以下顺序添加字段，**字段名必须完全一致**：

#### 1. content（文本）
- **字段名**: `content`
- **类型**: 文本
- **说明**: 记忆内容

#### 2. importance（单选）
- **字段名**: `importance`
- **类型**: 单选
- **选项**（必须完全一致）:
  - `CRITICAL`
  - `HIGH`
  - `MEDIUM`
  - `LOW`
  - `MINIMAL`

#### 3. memory_type（单选）
- **字段名**: `memory_type`
- **类型**: 单选
- **选项**:
  - `SHORT_TERM`
  - `LONG_TERM`

#### 4. tags（多选）
- **字段名**: `tags`
- **类型**: 多选
- **选项**:（可以留空，系统会自动添加）

#### 5. extraction_type（单选）
- **字段名**: `extraction_type`
- **类型**: 单选
- **选项**:
  - `PREFERENCE`
  - `RULE`
  - `TASK`
  - `PROJECT`
  - `IDENTITY`
  - `DECISION`
  - `PROCEDURE`
  - `RELATIONSHIP`

#### 6. created_at（日期）
- **字段名**: `created_at`
- **类型**: 日期
- **包含时间**: ✅ 是

#### 7. source_turn_id（文本）
- **字段名**: `source_turn_id`
- **类型**: 文本
- **说明**: 来源对话 ID

### 步骤 3: 获取凭证

1. 打开创建的多维表格
2. 复制 URL 中的 `app_token`
   - URL 格式: `https://example.feishu.cn/base/APP_TOKEN?table=TABLE_ID`
   - `APP_TOKEN` 就是 `app_token`
3. 获取 `table_id`
   - URL 中的 `table=TABLE_ID`
   - 或者在表格中右键 → 查看表格信息

### 步骤 4: 配置系统

```python
engine = create_context_engine({
    "enable_feishu": True,
    "feishu_app_token": "your_app_token",  # 从步骤 3 获取
    "feishu_table_id": "your_table_id",    # 从步骤 3 获取
})
```

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
    
    # 添加测试记录
    msg = Message(
        id="test_001",
        role="user",
        content="测试记录"
    )
    await engine.ingest(msg)
    
    print("✅ 请检查飞书表格，应该能看到测试记录")

asyncio.run(test())
```

---

## ❌ 常见错误

### 错误 1: 400 Unknown error

**原因**: 字段配置不正确

**解决**:
1. 检查字段名是否完全一致（区分大小写）
2. 检查单选/多选选项是否完全一致
3. 删除表格，重新创建

### 错误 2: permission_denied

**原因**: 没有权限访问表格

**解决**:
1. 检查 app_token 和 table_id 是否正确
2. 确保表格有权限访问
3. 检查飞书开放平台权限配置

### 错误 3: invalid_token

**原因**: app_token 不正确

**解决**:
1. 重新复制 app_token
2. 确保没有多余的空格
3. 检查 URL 是否正确

---

## 📊 表格示例

正确配置后，表格应该长这样：

| content | importance | memory_type | tags | extraction_type | created_at | source_turn_id |
|---------|------------|-------------|------|-----------------|------------|----------------|
| 用户喜欢使用 Python | HIGH | LONG_TERM | ["偏好", "python"] | PREFERENCE | 2026-03-15 14:00 | turn_001 |
| Git 推送前必须确认 | CRITICAL | LONG_TERM | ["git", "规则"] | RULE | 2026-03-15 14:01 | turn_002 |
| 明天完成测试 | HIGH | LONG_TERM | ["任务", "测试"] | TASK | 2026-03-15 14:02 | turn_003 |

---

## 🎯 快速检查清单

创建表格后，确认以下内容：

- [ ] 表格名称: 记忆系统 Mem9
- [ ] 字段数: 7 个
- [ ] 字段名完全一致（区分大小写）
- [ ] 单选选项完全一致（大写）
- [ ] 多选选项可以为空
- [ ] 日期字段包含时间
- [ ] 已获取 app_token 和 table_id
- [ ] 已运行测试脚本

---

## 💡 提示

1. **字段名必须完全一致**，包括大小写
2. **单选选项必须完全一致**，包括大写
3. **删除重建比修改更简单**
4. **测试时先添加一条记录，验证成功后再批量添加**

---

**完整配置指南**: `FEISHU_SETUP.md`
**测试脚本**: `examples/feishu_sync.py`
