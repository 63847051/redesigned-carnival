# 变化检测 Skill

**Skill 名称**: `competitor-diff-detector`

**版本**: v1.0

---

## description

当用户要求对比竞品数据、检测变化、查看竞品动态时使用此技能。

不适用于：非竞品数据对比、非 JSON 格式数据。

---

## 触发条件

- 用户要求检测竞品变化
- 信息抓取 Agent 完成后自动触发
- 用户问"有什么变化吗"、"对比一下"等

---

## 工作流程

### 1. 加载数据

- 读取今天的 JSON：`data/YYYY-MM-DD.json`
- 读取昨天的 JSON：`data/YYYY-MM-DD-1.json`
- 如果昨天数据不存在，说明是首次运行

### 2. 检测变化类型

**新增页面**:
- 今天有，昨天没有
- 标记为 `type: 'new'`

**更新页面**:
- 今天和昨天都有
- 对比标题、内容、价格
- 标记为 `type: 'updated'`

**删除页面**:
- 昨天有，今天没有
- 标记为 `type: 'deleted'`

### 3. 对比字段

**标题对比**:
- 直接字符串对比
- 不一样就记录

**内容对比**:
- 使用 `difflib` 计算相似度
- 相似度 < 90% 认为有变化
- 生成差异片段

**价格对比**:
- 直接字符串对比
- 记录旧价格和新价格

### 4. 保存变化

- 输出为 JSON 格式
- 文件路径：`data/diff-YYYY-MM-DD.json`
- 格式：
  ```json
  [
    {
      "type": "new|updated|deleted",
      "competitor": "竞品A",
      "page_type": "homepage",
      "url": "https://...",
      "message": "变化描述",
      "similarity": 0.85,
      "diff": "差异片段..."
    }
  ]
  ```

### 5. 输出摘要

- 在对话中输出：
  ```
  ✅ 变化检测完成！
  📊 变化统计:
    ➕ 新增: X
    🔄 更新: X
    ➖ 删除: X
  📁 文件保存到: data/diff-YYYY-MM-DD.json
  
  📋 变化详情:
    新增页面: 竞品A - 产品页
    内容变化: 竞品B - 首页 (相似度: 85%)
    价格变化: 竞品C - 价格页
  ```

---

## 需要的环境变量

无

---

## 使用的脚本

- `scripts/diff.py` - 变化检测脚本

---

## 算法说明

### 相似度计算

使用 `difflib.SequenceMatcher`:
```python
seq = difflib.SequenceMatcher(None, text1, text2)
similarity = seq.ratio()  # 0.0 到 1.0
```

**阈值**: 0.9（90%）
- 相似度 >= 0.9：认为无变化
- 相似度 < 0.9：认为有变化

### 差异生成

使用 `difflib.unified_diff`:
```python
diff = list(difflib.unified_diff(
    text1.splitlines(),
    text2.splitlines(),
    fromfile='yesterday',
    tofile='today'
))
```

---

## 注意事项

### 首次运行
- ⚠️ 如果昨天数据不存在，会提示"首次运行"
- 💡 第二天才能开始检测变化

### 内容截断
- ⚠️ 差异片段只保留前 500 字符
- 💡 避免数据过大

### 性能优化
- ✅ 使用字典快速查找
- ✅ 只对比必要字段
- ✅ 复杂度 O(n)

---

## 输出示例

### 用户输入
```
检测一下竞品有什么变化
```

### Agent 输出
```
收到，正在检测竞品变化...

📅 今天: 2026-03-18
📅 昨天: 2026-03-17

✅ 变化检测完成！
📊 变化统计:
  ➕ 新增: 1
  🔄 更新: 2
  ➖ 删除: 0
📁 文件保存到: data/diff-2026-03-18.json

📋 变化详情:
  新增页面: Apple - iPad 页面
  内容变化: Microsoft - 首页 (相似度: 85.23%)
  价格变化: Apple - iPhone 页面
```

---

## 与其他 Agent 的协作

### 上游 Agent
- **competitor-scraper**（信息抓取 Agent）
  - 读取其输出的 JSON 文件
  - 作为输入数据

### 下游 Agent
- **competitor-reporter**（报告汇总 Agent）
  - 读取本 Agent 输出的 diff JSON
  - 生成分析报告

### 触发方式
- 上游 Agent 完成后，自动触发本 Agent

---

## 数据结构

### 输入数据结构
```json
[
  {
    "competitor": "Apple",
    "page_type": "homepage",
    "url": "https://www.apple.com",
    "title": "Apple",
    "content": "页面内容...",
    "price": "价格信息",
    "timestamp": "2026-03-18T09:00:00"
  }
]
```

### 输出数据结构
```json
[
  {
    "type": "new",
    "competitor": "Apple",
    "page_type": "homepage",
    "url": "https://www.apple.com",
    "title": "Apple",
    "message": "新增页面: Apple - homepage"
  },
  {
    "type": "updated",
    "field": "content",
    "competitor": "Microsoft",
    "page_type": "homepage",
    "url": "https://www.microsoft.com",
    "similarity": 0.8523,
    "diff": "@@ -1,5 +1,5 @@...",
    "message": "内容变化: Microsoft - homepage (相似度: 85.23%)"
  }
]
```

---

**Skill 版本**: v1.0
**创建时间**: 2026-03-18
**作者**: 大领导 🎯
