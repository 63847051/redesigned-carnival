# 检查清单：API 数据获取完整检查

**清单ID**: CL-API-001
**创建时间**: 2026-03-13 08:20
**适用范围**: 所有 API 数据获取操作
**状态**: ✅ 激活

---

## 🎯 使用场景

当需要从任何 API 获取数据时，必须完成此检查清单。

---

## 📋 检查清单

### Phase 1: 调用前检查

- [ ] **1.1 检查 API 文档**
  - [ ] 确认 API 支持分页吗？
  - [ ] 分页参数是什么？（page_size, page_token, cursor?）
  - [ ] 单页最大记录数是多少？
  - [ ] 有没有速率限制（Rate Limit）？

- [ ] **1.2 确定数据规模**
  - [ ] 预期有多少条记录？
  - [ ] 需要读取所有数据吗？
  - [ ] 可以分批处理吗？

### Phase 2: 实现检查

- [ ] **2.1 实现分页逻辑**
  - [ ] 使用 while 循环或 for 循环
  - [ ] 正确处理 `has_more` / `has_next` 字段
  - [ ] 正确使用 `page_token` / `cursor` / `offset`
  - [ ] 设置合理的 `page_size`

- [ ] **2.2 添加安全措施**
  - [ ] 设置最大页数限制（防止无限循环）
  - [ ] 添加超时处理
  - [ ] 添加错误处理

- [ ] **2.3 添加日志**
  - [ ] 记录每页的读取进度
  - [ ] 记录累计记录数
  - [ ] 记录任何错误或异常

### Phase 3: 验证检查

- [ ] **3.1 数据完整性验证**
  - [ ] 检查实际读取数量
  - [ ] 与 API 返回的 `total` 字段对比
  - [ ] 如果数量不符，记录警告

- [ ] **3.2 数据质量验证**
  - [ ] 检查数据是否为空
  - [ ] 检查必需字段是否存在
  - [ ] 检查数据格式是否正确

### Phase 4: 汇报检查

- [ ] **4.1 向用户报告**
  - [ ] 明确告诉用户读取了多少条记录
  - [ ] 如果数据不完整，明确说明
  - [ ] 提供数据摘要（总数、完成率等）

- [ ] **4.2 记录日志**
  - [ ] 记录到 working-buffer.md
  - [ ] 记录任何异常或问题
  - [ ] 记录用户反馈

---

## 🚨 常见错误（必须避免）

### ❌ 错误 1: 不处理分页
```python
# 错误
response = api.list_records()
records = response['records']  # 只有第一页！
```

### ❌ 错误 2: 假设一次获取所有数据
```python
# 错误
response = api.list_records(page_size=10000)  # 超过限制
```

### ❌ 错误 3: 不验证数据
```python
# 错误
records = get_all_records()
# 直接使用，不检查数量
```

### ❌ 错误 4: 不向用户报告实际数量
```python
# 错误
records = get_all_records()
print("✅ 数据读取完成")  # 不说有多少条
```

---

## ✅ 正确示例

### 示例 1: 飞书多维表格
```python
def get_feishu_records(app_token, table_id):
    all_records = []
    page_token = None
    page_count = 0

    while True:
        page_count += 1
        print(f"读取第 {page_count} 页...")

        response = feishu_bitable_list_records(
            app_token=app_token,
            table_id=table_id,
            page_size=100,
            page_token=page_token
        )

        all_records.extend(response['records'])
        print(f"  累计: {len(all_records)} 条")

        if not response['has_more']:
            break

        page_token = response.get('page_token')

    # 验证
    print(f"✅ 成功读取 {len(all_records)} 条记录")
    return all_records
```

### 示例 2: GitHub API
```python
def get_github_issues(repo):
    all_issues = []
    page = 1
    max_pages = 100  # 防止无限循环

    while page <= max_pages:
        print(f"读取第 {page} 页...")

        response = github.get_issues(repo, page=page)

        if not response:
            break

        all_issues.extend(response)
        print(f"  累计: {len(all_issues)} 个 issues")

        if len(response) < 30:  # GitHub 默认每页 30 条
            break

        page += 1

    print(f"✅ 成功读取 {len(all_issues)} 个 issues")
    return all_issues
```

---

## 📊 验证报告模板

在完成数据获取后，使用此模板报告：

```
✅ 数据获取完成

📊 数据统计:
  - 总记录数: {actual_count} 条
  - 预期数量: {expected_count} 条（如果有）
  - 完整性: {completeness}%

📋 读取详情:
  - API: {api_name}
  - 端点: {endpoint}
  - 分页: {page_count} 页
  - 耗时: {duration}

✅ 数据验证: 通过
```

---

## 🎯 快速检查（5 秒）

在调用 API 前，快速问自己：

1. ✅ "这个 API 支持分页吗？"
2. ✅ "我处理了所有页面吗？"
3. ✅ "我验证数据完整性了吗？"
4. ✅ "我向用户报告实际数量了吗？"

**任何一项为"否"，立即停止并修复！**

---

## 📚 相关资源

- **设计模式**: `DP-API-001` - API 分页处理模式
- **错误案例**: `ERROR-20260313-001` - 飞书数据读取不完整
- **最佳实践**: `.learnings/best-practices/api-calls.md`

---

**创建时间**: 2026-03-13 08:20
**状态**: ✅ 激活
**用途**: 防止 API 数据获取错误
