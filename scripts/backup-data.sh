#!/bin/bash
# 数据备份脚本
# 自动备份重要数据和配置

BACKUP_ROOT="/root/.openclaw/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$DATE"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo "🔄 开始备份..."
echo "备份目录: $BACKUP_DIR"
echo ""

# 1. 备份 OpenClaw 配置
echo "📦 备份 OpenClaw 配置..."
cp -r /root/.openclaw/openclaw.json "$BACKUP_DIR/"
cp -r /root/.openclaw/credentials "$BACKUP_DIR/" 2>/dev/null || echo "  ⚠️  credentials 目录不存在"
echo "  ✅ OpenClaw 配置已备份"

# 2. 备份工作空间配置
echo "📦 备份工作空间配置..."
cp -r /root/.openclaw/workspace/*.json "$BACKUP_DIR/" 2>/dev/null || echo "  ⚠️  没有配置文件"
cp -r /root/.openclaw/workspace/.learnings "$BACKUP_DIR/"
cp -r /root/.openclaw/workspace/.pai-learning "$BACKUP_DIR/" 2>/dev/null || echo "  ⚠️  pai-learning 目录不存在"
echo "  ✅ 工作空间配置已备份"

# 3. 备份重要脚本
echo "📦 备份重要脚本..."
mkdir -p "$BACKUP_DIR/scripts"
cp /root/.openclaw/workspace/scripts/*.sh "$BACKUP_DIR/scripts/" 2>/dev/null
echo "  ✅ 脚本已备份"

# 4. 备份 Dashboard 配置
echo "📦 备份 Dashboard 配置..."
if [ -f /root/.openclaw/workspace/ai-team-dashboard/dashboard/config.json ]; then
  cp /root/.openclaw/workspace/ai-team-dashboard/dashboard/config.json "$BACKUP_DIR/"
  echo "  ✅ Dashboard 配置已备份"
else
  echo "  ⚠️  Dashboard 配置不存在"
fi

# 5. 创建备份清单
echo "📝 生成备份清单..."
cat > "$BACKUP_DIR/backup_manifest.txt" << EOF
备份时间: $(date)
备份目录: $BACKUP_DIR
备份内容:
- OpenClaw 配置
- 工作空间配置
- 学习数据
- 重要脚本
- Dashboard 配置
EOF

# 6. 压缩备份
echo "🗜️  压缩备份..."
cd "$BACKUP_ROOT"
tar -czf "${DATE}_backup.tar.gz" "$DATE"
rm -rf "$DATE"

# 7. 清理旧备份（保留 4 周）
echo "🧹 清理旧备份..."
find "$BACKUP_ROOT" -name "*_backup.tar.gz" -mtime +28 -delete

# 8. 统计信息
BACKUP_SIZE=$(du -sh "$BACKUP_ROOT/${DATE}_backup.tar.gz" | awk '{print $1}')
BACKUP_COUNT=$(ls -1 "$BACKUP_ROOT"/*_backup.tar.gz 2>/dev/null | wc -l)

echo ""
echo "✅ 备份完成！"
echo "   备份文件: ${DATE}_backup.tar.gz"
echo "   备份大小: $BACKUP_SIZE"
echo "   保留备份数: $BACKUP_COUNT"
echo ""

# 发送飞书通知
if [ -n "$FEISHU_WEBHOOK_URL" ]; then
  bash /root/.openclaw/workspace/scripts/feishu-notify.sh \
    "✅ 备份完成" \
    "**数据备份成功**

备份大小: $BACKUP_SIZE
保留数量: $BACKUP_COUNT 个
备份时间: $(date '+%Y-%m-%d %H:%M:%S')"
fi
