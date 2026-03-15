# mem9 记忆系统 - 飞书表格创建指南

**版本**: 1.0
**更新**: 2026-03-15

---

## 🎯 目标

创建一个专用的飞书多维表格用于存储 mem9 记忆。

---

## 📋 步骤 1: 创建多维表格

### 方法 1: 在飞书中创建（推荐）

1. 打开飞书
2. 点击左上角 **+** 按钮
3. 选择 **多维表格**
4. 命名：`mem9 记忆系统`
5. 点击 **创建**

---

## 📋 步骤 2: 添加字段

创建表格后，需要添加以下字段：

### 必需字段（7 个）

| 字段名 | 类型 | 配置说明 |
|--------|------|----------|
| **content** | 文本 | - |
| **importance** | 单选 | 添加 5 个选项（见下方） |
| **memory_type** | 单选 | 添加 2 个选项 |
| **extraction_type** | 单选 | 添加 6 个选项 |
| **created_at** | 日期 | ✅ 包含时间 |
| **source_turn_id** | 文本 | - |
| **tags** | 多选 | 添加预设标签（可选） |

---

## 📋 步骤 3: 配置单选字段

### importance（重要性）

**添加 5 个选项**：

1. 点击 **添加字段**
2. 选择 **单选**
3. 字段名：`importance`
4. 添加选项：
   - `CRITICAL`（颜色：红色）
   - `HIGH`（颜色：橙色）
   - `MEDIUM`（颜色：黄色）
   - `LOW`（颜色：蓝色）
   - `MINIMAL`（颜色：灰色）
5. 点击 **创建**

### memory_type（记忆类型）

**添加 2 个选项**：

1. 添加新字段 → 单选
2. 字段名：`memory_type`
3. 添加选项：
   - `SHORT_TERM`
   - `LONG_TERM`
4. 点击 **创建**

### extraction_type（提取类型）

**添加 6 个选项**：

1. 添加新字段 → 单选
2. 字段名：`extraction_type`
3. 添加选项：
   - `PREFERENCE`（偏好）
   - `RULE`（规则）
   - `TASK`（任务）
   - `PROJECT`（项目）
   - `IDENTITY`（身份）
   - `MANUAL`（手动）
4. 点击 **创建**

---

## 📋 步骤 4: 配置其他字段

### created_at（创建时间）

1. 添加新字段 → **日期**
2. 字段名：`created_at`
3. ✅ 勾选 **包含时间**
4. 点击 **创建**

### source_turn_id（来源 ID）

1. 添加新字段 → **文本**
2. 字段名：`source_turn_id`
3. 点击 **创建**

### tags（标签）- 可选

1. 添加新字段 → **多选**
2. 字段名：`tags`
3. 添加预设标签（可选）：
   - `python`
   - `编程`
   - `规则`
   - `任务`
   - `项目`
4. 点击 **创建**

---

## 📋 步骤 5: 获取凭证

创建完成后，从 URL 中获取凭证：

**URL 格式**：
```
https://bytedance.larkoffice.com/bitation/{app_token}?table={table_id}
```

**示例**：
```
https://bytedance.larkoffice.com/bitation/ BISAbNgYXa7Do1sc36YcBChInnS ?table= tbl5s8TEZ0tKhEm7
```

**提取**：
- `app_token`: `BISAbNgYXa7Do1sc36YcBChInnS`
- `table_id`: `tbl5s8TEZ0tKhEm7`

---

## 🎯 步骤 6: 测试连接

获取凭证后，测试连接：

```python
from skills.feishu_worklog.bitable_manager import BitableManager

# 使用新的凭证
manager = BitableManager(
    app_token="your_new_app_token",
    table_id="your_new_table_id"
)

# 查询记录（应该是空的）
records = manager.query_records()
print(f"✅ 新表格中有 {len(records)} 条记录")
```

---

## 🎉 完成！

创建完成后：

1. ✅ 复制 `app_token` 和 `table_id`
2. ✅ 更新 mem9 配置
3. ✅ 测试添加记忆
4. ✅ 在飞书中查看

---

## 📊 字段总结

**最终表格结构**：

| 字段名 | 类型 | 选项 |
|--------|------|------|
| content | 文本 | - |
| importance | 单选 | CRITICAL, HIGH, MEDIUM, LOW, MINIMAL |
| memory_type | 单选 | SHORT_TERM, LONG_TERM |
| extraction_type | 单选 | PREFERENCE, RULE, TASK, PROJECT, IDENTITY, MANUAL |
| created_at | 日期 | 包含时间 ✅ |
| source_turn_id | 文本 | - |
| tags | 多选 | 预设标签 |

---

## 🎯 下一步

创建完成后：

1. **获取凭证**
2. **告诉我新的 app_token 和 table_id**
3. **我帮你更新配置**
4. **开始使用！**

---

**准备好了吗？开始创建吧！** 🚀

---

**文档版本**: 1.0
**最后更新**: 2026-03-15
