#!/bin/bash
# =====================================================
# 记忆扫描脚本 - memory-scanner.sh
# 彬子记忆系统 - 第二道防线：心跳扫描（60分钟周期）
# =====================================================

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
SESSIONS_DIR="$WORKSPACE/.openclaw/sessions"
LOG_FILE="$WORKSPACE/logs/memory-scanner.log"

mkdir -p "$MEMORY_DIR" "$WORKSPACE/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "========== 记忆扫描开始 =========="

TODAY=$(date '+%Y-%m-%d')
DAILY_LOG="$MEMORY_DIR/$TODAY.md"

# 初始化每日日志
init_daily_log() {
    if [ ! -f "$DAILY_LOG" ]; then
        cat > "$DAILY_LOG" << EOF
# 日记 - $TODAY

## 扫描记录

EOF
        log "创建每日日志: $DAILY_LOG"
    fi
}

# 扫描最近的 session 文件
scan_sessions() {
    log "扫描最近 session 文件..."
    
    local recent_sessions=$(find "$SESSIONS_DIR" -name "*.json" -mmin -60 2>/dev/null | head -10)
    
    if [ -z "$recent_sessions" ]; then
        log "最近 60 分钟无 session 文件"
        return
    fi
    
    local session_count=0
    local total_messages=0
    
    for session_file in $recent_sessions; do
        session_count=$((session_count + 1))
        
        # 提取关键信息
        local messages=$(cat "$session_file" 2>/dev/null | grep -o '"content":"[^"]*"' | head -20 || echo "")
        total_messages=$((total_messages + $(echo "$messages" | wc -l)))
        
        # 提取关键模式
        extract_insights "$messages" "$session_file"
    done
    
    log "扫描完成: $session_count 个 session, $total_messages 条消息"
}

# 提取洞察和决策
extract_insights() {
    local messages="$1"
    local session_file="$2"
    
    # 关键词模式
    local patterns=(
        "决定"
        "结论"
        "已完成"
        "完成"
        "建议"
        "教训"
        "错误"
        "根因"
        "问题"
        "解决方案"
    )
    
    local insights_found=0
    
    for pattern in "${patterns[@]}"; do
        local matches=$(echo "$messages" | grep -c "$pattern" 2>/dev/null || echo "0")
        if [ "$matches" -gt 0 ] 2>/dev/null; then
            insights_found=$((insights_found + matches))
        fi
    done
    
    if [ "$insights_found" -gt 0 ]; then
        log "发现 $insights_found 个潜在洞察"
        
        # 追加到每日日志
        echo "## $(( $(grep -c "^## " "$DAILY_LOG" 2>/dev/null || echo "0") + 1 )) 自动扫描 $(date '+%H:%M:%S')" >> "$DAILY_LOG"
        echo "- 扫描 session: $(basename "$session_file")" >> "$DAILY_LOG"
        echo "- 潜在洞察数量: $insights_found" >> "$DAILY_LOG"
        echo "" >> "$DAILY_LOG"
    fi
}

# 更新 NOW.md（如果存在）
update_now() {
    local now_file="$MEMORY_DIR/NOW.md"
    
    if [ -f "$now_file" ]; then
        log "检查 NOW.md 需要更新的内容..."
        # 可以添加自动检查逻辑
    fi
}

# 生成扫描摘要
generate_summary() {
    local scan_time=$(date '+%Y-%m-%d %H:%M:%S')
    local log_lines=$(wc -l < "$DAILY_LOG" 2>/dev/null || echo "0")
    
    echo "" >> "$DAILY_LOG"
    echo "---" >> "$DAILY_LOG"
    echo "*扫描时间: $scan_time | 总行数: $log_lines*" >> "$DAILY_LOG"
    
    log "扫描摘要: $log_lines 行"
}

# 主流程
main() {
    init_daily_log
    scan_sessions
    update_now
    generate_summary
    
    log "========== 记忆扫描完成 =========="
}

main "$@"
