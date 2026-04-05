#!/bin/bash
# =============================================================================
# PAI 智能建议系统（简化版 v2）
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
HOT_MEMORY="$PAI_DIR/hot-memory.jsonl"
REPORT_DIR="$PAI_DIR/advice-reports"
TODAY=$(date +%Y-%m-%d)

mkdir -p "$REPORT_DIR"

echo "💡 PAI 智能建议系统 v2"
echo "======================================"

# =============================================================================
# 快速建议
# =============================================================================

quick_advice() {
    echo "💡 生成快速建议..."

    if [ ! -f "$HOT_MEMORY" ]; then
        echo "⚠️  Hot Memory 为空"
        return 1
    fi

    local report="$REPORT_DIR/quick-advice-$TODAY.md"

    # 统计
    local total=$(wc -l < "$HOT_MEMORY")
    local success=$(jq -r 'select(.success == 1) .success' "$HOT_MEMORY" | wc -l)
    local rate=$(awk "BEGIN {printf \"%.1f\", ($success/$total)*100}")
    local avg=$(jq -r '[.complexity] | add / length' "$HOT_MEMORY" 2>/dev/null || echo "0")
    local positive=$(jq -r 'select(.emotion == "positive") .emotion' "$HOT_MEMORY" | wc -l)
    local positive_rate=$(awk "BEGIN {printf \"%.1f\", ($positive/$total)*100}")

    cat > "$report" <<EOF
# 💡 快速建议报告

**日期**: $TODAY
**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## 📊 当前状态

- **成功率**: $rate%
- **平均复杂度**: $avg/5
- **积极情感**: $positive_rate%

---

## 🎯 建议

EOF

    # 成功率建议
    if awk "BEGIN {exit !($rate < 60)}"; then
        cat >> "$report" <<'EOF'
### 🔴 高优先级：提升成功率
- 降低任务复杂度到 2-3
- 专注于擅长领域
- 增加任务前准备
EOF
    elif awk "BEGIN {exit !($rate < 80)}"; then
        cat >> "$report" <<'EOF'
### 🟡 中优先级：稳步提升
- 保持当前节奏
- 适度提升复杂度
- 分析失败模式
EOF
    else
        cat >> "$report" <<'EOF'
### 🟢 低优先级：保持优秀
- 继续保持高成功率
- 挑战更高复杂度
- 分享成功经验
EOF
    fi

    # 复杂度建议
    if awk "BEGIN {exit !($avg < 2.5)}"; then
        cat >> "$report" <<'EOF'

### 💪 挑战自我
- 尝试复杂度 3-4 的任务
- 逐步提升技能
EOF
    elif awk "BEGIN {exit !($avg > 4.0)}"; then
        cat >> "$report" <<'EOF'

### ⚖️ 平衡发展
- 适当降低复杂度
- 分解复杂任务
EOF
    fi

    echo "" >> "$report"
    echo "---" >> "$report"
    echo "" >> "$report"
    echo "**建议完成**: PAI 智能系统" >> "$report"

    echo "✅ 快速建议完成: $report"
}

# =============================================================================
# 主程序
# =============================================================================

case "$1" in
    all|quick)
        quick_advice
        ;;
    *)
        echo "用法: $0 <命令>"
        echo "命令: all, quick"
        ;;
esac
