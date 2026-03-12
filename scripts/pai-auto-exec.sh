#!/bin/bash
# =============================================================================
# 🔄 PAI 自动化执行脚本
# =============================================================================
# 功能：在后台自动运行 PAI 系统，持续进化学习
# 使用：通过 cron 或后台服务自动调用
# =============================================================================

WORKSPACE="/root/.openclaw/workspace"
PAI_DIR="$WORKSPACE/.pai-learning"
LOG_FILE="$PAI_DIR/auto-execution.log"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%s)

# 创建日志
mkdir -p "$PAI_DIR"

echo "🔄 PAI 自动化执行系统 v1.0"
echo "======================================"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "" | tee -a "$LOG_FILE"

# =============================================================================
# 自动化任务 1: 检查系统健康
# =============================================================================

check_system_health() {
    echo "🔍 任务 1: 检查系统健康..." | tee -a "$LOG_FILE"
    
    # 检查 Gateway 状态
    if systemctl --user is-active --quiet openclaw-gateway; then
        echo "   ✅ Gateway: 运行中" | tee -a "$LOG_FILE"
    else
        echo "   ⚠️  Gateway: 未运行" | tee -a "$LOG_FILE"
    fi
    
    # 检查内存使用
    local mem_usage=$(free | awk '/Mem/{printf "%.1f", $3/$2*100}')
    echo "   📊 内存: $mem_usage" | tee -a "$LOG_FILE"
    
    # 检查学习信号数量
    local signal_count=$(find "$PAI_DIR/signals" -name "*.jsonl" -type f 2>/dev/null | wc -l)
    echo "   📚 学习信号: $signal_count 条" | tee -a "$LOG_FILE"
    
    echo "" | tee -a "$LOG_FILE"
}

# =============================================================================
# 自动化任务 2: 运行完整 PAI 工作流
# =============================================================================

run_pai_workflow() {
    echo "🚀 任务 2: 运行完整 PAI 工作流..." | tee -a "$LOG_FILE"
    
    # 运行完整工作流
    bash "$WORKSPACE/scripts/pai-workflow.sh" >> "$LOG_FILE" 2>&1
    
    echo "   ✅ 工作流完成" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# =============================================================================
# 自动化任务 3: 生成每日总结
# =============================================================================

generate_daily_summary() {
    echo "📝 任务 3: 生成每日总结..." | tee -a "$LOG_FILE"
    
    # 读取最新分析报告
    local latest_report="$PAI_DIR/analysis-reports/quick-analysis-$TODAY.md"
    if [ -f "$latest_report" ]; then
        echo "   📊 今日统计:" | tee -a "$LOG_FILE"
        grep -E "总任务数|成功率|平均复杂度|积极情感" "$latest_report" | tee -a "$LOG_FILE"
    fi
    
    echo "" | tee -a "$LOG_FILE"
}

# =============================================================================
# 自动化任务 4: 智能建议（如需要）
# =============================================================================

provide_smart_advice() {
    echo "💡 任务 4: 检查智能建议..." | tee -a "$LOG_FILE"
    
    # 检查成功率
    local latest_report="$PAI_DIR/analysis-reports/quick-analysis-$TODAY.md"
    if [ -f "$latest_report" ]; then
        local success_rate=$(grep "成功率" "$latest_report" | grep -o "[0-9]*\.[0-9]" | head -1)
        
        if [ -n "$success_rate" ]; then
            # 使用 awk 进行浮点比较
            if awk "BEGIN {exit !($success_rate < 80)}"; then
                echo "   ⚠️  建议: 成功率低于 80%，建议降低任务复杂度" | tee -a "$LOG_FILE"
            else
                echo "   ✅ 成功率良好: $success_rate%" | tee -a "$LOG_FILE"
            fi
        fi
    fi
    
    echo "" | tee -a "$LOG_FILE"
}

# =============================================================================
# 主程序
# =============================================================================

main() {
    # 记录开始
    echo "======================================" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # 执行自动化任务
    check_system_health
    run_pai_workflow
    generate_daily_summary
    provide_smart_advice
    
    # 记录完成
    echo "✅ 自动化执行完成" | tee -a "$LOG_FILE"
    echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
    echo "======================================" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# 如果直接运行脚本
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
