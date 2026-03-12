# OpenClaw 自动备份配置

## 自动化脚本已创建 ✅

### 脚本列表

1. **backup-before-update.sh** - 快速备份脚本
   - 位置: `/root/.openclaw/workspace/scripts/backup-before-update.sh`
   - 功能: 备份配置、凭证、工作区
   - 用法: `bash /root/.openclaw/workspace/scripts/backup-before-update.sh`

2. **safe-upgrade.sh** - 安全升级脚本
   - 位置: `/root/.openclaw/workspace/scripts/safe-upgrade.sh`
   - 功能: 自动备份 → 升级 → 恢复 → 验证
   - 用法: `bash /root/.openclaw/workspace/scripts/safe-upgrade.sh`

3. **restore-pairing.sh** - 飞书配对恢复脚本
   - 位置: `/root/.openclaw/workspace/scripts/restore-pairing.sh`
   - 功能: 恢复飞书配对文件
   - 用法: `bash /root/.openclaw/workspace/scripts/restore-pairing.sh <备份目录>`

---

## 自动备份设置（每日凌晨 2 点）

### 配置 Cron 任务

```bash
# 编辑 crontab
crontab -e

# 添加以下行
0 2 * * * /root/.openclaw/workspace/scripts/auto-backup.sh >> /root/.openclaw/logs/backup.log 2>&1
```

### 自动备份脚本

```bash
#!/bin/bash
# /root/.openclaw/workspace/scripts/auto-backup.sh
# 自动备份脚本（用于 cron）

BACKUP_DIR="/root/.openclaw/backups/daily/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 备份配置
cp /root/.openclaw/openclaw.json "$BACKUP_DIR/" 2>/dev/null

# 备份凭证
cp -r /root/.openclaw/credentials "$BACKUP_DIR/" 2>/dev/null

# 备份工作区
cp -r /root/.openclaw/workspace "$BACKUP_DIR/workspace_backup" 2>/dev/null

# 清理旧备份（保留 7 天）
find /root/.openclaw/backups/daily -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null

echo "自动备份完成: $(date)" >> "$BACKUP_DIR/backup_info.txt"
```

---

## 使用方法

### 快速备份

```bash
bash /root/.openclaw/workspace/scripts/backup-before-update.sh
```

### 安全升级

```bash
bash /root/.openclaw/workspace/scripts/safe-upgrade.sh
```

### 恢复飞书配对

```bash
# 列出可用备份
ls -td /root/.openclaw/backups/manual_*

# 恢复配对
bash /root/.openclaw/workspace/scripts/restore-pairing.sh /root/.openclaw/backups/manual_20260302_120000
```

---

## 备份目录结构

```
/root/.openclaw/backups/
├── manual_20260302_120000/    # 手动备份
│   ├── openclaw.json
│   ├── credentials/
│   │   └── feishu-pairing.json
│   ├── workspace_backup/
│   ├── skills_list.txt
│   ├── version.txt
│   └── git_commit.txt
└── daily/                      # 自动备份
    ├── 20260301/
    ├── 20260302/
    └── ...
```

---

## 状态：✅ 配置完成

- [x] 脚本已创建
- [x] 权限已设置（可执行）
- [ ] Cron 自动备份待配置（需要时手动添加）

---

*配置时间: 2026-03-02*
