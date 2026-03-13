#!/bin/bash
# =============================================================================
# PAI 智能建议系统
# =============================================================================
# 功能：基于学习历史生成智能建议
# 使用：定期运行（通过心跳或手动）
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
HOT_MEMORY="$PAI_DIR/hot-memory.jsonl"
REPORT_DIR="$PAI_DIR/advice-reports"
TODAY=$(date +%Y-%m-%d)

mkdir -p "$REPORT_DIR"

echo "💡 PAI 智能建议系统"
echo "======================================"

# =============================================================================
# 建议 1: 优化建议
# =============================================================================

generate_optimization_advice() {
    echo "🔧 生成优化建议..."

    if [ ! -f "$HOT_MEMORY" ]; then
        echo "⚠️  Hot Memory 为空，无法生成建议"
        return 1
    fi

    local report="$REPORT_DIR/optimization-$TODAY.md"

    cat > "$report" <<'EOF'
# 🔧 优化建议报告

**生成时间**: DATE_PLACEHOLDER

---

## 📊 当前状态分析

EOF

    # 统计数据
    local total=$(wc -l < "$HOT_MEMORY")
    local success_count=$(jq -r 'select(.success == 1) .success' "$HOT_MEMORY" | wc -l)
    local success_rate=$(awk "BEGIN {printf \"%.1f\", ($success_count/$total)*100}")
    local avg_complexity=$(jq -r '[.complexity] | add / length' "$HOT_MEMORY" 2>/dev/null || echo "0")
    local positive_count=$(jq -r 'select(.emotion == "positive") .emotion' "$HOT_MEMORY" | wc -l)
    local positive_rate=$(awk "BEGIN {printf \"%.1f\", ($positive_count/$total)*100}")

    cat >> "$report" <<EOF
- **总任务数**: $total
- **成功率**: $success_rate%
- **平均复杂度**: $(printf "%.1f" $avg_complexity)/5
- **积极情感**: $positive_rate%

---

## 🚀 优化建议

### 工作流程优化
EOF

    # 成功率优化建议
    if (( $(echo "$success_rate < 60" | bc -l) )); then
        cat >> "$report" <<'EOF'
- **🔴 高优先级**: 成功率过低（< 60%）
  - 建议降低任务复杂度
  - 专注于擅长领域
  - 增加任务前的准备时间
EOF
    elif (( $(echo "$success_rate < 80" | bc -l) )); then
        cat >> "$report" <<'EOF'
- **🟡 中优先级**: 成功率中等（60-80%）
  - 可以尝试适度提高复杂度
  - 分析失败任务的模式
  - 优化工作流程
EOF
    else
        cat >> "$report" <<'EOF'
- **🟢 低优先级**: 成功率良好（> 80%）
  - 保持当前节奏
  - 可以挑战更高复杂度
  - 分享成功经验
EOF
    fi

    cat >> "$report" <<'EOF'

### 复杂度优化
EOF

    # 复杂度优化建议
    if (( $(echo "$avg_complexity < 2.5" | bc -l) )); then
        cat >> "$report" <<'EOF'
- **💪 挑战自我**: 当前复杂度偏低（< 2.5）
  - 建议尝试复杂度 3-4 的任务
  - 逐步提升技能水平
  - 跳出舒适区
EOF
    elif (( $(echo "$avg_complexity > 4.0" | bc -l) )); then
        cat >> "$report" <<'EOF'
- **⚖️ 平衡发展**: 当前复杂度偏高（> 4.0）
  - 建议适当降低复杂度
  - 分解复杂任务
  - 确保质量优先
EOF
    else
        cat >> "$report" <<'EOF'
- **✅ 节奏适中**: 当前复杂度合理（2.5-4.0）
  - 保持当前节奏
  - 根据实际情况微调
EOF
    fi

    cat >> "$report" <<'EOF'

### 情感优化
EOF

    # 情感优化建议
    if (( $(echo "$positive_rate < 70" | bc -l) )); then
        cat >> "$report" <<'EOF'
- **😊 提升积极情感**: 当前积极情感较低（< 70%）
  - 调整工作方式，增加成功体验
  - 适当降低任务难度
  - 积极反思每次任务
EOF
    else
        cat >> "$report" <<'EOF'
- **🎉 保持积极**: 当前积极情感良好（> 70%）
  - 继续保持积极心态
  - 分享成功经验
EOF
    fi

    cat >> "$report" <<'EOF'

---

## 🎯 明日行动计划

### 立即行动
EOF

    # 根据分析生成明日计划
    if (( $(echo "$success_rate < 70" | bc -l) )); then
        echo "- 选择成功率高的任务类型" >> "$report"
        echo "- 适当降低复杂度到 2-3" >> "$report"
    elif (( $(echo "$avg_complexity < 3.0" | bc -l) )); then
        echo "- 尝试复杂度 3-4 的任务" >> "$report"
        echo "- 挑战舒适区" >> "$report"
    else
        echo "- 保持当前节奏" >> "$report"
        echo "- 适度提升复杂度" >> "$report"
    fi

    cat >> "$report" <<'EOF'

### 持续改进
- 定期回顾学习信号
- 根据数据调整策略
- 记录改进效果

---

EOF

    # 替换日期占位符
    sed -i "s/DATE_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/" "$report"

    echo "✅ 优化建议生成完成: $report"
}

# =============================================================================
# 建议 2: 风险预警
# =============================================================================

generate_risk_warnings() {
    echo "⚠️  生成风险预警..."

    if [ ! -f "$HOT_MEMORY" ]; then
        echo "⚠️  Hot Memory 为空，无法生成预警"
        return 1
    fi

    local report="$REPORT_DIR/risk-warnings-$TODAY.md"

    cat > "$report" <<'EOF'
# ⚠️ 风险预警报告

**生成时间**: DATE_PLACEHOLDER

---

## 🚨 风险评估

EOF

    local risk_level="低"
    local risks=()

    # 检查成功率风险
    local total=$(wc -l < "$HOT_MEMORY")
    local success_count=$(jq -r 'select(.success == 1) .success' "$HOT_MEMORY" | wc -l)
    local success_rate=$(awk "BEGIN {printf \"%.1f\", ($success_count/$total)*100}")

    if (( $(echo "$success_rate < 50" | bc -l) )); then
        risks+=("🔴 **高风险**: 成功率低于 50%，需要立即调整")
        risk_level="高"
    elif (( $(echo "$success_rate < 70" | bc -l) )); then
        risks+=("🟡 **中风险**: 成功率低于 70%，建议调整")
        [ "$risk_level" = "低" ] && risk_level="中"
    fi

    # 检查复杂度风险
    local avg_complexity=$(jq -r '[.complexity] | add / length' "$HOT_MEMORY" 2>/dev/null || echo "0")
    if (( $(echo "$avg_complexity > 4.5" | bc -l) )); then
        risks+=("🟡 **中风险**: 复杂度过高（> 4.5），可能导致更多失败")
        [ "$risk_level" = "低" ] && risk_level="中"
    fi

    # 检查情感风险
    local positive_count=$(jq -r 'select(.emotion == "positive") .emotion' "$HOT_MEMORY" | wc -l)
    local positive_rate=$(awk "BEGIN {printf \"%.1f\", ($positive_count/$total)*100}")
    if (( $(echo "$positive_rate < 50" | bc -l) )); then
        risks+=("🔴 **高风险**: 积极情感过低（< 50%），可能影响长期表现")
        risk_level="高"
    fi

    echo "**总体风险级别**: $risk_level" >> "$report"

    if [ ${#risks[@]} -gt 0 ]; then
        echo "" >> "$report"
        echo "## 🚨 具体风险" >> "$report"
        for risk in "${risks[@]}"; do
            echo "- $risk" >> "$report"
        done
    else
        echo "" >> "$report"
        echo "✅ **未发现明显风险**" >> "$report"
    fi

    cat >> "$report" <<'EOF'

---

## 🛡️ 风险缓解建议

### 预防措施
EOF

    if (( $(echo "$success_rate < 70" | bc -l) )); then
        cat >> "$report" <<'EOF'
- 降低任务复杂度到 2-3
- 专注于成功率高的任务类型
- 增加任务前的准备和规划
EOF
    fi

    if (( $(echo "$avg_complexity > 4.0" | bc -l) )); then
        cat >> "$report" <<'EOF'
- 避免同时处理多个高复杂度任务
- 分解复杂任务为简单步骤
- 适当降低任务复杂度
EOF
    fi

    if (( $(echo "$positive_rate < 70" | bc -l) )); then
        cat >> "$report" <<'EOF'
- 调整工作方式，增加成功体验
- 积极反思每次任务
- 适当降低任务难度
EOF
    fi

    cat >> "$report" <<'EOF'

---

EOF

    # 替换日期占位符
    sed -i "s/DATE_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/" "$report"

    echo "✅ 风险预警生成完成: $report"
}

# =============================================================================
# 主程序
# =============================================================================

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 <命令>"
    echo ""
    echo "命令:"
    echo "  all       - 生成所有建议"
    echo "  optimize  - 优化建议"
    echo "  risk      - 风险预警"
    echo ""
    echo "示例:"
    echo "  $0 all"
    echo "  $0 optimize"
    exit 1
fi

command="$1"

case "$command" in
    all)
        generate_optimization_advice
        generate_risk_warnings
        echo ""
        echo "🎉 所有建议生成完成！"
        echo "📁 报告目录: $REPORT_DIR"
        ;;
    optimize)
        generate_optimization_advice
        ;;
    risk)
        generate_risk_warnings
        ;;
    *)
        echo "❌ 未知命令: $command"
        exit 1
        ;;
esac
