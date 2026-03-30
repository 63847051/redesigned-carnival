#!/bin/bash
# 记忆更新脚本 - 对话结束后自动运行

MEMORY_DIR="/root/.openclaw/workspace/memory"
MEMORY_FILE="$MEMORY_DIR/MEMORY.md"
TODAY=$(date +%Y-%m-%d)
TODAY_FILE="$MEMORY_DIR/$TODAY.md"
TIME=$(date +%H:%M)

# 创建今日日志文件（如果不存在）
init_today_file() {
    if [ ! -f "$TODAY_FILE" ]; then
        echo "# $TODAY 记忆" > "$TODAY_FILE"
        echo "" >> "$TODAY_FILE"
    fi
}

# 追加到今日日志
append_to_today() {
    local content="$1"
    local is_important="$2"

    echo "## $TIME 对话总结" >> "$TODAY_FILE"
    echo "" >> "$TODAY_FILE"
    echo "$content" >> "$TODAY_FILE"
    echo "" >> "$TODAY_FILE"
    echo "---" >> "$TODAY_FILE"
    echo "" >> "$TODAY_FILE"

    # 如果是重要信息，同时更新 MEMORY.md
    if [ "$is_important" = "true" ]; then
        append_to_memory "$content"
    fi
}

# 追加到长期记忆
append_to_memory() {
    local content="$1"

    # 添加时间戳
    echo "" >> "$MEMORY_FILE"
    echo "## $TODAY - $TIME" >> "$MEMORY_FILE"
    echo "" >> "$MEMORY_FILE"
    echo "$content" >> "$MEMORY_FILE"
    echo "" >> "$MEMORY_FILE"
}

# 主函数
main() {
    local content="$1"
    local is_important="${2:-false}"

    if [ -z "$content" ]; then
        echo "使用方法: $0 <内容> [important]"
        exit 1
    fi

    # 初始化文件
    init_today_file

    # 追加内容
    append_to_today "$content" "$is_important"

    echo "✅ 记忆已更新"
    echo "   - 今日日志: $TODAY_FILE"
    if [ "$is_important" = "true" ]; then
        echo "   - 长期记忆: $MEMORY_FILE"
    fi
}

main "$@"
