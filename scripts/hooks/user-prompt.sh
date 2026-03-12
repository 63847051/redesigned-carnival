#!/bin/bash
# Hook: User Prompt
# 触发时机: 用户输入时
# 功能: 记录用户输入事件

HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"
LOG_FILE="$HOOKS_DIR/prompts-$(date +%Y%m%d).log"

# 记录用户输入（通过参数传入）
PROMPT="${1:-无输入}"

# 记录用户输入
echo "=== User Prompt ===" >> "$LOG_FILE"
echo "Time: $(date)" >> "$LOG_FILE"
echo "Prompt: $PROMPT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "✅ User Prompt Hook 执行完成" >> "$LOG_FILE"
