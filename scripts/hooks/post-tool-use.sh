#!/bin/bash
# Hook: PostToolUse
# 触发时机: 工具使用后
# 功能: 分析执行结果，评估成功/失败

HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"
LOG_FILE="$HOOKS_DIR/post-tool-$(date +%Y%m%d).log"

TOOL_NAME="$1"
TOOL_ARGS="$2"
EXIT_CODE="$3"

# 记录工具使用后状态
echo "=== PostToolUse ===" >> "$LOG_FILE"
echo "Time: $(date)" >> "$LOG_FILE"
echo "Tool: $TOOL_NAME" >> "$LOG_FILE"
echo "Args: $TOOL_ARGS" >> "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 分析执行结果
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✅ 执行成功" >> "$LOG_FILE"

    # 提取成功模式
    case "$TOOL_NAME" in
        "exec"|"bash")
            echo "成功命令: $TOOL_ARGS" >> "$LOG_FILE"
            ;;
        "read"|"write")
            echo "文件操作成功: $TOOL_ARGS" >> "$LOG_FILE"
            ;;
    esac

    # 调用成功 Hook
    /root/.openclaw/workspace/scripts/hooks/success.sh "$TOOL_NAME" "$TOOL_ARGS" 2>/dev/null

else
    echo "❌ 执行失败" >> "$LOG_FILE"
    echo "退出码: $EXIT_CODE" >> "$LOG_FILE"

    # 调用错误 Hook
    /root/.openclaw/workspace/scripts/hooks/error.sh "$TOOL_NAME" "$TOOL_ARGS" "$EXIT_CODE" 2>/dev/null
fi

echo "" >> "$LOG_FILE"
echo "✅ PostToolUse Hook 执行完成" >> "$LOG_FILE"
