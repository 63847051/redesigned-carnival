# QMD Memory Search Skill

**版本**: 1.0.0
**创建时间**: 2026-03-22
**作者**: 大领导 🎯

---

## 📖 概述

QMD Memory Search Skill 是一个快速记忆检索工具，基于 QMD（Quick Markdown Search）实现，支持全文搜索和语义搜索。

### 核心特性

- ✅ **快速全文搜索** - BM25 算法，毫秒级响应
- ✅ **智能语义搜索** - 使用 Groq API embeddings
- ✅ **混合搜索** - 自动融合全文和语义
- ✅ **文件查看** - 快速查看记忆文件
- ✅ **38 个文件索引** - 覆盖所有记忆

---

## 🎯 使用方法

### 1️⃣ 搜索记忆

#### 全文搜索（快速）

```bash
qmd-search "蓝色光标"
```

**返回**:
```
🔍 搜索结果: "蓝色光标"

📄 memory/long-term/projects/blue-focus-shanghai.md
   Score: 73%
   📝 蓝色光标上海办公室工作日志
```

#### 语义搜索（智能）

```bash
qmd-search "幸运小行星的工作风格"
```

**返回**:
```
🧠 语义搜索: "幸运小行星的工作风格"

📄 memory/long-term/people/lucky-asteroid.md
   Score: 85%
   📝 幸运小行星喜欢高效、直接的工作方式...
```

### 2️⃣ 查看文件

#### 查看完整文件

```bash
qmd-get memory/long-term/people/lucky-asteroid.md
```

#### 查看特定行

```bash
qmd-get memory/long-term/people/lucky-asteroid.md:10
```

**返回**: 从第 10 行开始的内容

### 3️⃣ 批量查看

```bash
qmd-multi "memory/**/*.md"
```

---

## 🔧 技术细节

### QMD 配置

**配置文件**: `~/.qmd/config.json`

```json
{
  "collections": [
    {
      "name": "memory-root",
      "path": "/root/.openclaw/workspace",
      "pattern": "MEMORY.md"
    },
    {
      "name": "memory-dir",
      "path": "/root/.openclaw/workspace/memory",
      "pattern": "**/*.md"
    }
  ],
  "search": {
    "mode": "query",
    "embedding": {
      "provider": "openai",
      "model": "text-embedding-3-small",
      "baseUrl": "https://api.groq.com/openai/v1",
      "apiKey": "gsk_********************"
    }
  }
}
```

### 索引文件

**总计**: 38 个 Markdown 文件

**分类**:
- `memory/long-term/` - 长期记忆
- `memory/short-term/` - 短期记忆
- `memory/YYYY-MM-DD.md` - 每日日志

---

## 📊 性能指标

| 操作 | 速度 | 说明 |
|------|------|------|
| **全文搜索** | < 1 秒 | BM25 算法 |
| **语义搜索** | 2-5 秒 | Groq API |
| **文件查看** | < 0.5 秒 | 直接读取 |
| **批量查看** | 1-2 秒 | 取决于文件数 |

---

## 💡 最佳实践

### 1️⃣ 优先使用语义搜索

```bash
# ✅ 推荐：理解自然语言
qmd-search "幸运小行星的工作风格"

# ❌ 不推荐：简单关键词
qmd-search "工作 风格"
```

### 2️⃣ 使用具体问题

```bash
# ✅ 推荐：具体问题
qmd-search "蓝色光标项目的待办任务"

# ❌ 不推荐：模糊关键词
qmd-search "蓝色光标"
```

### 3️⃣ 查看完整上下文

```bash
# 搜索到结果后，查看完整文件
qmd-get memory/long-term/projects/blue-focus-shanghai.md
```

---

## 🚨 注意事项

### API 依赖

**语义搜索**需要网络连接（Groq API）

**离线方案**: 使用全文搜索（无需网络）

### API Key 安全

⚠️ **重要**: API Key 存储在 `~/.qmd/config.json`

**建议**:
- 定期轮换 Key
- 限制 API 权限
- 使用环境变量（可选）

---

## 📚 相关文档

- **QMD 官方文档**: https://github.com/tobilu/qmd
- **安装报告**: `/root/.openclaw/workspace/.learnings/improvements/qmd-installation-report-20260322.md`
- **MEMORY.md**: `/root/.openclaw/workspace/MEMORY.md`

---

## 🎉 快速开始

```bash
# 搜索记忆
qmd-search "你的问题"

# 查看文件
qmd-get memory/file.md

# 批量查看
qmd-multi "memory/**/*.md"
```

---

**版本**: 1.0.0
**状态**: ✅ 活跃
**最后更新**: 2026-03-22
