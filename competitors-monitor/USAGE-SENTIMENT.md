# 客户舆情监控 - 使用指南

## 概述

客户舆情监控帮助企业跟踪社交媒体和新闻网站上关于品牌、产品或竞争对手的讨论，进行情感分析并及时发现负面舆情。

## 功能特性

- **多平台监控**: 支持 Twitter、News API、RSS 订阅
- **情感分析**: 自动分析文本情感（正面/中性/负面）
- **关键词追踪**: 监控品牌名、产品名相关讨论
- **异常告警**: 负面舆情、热度飙升自动告警

## 配置说明

编辑 `config/sentiment.json`:

```json
{
  "data_sources": {
    "rss_feed": {
      "enabled": true,
      "feeds": [
        "https://news.google.com/rss/search?q=YOUR_BRAND"
      ]
    },
    "mock": {
      "enabled": true
    }
  },
  "targets": [
    {
      "name": "品牌舆情",
      "keywords": ["产品名", "公司名"],
      "negative_keywords": ["投诉", "欺诈", "bug"]
    }
  ],
  "check_rules": {
    "sentiment_threshold_negative": -0.3,
    "sentiment_threshold_positive": 0.3
  }
}
```

## 运行方式

```bash
cd /root/.openclaw/workspace/competitors-monitor
python3 plugins/sentiment.py
```

## 输出示例

```
获取到 6 条舆情数据
发现 2 条告警

## 📊 舆情监控报告

### 情感分布

- 正面: 2 条
- 负面: 2 条
- 中性: 2 条

### ⚠️ 告警

🔴 检测到负面舆情: 产品体验很差，客服态度不好...
🔴 检测到负面舆情: 产品有bug，经常崩溃...
```

## 数据源配置

### RSS 订阅

启用 RSS 订阅:

```json
"rss_feed": {
  "enabled": true,
  "feeds": [
    "https://news.google.com/rss/search?q=YOUR_BRAND",
    "https://www.example.com/feed.xml"
  ]
}
```

### Twitter API

1. 访问 https://developer.twitter.com
2. 创建项目获取 Bearer Token
3. 配置:

```json
"twitter": {
  "enabled": true,
  "bearer_token": "YOUR_BEARER_TOKEN"
}
```

### News API

1. 访问 https://newsapi.org 注册
2. 获取 API Key
3. 配置:

```json
"news_api": {
  "enabled": true,
  "api_key": "YOUR_API_KEY"
}
```

## 告警类型

| 类型 | 严重程度 | 说明 |
|------|----------|------|
| negative_sentiment | warning | 检测到负面情感 |
| crisis_detected | error | 危机舆情（高互动量负面） |
| viral_post | info | 热度飙升 |

## 集成飞书通知

配置 webhook 接收实时告警:

```json
"notification": {
  "feishu_webhook": "YOUR_WEBHOOK_URL"
}
```
