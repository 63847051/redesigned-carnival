#!/bin/bash
# pageindex-rag 用户反馈收集

WORKSPACE="/root/.openclaw/workspace"
FEEDBACK_FILE="$WORKSPACE/pageindex-feedback.log"

# 收集反馈
collect_feedback() {
    local query="$1"
    local result_count="$2"
    local satisfaction="${3:-5}"
    local comments="${4:-无}"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] 查询: $query | 结果数: $result_count | 满意度: $satisfaction/5 | 备注: $comments" >> "$FEEDBACK_FILE"
    
    echo "✅ 反馈已记录"
    echo "   查询: $query"
    echo "   结果数: $result_count"
    echo "   满意度: $satisfaction/5"
    echo "   备注: $comments"
}

# 显示反馈统计
show_feedback_stats() {
    if [ ! -f "$FEEDBACK_FILE" ]; then
        echo "📊 暂无反馈数据"
        return
    fi
    
    echo "📊 pageindex-rag 反馈统计"
    echo "======================================"
    echo ""
    
    local total=$(wc -l < "$FEEDBACK_FILE")
    echo "总反馈数: $total"
    echo ""
    
    echo "最近 10 条反馈:"
    tail -10 "$FEEDBACK_FILE" | while IFS= read -r line; do
        echo "  $line"
    done
    echo ""
    
    # 计算平均满意度
    local avg_satisfaction=$(grep "满意度:" "$FEEDBACK_FILE" | sed 's/.*满意度: \([0-9]*\).*/\1/' | awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')
    echo "平均满意度: $avg_satisfaction/5"
}

# 如果直接运行，显示统计
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-stats}" in
        stats)
            show_feedback_stats
            ;;
        *)
            echo "使用方法:"
            echo "  $0 stats                    # 显示统计"
            echo "  $0 add <查询> <结果数> <满意度> [备注]"
            echo ""
            echo "示例:"
            echo "  $0 add \"部署\" 3 5 \"非常准确\""
            ;;
    esac
fi
