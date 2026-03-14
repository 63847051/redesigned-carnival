#!/bin/bash
# 内存监控脚本
# 当内存使用超过 80% 时记录到系统日志

MEMORY_USAGE=$(free | awk '/Mem/{printf("%.0f"), $3/$2*100}')
THRESHOLD=80

if [ $MEMORY_USAGE -gt $THRESHOLD ]; then
  MESSAGE="⚠️ 内存使用过高: ${MEMORY_USAGE}% (阈值: ${THRESHOLD}%)"
  echo "$MESSAGE" | logger -t memory-monitor -p user.warning
  
  # 发送飞书通知
  if [ -n "$FEISHU_WEBHOOK_URL" ]; then
    bash /root/.openclaw/workspace/scripts/feishu-notify.sh memory "$MEMORY_USAGE" "$THRESHOLD"
  fi
fi
