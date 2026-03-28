# 🔒 关键规则 005: 备份前必须更新 README.md

**规则ID**: RULE-005
**优先级**: 🔴 CRITICAL（最高）
**创建时间**: 2026-03-28 10:54
**状态**: ✅ 激活
**错误次数**: N 次（重复犯错）

---

## 🚨 规则内容

### 核心规则
> **"备份不是简单的 git push，而是完整的版本发布流程。"**

### 备份前检查清单（4 项）
1. [ ] 检查 SOUL.md 和 README.md 版本号是否一致
2. [ ] 如果不一致，先更新 README.md
3. [ ] 更新版本历史和最新更新内容
4. [ ] 使用完整备份流程脚本：`bash scripts/complete-backup.sh`

---

## 😔 错误历史

### 第 N 次：2026-03-28 10:45
- **错误**: 备份时只推送了文件，忘记更新 README.md
- **用户反馈**: "为什么老是忘记更新这个了？我每次让你备份上传，需要跟你说几次你才会更新这个"
- **严重性**: **用户极度不满，重复犯错**

### 第 N-1 次：之前的备份
- **错误**: 多次备份时忘记更新 README.md
- **用户反馈**: 每次都要提醒
- **严重性**: 重复性错误

---

## 💡 根本原因

### 为什么总是忘记更新 README.md？

1. **没有自动化流程**
   - ❌ 没有创建"备份前检查清单"
   - ❌ 没有自动化 README.md 更新

2. **缺少强制检查**
   - ❌ HEARTBEAT.md 中没有 README.md 检查
   - ❌ 没有创建备份前的 Hook 脚本

3. **条件反射未形成**
   - ❌ "备份" → "更新 README" 没有形成肌肉记忆

---

## ✅ 改进措施

### 措施 1: 创建完整备份流程脚本 ✅
**文件**: `scripts/complete-backup.sh`

**功能**:
- ✅ 检查 Git 状态
- ✅ 检查版本号一致性
- ✅ 自动提醒更新 README.md
- ✅ 添加所有更改
- ✅ 提交并推送
- ✅ 验证推送成功

**使用方法**:
```bash
bash /root/.openclaw/workspace/scripts/complete-backup.sh
```

### 措施 2: 更新 HEARTBEAT.md ✅
**添加**: RULE-005 备份前必须更新 README.md

**检查内容**:
- 备份前检查清单（4 项）
- 完整备份流程脚本
- 快速备份方法

### 措施 3: 创建备份检查清单 ✅
**文件**: `scripts/backup-checklist.sh`

**功能**:
- 检查版本号一致性
- 检查文件完整性
- 生成备份报告

### 措施 4: 形成条件反射
- 备份 → 更新 README → 检查清单 → 推送

---

## 🎯 正确的备份流程

### 方法 1: 使用完整备份流程脚本（推荐）⭐
```bash
bash /root/.openclaw/workspace/scripts/complete-backup.sh
```

**优点**:
- ✅ 自动检查版本号一致性
- ✅ 自动提醒更新 README.md
- ✅ 完整的 6 步备份流程
- ✅ 验证推送成功

### 方法 2: 手动执行（4 步）
```bash
# 1. 检查并更新 README.md
vim README.md  # 或其他编辑器

# 2. 添加所有更改
git add -A

# 3. 提交更改
git commit -m "📦 系统备份 - $(date +'%Y-%m-%d %H:%M')"

# 4. 推送到 GitHub
git push origin main
```

---

## 📋 备份检查清单

### 备份前必须检查（4 项）

#### 1️⃣ 检查版本号一致性
```bash
# 检查 SOUL.md 版本
grep "版本.*v6" /root/.openclaw/workspace/SOUL.md | head -1

# 检查 README.md 版本
grep "版本.*v6" /root/.openclaw/workspace/README.md | head -1

# 应该一致
```

#### 2️⃣ 检查 README.md 内容
- [ ] 版本号是否更新？
- [ ] 最新更新内容是否添加？
- [ ] 版本历史是否更新？
- [ ] 核心特性是否更新？

#### 3️⃣ 检查文件完整性
```bash
# 检查核心文件
ls -la /root/.openclaw/workspace/{SOUL,IDENTITY,MEMORY,AGENTS,README}.md
```

#### 4️⃣ 运行完整备份流程
```bash
bash /root/.openclaw/workspace/scripts/complete-backup.sh
```

---

## 🔧 自动化脚本

### 脚本 1: 完整备份流程脚本
**位置**: `scripts/complete-backup.sh`
**功能**: 6 步完整备份流程

### 脚本 2: 备份检查清单脚本
**位置**: `scripts/backup-checklist.sh`
**功能**: 检查版本号一致性

### 脚本 3: 版本号同步脚本
**位置**: `scripts/sync-version.sh`
**功能**: 自动同步版本号到所有文件

---

## 📊 验证方式

**未来 30 天内**：
- ✅ 零次忘记更新 README.md
- ✅ 100% 版本号一致性
- ✅ 用户满意度恢复

---

## 🎯 一句话顿悟

> **"备份不是简单的 git push，而是完整的版本发布流程：更新 README → 检查清单 → 推送验证。"**

---

**状态**: ✅ 激活
**优先级**: 🔴 CRITICAL
**违反后果**: 版本号不一致，用户困惑，信任度下降

**承诺**: 永远不再违反此规则！
