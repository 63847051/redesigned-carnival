# 📦 OpenClaw 重装备份指南

**更新时间**: 2026-03-02
**重要性**: ⭐⭐⭐⭐⭐

---

## 🎯 快速备份（推荐）

### 一键备份
```bash
# 备份所有重要文件
/root/.openclaw/workspace/scripts/backup-before-update.sh
```

### 一键安全升级（自动备份→升级→恢复）
```bash
# 推荐使用！会自动备份、升级、迁移配置、验证
/root/.openclaw/workspace/scripts/safe-upgrade.sh
```

---

## 📋 需要备份的内容

### 1️⃣ 核心配置文件（必须）
```
/root/.openclaw/openclaw.json          # 主配置文件
/root/.openclaw/credentials/           # 凭证目录
  ├── feishu-pairing.json             # 飞书配对（最重要！）
  └── ...                             # 其他凭证
```

### 2️⃣ 工作区（重要）
```
/root/.openclaw/workspace/             # 工作区
  ├── IDENTITY.md                     # 身份配置
  ├── SOUL.md                         # 核心逻辑
  ├── MEMORY.md                       # 长期记忆
  ├── memory/                         # 每日记忆
  ├── SKILLS/                         # 技能配置
  ├── scripts/                        # 脚本
  └── .learnings/                     # 学习记录
```

### 3️⃣ 已安装技能（建议）
```
# 列出已安装技能
clawhub list > installed_skills.txt
```

### 4️⃣ 日志（可选）
```
/root/.openclaw/logs/                  # 日志目录
```

---

## 🚀 完整备份步骤

### 方法 1: 使用自动化脚本（推荐）

```bash
# 执行安全升级脚本（自动备份 + 升级 + 验证）
/root/.openclaw/workspace/scripts/safe-upgrade.sh
```

**脚本会自动：**
1. ✅ 备份配置文件
2. ✅ 备份飞书配对
3. ✅ 备份技能列表
4. ✅ 记录当前版本
5. ✅ 执行升级
6. ✅ 自动迁移配置
7. ✅ 验证 Gateway 启动
8. ✅ 清理旧备份（保留最近 7 个）

### 方法 2: 手动备份

```bash
# 创建备份目录
BACKUP_DIR="/root/.openclaw/backups/manual_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 1. 备份配置文件
cp /root/.openclaw/openclaw.json "$BACKUP_DIR/"

# 2. 备份凭证目录
cp -r /root/.openclaw/credentials "$BACKUP_DIR/"

# 3. 备份工作区
cp -r /root/.openclaw/workspace "$BACKUP_DIR/workspace_backup"

# 4. 备份已安装技能
clawhub list > "$BACKUP_DIR/skills_list.txt"

# 5. 记录当前版本
openclaw --version > "$BACKUP_DIR/version.txt"

# 6. 记录 git commit（如果是 git 安装）
cd /root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw
git rev-parse HEAD > "$BACKUP_DIR/git_commit.txt"

echo "✅ 备份完成: $BACKUP_DIR"
```

---

## 🔄 恢复步骤

### 如果重装后需要恢复

```bash
# 1. 停止 Gateway
systemctl --user stop openclaw-gateway

# 2. 恢复配置文件
cp /root/.openclaw/backups/YOUR_BACKUP/openclaw.json /root/.openclaw/

# 3. 恢复飞书配对（最重要！）
cp /root/.openclaw/backups/YOUR_BACKUP/credentials/feishu-pairing.json \
   /root/.openclaw/credentials/

# 4. 恢复工作区
cp -r /root/.openclaw/backups/YOUR_BACKUP/workspace_backup/* \
       /root/.openclaw/workspace/

# 5. 重启 Gateway
systemctl --user start openclaw-gateway

# 6. 验证状态
systemctl --user status openclaw-gateway
```

---

## ⚠️ 特别注意

### 飞书配对（最重要！）
```
文件: /root/.openclaw/credentials/feishu-pairing.json
重要性: ⭐⭐⭐⭐⭐
说明: 如果丢失这个文件，飞书会断连，需要重新配对
```

### 自动备份
系统已配置每日凌晨 2 点自动备份到：
```
/root/.openclaw/backups/daily/YYYYMMDD/
```

保留最近 7 天的备份。

---

## 📊 备份清单

在重装前，请确认：

- [ ] 配置文件已备份（openclaw.json）
- [ ] 飞书配对已备份（feishu-pairing.json）
- [ ] 工作区已备份（workspace/）
- [ ] 技能列表已记录（skills_list.txt）
- [ ] 当前版本已记录（version.txt）
- [ ] 备份文件已验证可读

---

## 🎯 推荐流程

1. **使用自动化脚本**（最安全）
   ```bash
   /root/.openclaw/workspace/scripts/safe-upgrade.sh
   ```

2. **如果手动重装**
   ```bash
   # 先备份
   /root/.openclaw/workspace/scripts/backup-before-update.sh

   # 重装...
   npm install -g openclaw

   # 恢复配置
   /root/.openclaw/workspace/scripts/restore-pairing.sh
   ```

3. **验证恢复**
   ```bash
   # 检查 Gateway 状态
   systemctl --user status openclaw-gateway

   # 检查飞书连接
   # （发送测试消息）
   ```

---

**记住**：备份多一份，安全多一分！🛡️

---

*创建时间: 2026-03-02*
*状态: ✅ 就绪*
