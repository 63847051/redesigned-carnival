#!/bin/bash
# Hook: PreToolUse
# 触发时机: 工具使用前
# 功能: 验证工具参数，检查安全风险

HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"
LOG_FILE="$HOOKS_DIR/pre-tool-$(date +%Y%m%d).log"

TOOL_NAME="$1"
TOOL_ARGS="$2"

# 记录工具使用前状态
echo "=== PreToolUse ===" >> "$LOG_FILE"
echo "Time: $(date)" >> "$LOG_FILE"
echo "Tool: $TOOL_NAME" >> "$LOG_FILE"
echo "Args: $TOOL_ARGS" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 安全验证
case "$TOOL_NAME" in
    "exec"|"bash"|"shell")
        # 检查危险命令
        if echo "$TOOL_ARGS" | grep -qE "(rm -rf|dd if=/dev|mkfs|format|erase)"; then
            echo "🚨 危险命令检测: $TOOL_ARGS" >> "$LOG_FILE"
            echo "建议: 请确认此操作" >> "$LOG_FILE"
        else
            echo "✅ 命令安全检查通过" >> "$LOG_FILE"
        fi
        ;;
    "write"|"edit")
        # 检查文件路径
        if echo "$TOOL_ARGS" | grep -qE "(/etc|/boot|/root/.ssh)"; then
            echo "⚠️  系统文件操作: $TOOL_ARGS" >> "$LOG_FILE"
        else
            echo "✅ 文件操作安全" >> "$LOG_FILE"
        fi
        ;;
    *)
        echo "ℹ️  工具: $TOOL_NAME" >> "$LOG_FILE"
        ;;
esac

echo "" >> "$LOG_FILE"
echo "✅ PreToolUse Hook 执行完成" >> "$LOG_FILE"
