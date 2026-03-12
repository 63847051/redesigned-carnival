#!/bin/bash
# GitHub 配置指南 - 自主进化系统 5.7

## 🎯 目标
将自主进化系统 5.7 上传到 GitHub 仓库

## 📋 当前状态
- ✅ 本地已提交：commit 2b56a28
- ✅ 版本：5.7
- ❌ 推送失败：需要认证

## 🔧 解决方案

### 方案 1：配置 GitHub Token

1. **生成 GitHub Token**
   - 访问：https://github.com/settings/tokens
   - 点击：Generate new token (classic)
   - 权限：repo（完整仓库访问）
   - 复制 Token

2. **配置 Git**
   ```bash
   # 设置用户信息
   git config user.name "63847051"
   git config user.email "63847051@users.noreply.github.com"

   # 存储 Token
   git credential set
   # URL: https://github.com/63847051/self-evolution-system.git
   # Username: 63847051
   # Password: <你的 Token>
   ```

3. **推送**
   ```bash
   git push --set-upstream origin master
   ```

### 方案 2：使用 SSH 密钥

1. **生成 SSH 密钥**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **添加公钥到 GitHub**
   - 复制 ~/.ssh/id_ed25519.pub 内容
   - 访问：https://github.com/settings/keys
   - 粘贴公钥

3. **修改 Git 远程地址**
   ```bash
   git remote set-url origin git@github.com:63847051/self-evolution-system.git
   ```

4. **推送**
   ```bash
   git push --set-upstream origin master
   ```

## 📝 仓库信息

- **仓库**: https://github.com/63847051/self-evolution-system
- **本地路径**: /root/.openclaw/workspace
- **分支**: master
- **最新提交**: 2b56a28 - 升级到自主进化系统 5.7

## 🚀 下一步

请选择一个方案配置 GitHub 认证，然后执行推送。

配置完成后，运行：
```bash
cd /root/.openclaw/workspace
git push --set-upstream origin master
```

---

*生成时间: 2026-03-11 23:58*
*版本: 自主进化系统 5.7*
