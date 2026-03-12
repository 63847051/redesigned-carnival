# 📤 推送到GitHub - 完整指南

## 🎯 你的GitHub信息

- **用户名**: `logseq_xiangchao`
- **仓库地址**: https://github.com/logseq_xiangchao/self-evolution-system
- **本地路径**: `/root/.openclaw/workspace/github-repo/self-evolution-system`

---

## 🚀 推送步骤

### Step 1: 创建GitHub仓库（如果还没有）

1. 访问 **https://github.com/new**
2. 仓库名称: `self-evolution-system`
3. 描述: `让您的OpenClaw Agent拥有自动进化能力`
4. 选择: **Public**
5. **不要**勾选 "Add a README file"
6. 点击 **"Create repository"**

### Step 2: 配置Git认证（选择一种方式）

#### 方式A: 使用GitHub Token（推荐）

**创建Token**:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" (生成新令牌)
3. Note: `Self-Evolution-System-Deploy`
4. Expiration: 选择过期时间（建议选择90天）
5. 勾选权限:
   - ☑️ repo (全选)
   - ☑️ workflow
   - ☑️ write
6. 点击 "Generate token"
7. **复制Token**（只显示一次！）

**配置Git**:
```bash
cd /root/.openclaw/workspace/github-repo/self-evolution-system

# 推送到GitHub
git push -u origin main
```

**输入**:
- Username: `logseq_xiangchao`
- Password: `ghp_...` （你刚复制的Token）

#### 方式B: 使用SSH密钥（如果有）

```bash
# 检查SSH密钥
ls -la ~/.ssh/id_rsa.pub

# 如果没有，创建SSH密钥
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 添加SSH密钥到GitHub
cat ~/.ssh/id_rsa.pub | pbcopy  # Mac
# 或
cat ~/.ssh/id_rsa.pub  # Linux，复制输出

# 访问 https://github.com/settings/keys
# 点击 "New SSH key"
# 粘贴密钥，添加

# 推送
git push -u origin main
```

---

## 📋 完整命令（准备好执行）

### 现在可以执行的命令

```bash
cd /root/.openclaw/workspace/github-repo/self-evolution-system

# 方式1: Token方式（推荐）
git push -u origin main
# Username: logseq_xiangchao
# Password: <你的GitHub Token>

# 方式2: SSH方式
# 如果已配置SSH密钥
git push -u origin main
```

---

## 🎯 推送成功后

### 仓库地址

```
https://github.com/logseq_xiangchao/self-evolution-system
```

### 克隆命令

```bash
git clone https://github.com/logseq_xiangchao/self-evolution-system.git
```

### 直接下载脚本

```bash
# 下载核心脚本
wget https://raw.githubusercontent.com/logseq_xiangchao/self-evolution-system/main/self-evolution-system.sh
wget https://raw.githubusercontent.com/logseq_xiangchao/self-evolution-system/main/l7-config-validation.sh

# 使用
bash self-evolution-system.sh
```

---

## 🔍 故障排除

### 问题1: 认证失败

**错误**: `fatal: could not read Username`

**解决**: 
1. 使用GitHub Token（见Step 2）
2. 或配置SSH密钥（见Step 2）

### 问题2: 权限不足

**错误**: `remote: Permission denied`

**解决**:
1. 检查Token权限（需要repo全选）
2. 确认仓库是你的

### 问题3: 仓库已存在

**错误**: `repository already exists`

**解决**:
```bash
# 强制推送
git push -u origin main --force
```

---

## ✅ 验证部署

### 检查仓库

访问: https://github.com/logseq_xiangchao/self-evolution-system

应该能看到:
- README.md
- LICENSE
- self-evolution-system.sh
- l7-config-validation.sh

### 克隆测试

```bash
# 在新服务器测试
cd /tmp
git clone https://github.com/logseq_xiangchao/self-evolution-system.git test
cd test/self-evolution-system
bash self-evolution-system.sh
```

---

## 🎉 成功后

**你的自我进化系统就可以在任何地方使用了！**

```bash
# 在任何OpenClaw环境
git clone https://github.com/logseq_xiangchao/self-evolution-system.git ~/.openclaw/skills/self-evolution-system
cd ~/.openclaw/skills/self-evolution-system
bash install.sh
```

---

**准备好了吗？需要我帮你执行推送命令吗？** 🚀

（我已经准备好了，只需要你的GitHub Token或配置好SSH密钥）
