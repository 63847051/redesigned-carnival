#!/bin/bash
# Hook: Error
# 触发时机: 工具执行失败时
# 功能: 捕获错误信息，分析原因，生成学习记录

HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"
LEARNING_DIR="/root/.openclaw/workspace/.learnings/errors"

ERROR_LOG="$HOOKS_DIR/errors-$(date +%Y%m%d).log"

TOOL_NAME="$1"
TOOL_ARGS="$2"
EXIT_CODE="$3"

# 记录错误
echo "=== Error Captured ===" >> "$ERROR_LOG"
echo "Time: $(date)" >> "$ERROR_LOG"
echo "Tool: $TOOL_NAME" >> "$ERROR_LOG"
echo "Args: $TOOL_ARGS" >> "$ERROR_LOG"
echo "Exit Code: $EXIT_CODE" >> "$ERROR_LOG"
echo "" >> "$ERROR_LOG"

# 分析错误原因
case "$EXIT_CODE" in
    1)
        echo "错误类型: 一般错误" >> "$ERROR_LOG"
        ;;
    2)
        echo "错误类型: 误用 Shell 命令" >> "$ERROR_LOG"
        ;;
    126)
        echo "错误类型: 命令无法执行" >> "$ERROR_LOG"
        ;;
    127)
        echo "错误类型: 命令未找到" >> "$ERROR_LOG"
        ;;
    130)
        echo "错误类型: 被 Ctrl+C 中断" >> "$ERROR_LOG"
        ;;
    *)
        echo "错误类型: 未知错误" >> "$ERROR_LOG"
        ;;
esac

# 生成学习记录
LEARNING_FILE="$LEARNING_DIR/error-$(date +%Y%m%d-%H%M%S).md"
mkdir -p "$LEARNING_DIR"

cat > "$LEARNING_FILE" << EOF
# 错误学习记录

**时间**: $(date)
**工具**: $TOOL_NAME
**参数**: $TOOL_ARGS
**退出码**: $EXIT_CODE

## 错误分析

### 问题描述
$(eval "$TOOL_ARGS" 2>&1 | tail -10)

### 可能原因
- 命令语法错误
- 权限不足
- 文件不存在
- 依赖缺失

### 学习要点
1. 检查命令语法
2. 验证权限
3. 确认文件存在
4. 安装依赖

### 防止措施
- 使用前验证
- 添加错误处理
- 检查依赖
- 测试命令

EOF

echo "学习记录: $LEARNING_FILE" >> "$ERROR_LOG"
echo "" >> "$ERROR_LOG"
echo "✅ Error Hook 执行完成" >> "$ERROR_LOG"
