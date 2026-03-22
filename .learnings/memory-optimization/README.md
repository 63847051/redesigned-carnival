# OpenClaw 记忆系统优化指南（Groq 免费版）

**更新时间**: 2026-03-21
**基于**: 彬子 OpenClaw 记忆系统系列文章
**Provider**: Groq（免费）
**状态**: 准备就绪

---

## 🎉 **好消息！你已经有 Groq 了！**

你的系统已经配置了 Groq API Key，可以直接使用 Groq 的 embedding 模型，**完全免费**！

---

## 🚀 **快速开始（3 步完成）**

### 第一步：合并配置

运行配置合并脚本：

```bash
bash /root/.openclaw/workspace/scripts/merge-memory-config.sh
```

**选择选项 1**（使用 Groq）

脚本会自动：
- ✅ 备份原配置
- ✅ 合并 memorySearch 配置
- ✅ 使用你现有的 Groq API Key

---

### 第二步：验证配置

运行验证脚本：

```bash
bash /root/.openclaw/workspace/scripts/verify-memory-config.sh
```

你应该看到：
```
✅ Provider: openai
✅ Model: text-embedding-3-small
✅ 混合检索: 已启用
✅ MMR 多样性重排: 已启用
✅ 时间衰减: 已启用
✅ 批量 embedding: 已启用
✅ 缓存: 已启用
```

---

### 第三步：重启 Gateway

```bash
systemctl --user restart openclaw-gateway
```

检查状态：
```bash
systemctl --user status openclaw-gateway
```

---

## ✅ **完成！**

配置完成后，你的记忆系统将会：

| 功能 | 配置 | 效果 |
|------|------|------|
| **混合检索** | 语义 70% + 关键词 30% | 更准确的语义理解 |
| **Embedding 模型** | Groq (text-embedding-3-small) | 免费、快速 |
| **MMR 重排** | Lambda 0.7 | 避免结果重复 |
| **时间衰减** | 30 天半衰期 | 新内容优先 |
| **批量处理** | 并发 2 | 更快的 embedding |
| **缓存** | 50000 条目 | 减少 API 调用 |

---

## 📊 **配置详情**

### Groq 配置

```json
{
  "memorySearch": {
    "provider": "openai",
    "model": "text-embedding-3-small",
    "remote": {
      "baseUrl": "https://api.groq.com/openai/v1",
      "apiKey": "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",
      "batch": {
        "enabled": true,
        "concurrency": 2
      }
    },
    "query": {
      "hybrid": {
        "enabled": true,
        "vectorWeight": 0.7,
        "textWeight": 0.3,
        "candidateMultiplier": 4,
        "mmr": {
          "enabled": true,
          "lambda": 0.7
        },
        "temporalDecay": {
          "enabled": true,
          "halfLifeDays": 30
        }
      }
    },
    "cache": {
      "enabled": true,
      "maxEntries": 50000
    }
  }
}
```

---

## 🎯 **参数说明**

### 混合检索（Hybrid Search）

```json
"vectorWeight": 0.7,    // 语义检索权重（70%）
"textWeight": 0.3,      // 关键词检索权重（30%）
"candidateMultiplier": 4 // 候选池大小（4倍）
```

**为什么 70:30?**
- 概念式查询更适合语义检索（如"上次我们定的方案是啥"）
- 关键词检索负责兜底
- 三七开比较适合常规记忆检索

### MMR 多样性重排

```json
"mmr": {
  "enabled": true,
  "lambda": 0.7  // 70% 相关性，30% 多样性
}
```

**为什么需要 MMR?**
- 避免结果太相似（如搜"OpenClaw"，前几条都在讲安装步骤）
- 提高信息密度
- 70% 看相关性，30% 看多样性

### 时间衰减

```json
"temporalDecay": {
  "enabled": true,
  "halfLifeDays": 30  // 30 天半衰期
}
```

**为什么需要时间衰减?**
- 新内容优先（符合人的记忆方式）
- 半衰期 30 天（一个月前的内容权重衰减到一半）
- 只影响 `memory/YYYY-MM-DD.md`，不影响 `MEMORY.md` 等长期知识文件

---

## 💡 **常见问题**

### Q1: Groq 是免费的吗？

**A**: 是的！Groq 提供免费的 API 访问，包括 embedding 模型。

### Q2: 配置后需要多久才能生效？

**A**:
- 首次启动需要时间完成初始索引（取决于文件数量）
- 之后是增量更新（几乎无感知）
- 重启 Gateway 后立即生效

### Q3: 如何验证配置是否生效？

**A**:
1. 运行验证脚本：`bash /root/.openclaw/workspace/scripts/verify-memory-config.sh`
2. 查看 Gateway 日志：`journalctl --user -u openclaw-gateway -f`
3. 在对话中触发记忆检索

### Q4: 可以切换到 DashScope 吗？

**A**: 可以！
1. 获取 DashScope API Key: https://dashscope.console.aliyun.com/
2. 编辑 `/root/.openclaw/openclaw-memory-config.json`
3. 替换 `YOUR_DASHSCOPE_API_KEY_HERE`
4. 重新运行合并脚本，选择选项 2

### Q5: 配置出问题了怎么办？

**A**: 回滚到备份：
```bash
cp /root/.openclaw/openclaw.json.backup /root/.openclaw/openclaw.json
systemctl --user restart openclaw-gateway
```

---

## 🎯 **下一步（可选）**

### 中期优化

#### 1. 创建记忆扫描脚本

**功能**:
- 📊 每天定时扫描对话
- 🤝 自动提取关键信息
- 📝 自动更新 MEMORY.md

#### 2. 创建夜间反思脚本

**功能**:
- 🌙 每天 00:45 执行日志查缺补漏
- 🌙 每天 01:00 执行深度反思
- 📚 自动回写知识库

#### 3. 安装 QMD 系统（高级）

**优势**:
- ✅ 多 Collection 管理
- ✅ 跨 App 统一检索（Memory + Obsidian）
- ✅ 更高质量的检索（查询扩展 + Reranker）

---

## 📈 **预期效果**

根据 彬子 的实测数据：

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| **日志完整性** | ~60% | ~95% |
| **检索准确度** | 靠关键词 | 语义 + 关键词 |
| **结果多样性** | 经常重复 | MMR 去重 |
| **时间敏感度** | 无 | 新内容优先 |

---

## 🎉 **总结**

**使用 Groq 的优势**:
- ✅ **完全免费** - 无需付费
- ✅ **快速** - Groq 的推理速度很快
- ✅ **已配置** - 直接使用现有 API Key
- ✅ **简单** - 3 步完成配置

**准备好了吗？**

```bash
# 第 1 步：合并配置
bash /root/.openclaw/workspace/scripts/merge-memory-config.sh

# 第 2 步：验证配置
bash /root/.openclaw/workspace/scripts/verify-memory-config.sh

# 第 3 步：重启 Gateway
systemctl --user restart openclaw-gateway
```

**就这么简单！** 🚀✨

---

**最后更新**: 2026-03-21
**状态**: 准备就绪
**Provider**: Groq（免费）
