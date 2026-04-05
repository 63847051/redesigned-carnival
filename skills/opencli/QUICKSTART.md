# OpenCLI 快速使用指南

**安装完成时间**: 2026-04-01
**OpenCLI 版本**: 1.5.6
**状态**: ✅ 已安装并可用

---

## 🎯 快速开始

### 1. 验证安装

```bash
# 检查版本
opencli --version

# 列出所有命令
opencli list

# 诊断浏览器连接
opencli doctor
```

### 2. 基础使用

```bash
# B 站热门（需要登录）
opencli bilibili hot

# 知乎热榜（需要登录）
opencli zhihu hot

# BBC 新闻（公开 API，无需登录）
opencli bbc news

# 36 氦热榜（公开 API，无需登录）
opencli 36kr hot
```

### 3. 指定输出格式

```bash
# JSON 格式（适合 AI 处理）
opencli bilibili hot -f json

# Markdown 格式（适合阅读）
opencli zhihu hot -f markdown

# YAML 格式
opencli twitter timeline -f yaml

# CSV 格式（适合导入表格）
opencli reddit hot -f csv
```

---

## 📚 常用命令示例

### 视频平台

#### B 站
```bash
# 热门视频
opencli bilibili hot

# 搜索视频
opencli bilibili search "关键词"

# 获取视频字幕
opencli bilibili subtitle <视频ID>

# 获取视频评论
opencli bilibili comments <视频ID>

# 下载视频（需要 yt-dlp）
opencli bilibili download <视频ID>
```

#### YouTube
```bash
# 获取视频信息
opencli youtube video <视频ID>

# 搜索视频
opencli youtube search "关键词"
```

### 社交平台

#### 知乎
```bash
# 热榜
opencli zhihu hot

# 搜索
opencli zhihu search "关键词"
```

#### Twitter/X
```bash
# 时间线
opencli twitter timeline

# 书签
opencli twitter bookmarks
```

#### Reddit
```bash
# 热帖
opencli reddit hot

# 特定 subreddit
opencli reddit hot python

# 搜索
opencli reddit search "关键词"
```

### 财经数据

#### 雪球
```bash
# 股票信息
opencli xueqiu stock 600000

# 搜索股票
opencli xueqiu search "贵州茅台"
```

#### Barchart
```bash
# 期权链
opencli barchart options AAPL

# 期权流量
opencli barchart flow

# 希腊值
opencli barchart greeks
```

### 新闻资讯

```bash
# 36 氦
opencli 36kr hot

# BBC 新闻
opencli bbc news

# 彭博社
opencli bloomberg news

# 彭博社科技版块
opencli bloomberg tech
```

### 学术搜索

#### arXiv
```bash
# 搜索论文
opencli arxiv search "machine learning"

# 获取论文详情
opencli arxiv paper <论文ID>
```

---

## 🤖 AI Agent 使用场景

### 场景 1: 内容分析管道

```bash
# 1. 获取 B 站热门
opencli bilibili hot -f json > bilibili_hot.json

# 2. AI 分析（使用你的 AI Agent）
# ... 分析数据 ...

# 3. 发送到飞书
# ... 发送结果 ...
```

### 场景 2: 知识库更新

```bash
# 获取知乎热榜
opencli zhihu hot -f json > zhihu_hot.json

# 提取关键词
# 使用 AI 处理

# 更新 Notion 知识库
# ... 更新 ...
```

### 场景 3: 股票监控

```bash
# 获取股票数据
opencli xueqiu stock 600000 -f json > stock.json

# AI 分析趋势
# ... 分析 ...

# 发送提醒
# ... 发送通知 ...
```

---

## 🔧 浏览器扩展安装

### 步骤 1: 下载扩展

访问 OpenCLI GitHub:
https://github.com/jackwener/opencli

### 步骤 2: 安装到 Chrome

1. 打开 Chrome 扩展管理页面
2. 开启"开发者模式"
3. 加载已解压的扩展程序
4. 选择 OpenCLI 扩展目录

### 步骤 3: 验证连接

```bash
# 诊断连接
opencli doctor

# 应该显示类似：
# ✅ Browser extension connected
# ✅ Daemon running on localhost:19825
```

---

## ⚠️ 重要提示

### 权限说明

OpenCLI 复用你的浏览器登录态，所以：

- ✅ 你在浏览器中能做什么，OpenCLI 就能做什么
- ⚠️ Agent 拥有和你一样的权限
- 🔒 建议限制敏感操作（发帖、删除等）

### 稳定性

- ✅ OpenCLI 定期更新
- ⚠️ 网站改版可能导致命令失效
- 💡 遇到问题使用 `opencli doctor` 诊断

### 性能

- ✅ Daemon 空闲 5 分钟自动退出
- ✅ 不占用常驻资源
- ⚠️ 首次启动可能需要几秒钟

---

## 📚 更多资源

- **GitHub**: https://github.com/jackwener/opencli
- **文档**: https://github.com/jackwener/opencli/blob/main/README.md
- **本地技能**: `/root/.openclaw/workspace/skills/opencli/`

---

## 🎯 下一步

1. ✅ 安装 Chrome 扩展
2. ✅ 在浏览器中登录常用网站
3. ✅ 测试几个命令
4. ✅ 集成到你的工作流

---

**安装完成！开始探索万物皆可 CLI 的世界吧！** 🚀
