#!/bin/bash
# =============================================================================
# PAI 学习信号捕获脚本
# =============================================================================
# 功能：自动捕获学习信号并记录到 PAI 系统
# 使用：每次任务完成后自动调用
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%s)
LOG_FILE="$PAI_DIR/signals/$TODAY-signals.jsonl"

# 创建目录
mkdir -p "$PAI_DIR/signals"
mkdir -p "$PAI_DIR/reports"

# 检查参数
if [ $# -lt 4 ]; then
    echo "用法: $0 <任务类型> <复杂度(1-5)> <成功(1/0)> <描述> [标签]"
    echo "示例: $0 设计 4 1 完成会议室平面图 CAD绘图"
    exit 1
fi

TASK_TYPE="$1"
COMPLEXITY="$2"
SUCCESS="$3"
DESCRIPTION="$4"
TAGS="${5:-}"

# 验证复杂度范围
if [ "$COMPLEXITY" -lt 1 ] || [ "$COMPLEXITY" -gt 5 ]; then
    echo "❌ 复杂度必须在 1-5 之间"
    exit 1
fi

# 生成学习信号 JSON（单行格式）
echo "{\"timestamp\":$NOW,\"date\":\"$TODAY\",\"task_type\":\"$TASK_TYPE\",\"complexity\":$COMPLEXITY,\"success\":$SUCCESS,\"description\":\"$DESCRIPTION\",\"tags\":\"$TAGS\",\"emotion\":\"$(if [ "$SUCCESS" = "1" ]; then echo "positive"; else echo "negative"; fi)\"}" >> "$LOG_FILE"

echo "✅ 学习信号已捕获"
echo "   类型: $TASK_TYPE"
echo "   复杂度: $COMPLEXITY"
echo "   结果: $(if [ "$SUCCESS" = "1" ]; then echo "成功 ✅"; else echo "失败 ❌"; fi)"
echo "   描述: $DESCRIPTION"
