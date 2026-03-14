#!/bin/bash
# 日志清理脚本
# 清理旧日志文件，节省磁盘空间

echo "🧹 开始清理日志..."

# 清理 30 天前的通用日志
GENERAL_LOGS=$(find /root/.openclaw/workspace -name "*.log" -mtime +30 -type f 2>/dev/null | wc -l)
if [ $GENERAL_LOGS -gt 0 ]; then
  find /root/.openclaw/workspace -name "*.log" -mtime +30 -delete 2>/dev/null
  echo "✅ 清理了 $GENERAL_LOGS 个旧日志文件（30 天前）"
fi

# 清理 7 天前的 Dashboard 日志
DASHBOARD_LOGS=$(find /root/.openclaw/workspace/ai-team-dashboard/dashboard/logs -name "*.log" -mtime +7 -type f 2>/dev/null | wc -l)
if [ $DASHBOARD_LOGS -gt 0 ]; then
  find /root/.openclaw/workspace/ai-team-dashboard/dashboard/logs -name "*.log" -mtime +7 -delete 2>/dev/null
  echo "✅ 清理了 $DASHBOARD_LOGS 个 Dashboard 日志文件（7 天前）"
fi

if [ $GENERAL_LOGS -eq 0 ] && [ $DASHBOARD_LOGS -eq 0 ]; then
  echo "✅ 没有需要清理的日志文件"
fi

# 显示磁盘空间
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')
echo "💾 当前磁盘使用: $DISK_USAGE"

echo "✅ 日志清理完成: $(date)"
