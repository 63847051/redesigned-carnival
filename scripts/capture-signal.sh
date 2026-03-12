#!/bin/bash
# 学习信号捕获脚本
# 捕获学习信号并记录到学习目录

LEARNING_DIR="/root/.openclaw/workspace/.learnings/signals"
SIGNALS_FILE="$LEARNING_DIR/signals-$(date +%Y%m%d).jsonl"

# 创建学习目录
mkdir -p "$LEARNING_DIR"

# 初始化信号文件
if [ ! -f "$SIGNALS_FILE" ]; then
    echo "[]" > "$SIGNALS_FILE"
fi

# 捕获信号函数
capture_signal() {
    local task="$1"
    local rating="$2"
    local sentiment="$3"
    local outcome="$4"
    local learning="$5"

    local signal=$(cat <<EOF
{
  "timestamp": $(date +%s),
  "date": "$(date +%Y-%m-%d)",
  "task": "$task",
  "rating": $rating,
  "sentiment": "$sentiment",
  "outcome": "$outcome",
  "learning": "$learning"
}
EOF
)

    # 追加到信号文件
    echo "$signal," >> "$SIGNALS_FILE"
}

# 导出函数供其他脚本使用
export -f capture_signal
