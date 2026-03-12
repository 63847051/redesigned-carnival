#!/bin/bash
# 定时任务系统优化脚本
# 监控、日志清理、性能优化

set -e

WORKSPACE="/root/.openclaw/workspace"
LOG_DIR="$WORKSPACE/logs"
SCRIPTS_DIR="$WORKSPACE/scripts"
MONITOR_LOG="$LOG_DIR/scheduled-tasks-monitor.log"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$MONITOR_LOG"
}

# 检查日志文件大小
check_log_size() {
    local max_size=10485760  # 100MB
    
    find "$LOG_DIR" -name "*.log" -type f -size +$max_size -exec ls -lh {} \; | \
    while read size file; do
        log "⚠️  日志文件过大: $file ($size)"
        # 清理旧日志（保留最新 1000 行）
        tail -n 1000 "$file" > "${file}.tmp"
        mv "${file}.tmp" "$file"
        log "✅ 已清理日志文件: $file"
    done
}

# 检查脚本执行时间
check_execution_time() {
    local start_time=$1
    local script_name=$2
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [ $duration -gt 60 ]; then
        log "⚠️  $script_name 执行时间过长: ${duration}秒"
    fi
    
    echo $duration
}

# 测试所有脚本
test_all_scripts() {
    log "🔍 开始测试所有定时任务脚本..."
    
    # 测试 news-fetcher.py
    local start_time=$(date +%s)
    python3 "$SCRIPTS_DIR/news-fetcher.py" morning >/dev/null 2>&1
    local duration=$(check_execution_time $start_time "news-fetcher")
    log "✅ news-fetcher.py: ${duration}秒"
    
    # 测试 daily-news-summary.sh
    local start_time=$(date +%s)
    bash "$SCRIPTS_DIR/daily-news-summary.sh" >/dev/null 2>&1
    local duration=$(check_execution_time $start_time "daily-news-summary")
    log "✅ daily-news-summary.sh: ${duration}秒"
    
    # 测试 daily-digest.sh
    local start_time=$(date +%s)
    bash "$SCRIPTS_DIR/daily-digest.sh" >/dev/null 2>&1
    local duration=$(check_execution_time $start_time "daily-digest")
    log "✅ daily-digest.sh: ${duration}秒"
    
    log "🎉 测试完成！所有脚本运行正常"
}

# 清理临时文件
cleanup_temp_files() {
    log "🧹 清理临时文件..."
    
    # 清理 /tmp 下的新闻缓存
    find /tmp -name "news-*.txt" -mtime +1 -delete 2>/dev/null || true
    find /tmp -name "digest-*.txt" -mtime +1 -delete 2>/dev/null || true
    
    log "✅ 临时文件已清理"
}

# 生成性能报告
generate_performance_report() {
    local report="$LOG_DIR/performance-report-$(date +%Y%m%d).txt"
    
    echo "======================================" > "$report"
    echo "定时任务性能报告 - $(date '+%Y-%m-%d %H:%M:%S')" >> "$report"
    echo "======================================" >> "$report"
    echo "" >> "$report"
    
    # 统计日志数量
    echo "📊 日志统计:" >> "$report"
    echo "────────────────────────────────────" >> "$report"
    echo "日志文件数: $(find $LOG_DIR -name "*.log" | wc -l)" >> "$report"
    echo "总大小: $(du -sh $LOG_DIR | cut -f1)" >> "$report"
    echo "" >> "$report"
    
    # 最新的日志
    echo "📋 最新日志:" >> "$report"
    echo "────────────────────────────────────" >> "$report"
    tail -20 "$MONITOR_LOG" >> "$report"
    echo "" >> "$report"
    
    # 建议
    echo "💡 优化建议:" >> "$report"
    echo "────────────────────────────────────" >> "$report"
    echo "1. 定期清理日志文件（每周一次）" >> "$report"
    echo "2. 监控脚本执行时间（>60秒需优化）" >> "$report"
    echo "3. 监控错误日志（每日检查）" >> "$report"
    echo "" >> "$report"
    
    log "✅ 性能报告已生成: $report"
}

# 主函数
main() {
    local action=${1:-"check"}
    
    case "$action" in
        "check")
            log "🔍 执行定时任务系统检查..."
            check_log_size
            cleanup_temp_files
            log "✅ 检查完成"
            ;;
        "test")
            test_all_scripts
            ;;
        "report")
            generate_performance_report
            ;;
        "all")
            log "🚀 执行完整优化流程..."
            check_log_size
            cleanup_temp_files
            test_all_scripts
            generate_performance_report
            log "🎉 优化完成！"
            ;;
        *)
            echo "用法: $0 {check|test|report|all}"
            echo "  check  - 检查日志大小和临时文件"
            echo "  test   - 测试所有脚本"
            echo "  report - 生成性能报告"
            echo "  all    - 执行所有优化"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"

exit 0
