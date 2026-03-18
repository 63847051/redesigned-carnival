# 错误记录：OpenCode 调用错误

**错误时间**: 2026-03-18 12:17
**错误类型**: 错误的子 Agent 调用方式
**严重程度**: 高（反复犯错）

---

## ❌ 错误描述

### 我做了什么

**错误调用**:
```python
sessions_spawn(
    runtime="subagent",
    model="opencode/minimax-m2.5-free",
    task="..."
)
```

**错误原因**:
- `runtime="subagent"` 需要 provider 配置
- `opencode/minimax-m2.5-free` 不是 provider，是 OpenCode CLI 的免费模型
- 这个模型通过 CLI 直接调用，不需要 API Key

### 正确做法

**正确调用方式 1: 直接调用 CLI** ✅
```bash
opencode -m opencode/minimax-m2.5-free run "任务"
```

**正确调用方式 2: 使用包装脚本** ✅
```bash
~/.openclaw/workspace/scripts/opencode-free.sh "任务"
```

**正确调用方式 3: 通过 exec 调用** ✅
```python
exec(command='opencode -m opencode-minimax-m2.5-free run "任务"')
```

---

## 🔴 严重程度：高

### 为什么严重

1. **反复犯错**
   - 这是第 N 次犯同样的错误
   - 用户多次提醒，我总是忘记

2. **浪费时间**
   - 每次错误都会浪费 5-10 分钟
   - 用户等待时间变长

3. **影响体验**
   - 用户需要反复纠正
   - 降低用户对我的信任

---

## 💡 根本原因分析

### 我为什么会犯错

1. **记忆问题**
   - 我没有记住之前犯过的错误
   - 每次遇到类似情况就忘记

2. **调用方式混淆**
   - 我混淆了不同的调用方式
   - `sessions_spawn` vs `exec` vs CLI 直接调用

3. **没有检查文档**
   - 我没有查看 SKILL.md 或文档
   - 没有验证调用方式是否正确

---

## ✅ 解决方案

### 1. 创建此错误记录

**目的**: 永久记住这个错误

**位置**: `/root/.openclaw/workspace/.learnings/errors/`

**文件名**: `opencode-subagent-error-20260318.md`

---

### 2. 添加到启动检查

在每次启动时检查此错误记录。

**脚本**: `scripts/check-critical-rules.sh`

**添加检查项**:
```bash
# 检查：是否正确使用 opencode
echo "检查 opencode 调用方式..."
```

---

### 3. 更新 IDENTITY.md

在 IDENTITY.md 中添加：

```markdown
## ⚠️ 重要注意事项

### OpenCode 调用

**正确方式**:
```bash
opencode -m opencode/minimax-m2.5-free run "任务"
```

**错误方式**（不要使用）:
```python
sessions_spawn(runtime="subagent", model="opencode/minimax-m2.5-free")
```

**原因**: opencode 免费模型通过 CLI 直接调用，不需要 API Key。
```

---

### 4. 更新 SOUL.md

在 SOUL.md 的关键规则章节添加：

```markdown
## 规则：正确调用 OpenCode

**规则ID**: RULE-OPENCODE-001

**正确调用**:
- ✅ 直接 CLI: `opencode -m opencode/minimax-m2.5-free run "任务"`
- ✅ 包装脚本: `~/.openclaw/workspace/scripts/opencode-free.sh "任务"`
- ✅ exec 调用

**错误调用**:
- ❌ sessions_spawn(runtime="subagent", model="opencode/minimax-m2.5-free")
```

---

## 🎯 防止再犯

### 检查清单

在调用 OpenCode 之前，问自己：

1. **是 opencode 免费模型吗？**
   - 是 → 使用 CLI 或 exec
   - 否 → 可以考虑 sessions_spawn

2. **需要子 Agent 会话吗？**
   - 是 → 使用 `runtime="acp"` 调用 OpenCode
   - 否 → 使用 CLI 直接调用

3. **是否需要线程会话？**
   - 是 → 使用 `sessions_spawn` + `thread: true`
   - 否 → 使用一次性 run 模式

---

## 📝 承诺

### 我承诺

1. **不再犯同样的错误**
   - 记住 opencode 的正确调用方式
   - 使用前检查调用方式是否正确

2. **遇到不确定时**
   - 先查看文档
   - 先询问用户
   - 不要假设

3. **记录所有错误**
   - 每次错误都记录
   - 定期回顾
   - 持续改进

---

## 🙏 致歉

**亲爱的用户**，

非常抱歉我反复犯了同样的错误。

我承诺：
- ✅ 已经记录此错误
- ✅ 会添加到启动检查
- ✅ 会更新相关文档
- ✅ 不会再犯同样的错误

感谢你的耐心和指正。

---

**错误记录时间**: 2026-03-18 12:57
**记录者**: 大领导 🎯
**状态**: ✅ 已记录，承诺不再犯
