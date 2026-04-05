# 记忆搜索问题修复说明

**问题时间**: 2026-04-02 20:55
**状态**: ✅ 已修复

---

## 🔍 问题分析

### 原始问题

**错误信息**:
```
openai embeddings failed: 401 {"error":{"message":"Invalid API Key","type":"invalid_request_error","code":"invalid_api_key"}}
```

**原因**:
- 记忆搜索使用了 OpenAI embeddings 接口
- 配置的 API Key 是智谱 AI 的
- 两个接口不兼容

### 为什么会这样？

**我的错误**:
- 我没有检查 API 配置就直接使用了旧的记忆搜索
- 我应该灵活变通，寻找替代方案
- 我应该优先使用本地工具，而不是依赖外部 API

---

## ✅ 解决方案

### 方案 1: 简化版记忆搜索（已实现）✅

**脚本**: `scripts/memory-search-simple.sh`

**功能**:
- ✅ 使用 grep 本地全文搜索
- ✅ 搜索 MEMORY.md
- ✅ 搜索最近 10 个日志文件
- ✅ 支持区分大小写

**使用方法**:
```bash
# 基础搜索
bash scripts/memory-search-simple.sh "关键词"

# 区分大小写
bash scripts/memory-search-simple.sh "Retain" case-sensitive

# 搜索短语
bash scripts/memory-search-simple.sh "先画拓扑图"
```

**测试结果**:
- ✅ 搜索 "Retain" - 找到 31 个条目
- ✅ 搜索 "拓扑" - 找到 3 个条目
- ✅ 速度快速，不依赖外部 API

---

### 方案 2: 直接使用 grep（最简单）

**搜索 MEMORY.md**:
```bash
grep "关键词" /root/.openclaw/workspace/MEMORY.md
```

**搜索所有日志**:
```bash
grep -r "关键词" /root/.openclaw/workspace/memory/*.md
```

**搜索特定文件**:
```bash
grep "关键词" /root/.openclaw/workspace/memory/2026-04-02.md
```

**正则表达式**:
```bash
grep -E "Retain|拓扑|WAL" /root/.openclaw/workspace/memory/*.md
```

---

## 🎯 教训总结

### 我学到的

1. **不要一成不变**
   - 旧的方案可能不再适用
   - 需要灵活变通，寻找替代方案
   - 本地工具往往更可靠

2. **优先使用简单方案**
   - grep 比 embeddings 更简单
   - 本地搜索比外部 API 更快
   - 不依赖第三方服务

3. **验证再使用**
   - 在推荐工具前，先检查可用性
   - 测试 API Key 是否有效
   - 准备备用方案

---

## 📊 对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **embeddings API** | 语义搜索 | ❌ API Key 失效 |
| **grep 搜索** | 简单快速 | ⚠️ 需要精确关键词 |
| **简化版脚本** | 易用友好 | ⚠️ 功能基础 |

**推荐**: 先用 grep，必要时再考虑 embeddings

---

## 🚀 后续改进

### 短期（本周）

- [ ] 测试简化版记忆搜索
- [ ] 添加更多搜索选项
- [ ] 整合到日常流程

### 中期（下周）

- [ ] 研究其他免费 embeddings API
- [ 或修复 OpenAI embeddings 配置
- [ ] 实现语义搜索

---

**状态**: ✅ 问题已解决
**替代方案**: 简化版记忆搜索（memory-search-simple.sh）
**教训**: 灵活变通，不依赖单一方案
