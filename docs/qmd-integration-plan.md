# 🚀 OpenClaw 记忆系统集成方案

**制定时间**: 2026-03-30 07:25
**制定人**: 大领导 🎯
**状态**: 🎯 执行中

---

## 📋 执行计划（按顺序）

### ✅ Step 1: 理解 OpenClaw 集成点（已完成）

**发现**:
- **Skill 系统**: `~/.agents/skills/<skill-name>/SKILL.md`
- **配置文件**: `/root/.openclaw/openclaw.json`
- **MCP Bridge**: `@aiwerk/openclaw-mcp-bridge`
- **触发机制**: 通过 `description` 自动匹配

**关键文件**:
- `/root/.agents/skills/heycube-get-config-0.1.0/SKILL.md` - Hook 示例
- `/root/.agents/skills/lark-im/SKILL.md` - Skill 示例
- `/root/.openclaw/openclaw.json` - 主配置文件

---

### 🔴 Step 2: 修复记忆系统（进行中）

#### 问题诊断

**全文搜索（BM25）**: ✅ 正常工作
```bash
qmd-search "MEMORY" --mode text
# 返回正确结果
```

**语义搜索**: ❌ Embeddings 生成失败
```
错误: Could NOT find Vulkan (missing: Vulkan_LIBRARY Vulkan_INCLUDE_DIR glslc)
原因: QMD 尝试编译本地模型（需要 Vulkan 依赖）
```

#### 解决方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **A. 禁用 embeddings** | 立即可用，无依赖 | 失去语义搜索 | ⭐⭐ |
| **B. 修复 Vulkan** | 完整功能 | 需要系统依赖，耗时 | ⭐⭐⭐ |
| **C. API embeddings** | 快速，可靠 | Groq 不支持 embeddings API | ❌ |

#### 问题发现：Groq 不支持 Embeddings API

**测试结果**:
```bash
curl https://api.groq.com/openai/v1/embeddings
# 返回: {"error":"model not found"}
```

**结论**: Groq API **不支持 embeddings**，只支持聊天模型。

#### 新解决方案

**方案 D: 使用 OpenAI Embeddings API（付费但可靠）**
- **成本**: $0.00002 / 1K tokens（非常便宜）
- **速度**: 快速（< 1 秒）
- **质量**: 高质量（text-embedding-3-small）

**方案 E: 使用本地 embeddings（无 GPU）**
- **成本**: 免费
- **速度**: 慢（CPU 推理）
- **质量**: 中等

**方案 F: 暂时禁用 embeddings（短期）**
- **优点**: 立即可用
- **缺点**: 只有全文搜索

---

### 📝 Step 3: 创建核心 Skills（待执行）

优先级列表：

1. **🔴 P0: 记忆搜索 Skill** - 对话前自动搜索
2. **🔴 P0: 记忆更新 Skill** - 对话后自动更新
3. **🟡 P1: 规则检查 Skill** - 操作前自动检查
4. **🟡 P1: 错误学习 Skill** - 错误后自动学习

---

### 🔧 Step 4: 配置 Hooks（待执行）

需要在 `openclaw.json` 中添加：

```json
{
  "plugins": {
    "entries": {
      "memory-hooks": {
        "enabled": true,
        "config": {
          "onMessage": "skills/memory-search",
          "onSessionStart": "skills/session-init",
          "onSessionEnd": "skills/memory-update"
        }
      }
    }
  }
}
```

---

## 🎯 下一步行动

### 立即执行（现在）

1. **确认方案**: 你希望使用哪个方案修复记忆系统？
   - 方案 A: 禁用 embeddings（最快）
   - 方案 D: OpenAI embeddings（付费但可靠）
   - 方案 E: 本地 embeddings（免费但慢）

2. **开始实施**: 一旦确认方案，立即执行

### 后续步骤

3. **创建 Skills**: 基于 P0 优先级创建核心 Skills
4. **配置 Hooks**: 修改 `openclaw.json` 添加自动触发
5. **测试验证**: 确保系统真正变聪明

---

## 💡 关键发现

> **"我之前创建了 255 个文件，但没有修改 OpenClaw 的核心配置！"**

**真正需要做的**:
1. ✅ 修改 `openclaw.json` - 添加 Skill/Hook 配置
2. ✅ 创建 Skill 文件 - `~/.agents/skills/<skill-name>/SKILL.md`
3. ✅ 集成到对话流程 - 不是独立脚本，而是被自动调用

---

**文档版本**: v1.0
**状态**: 🎯 等待用户确认方案
**下一步**: Step 2 - 修复记忆系统
