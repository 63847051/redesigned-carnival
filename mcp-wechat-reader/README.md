# 微信公众号文章阅读器 MCP 服务器

**版本**: 1.0.0
**创建时间**: 2026-03-12
**状态**: ✅ 已创建

---

## 🎯 功能

### 工具 1: read_wechat_article
读取微信公众号文章的完整内容

**输入**:
- `url`: 微信公众号文章 URL (mp.weixin.qq.com)

**输出**:
- 标题
- 作者
- 公众号名称
- 发布时间
- 正文内容
- 摘要（前200字）

---

### 工具 2: extract_article_info
提取文章的关键信息

**输入**:
- `url`: 微信公众号文章 URL (mp.weixin.qq.com)

**输出**:
- 标题、作者、公众号、发布时间
- 字数统计
- 图片链接（前5张）
- 摘要

---

### 工具 3: summarize_article
生成文章摘要

**输入**:
- `url`: 微信公众号文章 URL (mp.weixin.qq.com)
- `max_length`: 摘要最大长度（默认200字）

**输出**:
- 摘要内容
- 原文字数

---

## 🚀 使用方式

### 方式 1: 直接读取文章
```python
# 输入
read_wechat_article(url="https://mp.weixin.qq.com/s/xxx")

# 输出
{
  "title": "文章标题",
  "author": "作者名",
  "content": "文章正文...",
  "summary": "文章摘要..."
}
```

### 方式 2: 提取关键信息
```python
extract_article_info(url="https://mp.weixin.qq.com/s/xxx")

# 输出
{
  "title": "...",
  "word_count": 1234,
  "image_count": 5,
  "images": [...]
}
```

### 方式 3: 生成摘要
```python
summarize_article(url="https://mp.weixin.qq.com/s/xxx", max_length=100)

# 输出
{
  "summary": "100字摘要..."
}
```

---

## 🔧 依赖项

### 必需
- Python 3.10+
- fastmcp
- httpx
- beautifulsoup4

### 安装依赖
```bash
pip install fastmcp httpx beautifulsoup4
```

---

## 🚀 启动服务器

### 方式 1: 直接运行
```bash
python server.py
```

### 方式 2: 通过 mcp-bridge
```bash
mcp-bridge start /path/to/mcp-wechat-reader
```

---

## 📝 测试

### 测试 URL
可以使用任意微信公众号文章链接进行测试。

### 预期结果
- ✅ 成功读取文章
- ✅ 提取关键信息
- ✅ 生成摘要

---

**创建时间**: 2026-03-12
**状态**: ✅ 已创建，待启动测试
