# mem9 记忆系统 - 飞书表格创建完成！

**表格名称**: mem9 记忆系统
**创建时间**: 2026-03-15
**状态**: ✅ 已创建

---

## 📊 表格信息

**凭证**：
- **app_token**: `Vg0CbokIeaTUAqsjolVcH1Xpnlg`
- **table_id**: `tblfs59X2SkzHRwN`（默认表格）

**访问链接**: https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg

---

## 🎯 下一步：添加字段

### 方法 1: 在飞书中手动添加（推荐）

1. 打开表格: https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg
2. 点击 **添加字段**
3. 按顺序添加以下字段：

#### 字段列表（7 个）

| # | 字段名 | 类型 | 配置 |
|---|--------|------|------|
| 1 | **content** | 文本 | - |
| 2 | **importance** | 单选 | CRITICAL, HIGH, MEDIUM, LOW, MINIMAL |
| 3 | **memory_type** | 单选 | SHORT_TERM, LONG_TERM |
| 4 | **extraction_type** | 单选 | PREFERENCE, RULE, TASK, PROJECT, IDENTITY, MANUAL |
| 5 | **created_at** | 日期 | ✅ 包含时间 |
| 6 | **source_turn_id** | 文本 | - |
| 7 | **tags** | 多选 | 预设标签（可选） |

---

## 🎯 添加字段详细步骤

### 字段 1: content（文本）

1. 点击 **+** 添加字段
2. 选择 **文本**
3. 字段名：`content`
4. 点击 **完成**

### 字段 2: importance（单选）

1. 点击 **+** 添加字段
2. 选择 **单选**
3. 字段名：`importance`
4. 添加 5 个选项：
   - `CRITICAL`（红色）
   - `HIGH`（橙色）
   - `MEDIUM`（黄色）
   - `LOW`（蓝色）
   - `MINIMAL`（灰色）
5. 点击 **完成**

### 字段 3: memory_type（单选）

1. 点击 **+** 添加字段
2. 选择 **单选**
3. 字段名：`memory_type`
4. 添加 2 个选项：
   - `SHORT_TERM`
   - `LONG_TERM`
5. 点击 **完成**

### 字段 4: extraction_type（单选）

1. 点击 **+** 添加字段
2. 选择 **单选**
3. 字段名：`extraction_type`
4. 添加 6 个选项：
   - `PREFERENCE`
   - `RULE`
   - `TASK`
   - `PROJECT`
   - `IDENTITY`
   - `MANUAL`
5. 点击 **完成**

### 字段 5: created_at（日期）

1. 点击 **+** 添加字段
2. 选择 **日期**
3. 字段名：`created_at`
4. ✅ **勾选"包含时间"**
5. 点击 **完成**

### 字段 6: source_turn_id（文本）

1. 点击 **+** 添加字段
2. 选择 **文本**
3. 字段名：`source_turn_id`
4. 点击 **完成**

### 字段 7: tags（多选）- 可选

1. 点击 **+** 添加字段
2. 选择 **多选**
3. 字段名：`tags`
4. 添加预设标签（可选）：
   - `python`
   - `编程`
   - `规则`
   - `任务`
   - `项目`
5. 点击 **完成**

---

## 🎉 完成后

添加完所有字段后：

1. ✅ 表格结构完成
2. ✅ 告诉我已完成
3. ✅ 我帮你测试连接
4. ✅ 添加第一条测试记忆

---

## 📝 配置信息

**保存这些信息**：

```python
# mem9 记忆系统配置
FEISHU_CONFIG = {
    "app_token": "Vg0CbokIeaTUAqsjolVcH1Xpnlg",
    "table_id": "tblfs59X2SkzHRwN",
    "enable_feishu": True,
}

# 使用
from memory import create_context_engine

engine = create_context_engine(FEISHU_CONFIG)
```

---

## 🎯 准备好了吗？

**开始添加字段吧！完成后告诉我！** 🚀

---

**表格链接**: https://ux7aumj3ud.feishu.cn/base/Vg0CbokIeaTUAqsjolVcH1Xpnlg
**文档版本**: 1.0
**状态**: ⏳ 等待添加字段
