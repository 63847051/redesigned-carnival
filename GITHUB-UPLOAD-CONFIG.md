# GitHub 上传配置 - 重要备忘

**更新时间**: 2026-03-09 13:25
**状态**: ✅ 已验证

---

## 🎯 正确的 GitHub 仓库配置

### 仓库信息
- **用户名**: `63847051`
- **仓库名**: `self-evolution-system`
- **仓库地址**: https://github.com/63847051/self-evolution-system

### 正确的工作目录
```
/root/.openclaw/workspace/github-repo/self-evolution-system
```

**⚠️ 重要**: 不是 `/root/.openclaw/workspace`！

### 分支名称
- **主分支**: `main` (不是 `master`)

---

## 🚀 标准推送流程

### 1. 切换到正确目录
```bash
cd /root/.openclaw/workspace/github-repo/self-evolution-system
```

### 2. 检查状态
```bash
git status
git log --oneline -3
```

### 3. 添加文件
```bash
git add <files>
```

### 4. 提交
```bash
git commit -m "提交信息"
```

### 5. 推送
```bash
git push origin main
```

---

## ⚠️ 常见错误（绝不再犯）

### ❌ 错误 1: 用错了目录
```
错误: cd /root/.openclaw/workspace
正确: cd /root/.openclaw/workspace/github-repo/self-evolution-system
```

### ❌ 错误 2: 用错了分支
```
错误: git push origin master
正确: git push origin main
```

### ❌ 错误 3: 用错了用户名
```
错误: logseq_xiangchao
正确: 63847051
```

---

## ✅ 验证配置

### 检查远程仓库
```bash
cd /root/.openclaw/workspace/github-repo/self-evolution-system
git remote -v
```

**应该输出**:
```
origin	https://github.com/63847051/self-evolution-system.git (fetch)
origin	https://github.com/63847051/self-evolution-system.git (push)
```

### 检查分支
```bash
git branch -a
```

**应该包含**:
```
* main
  remotes/origin/main
```

### 检查最新提交
```bash
git log --oneline -3
```

**最新应该是**: v5.3 提交 (5afe146)

---

## 📋 快速命令清单

### 完整推送流程
```bash
# 1. 切换目录
cd /root/.openclaw/workspace/github-repo/self-evolution-system

# 2. 同步 workspace 文件
cp -r /root/.openclaw/workspace/<新文件> .

# 3. 添加文件
git add .

# 4. 提交
git commit -m "版本号: 提交信息"

# 5. 推送
git push origin main
```

---

## 🎯 记住这个！

**黄金法则**:
1. **目录**: `github-repo/self-evolution-system`
2. **分支**: `main`
3. **用户**: `63847051`
4. **仓库**: `self-evolution-system`

**推送前检查**:
- [ ] 在正确目录？
- [ ] 用了正确的分支？
- [ ] 提交信息清晰？

---

*创建时间: 2026-03-09 13:25*
*目的: 防止再犯同样的错误*
*状态: ✅ 已记录*
