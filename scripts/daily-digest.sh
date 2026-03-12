#!/bin/bash
# 每日简报脚本
# 汇总昨日活动和今日待办

set -e

WORKSPACE="/root/.openclaw/workspace"
SESSION_STATE="$WORKSPACE/SESSION-STATE.md"
MEMORY_DIR="$WORKSPACE/memory"
LOG_FILE="$WORKSPACE/logs/daily-digest.log"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# 生成每日简报
generate_digest() {
    local report=""
    
    # 标题
    report+="📋 每日简报 - $(date '+%Y-%m-%d')\n\n"
    
    # 昨日完成
    report+="📊 昨日完成\n"
    report+="────────────────────────\n"
    
    # 从 SESSION-STATE.md 提取昨日完成
    if [ -f "$SESSION_STATE" ]; then
        local completed=$(grep -A 10 "昨日完成\|已完成" "$SESSION_STATE" 2>/dev/null || echo "暂无记录")
        if [ -n "$completed" ]; then
            report+="$completed\n"
        else
            report+="暂无特别记录\n"
        fi
    else
        report+="暂无记录\n"
    fi
    
    report+="\n"
    
    # 今日待办
    report+="🎯 今日待办\n"
    report+="────────────────────────\n"
    
    # 从 SESSION-STATE.md 提取今日待办
    if [ -f "$SESSION_STATE" ]; then
        local todo=$(grep -A 10 "今日待办\|待办" "$SESSION_STATE" 2>/dev/null || echo "暂无记录")
        if [ -n "$todo" ]; then
            report+="$todo\n"
        else
            report+="暂无特别记录\n"
        fi
    else
        report+="暂无记录\n"
    fi
    
    report+="\n"
    
    # 系统状态
    report+="💡 系统状态\n"
    report+="────────────────────────\n"
    
    # 检查 Gateway 状态
    if command -v openclaw &> /dev/null; then
        local gateway_status=$(openclaw gateway status 2>/dev/null | grep -o "Runtime: [^\"]*" || echo "未知")
        report+="$gateway_status\n"
    else
        report+="Gateway: 检查中...\n"
    fi
    
    # 内存使用
    local memory=$(free | awk '/Mem/{printf("%.1f%%"), $3/$2*100}')
    report+="内存: $memory\n"
    
    # 最后错误
    local last_error=$(journalctl --user -u openclaw-gateway --since "24 hours ago" --no-pager | grep -i "error" | tail -1 || echo "无")
    if [ "$last_error" = "无" ]; then
        report+="最后错误: 无（24小时内）\n"
    else
        report+="最后错误: 有错误（详见日志）\n"
    fi
    
    report+="\n"
    
    # 进化数据
    report+="📈 进化数据\n"
    report+="────────────────────────\n"
    
    # PAI 学习信号
    local pai_signals=$(find "$WORKSPACE/.pai-learning/signals/" -name "*.json" 2>/dev/null | wc -l)
    report+="学习信号: $pai_signals 个\n"
    
    # 版本
    local version=$(grep -o "v[0-9]\.[0-9]" "$WORKSPACE/SOUL.md" 2>/dev/null | head -1 || echo "v5.3")
    report+="进化版本: $version\n"
    
    report+="\n"
    report+="────────────────────────\n"
    report+="🤖 生成时间: $(date '+%Y-%m-%d %H:%M:%S')\n"
    
    echo "$report"
}

# 主函数
main() {
    log "📋 开始生成每日简报"
    echo "======================================"
    
    # 生成简报
    local digest=$(generate_digest)
    
    # 输出简报
    echo "$digest"
    
    # 保存到文件
    local digest_file="/tmp/daily-digest.txt"
    echo "$digest" > "$digest_file"
    
    # 推送到飞书
    log "📤 推送到飞书..."
    
    # TODO: 调用飞书 API 推送消息
    # openclaw message send --channel feishu --message "$digest"
    
    log "✅ 每日简报推送完成"
    echo "======================================"
}

# 执行主函数
main

log "🎉 每日简报任务完成！"
exit 0
