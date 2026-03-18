# 竞品监控系统 - 快速开始指南

**版本**: v1.0
**创建时间**: 2026-03-18

---

## 🎯 系统简介

这是一个基于 OpenClaw 的竞品监控系统，能够自动抓取竞品官网、检测变化、生成报告并推送到飞书。

**核心特性**:
- ✅ 自动化抓取竞品官网
- ✅ 智能检测内容变化
- ✅ 生成专业分析报告
- ✅ 推送到飞书群

**所需时间**: 5 分钟配置，每天自动运行

---

## 📋 前置要求

### 必须安装

- Python 3.6+
- pip

### 可选安装

- 飞书群（用于接收报告）

---

## 🚀 5 分钟快速开始

### Step 1: 安装依赖（1 分钟）

```bash
cd /root/.openclaw/workspace/competitors-monitor

pip3 install requests beautifulsoup4
```

---

### Step 2: 配置竞品 URL（2 分钟）

编辑 `config.json`:

```json
{
  "competitors": [
    {
      "name": "你的竞品A",
      "url": "https://competitor-a.com",
      "pages": [
        {
          "name": "首页",
          "url": "https://competitor-a.com",
          "type": "homepage"
        },
        {
          "name": "产品页",
          "url": "https://competitor-a.com/products",
          "type": "products"
        }
      ]
    },
    {
      "name": "你的竞品B",
      "url": "https://competitor-b.com",
      "pages": [
        {
          "name": "首页",
          "url": "https://competitor-b.com",
          "type": "homepage"
        }
      ]
    }
  ],
  "scraping_rules": {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "timeout": 30,
    "retry_times": 3,
    "delay_between_requests": 2
  }
}
```

**提示**:
- 把 `你的竞品A` 替换成真实的竞品名称
- 把 URL 替换成真实的 URL
- 可以添加更多竞品和页面

---

### Step 3: 配置飞书 Webhook（可选，1 分钟）

#### 3.1 获取飞书 Webhook URL

1. 打开飞书群
2. 点击群设置 → 群机器人 → 添加机器人
3. 选择"自定义机器人"
4. 复制 Webhook URL

#### 3.2 更新配置

编辑 `config.json`, 添加:

```json
{
  "notification": {
    "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    "report_time": "09:00",
    "timezone": "Asia/Shanghai"
  }
}
```

**如果不配置飞书**:
- 报告会保存到本地
- 可以手动查看 `reports/` 目录

---

### Step 4: 运行测试（1 分钟）

```bash
cd /root/.openclaw/workspace/competitors-monitor

# 完整流程
python3 scripts/scrape.py && \
python3 scripts/diff.py && \
python3 scripts/report.py && \
python3 scripts/notify.py
```

**预期输出**:
```
🚀 开始抓取竞品信息...
✅ 抓取完成！

🔍 开始检测竞品变化...
✅ 变化检测完成！

📝 开始生成竞品监控报告...
✅ 报告生成完成！

📤 开始推送报告到飞书...
✅ 推送成功！（或提示配置 Webhook）
```

---

## 📊 查看报告

### 方式 1: 本地查看

```bash
# 查看今天的报告
cat reports/$(date +%Y-%m-%d).md

# 或用任何文本编辑器打开
```

### 方式 2: 飞书查看

如果配置了飞书 Webhook，报告会自动推送到群。

---

## ⏰ 设置定时任务

### 使用 cron（推荐）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天早上 9:00 运行）
0 9 * * * cd /root/.openclaw/workspace/competitors-monitor && python3 scripts/scrape.py && python3 scripts/diff.py && python3 scripts/report.py && python3 scripts/notify.py
```

### 保存并退出

- 保存: `Ctrl + O` → `Enter`
- 退出: `Ctrl + X`

---

## 🎯 日常使用

### 手动运行

```bash
cd /root/.openclaw/workspace/competitors-monitor

# 运行完整流程
python3 scripts/scrape.py && \
python3 scripts/diff.py && \
python3 scripts/report.py && \
python3 scripts/notify.py
```

### 查看日志

```bash
# 查看今天的数据
ls -lh data/$(date +%Y-%m-%d).json

# 查看今天的变化
ls -lh data/diff-$(date +%Y-%m-%d).json

# 查看今天的报告
ls -lh reports/$(date +%Y-%m-%d).md
```

---

## 🔧 常见问题

### Q1: 抓取失败怎么办？

**A**: 可能的原因和解决方案：

1. **网站有反爬虫**
   - 使用 Selenium（需要安装）
   - 添加代理 IP

2. **URL 错误**
   - 检查 URL 是否正确
   - 在浏览器中打开测试

3. **网络问题**
   - 检查网络连接
   - 增加超时时间

---

### Q2: 首次运行没有变化检测？

**A**: 正常现象。

- 首次运行没有昨天的数据
- 第二天开始会检测变化
- 第一天的数据会作为基准

---

### Q3: 如何添加更多竞品？

**A**: 编辑 `config.json`:

```json
{
  "competitors": [
    {
      "name": "竞品A",
      "url": "https://a.com",
      "pages": [...]
    },
    {
      "name": "竞品B",
      "url": "https://b.com",
      "pages": [...]
    },
    {
      "name": "竞品C",  // 新增
      "url": "https://c.com",  // 新增
      "pages": [...]  // 新增
    }
  ]
}
```

---

### Q4: 报告太长怎么办？

**A**: 飞书推送只发送摘要，完整报告在本地。

如果觉得本地报告也长，可以：
- 减少监控的页面数量
- 过滤不重要的变化
- 自定义报告格式

---

### Q5: 如何修改报告时间？

**A**: 编辑 crontab:

```bash
# 每天早上 8:00
0 8 * * * ...

# 每天中午 12:00
0 12 * * * ...

# 每天晚上 6:00
0 18 * * * ...
```

---

## 📁 文件结构

```
competitors-monitor/
├── config.json           # 配置文件
├── REQUIREMENTS.md       # 需求文档
├── SKILL.md             # Agent 1 手册
├── SKILL-DETECTOR.md    # Agent 2 手册
├── SKILL-REPORTER.md    # Agent 3 手册
├── SKILL-NOTIFIER.md    # Agent 4 手册
├── COMPLETE-TEST-REPORT.md  # 完整测试报告
├── scripts/
│   ├── scrape.py        # 抓取脚本
│   ├── diff.py          # 检测脚本
│   ├── report.py        # 报告脚本
│   └── notify.py        # 推送脚本
├── data/
│   ├── 2026-03-18.json  # 原始数据
│   ├── 2026-03-17.json
│   └── diff-2026-03-18.json  # 变化数据
└── reports/
    └── 2026-03-18.md    # 分析报告
```

---

## 🎓 进阶使用

### 自定义报告格式

编辑 `scripts/report.py`，修改 `generate_report()` 函数。

### 添加更多分析

在 `scripts/report.py` 中添加新的分析逻辑。

### 集成到其他系统

- 可以通过 API 调用
- 可以集成到 CI/CD
- 可以集成到监控面板

---

## 📞 获取帮助

- 查看 `REQUIREMENTS.md` 了解详细设计
- 查看 `COMPLETE-TEST-REPORT.md` 了解测试结果
- 查看 `SKILL*.md` 了解每个 Agent 的详细说明

---

**祝使用愉快！** 🎉

**文档版本**: v1.0
**最后更新**: 2026-03-18
