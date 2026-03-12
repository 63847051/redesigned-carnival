#!/bin/bash
# =============================================================================
# PAI 智能分析引擎
# =============================================================================
# 功能：分析学习信号，生成深度洞察
# 使用：定期运行（通过心跳或手动）
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
HOT_MEMORY="$PAI_DIR/hot-memory.jsonl"
WARM_MEMORY_DIR="$PAI_DIR/warm-memory"
REPORT_DIR="$PAI_DIR/analysis-reports"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%s)

mkdir -p "$REPORT_DIR"

echo "🔬 PAI 智能分析引擎"
echo "======================================"

# =============================================================================
# 分析 1: 成功模式识别
# =============================================================================

analyze_success_patterns() {
    echo "🎯 分析成功模式..."

    if [ ! -f "$HOT_MEMORY" ]; then
        echo "⚠️  Hot Memory 为空，无法分析"
        return 1
    fi

    local report="$REPORT_DIR/success-patterns-$TODAY.md"

    cat > "$report" <<'EOF'
# 🎯 成功模式分析报告

**生成时间**: DATE_PLACEHOLDER

---

## 📊 成功任务概览

EOF

    # 统计成功任务
    local total=$(wc -l < "$HOT_MEMORY")
    local success_count=$(jq -r 'select(.success == 1) .success' "$HOT_MEMORY" | wc -l)
    local success_rate=$(awk "BEGIN {printf \"%.1f\", ($success_count/$total)*100}")

    cat >> "$report" <<EOF
- **总任务数**: $total
- **成功任务**: $success_count
- **成功率**: $success_rate%

---

## 🏆 成功模式

### 按任务类型
EOF

    # 按类型统计成功率
    for type in 设计 技术 日志 系统; do
        local type_total=$(jq -r "select(.task_type == \"$type\") .task_type" "$HOT_MEMORY" | wc -l)
        if [ "$type_total" -gt 0 ]; then
            local type_success=$(jq -r "select(.task_type == \"$type\" and .success == 1) .task_type" "$HOT_MEMORY" | wc -l)
            local type_rate=$(awk "BEGIN {printf \"%.1f\", ($type_success/$type_total)*100}")
            echo "- **$type**: $type_success/$type_total ($type_rate%)" >> "$report"
        fi
    done

    cat >> "$report" <<'EOF'

### 按复杂度
EOF

    # 按复杂度统计成功率
    for complexity in 1 2 3 4 5; do
        local comp_total=$(jq -r "select(.complexity == $complexity) .complexity" "$HOT_MEMORY" | wc -l)
        if [ "$comp_total" -gt 0 ]; then
            local comp_success=$(jq -r "select(.complexity == $complexity and .success == 1) .complexity" "$HOT_MEMORY" | wc -l)
            local comp_rate=$(awk "BEGIN {printf \"%.1f\", ($comp_success/$comp_total)*100}")
            echo "- **复杂度 $complexity**: $comp_success/$comp_total ($comp_rate%)" >> "$report"
        fi
    done

    cat >> "$report" <<'EOF'

---

## 💡 成功因素

### 高成功率特征
- 任务类型匹配专长
- 复杂度适中（2-4）
- 有充足的上下文

### 最佳实践
- 继续保持高成功率的任务类型
- 适当挑战更高复杂度
- 保持积极的情感状态

---

EOF

    # 替换日期占位符
    sed -i "s/DATE_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/" "$report"

    echo "✅ 成功模式分析完成: $report"
}

# =============================================================================
# 分析 2: 失败根因分析
# =============================================================================

analyze_failure_root_cause() {
    echo "🔍 分析失败根因..."

    if [ ! -f "$HOT_MEMORY" ]; then
        echo "⚠️  Hot Memory 为空，无法分析"
        return 1
    fi

    local report="$REPORT_DIR/failure-analysis-$TODAY.md"

    cat > "$report" <<'EOF'
# 🔍 失败根因分析报告

**生成时间**: DATE_PLACEHOLDER

---

## 📊 失败任务概览

EOF

    # 统计失败任务
    local total=$(wc -l < "$HOT_MEMORY")
    local failed_count=$(jq -r 'select(.success == 0) .success' "$HOT_MEMORY" | wc -l)
    local failed_rate=$(awk "BEGIN {printf \"%.1f\", ($failed_count/$total)*100}")

    cat >> "$report" <<EOF
- **总任务数**: $total
- **失败任务**: $failed_count
- **失败率**: $failed_rate%

---

## ⚠️ 失败模式

### 按任务类型
EOF

    # 按类型统计失败率
    for type in 设计 技术 日志 系统; do
        local type_total=$(jq -r "select(.task_type == \"$type\") .task_type" "$HOT_MEMORY" | wc -l)
        if [ "$type_total" -gt 0 ]; then
            local type_failed=$(jq -r "select(.task_type == \"$type\" and .success == 0) .task_type" "$HOT_MEMORY" | wc -l)
            if [ "$type_failed" -gt 0 ]; then
                local type_rate=$(awk "BEGIN {printf \"%.1f\", ($type_failed/$type_total)*100}")
                echo "- **$type**: $type_failed/$type_total ($type_rate%)" >> "$report"
            fi
        fi
    done

    cat >> "$report" <<'EOF'

### 按复杂度
EOF

    # 按复杂度统计失败率
    for complexity in 1 2 3 4 5; do
        local comp_total=$(jq -r "select(.complexity == $complexity) .complexity" "$HOT_MEMORY" | wc -l)
        if [ "$comp_total" -gt 0 ]; then
            local comp_failed=$(jq -r "select(.complexity == $complexity and .success == 0) .complexity" "$HOT_MEMORY" | wc -l)
            if [ "$comp_failed" -gt 0 ]; then
                local comp_rate=$(awk "BEGIN {printf \"%.1f\", ($comp_failed/$comp_total)*100}")
                echo "- **复杂度 $complexity**: $comp_failed/$comp_total ($comp_rate%)" >> "$report"
            fi
        fi
    done

    cat >> "$report" <<'EOF'

---

## 🔧 改进建议

### 针对性改进
- 识别失败率高的任务类型
- 降低高失败率任务的复杂度
- 增加相关技能的练习

### 预防措施
- 任务前充分评估复杂度
- 分解复杂任务为简单步骤
- 寻求适合的模型支持

---

EOF

    # 替换日期占位符
    sed -i "s/DATE_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/" "$report"

    echo "✅ 失败根因分析完成: $report"
}

# =============================================================================
# 分析 3: 复杂度趋势分析
# =============================================================================

analyze_complexity_trend() {
    echo "📈 分析复杂度趋势..."

    if [ ! -f "$HOT_MEMORY" ]; then
        echo "⚠️  Hot Memory 为空，无法分析"
        return 1
    fi

    local report="$REPORT_DIR/complexity-trend-$TODAY.md"

    cat > "$report" <<'EOF'
# 📈 复杂度趋势分析报告

**生成时间**: DATE_PLACEHOLDER

---

## 📊 复杂度分布

EOF

    # 统计复杂度分布
    for complexity in 1 2 3 4 5; do
        local count=$(jq -r "select(.complexity == $complexity) .complexity" "$HOT_MEMORY" | wc -l)
        local percent=$(awk "BEGIN {printf \"%.1f\", ($count/$(wc -l < $HOT_MEMORY))*100}")
        echo "- **复杂度 $complexity**: $count 次 ($percent%)" >> "$report"
    done

    cat >> "$report" <<'EOF'

---

## 📈 趋势分析

### 复杂度适应度
- **平均复杂度**: AVG_PLACEHOLDER/5
- **成功任务平均复杂度**: SUCCESS_AVG_PLACEHOLDER/5
- **失败任务平均复杂度**: FAILED_AVG_PLACEHOLDER/5

### 建议
EOF

    local avg=$(jq -r '[.complexity] | add / length' "$HOT_MEMORY" 2>/dev/null || echo "N/A")
    local success_avg=$(jq -r 'select(.success == 1) | .complexity' "$HOT_MEMORY" | awk '{sum+=$1; count++} END {print count?sum/count:0}')
    local failed_avg=$(jq -r 'select(.success == 0) | .complexity' "$HOT_MEMORY" | awk '{sum+=$1; count++} END {print count?sum/count:0}')

    sed -i "s/AVG_PLACEHOLDER/$avg/" "$report"
    sed -i "s/SUCCESS_AVG_PLACEHOLDER/$success_avg/" "$report"
    sed -i "s/FAILED_AVG_PLACEHOLDER/$failed_avg/" "$report"

    if (( $(echo "$avg < 3" | bc -l) )); then
        echo "- 当前复杂度偏低，可以尝试更高挑战" >> "$report"
    elif (( $(echo "$avg > 4" | bc -l) )); then
        echo "- 当前复杂度偏高，建议适当降低" >> "$report"
    else
        echo "- 当前复杂度适中，保持节奏" >> "$report"
    fi

    cat >> "$report" <<'EOF'

---

EOF

    # 替换日期占位符
    sed -i "s/DATE_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/" "$report"

    echo "✅ 复杂度趋势分析完成: $report"
}

# =============================================================================
# 主程序
# =============================================================================

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 <命令>"
    echo ""
    echo "命令:"
    echo "  all           - 运行所有分析"
    echo "  success       - 成功模式分析"
    echo "  failure       - 失败根因分析"
    echo "  complexity    - 复杂度趋势分析"
    echo ""
    echo "示例:"
    echo "  $0 all"
    echo "  $0 success"
    exit 1
fi

command="$1"

case "$command" in
    all)
        analyze_success_patterns
        analyze_failure_root_cause
        analyze_complexity_trend
        echo ""
        echo "🎉 所有分析完成！"
        echo "📁 报告目录: $REPORT_DIR"
        ;;
    success)
        analyze_success_patterns
        ;;
    failure)
        analyze_failure_root_cause
        ;;
    complexity)
        analyze_complexity_trend
        ;;
    *)
        echo "❌ 未知命令: $command"
        exit 1
        ;;
esac
