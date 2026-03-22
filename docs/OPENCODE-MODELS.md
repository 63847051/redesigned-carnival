# opencode Agent 模型配置指南

**创建时间**: 2026-03-22 14:41
**最后更新**: 2026-03-22 14:41
**版本**: v1.0

---

## 📋 opencode 免费大模型

### 1. opencode/minimax-m2.5-free ⭐ 主要使用

**名称**: MiniMax M2.5 Free
**家族**: minimax-free
**状态**: active
**成本**: 完全免费

**特点**：
- 代码优化
- 快速响应
- 适合编程任务

**使用命令**：
```bash
opencode -m opencode/minimax-m2.5-free run "你的任务"
```

---

### 2. opencode/mimo-v2-pro-free

**名称**: MiMo V2 Pro Free
**家族**: mimo-pro-free
**状态**: active
**成本**: 完全免费

**特点**：
- 多模态能力
- 高级推理
- 适合复杂任务

**使用命令**：
```bash
opencode -m opencode/mimo-v2-pro-free run "你的任务"
```

---

### 3. opencode/nemotron-3-super-free

**名称**: Nemotron 3 Super Free
**家族**: nemotron-free
**状态**: active
**成本**: 完全免费

**特点**：
- 强大性能
- 深度理解
- 适合复杂分析

**使用命令**：
```bash
opencode -m opencode/nemotron-3-super-free run "你的任务"
```

---

## 🔧 查看模型命令

### 查看所有模型
```bash
opencode models
```

### 查看详细模型信息
```bash
opencode models opencode --verbose
```

### 查看特定模型
```bash
opencode models opencode/minimax-m2.5-free --verbose
```

---

## 🎯 使用建议

### 默认使用
**opencode/minimax-m2.5-free** ⭐
- 这是 opencode Agent 的主要免费模型
- 在 `/root/.openclaw/openclaw.json` 中配置
- 适合大部分编程任务

### 备选使用
- **复杂任务**: opencode/mimo-v2-pro-free
- **深度分析**: opencode/nemotron-3-super-free

---

## ⚠️ 重要规则

### ✅ 必须
- 使用 opencode 自己的免费模型
- 优先使用 `opencode/minimax-m2.5-free`
- 不要和其他 Agent 的模型混淆

### ❌ 不要
- 不要使用 `glmcode` 模型（那是其他 Agent 的）
- 不要混淆模型配置
- 不要随意切换模型

---

## 📊 模型对比

| 模型 | 名称 | 特点 | 用途 |
|------|------|------|------|
| **minimax-m2.5-free** | MiniMax M2.5 Free | 代码优化 | 主要使用 ⭐ |
| **mimo-v2-pro-free** | MiMo V2 Pro Free | 多模态 | 复杂任务 |
| **nemotron-3-super-free** | Nemotron 3 Super Free | 强大性能 | 深度分析 |

---

## 💡 记住

**opencode Agent 的模型**：
- ✅ `opencode/minimax-m2.5-free`（主要）
- ✅ `opencode/mimo-v2-pro-free`（备选）
- ✅ `opencode/nemotron-3-super-free`（备选）
- ❌ 不是 `glmcode/glm-4.5-air`

---

**大领导永久记住！** ✨

**最后更新**: 2026-03-22 14:41
**版本**: v1.0
