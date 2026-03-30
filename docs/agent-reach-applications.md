# Agent-Reach 应用示例

**版本**: v1.0
**创建时间**: 2026-03-30 18:10
**参考**: 无需API，一句话让Claude Code和OpenClaw刷小红书、抖音、B站、公众号等等

---

## 🎯 4 大应用场景

### 1️⃣ 市场调研

**目标**: 快速了解用户痛点和竞品反馈

**示例**：
```
用户: 搜索小红书"SK-II 神仙水"最近 10 篇笔记，总结用户痛点

Agent 执行:
1. agent-reach search-xiaohongshu "SK-II 神仙水" -n 10
2. 提取笔记内容
3. 总结用户痛点（敏感肌、价格、效果等）
```

**价值**：
- ✅ 快速收集用户反馈
- ✅ 发现产品痛点
- ✅ 竞品分析

---

### 2️⃣ 内容创作

**目标**: 解析热门视频，生成新内容

**示例**：
```
用户: 解析这个抖音视频，帮我生成小红书笔记
[抖音链接]

Agent 执行:
1. agent-reach parse-douyin [抖音链接]
2. 提取视频文案和背景音乐
3. 生成小红书笔记（标题、文案、标签）
```

**价值**：
- ✅ 跨平台内容复用
- ✅ 快速生成内容
- ✅ 素材收集

---

### 3️⃣ 学习总结

**目标**: 提取长视频/文章，转为结构化知识点

**示例**：
```
用户: 提取这个 B站视频的字幕，用中文总结重点
[B站链接]

Agent 执行:
1. agent-reach bilibili-subtitles [B站链接]
2. 提取字幕内容
3. 总结为结构化知识点（1、2、3...）
```

**价值**：
- ✅ 快速学习
- ✅ 知识沉淀
- ✅ 笔记整理

---

### 4️⃣ 趋势监控

**目标**: 实时了解赛道热度

**示例**：
```
用户: 监控最近 24 小时"AI Agent"相关讨论
- 微博热搜
- 雪球股票
- 小红书笔记

Agent 执行:
1. agent-reach weibo-trending
2. agent-reach xueqiu-search "AI Agent"
3. agent-reach search-xiaohongshu "AI Agent"
4. 汇总热度报告
```

**价值**：
- ✅ 实时监控
- ✅ 趋势分析
- ✅ 投资决策

---

## 📊 当前可用渠道

### ✅ 装好即用（8 个）

| 平台 | 状态 | 功能 |
|------|------|------|
| **YouTube** | ✅ 可用 | 视频信息和字幕 |
| **V2EX** | ✅ 可用 | 节点、主题、回复 |
| **RSS** | ✅ 可用 | RSS/Atom 源 |
| **全网搜索** | ✅ 可用 | 语义搜索 |
| **任意网页** | ✅ 可用 | Jina Reader |
| **B站** | ✅ 可用 | 视频和字幕 |
| **微博** | ✅ 可用 | 动态、热搜、评论 |
| **小宇宙** | ✅ 可用 | 播客转文字 |

### ⚠️ 需要配置（5 个）

| 平台 | 状态 | 需求 |
|------|------|------|
| **Twitter/X** | ⚠️ 未配置 | AUTH_TOKEN + CT0 |
| **Reddit** | ⚠️ 需要代理 | 服务器 IP 被封锁 |
| **小红书** | ⚠️ 需要 Docker | MCP 服务 + Cookie |
| **雪球** | ⚠️ 连接失败 | 可能需要代理 |
| **GitHub** | ⚠️ 未安装 gh CLI | 安装 gh CLI |

---

## 🔧 快速开始

### 检查状态
```bash
agent-reach doctor
```

### 配置 Twitter
```bash
export AUTH_TOKEN="xxx"
export CT0="yyy"
```

### 配置小红书（需要 Docker）
```bash
# 1. 安装 Docker
# 2. 配置 Cookie（使用 Chrome Cookie-Editor 插件）
# 3. 运行小红书 MCP 服务
```

---

## 🎯 触发词

Agent-Reach 会自动识别以下触发词：

**中文**：
- "搜推特"
- "搜小红书"
- "看视频"
- "搜一下"
- "上网搜"
- "帮我查"
- "B站"
- "bilibili"
- "抖音视频"
- "微信文章"
- "公众号"
- "微博"
- "小宇宙"
- "播客"
- "雪球"
- "股票"

**英文**：
- "search twitter"
- "youtube transcript"
- "search reddit"
- "read this link"
- "web search"
- "research"
- "帮我安装"

---

## 📚 参考文档

- **GitHub**: https://github.com/Panniantong/Agent-Reach
- **文档**: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
- **配置**: ~/.agent-reach/config.yaml

---

**状态**: ✅ Agent-Reach 已安装（9/16 渠道可用）
**覆盖率**: 56.25%
**下一步**: 配置 Twitter、小红书、Reddit
