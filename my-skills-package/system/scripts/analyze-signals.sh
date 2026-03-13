#!/bin/bash
# 自动学习信号分析系统
# 功能: 自动分析工具使用，生成学习信号

LEARNING_DIR="/root/.openclaw/workspace/.learnings/signals"
HOOKS_DIR="/root/.openclaw/workspace/.learnings/hooks"
SIGNALS_FILE="$LEARNING_DIR/signals-$(date +%Y%m%d).jsonl"

# 创建学习目录
mkdir -p "$LEARNING_DIR"

# 评分函数 (1-5 星)
rate_success() {
    local exit_code=$1
    local tool_name=$2

    if [ "$exit_code" -eq 0 ]; then
        # 成功，根据工具类型评分
        case "$tool_name" in
            "read"|"write"|"edit")
                echo "5"  # 文件操作成功 = 高分
                ;;
            "exec"|"bash")
                echo "4"  # 命令执行成功 = 中高分
                ;;
            *)
                echo "4"  # 其他成功 = 中高分
                ;;
        esac
    else
        # 失败，根据退出码评分
        case "$exit_code" in
            1|2)
                echo "2"  # 一般错误 = 低分
                ;;
            127)
                echo "1"  # 命令未找到 = 极低分
                ;;
            *)
                echo "2"  # 其他错误 = 低分
                ;;
        esac
    fi
}

# 情感分析函数
analyze_sentiment() {
    local exit_code=$1
    local tool_name=$2

    if [ "$exit_code" -eq 0 ]; then
        echo "positive"
    else
        echo "negative"
    fi
}

# 结果分析函数
analyze_outcome() {
    local exit_code=$1

    if [ "$exit_code" -eq 0 ]; then
        echo "success"
    else
        echo "failure"
    fi
}

# 学习提取函数
extract_learning() {
    local tool_name="$1"
    local tool_args="$2"
    local exit_code=$3

    if [ "$exit_code" -eq 0 ]; then
        echo "成功执行 $tool_name: $tool_args"
    else
        echo "失败 $tool_name (退出码 $exit_code): $tool_args"
    fi
}

# 捕获信号函数
capture_signal() {
    local tool_name="$1"
    local tool_args="$2"
    local exit_code=$3

    # 计算评分
    local rating=$(rate_success "$exit_code" "$tool_name")

    # 分析情感
    local sentiment=$(analyze_sentiment "$exit_code" "$tool_name")

    # 分析结果
    local outcome=$(analyze_outcome "$exit_code")

    # 提取学习
    local learning=$(extract_learning "$tool_name" "$tool_args" "$exit_code")

    # 创建信号
    local signal=$(cat <<EOF
{
  "timestamp": $(date +%s),
  "date": "$(date +%Y-%m-%d)",
  "time": "$(date +%H:%M:%S)",
  "tool": "$tool_name",
  "args": "$tool_args",
  "exit_code": $exit_code,
  "rating": $rating,
  "sentiment": "$sentiment",
  "outcome": "$outcome",
  "learning": "$learning"
}
EOF
)

    # 追加到信号文件
    echo "$signal" >> "$SIGNALS_FILE"

    echo "✅ 信号已捕获: $tool_name (评分: $rating/5)"
}

# 分析今日信号
analyze_today() {
    local today=$(date +%Y%m%d)
    local signals_file="$LEARNING_DIR/signals-$today.jsonl"

    if [ ! -f "$signals_file" ]; then
        echo "今日暂无信号记录"
        return
    fi

    echo "📊 今日学习信号分析"
    echo "=================="
    echo ""

    # 统计总数
    local total=$(wc -l < "$signals_file")
    echo "总信号数: $total"
    echo ""

    # 统计成功率
    local success=$(grep -c '"outcome": "success"' "$signals_file" 2>/dev/null || echo "0")
    local success_rate=$(echo "scale=1; $success * 100 / $total" | bc)
    echo "成功率: $success_rate% ($success/$total)"
    echo ""

    # 统计平均评分
    local total_rating=$(grep -o '"rating": [0-9]' "$signals_file" | awk '{sum+=$2} END {print sum}')
    local avg_rating=$(echo "scale=1; $total_rating / $total" | bc)
    echo "平均评分: $avg_rating/5"
    echo ""

    # 统计情感分布
    local positive=$(grep -c '"sentiment": "positive"' "$signals_file" 2>/dev/null || echo "0")
    local negative=$(grep -c '"sentiment": "negative"' "$signals_file" 2>/dev/null || echo "0")
    echo "正面情感: $positive"
    echo "负面情感: $negative"
    echo ""

    # 统计工具使用
    echo "工具使用排行:"
    grep -o '"tool": "[^"]*"' "$signals_file" | sort | uniq -c | sort -rn | head -5
}

# 导出函数
export -f capture_signal
export -f analyze_today
