# 通用监控框架 - 使用指南

## 快速开始

### 1. 安装依赖

```bash
cd /root/.openclaw/workspace/competitors-monitor
pip3 install requests beautifulsoup4
```

### 2. 运行监控

```bash
python3 scripts/run.py config/competitor.json
```

### 3. 查看结果

- 原始数据: `data/raw/YYYY-MM-DD.json`
- 变化数据: `data/diff-YYYY-MM-DD.json`
- 报告: `data/reports/YYYY-MM-DD.md`

---

## 配置说明

### 配置文件结构

```json
{
  "monitor_type": "webpage",
  "name": "监控名称",
  "user_agent": "浏览器标识",
  "targets": [...],
  "check_rules": {...},
  "notification": {...}
}
```

### 核心字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `monitor_type` | 监控类型 | `webpage` / `api` |
| `name` | 监控项目名称 | `竞品监控` |
| `user_agent` | HTTP 请求头 | `Mozilla/5.0 ...` |

### targets - 监控目标

```json
"targets": [
  {
    "name": "Apple",
    "pages": [
      {
        "name": "首页",
        "url": "https://www.apple.com",
        "type": "homepage"
      }
    ]
  }
]
```

### notification - 通知配置

```json
"notification": {
  "feishu_webhook": "飞书机器人Webhook地址",
  "report_time": "09:00"
}
```

---

## 常见问题

### Q: 如何添加新的监控目标？

编辑 JSON 配置文件，在 `targets` 数组中添加新目标。

### Q: 如何仅运行数据抓取？

直接调用 `Monitor` 类：

```python
from core.monitor import Monitor
monitor = Monitor(config)
data = monitor.fetch()
```

### Q: 如何跳过通知推送？

将配置中的 `feishu_webhook` 设为空或保持默认。

### Q: 支持哪些监控类型？

- `webpage`: 网页内容监控
- `api`: API 数据监控
