# 微信公众号文章阅读器 MCP 服务器 - 使用指南

## 🚀 快速开始

### 启动服务器
```bash
cd /root/.openclaw/workspace/mcp-wechat-reader
./start.sh
```

### 测试功能
```bash
python3 test_server.py <微信文章URL>
```

## 📋 工具列表

### 1. read_wechat_article
读取完整的微信文章内容

**输入**:
- `url`: 微信公众号文章 URL (mp.weixin.qq.com)

**输出**:
- 标题、作者、正文、发布时间、公众号名称

### 2. extract_article_info
提取文章的关键信息

**输入**:
- `url`: 微信公众号文章 URL

**输出**:
- 标题、作者、公众号、发布时间
- 字数统计
- 图片链接（前5张）
- 摘要

### 3. summarize_article
生成文章摘要

**输入**:
- `url`: 微信公众号文章 URL
- `max_length`: 摘要最大长度（默认200字）

**输出**:
- 摘要内容

## 🎯 使用示例

### 示例 1: 读取文章
```
# 输入
{
  "url": "https://mp.weixin.qq.com/s/xxx"
}

# 输出
{
  "title": "文章标题",
  "author": "作者名",
  "content": "文章正文...",
  "account": "公众号名称"
}
```

### 示例 2: 提取信息
```
# 输入
{
  "url": "https://mp.weixin.qq.com/s/xxx"
}

# 输出
{
  "title": "...",
  "word_count": 1234,
  "image_count": 5
}
```

### 示例 3: 生成摘要
```
# 输入
{
  "url": "https://mp.weixin.qq.com/s/xxx",
  "max_length": 100
}

# 输出
{
  "summary": "100字摘要..."
}
```

## 🔧 集成到 OpenClaw

### 配置 OpenClaw
在 openclaw.json 中添加：

```json
{
  "mcpServers": {
    "wechat-reader": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/root/.openclaw/workspace/mcp-wechat-reader"
    }
  }
}
```

### 使用
在对话中直接分享微信文章链接，系统会自动读取并总结。

---

**创建时间**: 2026-03-12
**版本**: 1.0.0
**状态**: ✅ 就绪
