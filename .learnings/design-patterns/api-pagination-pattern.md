# 设计模式：API 分页处理模式

**模式ID**: DP-API-001
**创建时间**: 2026-03-13 08:19
**来源错误**: ERROR-20260313-001（飞书数据读取不完整）
**状态**: ✅ 已验证

---

## 🎯 模式名称

**API 分页完整读取模式** (API Pagination Complete Read Pattern)

---

## 📋 问题描述

当调用支持分页的 API 时，只读取第一页数据，导致数据不完整。

---

## 🚨 错误示例

### ❌ 错误代码
```python
# 只读取第一页
response = api.list_records(page_size=100)
records = response['records']  # ❌ 可能只有部分数据
```

### 问题
- API 默认返回第一页（如 100 条）
- 实际可能有 1000 条数据
- 遗漏了 900 条数据（90%）

---

## ✅ 正确解决方案

### 方案 1: while 循环 + has_more

```python
def get_all_records(api, page_size=100):
    """获取所有记录，处理分页"""
    all_records = []
    page_token = None

    while True:
        # 调用 API
        response = api.list_records(
            page_size=page_size,
            page_token=page_token
        )

        # 累积数据
        all_records.extend(response['records'])

        # 检查是否还有更多数据
        if not response.get('has_more'):
            break

        # 获取下一页的 token
        page_token = response.get('page_token')

    return all_records
```

### 方案 2: for 循环 + 最大页数限制

```python
def get_all_records_safe(api, page_size=100, max_pages=100):
    """安全获取所有记录，防止无限循环"""
    all_records = []
    page_token = None

    for page_num in range(max_pages):
        response = api.list_records(
            page_size=page_size,
            page_token=page_token
        )

        all_records.extend(response['records'])

        if not response.get('has_more'):
            break

        page_token = response.get('page_token')

    return all_records
```

### 方案 3: 递归（不推荐，可能栈溢出）

```python
def get_all_records_recursive(api, page_token=None, all_records=None):
    """递归获取所有记录（不推荐）"""
    if all_records is None:
        all_records = []

    response = api.list_records(page_token=page_token)
    all_records.extend(response['records'])

    if response.get('has_more'):
        return get_all_records_recursive(
            api,
            page_token=response.get('page_token'),
            all_records=all_records
        )

    return all_records
```

---

## 🛡️ 防御性编程

### 1. 数据验证

```python
def get_all_records_validated(api, expected_min=10):
    """获取并验证数据"""
    records = get_all_records(api)

    # 验证数量
    if len(records) < expected_min:
        raise ValueError(
            f"数据量异常: 期望至少 {expected_min} 条，"
            f"实际 {len(records)} 条"
        )

    # 验证内容
    if not records:
        raise ValueError("数据为空")

    return records
```

### 2. 日志记录

```python
def get_all_records_logged(api):
    """带日志的完整读取"""
    all_records = []
    page_token = None
    page_count = 0

    while True:
        page_count += 1
        logger.info(f"读取第 {page_count} 页...")

        response = api.list_records(page_token=page_token)

        current_count = len(response['records'])
        all_records.extend(response['records'])

        logger.info(
            f"  第 {page_count} 页: {current_count} 条，"
            f"累计: {len(all_records)} 条"
        )

        if not response.get('has_more'):
            logger.info(f"✅ 读取完成，共 {len(all_records)} 条")
            break

        page_token = response.get('page_token')

    return all_records
```

### 3. 进度报告

```python
def get_all_records_with_progress(api):
    """带进度报告的完整读取"""
    all_records = []
    page_token = None

    while True:
        response = api.list_records(page_token=page_token)
        all_records.extend(response['records'])

        # 显示进度
        total = response.get('total', len(all_records))
        progress = len(all_records) / total * 100 if total > 0 else 0
        print(f"进度: {len(all_records)}/{total} ({progress:.1f}%)")

        if not response.get('has_more'):
            break

        page_token = response.get('page_token')

    return all_records
```

---

## 📊 适用场景

### 适合使用此模式的场景
- ✅ RESTful API（List 操作）
- ✅ GraphQL（分页查询）
- ✅ 数据库查询（LIMIT/OFFSET）
- ✅ 飞书多维表格
- ✅ GitHub API
- ✅ 任何支持分页的 API

### 不适合的场景
- ❌ 单次 API 调用（无分页）
- ❌ 实时数据流（WebSocket）
- ❌ 大数据量（需要流式处理）

---

## 🎯 最佳实践

### ✅ DO（应该做的）
1. **总是检查 `has_more` 字段**
2. **使用循环处理所有页面**
3. **验证数据总数**
4. **添加日志记录**
5. **限制最大页数**（防止无限循环）
6. **向用户报告实际读取数量**

### ❌ DON'T（不应该做的）
1. ❌ 假设一次调用获取所有数据
2. ❌ 忽略 `page_token`
3. ❌ 不验证就使用数据
4. ❌ 使用递归（可能栈溢出）
5. ❌ 没有最大页数限制

---

## 🔧 实现清单

在使用任何分页 API 时，必须：

- [ ] 检查 API 文档，确认分页机制
- [ ] 实现 while 循环或 for 循环
- [ ] 处理 `has_more` 或类似字段
- [ ] 使用 `page_token` 或 `cursor`
- [ ] 验证数据完整性
- [ ] 添加日志记录
- [ ] 设置最大页数限制
- [ ] 向用户报告总数

---

## 📚 相关模式

- **DP-API-002**: API 重试模式（处理网络错误）
- **DP-API-003**: API 限流模式（Rate Limiting）
- **DP-DATA-001**: 数据验证模式

---

## 💡 示例：飞书多维表格

```python
# OpenClaw 工具调用示例
def get_feishu_all_records(app_token, table_id):
    """获取飞书表格所有记录"""
    all_records = []
    page_token = None

    while True:
        response = feishu_bitable_list_records(
            app_token=app_token,
            table_id=table_id,
            page_size=100,
            page_token=page_token
        )

        all_records.extend(response['records'])

        if not response['has_more']:
            break

        page_token = response.get('page_token')

    return all_records
```

---

## 🎓 学习检查

在实现分页 API 调用时，问自己：

1. ✅ "这个 API 支持分页吗？"
2. ✅ "我是否处理了所有页面？"
3. ✅ "我是否验证了数据总数？"
4. ✅ "我是否向用户报告了实际数量？"
5. ✅ "我是否添加了日志记录？"

---

**创建时间**: 2026-03-13 08:19
**状态**: ✅ 已验证
**来源错误**: ERROR-20260313-001
