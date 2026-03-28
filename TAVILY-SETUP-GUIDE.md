#!/bin/bash
# Tavily 配置指南 - OpenClaw AI 搜索集成

## 🎯 目标
为 OpenClaw 添加 AI 搜索能力（Tavily）

## 📋 注册步骤（5 分钟）

### 步骤 1: 访问 Tavily 官网
打开浏览器访问：https://tavily.com

### 步骤 2: 注册账号
1. 点击右上角 "Sign Up"
2. 使用 Google 账号一键注册
3. 填写邮箱（或跳过）
4. 设置密码（或跳过）

### 步骤 3: 获取 API Key
1. 登录后进入 Dashboard
2. 点击顶部导航 "API Keys"
3. 复制 API Key（格式：tvly-xxxxxxxxxxxx）

## 🔧 配置到 OpenClaw

### 方法 1: 环境变量
编辑 OpenClaw 配置文件（.env 或 config）：
```bash
# Tavily AI 搜索 API
TAVILY_API_KEY=tvly-你的Key粘贴这里
```

### 方法 2: Skill 配置
创建 Skill 配置文件：
```yaml
name: tavily-search
description: AI 搜索引擎，为 AI Agent 提供实时搜索能力
version: 1.0
config:
  api_key: ${TAVILY_API_KEY}
  base_url: https://api.tavily.com
```

## 🧪 测试配置

### 测试搜索
```bash
# 方法 1: 使用 curl
curl -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -H "API-Key: tvly-你的Key" \
  -d '{
    "query": "AI 领域最新动态",
    "search_depth": "basic",
    "include_domains": ["techcrunch.com", "wired.com"],
    "max_results": 5
  }'

# 方法 2: 在 OpenClaw 中测试
# 发送消息："帮我搜索 AI 领域今天的新闻"
```

## 📊 使用场景

### 1️⃣ 每日选题灵感
**任务**: 每天 8:00 自动搜索
**提示词**: "搜索 AI 领域最新进展，找出 3 个值得写的选题"

### 2️⃣ 热点追踪
**任务**: 监控特定话题
**提示词**: "搜索 'AI 绘画版权' 最新进展"

### 3️⃣ 背景调研
**任务**: 快速了解全貌
**提示词**: "搜索 'SaaS 客户成功案例', 总结 3 个关键要素"

## 💰 费用

| 套餐 | 价格 | 说明 |
|------|------|------|
| Free | $0 | 1000 credits/月 |
| Researcher | $19/月起 | 5000 credits/月 |
| Teams | 按量计费 | 大规模商业 |

**个人使用建议**：
- 每天 5 次搜索 = 150 次/月
- 1000 次免费可用 200 天

## 🚀 下一步

1. 注册账号
2. 获取 API Key
3. 测试搜索功能
4. 创建自动化任务
5. 监控使用情况

---

**创建时间**: 2026-03-28 22:48
**版本**: v1.0
**状态**: 待执行
