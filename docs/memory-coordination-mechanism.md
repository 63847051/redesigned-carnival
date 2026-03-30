# 记忆系统协调机制文档

**版本**: v1.0
**创建时间**: 2026-03-29 20:04
**状态**: ✅ **已实施**

---

## 🎯 协调机制概述

### 📊 **双系统架构**

```
┌─────────────────────────────────────┐
│   .context/ (运行时)                │
│   - L0: 核心上下文                  │
│   - L1: 相关上下文                  │
│   - L2: 背景上下文                  │
│   用途: Token 优化 + 快速检索       │
└─────────────────────────────────────┘
              ↓ 每天 23:59 自动同步
┌─────────────────────────────────────┐
│   memory/ (长期存储)                │
│   - 2026-03-29.md                  │
│   - 2026-03-30.md                  │
│   用途: 历史记录 + 长期记忆         │
└─────────────────────────────────────┘
```

---

## 🔄 **同步协调器**

### 工具：`memory-sync-coordinator.py`

**功能**：
- ✅ 同步 `.context/` → `memory/`
- ✅ 检查一致性
- ✅ 自动协调
- ✅ 避免数据混乱

---

## 📋 **使用方法**

### 1️⃣ **手动同步**

```bash
# 同步到 memory/
python3 /root/.openclaw/workspace/scripts/memory-sync-coordinator.py --sync

# 强制同步
python3 /root/.openclaw/workspace/scripts/memory-sync-coordinator.py --sync --force
```

### 2️⃣ **检查一致性**

```bash
python3 /root/.openclaw/workspace/scripts/memory-sync-coordinator.py --check
```

### 3️⃣ **自动同步**

```bash
python3 /root/.openclaw/workspace/scripts/memory-sync-coordinator.py --auto
```

### 4️⃣ **设置每日自动同步**

```bash
# 添加到 crontab
crontab -e

# 添加以下行
59 23 * * * /root/.openclaw/workspace/scripts/daily-auto-sync.sh >> /root/.openclaw/workspace/logs/daily-sync.log 2>&1
```

---

## 🎯 **工作流程**

### ✅ **推荐工作流**

1. **运行时**：使用 `.context/`
   - 快速检索
   - Token 优化
   - 按需加载

2. **每天结束**：自动同步到 `memory/`
   - 每天 23:59 自动执行
   - 保存长期记录
   - 避免数据丢失

3. **需要历史**：从 `memory/` 加载
   - 查看历史记录
   - 时间序列检索

---

## 📊 **数据格式**

### `.context/` 结构
```
.context/
├── index.json           # 全局索引
├── memory/              # 记忆
├── resources/           # 资源
├── skills/              # 技能
├── l0/                  # L0 核心上下文
├── l1/                  # L1 相关上下文
└── l2/                  # L2 背景上下文
```

### `memory/` 格式
```markdown
# 2026-03-29

## 今日工作
...

---

# 🔄 上下文同步
**同步时间**: 2026-03-29 23:59:00

## 📝 记忆
...

## 📚 资源
...

## 🛠️ 技能
...
```

---

## 🎯 **最佳实践**

### ✅ **DO（应该做的）**

1. **运行时使用 `.context/`**
   - 快速检索
   - Token 优化

2. **每天自动同步**
   - 设置 cron 任务
   - 每天 23:59 执行

3. **定期检查一致性**
   - 使用 `--check` 命令
   - 确保数据一致

### ❌ **DON'T（不应该做的）**

1. **不要手动编辑两个系统**
   - 容易导致不一致
   - 使用协调器

2. **不要忽略同步**
   - 可能丢失数据
   - 设置自动同步

3. **不要混淆用途**
   - `.context/` 是运行时
   - `memory/` 是长期存储

---

## 🚨 **故障排除**

### 问题 1: 同步失败
**症状**: 同步时报错

**解决方案**:
```bash
# 检查一致性
python3 /root/.openclaw/workspace/scripts/memory-sync-coordinator.py --check

# 强制同步
python3 /root/.openclaw/workspace/scripts/memory-sync-coordinator.py --sync --force
```

### 问题 2: 数据不一致
**症状**: 两个系统数据不一致

**解决方案**:
```bash
# 检查一致性
python3 /root/.openclaw/workspace/scripts/memory-sync-coordinator.py --check

# 查看问题报告
# 根据提示修复
```

### 问题 3: 自动同步未执行
**症状**: cron 任务未执行

**解决方案**:
```bash
# 检查 cron 日志
tail -f /root/.openclaw/workspace/logs/daily-sync.log

# 检查 cron 服务
systemctl status cron

# 重启 cron
systemctl restart cron
```

---

## 🎯 **总结**

| 维度 | memory/ | .context/ |
|------|---------|-----------|
| **用途** | 长期存储 | 运行时 |
| **组织** | 时间序列 | 分类 |
| **加载** | 全量 | 按需 |
| **优化** | 无 | Token 优化 |
| **同步** | 每天自动 | - |

---

**核心价值**: ✅ **数据一致性 + 自动协调 + 避免混乱**

---

**文档人**: 大领导 🎯
**创建时间**: 2026-03-29 20:04
**版本**: v1.0
**状态**: ✅ **协调机制已实施！**
