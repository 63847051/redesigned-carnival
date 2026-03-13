#!/bin/bash
# =============================================================================
# PAI 三层记忆管理系统
# =============================================================================
# 功能：自动分层学习信号，实现三层记忆架构
# 使用：自动调用（通过心跳或任务完成时）
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
HOT_MEMORY="$PAI_DIR/hot-memory.jsonl"
WARM_MEMORY_DIR="$PAI_DIR/warm-memory"
COLD_MEMORY_DIR="$PAI_DIR/cold-memory"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%s)

# 创建目录
mkdir -p "$WARM_MEMORY_DIR"
mkdir -p "$COLD_MEMORY_DIR"

echo "🧠 PAI 三层记忆管理系统"
echo "======================================"

# =============================================================================
# 功能 1: 分层学习信号
# =============================================================================

layer_memory() {
    local signal_file="$1"

    if [ ! -f "$signal_file" ]; then
        echo "⚠️  信号文件不存在: $signal_file"
        return 1
    fi

    echo "📊 分层学习信号: $signal_file"

    # 读取所有信号
    local total=0
    local hot_count=0
    local warm_count=0
    local cold_count=0

    while IFS= read -r line; do
        [ -z "$line" ] && continue

        total=$((total + 1))

        # 提取时间戳
        local timestamp=$(echo "$line" | jq -r '.timestamp // 0')
        local days_ago=$(( ($NOW - timestamp) / 86400 ))

        # 分层逻辑
        if [ $total -le 50 ]; then
            # Hot Memory: 最近 50 条
            echo "$line" >> "$HOT_MEMORY.tmp"
            hot_count=$((hot_count + 1))
        elif [ $days_ago -le 7 ]; then
            # Warm Memory: 最近 7 天
            local date=$(echo "$line" | jq -r '.date // "unknown"')
            local warm_file="$WARM_MEMORY_DIR/$date-signals.jsonl"
            echo "$line" >> "$warm_file"
            warm_count=$((warm_count + 1))
        else
            # Cold Memory: 更早的数据
            local date=$(echo "$line" | jq -r '.date // "unknown"')
            local year_month=$(echo "$date" | cut -c1-7)
            local cold_file="$COLD_MEMORY_DIR/$year_month/$date-signals.jsonl"
            mkdir -p "$(dirname "$cold_file")"
            echo "$line" >> "$cold_file"
            cold_count=$((cold_count + 1))
        fi
    done < "$signal_file"

    # 原子替换 Hot Memory
    mv "$HOT_MEMORY.tmp" "$HOT_MEMORY"

    echo "✅ 分层完成:"
    echo "   Hot Memory: $hot_count 条"
    echo "   Warm Memory: $warm_count 条"
    echo "   Cold Memory: $cold_count 条"
    echo "   总计: $total 条"
}

# =============================================================================
# 功能 2: 查询记忆
# =============================================================================

query_memory() {
    local layer="$1"
    local filter="$2"
    local limit="${3:-10}"

    echo "🔍 查询 $layer Memory"
    echo "   过滤: $filter"
    echo "   限制: $limit"

    case "$layer" in
        hot)
            if [ ! -f "$HOT_MEMORY" ]; then
                echo "⚠️  Hot Memory 为空"
                return 1
            fi
            if [ -n "$filter" ]; then
                jq -r "select($filter)" "$HOT_MEMORY" | head -n "$limit"
            else
                tail -n "$limit" "$HOT_MEMORY"
            fi
            ;;
        warm)
            local recent_files=$(ls -t "$WARM_MEMORY_DIR"/*.jsonl 2>/dev/null | head -n 7)
            if [ -z "$recent_files" ]; then
                echo "⚠️  Warm Memory 为空"
                return 1
            fi
            for file in $recent_files; do
                if [ -n "$filter" ]; then
                    jq -r "select($filter)" "$file" 2>/dev/null
                else
                    cat "$file" 2>/dev/null
                fi
            done | head -n "$limit"
            ;;
        cold)
            local recent_files=$(find "$COLD_MEMORY_DIR" -name "*.jsonl" -type f | sort -r | head -n 30)
            if [ -z "$recent_files" ]; then
                echo "⚠️  Cold Memory 为空"
                return 1
            fi
            for file in $recent_files; do
                if [ -n "$filter" ]; then
                    jq -r "select($filter)" "$file" 2>/dev/null
                else
                    cat "$file" 2>/dev/null
                fi
            done | head -n "$limit"
            ;;
        *)
            echo "❌ 无效的记忆层: $layer"
            echo "   可用层: hot, warm, cold"
            return 1
            ;;
    esac
}

# =============================================================================
# 功能 3: 记忆统计
# =============================================================================

memory_stats() {
    echo "📊 PAI 记忆统计"
    echo "======================================"

    # Hot Memory
    if [ -f "$HOT_MEMORY" ]; then
        local hot_count=$(wc -l < "$HOT_MEMORY")
        echo "🔥 Hot Memory: $hot_count 条"
    else
        echo "🔥 Hot Memory: 0 条"
    fi

    # Warm Memory
    local warm_count=$(find "$WARM_MEMORY_DIR" -name "*.jsonl" -type f -exec wc -l {} + 2>/dev/null | awk '{sum+=$1} END {print sum}')
    echo "🌡️  Warm Memory: ${warm_count:-0} 条"

    # Cold Memory
    local cold_count=$(find "$COLD_MEMORY_DIR" -name "*.jsonl" -type f -exec wc -l {} + 2>/dev/null | awk '{sum+=$1} END {print sum}')
    echo "❄️  Cold Memory: ${cold_count:-0} 条"

    # 总计
    local total=$((${hot_count:-0} + ${warm_count:-0} + ${cold_count:-0}))
    echo "📦 总计: $total 条"
}

# =============================================================================
# 功能 4: 智能建议
# =============================================================================

smart_advice() {
    echo "💡 PAI 智能建议"
    echo "======================================"

    # 分析 Hot Memory
    if [ -f "$HOT_MEMORY" ]; then
        local success_rate=$(jq -r '[.success // 0] | add / length * 100' "$HOT_MEMORY" 2>/dev/null || echo "0")
        local avg_complexity=$(jq -r '[.complexity // 0] | add / length' "$HOT_MEMORY" 2>/dev/null || echo "0")

        echo "📊 近期表现:"
        echo "   成功率: $(printf "%.1f" $success_rate)%"
        echo "   平均复杂度: $(printf "%.1f" $avg_complexity)/5"

        if (( $(echo "$success_rate < 70" | bc -l) )); then
            echo ""
            echo "⚠️  建议:"
            echo "   - 成功率较低，建议降低任务复杂度"
            echo "   - 检查失败任务的共同模式"
        fi

        if (( $(echo "$avg_complexity < 3" | bc -l) )); then
            echo ""
            echo "💪 建议:"
            echo "   - 可以尝试更高复杂度的任务"
            echo "   - 挑战舒适区，促进成长"
        fi
    fi
}

# =============================================================================
# 主程序
# =============================================================================

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 <命令> [参数...]"
    echo ""
    echo "命令:"
    echo "  layer <信号文件>          - 分层学习信号到三层记忆"
    echo "  query <层> [过滤] [限制]  - 查询记忆"
    echo "  stats                     - 显示记忆统计"
    echo "  advice                    - 生成智能建议"
    echo ""
    echo "示例:"
    echo "  $0 layer signals/2026-03-05-signals.jsonl"
    echo "  $0 query hot '.task_type == \"设计\"' 5"
    echo "  $0 stats"
    echo "  $0 advice"
    exit 1
fi

command="$1"
shift

case "$command" in
    layer)
        if [ $# -lt 1 ]; then
            echo "❌ 缺少信号文件路径"
            exit 1
        fi
        layer_memory "$1"
        ;;
    query)
        if [ $# -lt 1 ]; then
            echo "❌ 缺少记忆层名称"
            exit 1
        fi
        query_memory "$@"
        ;;
    stats)
        memory_stats
        ;;
    advice)
        smart_advice
        ;;
    *)
        echo "❌ 未知命令: $command"
        exit 1
        ;;
esac
