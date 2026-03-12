#!/bin/bash
# WAL Protocol (Write-Ahead Logging) 自动化脚本
# 基于proactive-agent-skill的WAL Protocol

set -e

WORKSPACE="/root/.openclaw/workspace"
SESSION_STATE="$WORKSPACE/SESSION-STATE.md"
WORKING_BUFFER="$WORKSPACE/working-buffer.md"
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_MD="$WORKSPACE/MEMORY.md"
TODAY="$MEMORY_DIR/$(date +%Y-%m-%d).md"

# 确保目录存在
mkdir -p "$MEMORY_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$WORKSPACE/.evolution/evolution.log"
}

# ============================================================================
# 功能1: 初始化SESSION-STATE.md
# =============================================================================

init_session_state() {
    local task_name="$1"
    local task_description="${2:-无详细描述}"

    log "📝 初始化SESSION-STATE.md"

    cat > "$SESSION_STATE" << EOF
# SESSION-STATE.md

**更新时间**: $(date '+%Y-%m-%d %H:%M')

---

## 当前任务

- **任务**: $task_name
- **开始时间**: $(date '+%Y-%m-%d %H:%M')
- **状态**: 🔄 进行中

---

## 任务详情

### 描述
$task_description

### 目标
- 待添加...

---

## 关键细节

### 已完成
- 无

### 进行中
- 🔄 $task_name

### 待办
- [ ] 完成任务
- [ ] 验证结果
- [ ] 更新文档

---

## 下一步

### 立即执行
1. 继续当前任务
2. 记录到working-buffer
3. 定期更新状态

### 后续任务
- [ ] 任务1
- [ ] 任务2

---

## 依赖

### 已配置
- ✅ OpenClaw系统
- ✅ v3.0进化系统
- ✅ GitHub仓库

### 已安装
- ✅ proactive-agent-skill
- ✅ 免费模型系统

---

## 进度跟踪

- **开始**: $(date '+%Y-%m-%d %H:%M')
- **当前**: $(date '+%Y-%m-%d %H:%M')
- **预计完成**: 待定

**进度**: 0% ⭐☆☆☆☆

---

## 备注

### 重要信息
- 无

### 风险
- 无重大风险

### 机会
- 无特殊机会
EOF

    log "✅ SESSION-STATE.md已创建"
}

# ============================================================================
# 功能2: 记录到working-buffer
# =============================================================================

log_working_buffer() {
    local title="$1"
    local user_message="$2"
    local response="$3"
    local status="${4:-✅ 完成}"

    log "📝 记录到working-buffer.md"

    cat >> "$WORKING_BUFFER" << EOF

### [$(date '+%Y-%m-%d %H:%M')] $title
- **用户**: "$user_message"
- **响应**: $response
- **状态**: $status

EOF

    log "✅ 已记录到working-buffer.md"
}

# ============================================================================
# 功能3: 压缩working-buffer
# =============================================================================

compact_working_buffer() {
    log "🗜️  压缩working-buffer.md"

    # 提取关键信息到MEMORY.md
    # 清理working-buffer.md
    # 归档到今日日志

    # 1. 归档到今日日志
    if [ -f "$WORKING_BUFFER" ]; then
        cat >> "$TODAY" << EOF

## Working Buffer 归档 ($(date '+%Y-%m-%d %H:%M'))

$(cat "$WORKING_BUFFER")

EOF

        # 2. 清理working-buffer
        > "$WORKING_BUFFER"
        
        log "✅ working-buffer已压缩并归档"
    fi
}

# ============================================================================
# 功能4: 更新MEMORY.md
# =============================================================================

update_memory_md() {
    local content="$1"
    local section="${2:-日常更新}"

    log "📝 更新MEMORY.md"

    # 添加到MEMORY.md
    {
        echo ""
        echo "## $section ($(date '+%Y-%m-%d'))"
        echo ""
        echo "$content"
        echo ""
    } >> "$MEMORY_MD"

    log "✅ MEMORY.md已更新"
}

# ============================================================================
# 功能5: 每日记忆整理
# =============================================================================

daily_memory_compaction() {
    log "📅 每日记忆整理"

    # 1. 压缩working-buffer
    compact_working_buffer

    # 2. 整理今日日志到MEMORY.md
    if [ -f "$TODAY" ]; then
        # 提取关键信息
        echo "" >> "$MEMORY_MD"
        echo "## 今日总结 ($(date '+%Y-%m-%d'))" >> "$MEMORY_MD"
        echo "" >> "$MEMORY_MD"
        echo "### 完成的任务" >> "$MEMORY_MD"
        grep -E "✅ 完成|成功" "$TODAY" | head -10 >> "$MEMORY_MD" || true
        echo "" >> "$MEMORY_MD"
        
        log "✅ 今日日志已整理到MEMORY.md"
    fi

    # 3. 清理旧日志（30天前）
    find "$MEMORY_DIR" -name "*.md" -mtime +30 -delete 2>/dev/null || true
    log "✅ 旧日志已清理"
}

# ============================================================================
# 功能6: 状态恢复
# =============================================================================

restore_session_state() {
    log "🔄 恢复SESSION-STATE.md"

    if [ -f "$SESSION_STATE" ]; then
        log "✅ SESSION-STATE.md存在"
        log "📋 当前任务:"
        grep -A 5 "## 当前任务" "$SESSION_STATE" || echo "  无法读取任务信息"
    else
        log "⚠️ SESSION-STATE.md不存在"
    fi
}

# ============================================================================
# 主程序
# =============================================================================

case "${1:-help}" in
    init)
        init_session_state "$2" "$3"
        ;;
    
    log)
        log_working_buffer "$2" "$3" "$4" "$5"
        ;;
    
    compact)
        compact_working_buffer
        ;;
    
    update-memory)
        update_memory_md "$2" "$3"
        ;;
    
    daily)
        daily_memory_compaction
        ;;
    
    restore)
        restore_session_state
        ;;
    
    *)
        echo "WAL Protocol 自动化脚本"
        echo ""
        echo "用法:"
        echo "  $0 init <任务名> [描述]"
        echo "  $0 log <标题> <用户消息> <响应> [状态]"
        echo "  $0 compact"
        echo "  $0 update-memory <内容> [章节]"
        echo "  $0 daily"
        echo "  $0 restore"
        echo ""
        echo "示例:"
        echo "  $0 init '整合proactive-agent' '分析并整合skill'"
        echo "  $0 log '用户提问' '什么时候完成' '已完成' '✅'"
        echo "  $0 compact"
        echo "  $0 daily"
        exit 0
        ;;
esac

exit 0
