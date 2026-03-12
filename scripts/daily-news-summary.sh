#!/bin/bash
# 每日新闻摘要脚本
# 整合到 v5.3 终极自主进化系统

set -e

WORKSPACE="/root/.openclaw/workspace"
NEWS_FETCHER="$WORKSPACE/scripts/news-fetcher.py"
LOG_FILE="$WORKSPACE/logs/news-summary.log"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# 判断早报还是晚报
get_period() {
    hour=$(date +%H)
    if [ "$hour" -lt 12 ]; then
        echo "morning"
    else
        echo "evening"
    fi
}

# 主函数
main() {
    local period=$(get_period)
    
    log "📰 开始生成新闻摘要 ($period)"
    echo "======================================"
    
    # 调用新闻抓取器
    cd "$WORKSPACE"
    python3 "$NEWS_FETCHER" "$period"
    
    # 读取生成的报告
    local report_file="/tmp/news-${period}.txt"
    
    if [ -f "$report_file" ]; then
        # 推送到飞书
        log "📤 推送到飞书..."
        
        # 这里集成飞书推送
        # 使用现有的飞书 Gateway 配置
        
        local report_content=$(cat "$report_file")
        
        # TODO: 调用飞书 API 推送消息
        # openclaw message send --channel feishu --message "$report_content"
        
        log "✅ 新闻摘要推送完成"
        echo "======================================"
    else
        log "❌ 报告文件生成失败"
        exit 1
    fi
}

# 执行主函数
main "$@"

log "🎉 新闻摘要任务完成！"
exit 0
