#!/bin/bash
# =============================================================================
# PAI 智能分析引擎（简化版 v2）
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
HOT_MEMORY="$PAI_DIR/hot-memory.jsonl"
REPORT_DIR="$PAI_DIR/analysis-reports"
TODAY=$(date +%Y-%m-%d)

mkdir -p "$REPORT_DIR"

echo "🔬 PAI 智能分析引擎 v2"
echo "======================================"

# =============================================================================
# 快速统计和分析
# =============================================================================

quick_analysis() {
    echo "📊 快速分析..."

    if [ ! -f "$HOT_MEMORY" ]; then
        echo "⚠️  Hot Memory 为空"
        return 1
    fi

    local report="$REPORT_DIR/quick-analysis-$TODAY.md"

    # 统计
    local total=$(wc -l < "$HOT_MEMORY")
    local success=$(jq -r 'select(.success == 1) .success' "$HOT_MEMORY" | wc -l)
    local rate=$(awk "BEGIN {printf \"%.1f\", ($success/$total)*100}")
    local avg=$(jq -r '[.complexity] | add / length' "$HOT_MEMORY" 2>/dev/null || echo "0")

    cat > "$report" <<EOF
# 📊 快速分析报告

**日期**: $TODAY
**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## 📈 核心指标

- **总任务数**: $total
- **成功**: $success ✅
- **成功率**: $rate%
- **平均复杂度**: $avg/5

---

## 💡 快速建议

EOF

    # 使用 awk 进行浮点比较
    if awk "BEGIN {exit !($rate < 70)}"; then
        echo "- ⚠️  成功率低于 70%，建议降低复杂度" >> "$report"
    elif awk "BEGIN {exit !($rate < 85)}"; then
        echo "- ✅ 成功率良好，可以适度提升复杂度" >> "$report"
    else
        echo "- 🎉 成功率优秀，保持当前节奏" >> "$report"
    fi

    if awk "BEGIN {exit !($avg < 2.5)}"; then
        echo "- 💪 复杂度偏低，可以挑战更高难度" >> "$report"
    elif awk "BEGIN {exit !($avg > 4.0)}"; then
        echo "- ⚖️  复杂度偏高，建议适当降低" >> "$report"
    else
        echo "- ✅ 复杂度适中" >> "$report"
    fi

    echo "" >> "$report"
    echo "---" >> "$report"
    echo "" >> "$report"
    echo "**分析完成**: PAI 自动化系统" >> "$report"

    echo "✅ 快速分析完成: $report"
}

# =============================================================================
# 主程序
# =============================================================================

case "$1" in
    all|quick)
        quick_analysis
        ;;
    *)
        echo "用法: $0 <命令>"
        echo "命令: all, quick"
        ;;
esac
