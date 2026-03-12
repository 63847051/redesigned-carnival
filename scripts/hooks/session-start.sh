#!/bin/bash
# Hook: Session Start
# 触发时机: 会话开始时
# 功能: 记录会话开始事件

HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"
LOG_FILE="$HOOKS_DIR/session-$(date +%Y%m%d).log"

# 记录会话开始
echo "=== Session Start ===" >> "$LOG_FILE"
echo "Time: $(date)" >> "$LOG_FILE"
echo "Date: $(date +%Y-%m-%d)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 检查今日任务
if [ -f "/root/.openclaw/workspace/TODO.md" ]; then
    echo "今日任务:" >> "$LOG_FILE"
    cat "/root/.openclaw/workspace/TODO.md" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
fi

# 记录系统状态
echo "系统状态:" >> "$LOG_FILE"
systemctl --user is-active openclaw-gateway >> "$LOG_FILE" 2>&1 || echo "Gateway 未运行" >> "$LOG_FILE"
free | awk '/Mem/{printf "内存使用: %.1f%%\n", $3/$2*100}' >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "✅ Session Start Hook 执行完成" >> "$LOG_FILE"
