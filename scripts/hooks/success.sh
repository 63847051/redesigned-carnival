#!/bin/bash
# Hook: Success
# 触发时机: 工具执行成功时
# 功能: 标记成功模式，提取最佳实践

HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"
LEARNING_DIR="/root/.openclaw/workspace/.learnings/success"

SUCCESS_LOG="$HOOKS_DIR/success-$(date +%Y%m%d).log"

TOOL_NAME="$1"
TOOL_ARGS="$2"

# 记录成功
echo "=== Success Captured ===" >> "$SUCCESS_LOG"
echo "Time: $(date)" >> "$SUCCESS_LOG"
echo "Tool: $TOOL_NAME" >> "$SUCCESS_LOG"
echo "Args: $TOOL_ARGS" >> "$SUCCESS_LOG"
echo "" >> "$SUCCESS_LOG"

# 分析成功模式
case "$TOOL_NAME" in
    "exec"|"bash")
        echo "成功命令模式: $TOOL_ARGS" >> "$SUCCESS_LOG"
        ;;
    "read"|"write"|"edit")
        echo "成功文件操作: $TOOL_ARGS" >> "$SUCCESS_LOG"
        ;;
esac

# 提取最佳实践
PATTERN_FILE="$LEARNING_DIR/patterns-$(date +%Y%m%d).md"
mkdir -p "$LEARNING_DIR"

# 检查是否已有模式文件
if [ ! -f "$PATTERN_FILE" ]; then
    echo "# 成功模式集合" > "$PATTERN_FILE"
    echo "" >> "$PATTERN_FILE"
    echo "**日期**: $(date +%Y-%m-%d)" >> "$PATTERN_FILE"
    echo "" >> "$PATTERN_FILE"
fi

# 追加成功模式
cat >> "$PATTERN_FILE" << EOF
## $TOOL_NAME 成功模式

**时间**: $(date +%H:%M:%S)
**命令**: \`$TOOL_ARGS\`

### 成功要点
- 正确的语法
- 适当的参数
- 良好的权限

### 可重用模式
\`\`\`bash
$TOOL_ARGS
\`\`\`

EOF

echo "模式记录: $PATTERN_FILE" >> "$SUCCESS_LOG"
echo "" >> "$SUCCESS_LOG"
echo "✅ Success Hook 执行完成" >> "$SUCCESS_LOG"
