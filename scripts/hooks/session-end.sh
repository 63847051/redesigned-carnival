#!/bin/bash
# Hook: Session End
# 触发时机: 会话结束时
# 功能: 记录会话结束事件并总结

HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"
LOG_FILE="$HOOKS_DIR/session-$(date +%Y%m%d).log"

# 记录会话结束
echo "=== Session End ===" >> "$LOG_FILE"
echo "Time: $(date)" >> "$LOG_FILE"
echo "Date: $(date +%Y-%m-%d)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 统计今日活动
echo "今日工具使用:" >> "$LOG_FILE"
if [ -f "$HOOKS_DIR/tools-$(date +%Y%m%d).log" ]; then
    grep -c "Tool:" "$HOOKS_DIR/tools-$(date +%Y%m%d).log" >> "$LOG_FILE"
else
    echo "0" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

echo "今日用户输入:" >> "$LOG_FILE"
if [ -f "$HOOKS_DIR/prompts-$(date +%Y%m%d).log" ]; then
    grep -c "User Prompt:" "$HOOKS_DIR/prompts-$(date +%Y%m%d).log" >> "$LOG_FILE"
else
    echo "0" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

# 生成会话总结
echo "会话总结:" >> "$LOG_FILE"
echo "- 会话时长: $(date +%H:%M:%S)" >> "$LOG_FILE"
echo "- 工具使用次数: $(grep -c "Tool:" "$HOOKS_DIR/tools-$(date +%Y%m%d).log" 2>/dev/null || echo "0")" >> "$LOG_FILE"
echo "- 用户输入次数: $(grep -c "User Prompt:" "$HOOKS_DIR/prompts-$(date +%Y%m%d).log" 2>/dev/null || echo "0")" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "✅ Session End Hook 执行完成" >> "$LOG_FILE"
