# 🚀 快速恢复指南 - OpenClaw 完整备份

**备份时间**: 2026-03-28 10:34
**GitHub 仓库**: https://github.com/63847051/redesigned-carnival
**提交 ID**: 9620ac30

---

## 📋 方法 1: 使用快速恢复脚本（推荐）⭐

### 步骤

**1. 重装系统后，安装必要工具**:
```bash
# 安装 Git
yum install git -y

# 安装 Node.js（如果需要）
curl -fsSL https://rpm.nodesource.com/setup_22.x | bash -
yum install -y nodejs
```

**2. 下载并运行快速恢复脚本**:
```bash
# 下载恢复脚本
curl -o /tmp/quick-restore.sh https://raw.githubusercontent.com/63847051/redesigned-carnival/main/scripts/quick-restore.sh

# 运行恢复脚本
bash /tmp/quick-restore.sh
```

**或者**（如果已经有仓库）:
```bash
# 直接克隆仓库
git clone https://github.com/63847051/redesigned-carnival.git /root/.openclaw/workspace

# 设置脚本权限
chmod +x /root/.openclaw/workspace/scripts/quick-restore.sh

# 运行恢复脚本
bash /root/.openclaw/workspace/scripts/quick-restore.sh
```

**3. 验证恢复**:
```bash
# 检查核心文件
ls -la /root/.openclaw/workspace/SOUL.md
ls -la /root/.openclaw/workspace/IDENTITY.md
ls -la /root/.openclaw/workspace/MEMORY.md
ls -la /root/.openclaw/workspace/AGENTS.md
```

---

## 📋 方法 2: 手动恢复

### 步骤

**1. 备份现有工作区**（如果存在）:
```bash
mv /root/.openclaw/workspace /root/.openclaw/workspace-backup
```

**2. 克隆仓库**:
```bash
git clone https://github.com/63847051/redesigned-carnival.git /root/.openclaw/workspace
```

**3. 恢复配置文件**:
```bash
# 如果有备份，恢复配置
cp /root/.openclaw/workspace-backup/../openclaw.json /root/.openclaw/openclaw.json

# 或者重新配置 OpenClaw
openclaw config
```

**4. 设置脚本权限**:
```bash
chmod +x /root/.openclaw/workspace/scripts/*.sh
```

**5. 重启 Gateway**:
```bash
systemctl --user restart openclaw-gateway
```

---

## 📋 方法 3: 仅恢复核心文件

如果你只想恢复核心配置和记忆，不想要整个仓库：

**1. 下载单个文件**:
```bash
# 创建临时目录
mkdir -p /tmp/openclaw-restore
cd /tmp/openclaw-restore

# 下载核心文件
curl -O https://raw.githubusercontent.com/63847051/redesigned-carnival/main/SOUL.md
curl -O https://raw.githubusercontent.com/63847051/redesigned-carnival/main/IDENTITY.md
curl -O https://raw.githubusercontent.com/63847051/redesigned-carnival/main/MEMORY.md
curl -O https://raw.githubusercontent.com/63847051/redesigned-carnival/main/AGENTS.md
curl -O https://raw.githubusercontent.com/63847051/redesigned-carnival/main/HEARTBEAT.md

# 复制到工作区
cp *.md /root/.openclaw/workspace/
```

**2. 下载关键脚本**:
```bash
# 下载智能任务分配脚本
curl -o /root/.openclaw/workspace/scripts/assign-task.sh \
  https://raw.githubusercontent.com/63847051/redesigned-carnival/main/scripts/assign-task.sh

chmod +x /root/.openclaw/workspace/scripts/assign-task.sh
```

---

## 🎯 验证恢复成功

### 检查核心文件
```bash
# 检查核心文档
ls -la /root/.openclaw/workspace/{SOUL,IDENTITY,MEMORY,AGENTS,HEARTBEAT}.md

# 应该看到 5 个文件
```

### 检查脚本
```bash
# 检查脚本
ls -la /root/.openclaw/workspace/scripts/*.sh

# 应该看到多个脚本文件
```

### 检查版本
```bash
# 查看最新提交
cd /root/.openclaw/workspace
git log -1 --format='%h - %s'

# 应该看到: 9620ac30 - 🔄 系统改进完成 - 2026-03-28
```

---

## 💡 重要提示

### 1. OpenClaw 配置
- 配置文件位置: `/root/.openclaw/openclaw.json`
- 如果没有备份，需要重新运行 `openclaw config`

### 2. API 密钥
- OpenAI/Groq/其他 API 密钥需要重新配置
- 检查 `/root/.openclaw/credentials/` 目录

### 3. Gateway 配置
- 飞书配对信息需要重新配置
- 检查 `/root/.openclaw/credentials/feishu-pairing.json`

---

## 🚨 故障排除

### 问题 1: Git 克隆失败
```bash
# 检查网络
ping github.com

# 检查 DNS
nslookup github.com

# 尝试使用 SSH
git clone git@github.com:63847051/redesigned-carnival.git
```

### 问题 2: 权限错误
```bash
# 修复权限
chown -R root:root /root/.openclaw/workspace
chmod -R +x /root/.openclaw/workspace/scripts
```

### 问题 3: 文件缺失
```bash
# 检查 Git 状态
cd /root/.openclaw/workspace
git status

# 重新拉取
git pull origin main
```

---

## 📞 获取帮助

如果恢复过程中遇到问题：

1. **查看日志**: `journalctl --user -u openclaw-gateway -f`
2. **检查状态**: `openclaw status`
3. **查看文档**: `/root/.openclaw/workspace/docs/`

---

**状态**: ✅ 备份完成
**更新**: 2026-03-28 10:34
**版本**: v6.1.1
