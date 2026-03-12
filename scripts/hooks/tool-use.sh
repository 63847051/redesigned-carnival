#!/bin/bash
# Hook: Tool Use
# 触发时机: 工具使用后
# 功能: 记录工具使用事件

HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"
LOG_FILE="$HOOKS_DIR/tools-$(date +%Y%m%d).log"

TOOL_NAME="$1"
TOOL_ARGS="$2"
EXIT_CODE="$3"

# 记录工具使用
echo "=== Tool Use ===" >> "$LOG_FILE"
echo "Time: $(date)" >> "$LOG_FILE"
echo "Tool: $TOOL_NAME" >> "$LOG_FILE"
echo "Args: $TOOL_ARGS" >> "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 分析工具使用
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "Result: SUCCESS" >> "$LOG_FILE"
else
    echo "Result: FAILED" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"

echo "✅ Tool Use Hook 执行完成" >> "$LOG_FILE"
