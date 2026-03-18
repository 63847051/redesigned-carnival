# 竞品监控系统 - 需求拆解

**场景描述**: 搭建一个竞品监控系统，每天自动扫描 10 个竞品官网，检测产品更新、价格变化、新闻动态等变化，并生成简要报告推送到飞书。

---

## 📋 需求拆解 Prompt（可直接使用）

```
你是一个 AI Agent 架构师。我想在 OpenClaw 里搭建一个竞品监控系统的 Skill 体系。

请帮我完成以下任务：
1. 把我的需求拆解为 3-5 个独立的子任务（每个子任务对应一个 Agent 角色）
2. 为每个子任务明确：
   - 角色名称和职责定义
   - 输入数据来源（API/文件/用户输入）
   - 输出格式和交付物
   - 需要使用的工具或 API
   - 触发条件（什么时候这个 Agent 该开始工作）
3. 设计这些 Agent 之间的协作流程（谁先谁后、谁给谁传数据）
4. 列出需要的外部数据源和 API
5. 给出安全注意事项

我的场景描述：
我想搭建一个竞品监控系统，能够每天自动扫描 10 个竞品官网，
检测产品更新、价格变化、新闻动态等变化，
并生成简要报告推送到我的飞书里。
```

---

## 🎯 预期输出结构

### Agent 1: 信息抓取 Agent（侦察员）

**角色名称**: `competitor-scraper`

**职责定义**:
- 每天 9:00 自动扫描竞品官网
- 抓取产品页面、新闻页面、价格页面
- 提取关键信息（标题、内容、价格、日期）

**输入数据**:
- 竞品 URL 列表（配置文件）
- 抓取规则（选择器、XPath）

**输出格式**:
- JSON 文件：`workspace/data/competitors/YYYY-MM-DD.json`
- 格式：`{"url": "...", "title": "...", "content": "...", "price": "...", "timestamp": "..."}`

**使用工具**:
- `requests` - HTTP 请求
- `BeautifulSoup` - HTML 解析
- `selenium`（可选）- 处理 JavaScript 渲染

**触发条件**:
- 每天定时任务（9:00 AM）
- 手动触发：用户说"抓取一下竞品数据"

---

### Agent 2: 变化检测 Agent（对比员）

**角色名称**: `competitor-diff-detector`

**职责定义**:
- 对比昨天和今天的数据
- 识别新增、修改、删除的内容
- 计算价格变化幅度

**输入数据**:
- 今天的 JSON：`workspace/data/competitors/YYYY-MM-DD.json`
- 昨天的 JSON：`workspace/data/competitors/YYYY-MM-DD-1.json`

**输出格式**:
- JSON 文件：`workspace/data/competitors/diff-YYYY-MM-DD.json`
- 格式：`{"type": "new|updated|deleted", "url": "...", "change": "..."}`

**使用工具**:
- `difflib` - Python 标准库
- 自定义对比算法

**触发条件**:
- 信息抓取完成后自动触发
- 手动触发：用户说"对比一下今天和昨天的变化"

---

### Agent 3: 报告汇总 Agent（分析师）

**角色名称**: `competitor-reporter`

**职责定义**:
- 分析变化的重要性
- 生成 Markdown 报告
- 识别关键趋势

**输入数据**:
- 变化清单：`workspace/data/competitors/diff-YYYY-MM-DD.json`

**输出格式**:
- Markdown 文件：`workspace/reports/competitors/YYYY-MM-DD.md`
- 格式：标题、摘要、详细变化、趋势分析

**使用工具**:
- OpenClaw 内置 Markdown 生成
- 数据分析逻辑

**触发条件**:
- 变化检测完成后自动触发
- 手动触发：用户说"生成竞品分析报告"

---

### Agent 4: 推送通知 Agent（秘书）

**角色名称**: `feishu-notifier`

**职责定义**:
- 把报告推送到飞书
- 格式化消息
- 处理推送失败重试

**输入数据**:
- 报告文件：`workspace/reports/competitors/YYYY-MM-DD.md`

**输出格式**:
- 飞书群消息
- 格式：富文本、卡片消息

**使用工具**:
- 飞书 Webhook
- OpenClaw 飞书集成

**触发条件**:
- 报告生成完成后自动触发
- 手动触发：用户说"推送报告到飞书"

---

## 🔄 协作流程

```
信息抓取 Agent
    ↓ (输出: JSON 文件)
变化检测 Agent
    ↓ (输出: diff JSON)
报告汇总 Agent
    ↓ (输出: Markdown 报告)
推送通知 Agent
    ↓ (输出: 飞书消息)
✅ 完成
```

---

## 🌐 外部数据源和 API

### 数据源
- 竞品官网 HTML
- RSS 订阅（如果有）
- 社交媒体 API（可选）

### API
- 飞书 Webhook（消息推送）
- 网页截图 API（可选，用于保存快照）

---

## ⚠️ 安全注意事项

### 1. 频率限制
- ✅ 不要频繁抓取（每天 1 次足够）
- ✅ 遵守 robots.txt
- ✅ 设置 User-Agent

### 2. 数据存储
- ✅ 只存储必要信息
- ✅ 定期清理旧数据（保留 30 天）
- ✅ 敏感信息脱敏

### 3. 法律合规
- ✅ 只抓取公开信息
- ✅ 不抓取用户数据
- ✅ 遵守网站服务条款

---

## 📁 文件结构

```
workspace/
├── competitors/
│   ├── config.json          # 竞品 URL 列表
│   ├── scripts/
│   │   ├── scrape.py        # 抓取脚本
│   │   ├── diff.py          # 对比脚本
│   │   └── report.py        # 报告生成脚本
│   └── data/
│       ├── 2026-03-18.json  # 原始数据
│       ├── 2026-03-17.json
│       └── diff-2026-03-18.json  # 变化数据
└── reports/
    └── competitors/
        └── 2026-03-18.md    # 分析报告
```

---

## ✅ 下一步

现在我们已经有了清晰的需求拆解，下一步是：

**Step 1**: 创建第一个 Skill（信息抓取）
**Step 2**: 测试第一个 Agent
**Step 3**: 创建剩余三个 Agent
**Step 4**: 串成流水线

---

**文档版本**: v1.0
**创建时间**: 2026-03-18
**状态**: ✅ 需求拆解完成
