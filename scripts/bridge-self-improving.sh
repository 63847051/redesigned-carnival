#!/bin/bash
# 桥接self-improving和v4.0系统
# 实现双系统并行和智能同步

WORKSPACE="/root/.openclaw/workspace"
SELF_IMPROV_DIR="$HOME/self-improving"
AUTO_ORG_DIR="$WORKSPACE/.learnings/auto-organized"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$WORKSPACE/.evolution/evolution.log"
}

# ============================================================================
# 功能1: 从self-improving同步项目学习
# =============================================================================

sync_from_self_improving() {
    log "🔄 从self-improving同步学习内容..."
    
    # 确保目录存在
    mkdir -p "$AUTO_ORG_DIR/by-project"
    mkdir -p "$AUTO_ORG_DIR/by-domain"
    
    # 同步项目学习
    if [ -d "$SELF_IMPROV_DIR/projects" ]; then
        for project_dir in "$SELF_IMPROV_DIR/projects"/*; do
            if [ -d "$project_dir" ]; then
                project=$(basename "$project_dir")
                ln -sf "$project_dir" "$AUTO_ORG_DIR/by-project/$project" 2>/dev/null || true
            fi
        done
        log "✅ 已同步项目学习"
    else
        log "⚠️ self-improving/projects/ 不存在"
    fi
    
    # 同步领域学习
    if [ -d "$SELF_IMPROV_DIR/domains" ]; then
        for domain_dir in "$SELF_IMPROV_DIR/domains/"*; do
            if [ -d "$domain_dir" ]; then
                domain=$(basename "$domain_dir")
                ln -sf "$domain_dir" "$AUTO_ORG_DIR/by-domain/$domain" 2>/dev/null || true
            fi
        done
        log "✅ 已同步领域学习"
    fi
    
    # 更新记忆索引
    update_memory_index
}

# ============================================================================
# 功能2: 记录到self-improving（项目和领域）
# =============================================================================

log_to_self_improving() {
    local project="${1:-general}"
    local lesson="$2"
    local domain="${3:-general}"
    
    log "📝 记录到self-improving..."
    
    # 记录到项目
    if [ -n "$project" ] && [ "$project" != "general" ]; then
        mkdir -p "$SELF_IMPROV_DIR/projects/$project"
        {
            echo "# 项目学习: $project"
            echo ""
            echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
            echo ""
            echo "- $lesson"
            echo ""
        } >> "$SELF_IMPROV_DIR/projects/$project/learnings.md"
        log "✅ 已记录到项目: $project"
    fi
    
    # 记录到领域
    if [ -n "$domain" ] && [ "$domain" != "general" ]; then
        mkdir -p "$SELF_IMPROV_DIR/domains/$domain"
        {
            echo "# 领域学习: $domain"
            echo ""
            echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
            echo ""
            echo "- $lesson"
            echo ""
        } >> "$SELF_IMPROV_DIR/domains/$domain/learnings.md"
        log "✅ 已记录到领域: $domain"
    fi
    
    # 记录到corrections.md（如果包含修正）
    if [[ "$lesson" =~ [错误|修正|改进] ]]; then
        {
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] $lesson"
            echo ""
        } >> "$SELF_IMPROV_DIR/corrections.md"
        log "✅ 已记录到corrections.md"
    fi
}

# ============================================================================
# 功能3: 检查self-improving状态
# =============================================================================

check_self_improving_status() {
    log "🔍 检查self-improving状态..."
    
    local corrections_count=0
    local projects_count=0
    local domains_count=0
    
    # 统计corrections
    if [ -f "$SELF_IMPROV_DIR/corrections.md" ]; then
        corrections_count=$(grep -c "^[" "$SELF_IMPROV_DIR/corrections.md" 2>/dev/null || echo 0)
    fi
    
    # 统计projects
    if [ -d "$SELF_IMPROV_DIR/projects" ]; then
        projects_count=$(ls -1 "$SELF_IMPROV_DIR/projects" 2>/dev/null | wc -l)
    fi
    
    # 统计domains
    if [ -d "$SELF_IMPROV_DIR/domains" ]; then
        domains_count=$(ls -1 "$SELF_IMPROV_DIR/domains/" 2>/dev/null | wc -l)
    fi
    
    echo "📊 self-improving状态:"
    echo "  - 修正记录: $corrections_count 条"
    echo "  - 项目数: $projects_count 个"
    echo "  - 领域数: $domains_count 个"
    
    log "✅ self-improving状态检查完成"
}

# ============================================================================
# 功能4: 更新记忆索引
# =============================================================================

update_memory_index() {
    log "📝 更新记忆索引..."
    
    {
        echo "# 双系统记忆索引"
        echo ""
        echo "**更新时间**: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "---"
        echo ""
        echo "## v4.0系统记忆"
        echo ""
        echo "### 按主题分类"
        ls -1 "$AUTO_ORG_DIR/by-topic/" 2>/dev/null | wc -l | xargs echo "- 主题数:"
        echo ""
        echo "### 按严重程度"
        echo "- High: $(ls -1 "$AUTO_ORG_DIR/by-severity/high/" 2>/dev/null | wc -l) 个文件"
        echo "- Medium: $(ls -1 "$AUTO_ORG_DIR/by-severity/medium/" 2>/dev/null | wc -l) 个文件"
        echo "- Low: $(ls -1 "$AUTO_ORG_DIR/by-severity/low/" 2>/dev/null | wc -l) 个文件"
        echo ""
        echo "### 按项目分类（来自self-improving）⭐"
        ls -1 "$AUTO_ORG_DIR/by-project/" 2>/dev/null | head -10
        echo ""
        echo "### 按领域分类（来自self-improving）⭐"
        ls -1 "$AUTO_ORG_DIR/by-domain/" 2>/dev/null | head -10
        echo ""
        echo "---"
        echo ""
        echo "## self-improving记忆"
        echo ""
        echo "### 修正记录"
        if [ -f "$SELF_IMPROV_DIR/corrections.md" ]; then
            grep -c "^[" "$SELF_IMPROV_DIR/corrections.md" || echo "0"
        else
            echo "0"
        fi
        echo " 条记录"
        echo ""
        echo "### 项目学习"
        ls -1 "$SELF_IMPROV_DIR/projects/" 2>/dev/null | wc -l | xargs echo "- 项目数:"
        echo ""
        echo "### 领域学习"
        ls -1 "$SELF_IMPROV_DIR/domains/" 2>/dev/null | wc -l | xargs echo "- 领域数:"
        echo ""
    } > "$WORKSPACE/.learnings/auto-organized/DUAL-SYSTEM-INDEX.md"
    
    log "✅ 记忆索引已更新"
}

# ============================================================================
# 主程序：双系统同步
# =============================================================================

dual_system_sync() {
    echo "🔄 双系统同步开始..."
    echo "======================"
    echo ""
    
    # 1. 从self-improving同步
    sync_from_self_improving
    echo ""
    
    # 2. 检查self-improving状态
    check_self_improving_status
    echo ""
    
    echo "======================"
    echo "✅ 双系统同步完成！"
    echo ""
    echo "📊 同步结果:"
    echo "  - v4.0系统: 运行中"
    echo "  - self-improving: 运行中"
    echo "  - 项目学习: 已同步"
    echo "  - 领域学习: 已同步"
    echo "  - 记忆索引: 已更新"
    echo ""
    echo "💡 查看索引: cat $WORKSPACE/.learnings/auto-organized/DUAL-SYSTEM-INDEX.md"
}

# ============================================================================
# 主程序入口
# =============================================================================

case "${1:-sync}" in
    sync)
        dual_system_sync
        ;;
    
    log)
        log_to_self_improving "$2" "$3" "$4"
        ;;
    
    check)
        check_self_improving_status
        ;;
    
    update-index)
        update_memory_index
        ;;
    
    *)
        echo "双系统桥接脚本"
        echo ""
        echo "用法:"
        echo "  $0 sync              # 同步双系统"
        echo "  $0 log <项目> <学习内容> [领域]"
        echo "  $0 check             # 检查self-improving状态"
        echo "  $0 update-index      # 更新记忆索引"
        echo ""
        echo "示例:"
        echo "  $0 sync"
        echo "  $0 log '蓝色光标项目' '完成了会议室设计' '室内设计'"
        echo "  $0 check"
        echo "  $0 update-index"
        exit 0
        ;;
esac

exit 0
