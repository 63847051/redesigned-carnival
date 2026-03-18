# 通用监控框架 - 架构文档

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    scripts/run.py                       │
│                      (主入口)                            │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│  Monitor  │  │ Detector  │  │ Notifier  │
│  (抓取)   │  │  (检测)    │  │  (推送)   │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │
      ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│  Plugin   │  │  difflib  │  │  Webhook  │
│  系统     │  │  算法     │  │  协议     │
└───────────┘  └───────────┘  └───────────┘
```

### 核心模块

| 模块 | 文件 | 职责 |
|------|------|------|
| Monitor | `core/monitor.py` | 数据抓取、插件管理 |
| Detector | `core/detector.py` | 变化检测、文本比对 |
| Reporter | `core/reporter.py` | 报告生成、Markdown输出 |
| Notifier | `core/notifier.py` | 消息推送、飞书集成 |

---

## 插件开发指南

### 创建自定义数据源插件

```python
from core.monitor import DataSourcePlugin

class MyPlugin(DataSourcePlugin):
    def fetch(self, config):
        # 实现抓取逻辑
        return [...]
    
    def validate(self, data):
        # 实现验证逻辑
        return len(data) > 0
```

### 注册插件

在 `Monitor._load_plugin()` 中添加：

```python
elif plugin_type == 'my_plugin':
    return MyPlugin()
```

---

## 扩展说明

### 添加新的通知渠道

在 `Notifier.send()` 中添加：

```python
if notification.get('dingtalk_webhook'):
    # 钉钉推送逻辑
```

### 添加新的检测算法

在 `Detector` 中添加新方法：

```python
def detect_with_ai(self, data1, data2):
    # 使用 AI 进行语义分析
    pass
```

### 数据存储扩展

支持导出到：
- MySQL / PostgreSQL
- Elasticsearch
- Prometheus
