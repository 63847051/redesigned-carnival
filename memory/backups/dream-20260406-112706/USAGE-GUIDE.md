# Memory Persistence Hooks 使用指南

**创建时间**: 2026-04-04 22:18:48

---

## 🎯 功能说明

Memory Persistence Hooks 让 AI 自动记住项目相关的决策、模式和经验。

### 两个 Hook

1. **SessionStart Hook** - 会话开始时自动加载记忆
2. **SessionEnd Hook** - 会话结束时自动保存记忆

---

## 🚀 自动触发

### SessionStart Hook

**触发时机**: 会话开始时自动触发

**功能**:
- 检查项目记忆是否存在
- 显示项目记忆摘要
- 帮助 AI 快速了解项目背景

### SessionEnd Hook

**触发时机**: 会话结束时自动触发

**功能**:
- 分析2026-04-06的日志
- 提取关键决策和经验
- 追加到项目记忆

---

## 🔧 手动触发

### 触发 SessionStart

```bash
bash /root/.openclaw/workspace/hooks/session-start.sh
```

### 触发 SessionEnd

```bash
bash /root/.openclaw/workspace/hooks/session-end.sh
```

### 同时触发两个 Hook

```bash
bash /root/.openclaw/workspace/hooks/trigger-hooks.sh
```

---

## 📁 记忆位置

### 项目记忆

```
/root/.openclaw/workspace/projects/<project-hash>/memory.md
```

### 2026-04-06的日志

```
/root/.openclaw/workspace/memory/<today>.md
```

---

## 💡 工作原理

### SessionStart

1. 计算当前项目的哈希值
2. 检查项目记忆是否存在
3. 如果存在，显示记忆摘要
4. 帮助 AI 快速了解项目背景

### SessionEnd

1. 分析2026-04-06的日志
2. 提取关键信息:
   - 2026-04-06的决策
   - 成功经验
   - 错误教训
   - 技术细节
   - 待办事项
   - 学习记录
3. 追加到项目记忆

---

## 🎯 效果

### SessionStart

- ✅ 快速了解项目背景
- ✅ 记住之前的决策
- ✅ 避免重复错误

### SessionEnd

- ✅ 自动保存记忆
- ✅ 提取关键经验
- ✅ 积累项目知识

---

## 📊 记忆内容

项目记忆包含:

- 🎯 项目概览
- 🧠 2026-04-06的决策
- ✅ 成功经验
- ❌ 错误教训
- 🔧 技术细节
- 📝 待办事项
- 🎓 学习记录

---

## 💡 最佳实践

1. **每个项目一个记忆** - 不同项目的记忆分开存储
2. **定期回顾记忆** - 每周回顾一次项目记忆
3. **清理过期记忆** - 定期清理过期的记忆
4. **备份重要记忆** - 定期备份重要的项目记忆

---

**使用指南完成**: 2026-04-04 22:18:48
