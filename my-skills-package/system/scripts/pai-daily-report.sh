#!/bin/bash
# =============================================================================
# PAI 每日分析报告脚本
# =============================================================================
# 功能：分析每日学习信号，生成进化报告
# 使用：每天自动运行（通过心跳或 cron）
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
TODAY=$(date +%Y-%m-%d)
REPORT_DIR="$PAI_DIR/reports"
SIGNAL_FILE="$PAI_DIR/signals/$TODAY-signals.jsonl"
REPORT_FILE="$REPORT_DIR/$TODAY-report.md"

# 创建目录
mkdir -p "$REPORT_DIR"

echo "🔍 PAI 每日学习分析 - $TODAY"
echo "======================================"

# 检查是否有学习信号
if [ ! -f "$SIGNAL_FILE" ]; then
    echo "⚠️  今天还没有学习信号记录"
    exit 0
fi

# 统计数据
TOTAL_TASKS=$(wc -l < "$SIGNAL_FILE")
SUCCESS_COUNT=$(grep '"success": 1' "$SIGNAL_FILE" | wc -l)
FAILED_COUNT=$(grep '"success": 0' "$SIGNAL_FILE" | wc -l)
AVG_COMPLEXITY=$(jq -r '[.complexity] | add / length' "$SIGNAL_FILE" 2>/dev/null || echo "N/A")

# 按类型统计
DESIGN_COUNT=$(grep '"task_type": "设计"' "$SIGNAL_FILE" | wc -l)
TECH_COUNT=$(grep '"task_type": "技术"' "$SIGNAL_FILE" | wc -l)
LOG_COUNT=$(grep '"task_type": "日志"' "$SIGNAL_FILE" | wc -l)

# 情感分析
POSITIVE_COUNT=$(grep '"emotion": "positive"' "$SIGNAL_FILE" | wc -l)
NEGATIVE_COUNT=$(grep '"emotion": "negative"' "$SIGNAL_FILE" | wc -l)

# 生成报告
cat > "$REPORT_FILE" <<EOF
# 📊 PAI 每日学习报告

**日期**: $TODAY
**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## 📈 今日统计

### 总体概览
- **总任务数**: $TOTAL_TASKS
- **成功**: $SUCCESS_COUNT ✅
- **失败**: $FAILED_COUNT ❌
- **成功率**: $(awk "BEGIN {printf \"%.1f\", ($SUCCESS_COUNT/$TOTAL_TASKS)*100}")%
- **平均复杂度**: $AVG_COMPLEXITY / 5

### 任务类型分布
- **设计任务**: $DESIGN_COUNT
- **技术任务**: $TECH_COUNT
- **日志任务**: $LOG_COUNT

### 情感分析
- **积极情感**: $POSITIVE_COUNT 😊
- **消极情感**: $NEGATIVE_COUNT 😔
- **情感比率**: $(awk "BEGIN {printf \"%.1f\", ($POSITIVE_COUNT/($POSITIVE_COUNT+$NEGATIVE_COUNT))*100}")% 积极

---

## 🎯 今日学习信号

EOF

# 详细记录
jq -r '"- [" + .task_type + "] " + .description + " (复杂度: " + (.complexity|tostring) + ", 结果: " + (if .success == 1 then "✅" else "❌" end) + ")"' "$SIGNAL_FILE" >> "$REPORT_FILE"

cat >> "$REPORT_FILE" <<EOF

---

## 💡 改进建议

### 继续保持 🌟
EOF

# 提取成功的任务
if [ "$SUCCESS_COUNT" -gt 0 ]; then
    echo "- 成功完成了 $SUCCESS_COUNT 个任务，保持这个节奏！" >> "$REPORT_FILE"
fi

if [ "$POSITIVE_COUNT" -gt 0 ]; then
    echo "- 积极情感占主导，说明当前工作方式有效" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" <<EOF

### 需要改进 ⚠️
EOF

# 提取失败的任务
if [ "$FAILED_COUNT" -gt 0 ]; then
    echo "- 有 $FAILED_COUNT 个任务失败，需要分析原因" >> "$REPORT_FILE"
fi

if [ "$NEGATIVE_COUNT" -gt 0 ]; then
    echo "- 存在消极情感，可能需要调整工作方式" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" <<EOF

### 明日目标 🎯
- 继续积累学习信号
- 提高任务成功率
- 尝试新的任务类型

---

## 📊 进化追踪

### 本周累计
- 需要汇总本周数据

### 学习曲线
- 需要可视化图表

---

**报告生成**: PAI 自动化系统
**下次更新**: 明天同一时间

EOF

echo "✅ 每日报告已生成: $REPORT_FILE"

# 显示摘要
echo ""
echo "📊 今日摘要:"
echo "   总任务: $TOTAL_TASKS"
echo "   成功率: $(awk "BEGIN {printf \"%.1f\", ($SUCCESS_COUNT/$TOTAL_TASKS)*100}")%"
echo "   平均复杂度: $AVG_COMPLEXITY"
echo "   情感: $(awk "BEGIN {printf \"%.1f\", ($POSITIVE_COUNT/($POSITIVE_COUNT+$NEGATIVE_COUNT))*100}")% 积极"
