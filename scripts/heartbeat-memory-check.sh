#!/bin/bash
# =============================================================================
# 心跳记忆系统检查 - Heartbeat Memory Check
# =============================================================================
# 功能: 每次心跳时检查记忆系统健康状态
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
MEMORY_FILE="${MEMORY_FILE:-${MEMORY_DIR}/../MEMORY.md}"
ARCHIVE_DIR="${ARCHIVE_DIR:-${MEMORY_DIR}/archive}"
HEALTH_FILE="${HEALTH_FILE:-${MEMORY_DIR}/health-status.md}"
MAX_MEMORY_TOKENS="${MAX_MEMORY_TOKENS:-8000}"
MAX_LOG_AGE_HOURS="${MAX_LOG_AGE_HOURS:-48}"
MAX_CURRENT_LOGS="${MAX_CURRENT_LOGS:-50}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# 工具函数
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $@"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $@"
}

log_error() {
    echo -e "${RED}[✗]${NC} $@"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 获取文件 token 估算
get_file_tokens() {
    local file=$1
    if [ -f "$file" ]; then
        local chars=$(wc -c < "$file" 2>/dev/null || echo "0")
        echo $((chars / 2))
    else
        echo "0"
    fi
}

# 获取文件年龄（小时）
get_file_age_hours() {
    local file=$1
    if [ ! -f "$file" ]; then
        echo "9999"
        return
    fi

    local file_mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
    local current_time=$(date +%s)
    echo $(( (current_time - file_mtime) / 3600 ))
}

# 获取目录文件数量
count_files() {
    local dir=$1
    local pattern=${2:-*.md}
    find "$dir" -maxdepth 1 -name "$pattern" -type f 2>/dev/null | wc -l
}

# =============================================================================
# 检查函数
# =============================================================================

check_memory_md() {
    log_info "检查 MEMORY.md..."

    if [ ! -f "$MEMORY_FILE" ]; then
        log_error "MEMORY.md 不存在: $MEMORY_FILE"
        return 1
    fi

    local tokens=$(get_file_tokens "$MEMORY_FILE")
    local lines=$(wc -l < "$MEMORY_FILE" 2>/dev/null || echo "0")

    echo "  大小: $tokens tokens (约 $((tokens * 2)) 字符, $lines 行)"

    if [ $tokens -gt $MAX_MEMORY_TOKENS ]; then
        log_warning "MEMORY.md 过大！建议审计并清理"
        echo "  建议: 运行 bash scripts/audit-memory.sh"
        return 1
    fi

    log_success "MEMORY.md 大小正常"
    return 0
}

check_current_logs() {
    log_info "检查当前日志..."

    local count=$(count_files "$MEMORY_DIR" "*.md")
    # 排除 archive 目录
    count=$((count - 1))  # 减去 health-status.md

    echo "  数量: $count 个文件"

    if [ $count -gt $MAX_CURRENT_LOGS ]; then
        log_warning "日志文件过多！建议归档"
        echo "  建议: 运行 bash scripts/archive-old-logs.sh"
        return 1
    fi

    log_success "日志数量正常"
    return 0
}

check_archive() {
    log_info "检查归档..."

    if [ ! -d "$ARCHIVE_DIR" ]; then
        log_warning "归档目录不存在"
        echo "  建议: 运行 bash scripts/archive-old-logs.sh 创建归档"
        return 1
    fi

    local count=$(find "$ARCHIVE_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
    echo "  归档文件: $count 个"

    log_success "归档目录正常"
    return 0
}

check_latest_log() {
    log_info "检查最新日志..."

    # 优先检查今日日志
    local today_log="${MEMORY_DIR}/$(date +%Y-%m-%d).md"

    if [ -f "$today_log" ]; then
        local age_hours=$(get_file_age_hours "$today_log")
        local filename=$(basename "$today_log")

        echo "  最新: $filename"
        echo "  年龄: ${age_hours} 小时前"

        if [ $age_hours -gt $MAX_LOG_AGE_HOURS ]; then
            log_warning "今日日志超过 ${MAX_LOG_AGE_HOURS} 小时未更新"
            echo "  建议: 更新今日日志"
            return 1
        fi

        log_success "日志更新正常"
        return 0
    fi

    # 如果今日日志不存在，检查最新的日志文件
    local latest_log=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -type f ! -name "health-status.md" ! -name "cleanup-report.md" ! -name "audit-report.md" | sort -r | head -1)

    if [ -z "$latest_log" ]; then
        log_warning "没有找到日志文件"
        echo "  建议: 创建今日日志"
        return 1
    fi

    local age_hours=$(get_file_age_hours "$latest_log")
    local filename=$(basename "$latest_log")

    echo "  最新: $filename"
    echo "  年龄: ${age_hours} 小时前"

    if [ $age_hours -gt $MAX_LOG_AGE_HOURS ]; then
        log_warning "超过 ${MAX_LOG_AGE_HOURS} 小时未更新日志"
        echo "  建议: 创建今日日志"
        return 1
    fi

    log_success "日志更新正常"
    return 0
}

check_retain_format() {
    log_info "检查 Retain 格式..."

    # 优先检查今日日志
    local today_log="${MEMORY_DIR}/$(date +%Y-%m-%d).md"
    local check_log=""

    if [ -f "$today_log" ]; then
        check_log="$today_log"
    else
        # 检查最新的日志文件
        check_log=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -type f ! -name "health-status.md" ! -name "cleanup-report.md" ! -name "audit-report.md" | sort -r | head -1)
    fi

    if [ -z "$check_log" ] || [ ! -f "$check_log" ]; then
        log_warning "没有日志文件可检查"
        return 0
    fi

    local filename=$(basename "$check_log")
    echo "  检查文件: $filename"

    if grep -q "^## 🧠 Retain" "$check_log" 2>/dev/null; then
        local retain_count=$(grep -c "^- [WBO]" "$check_log" 2>/dev/null || echo "0")
        echo "  Retain 条目: $retain_count 个"

        if [ $retain_count -gt 0 ]; then
            log_success "使用 Retain 格式"
            return 0
        else
            log_warning "Retain 段落为空"
            return 1
        fi
    else
        log_warning "未使用 Retain 格式"
        echo "  建议: 在日志中添加 ## Retain 段落"
        return 1
    fi
}

check_duplicates() {
    log_info "检查重复发布..."

    # 检查最近 7 天的日志中是否有重复发布记录
    local recent_logs=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -type f -mtime -7 ! -name "health-status.md" ! -name "cleanup-report.md" ! -name "audit-report.md" 2>/dev/null)

    if [ -z "$recent_logs" ]; then
        log_success "无最近日志可检查"
        return 0
    fi

    # 检查是否有实际的重复发布事故（而不是技术讨论）
    local duplicate_incidents=0

    while IFS= read -r log_file; do
        # 检查是否有"重复发布"相关的事故记录
        if grep -qi "重复发布\|duplicate.*publish\|发了.*两次\|post.*twice" "$log_file" 2>/dev/null; then
            # 排除正常的讨论（如"避免重复"）
            if ! grep -qi "避免\|防止\|优化.*重复" "$log_file" 2>/dev/null; then
                duplicate_incidents=$((duplicate_incidents + 1))
            fi
        fi
    done <<< "$recent_logs"

    if [ $duplicate_incidents -gt 2 ]; then
        log_warning "检测到 $duplicate_incidents 次重复发布事故"
        echo "  建议: 审查发布机制，考虑使用发布锁"
        return 1
    fi

    log_success "无明显重复发布问题"
    return 0
}

# =============================================================================
# 报告生成
# =============================================================================

generate_summary() {
    # 从全局变量获取问题数量（在 main 中累积）
    # 这里只显示摘要，不重复计算

    echo ""
    echo "=========================================="
    log_info "记忆系统健康摘要"
    echo "=========================================="
    echo "所有检查已完成，详见上方输出"
    echo "=========================================="
}

save_health_status() {
    local memory_tokens=$(get_file_tokens "$MEMORY_FILE")
    local current_count=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -type f | wc -l)
    local archive_count=$(find "$ARCHIVE_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    local memory_status="正常"
    local logs_status="正常"

    [ $memory_tokens -gt $MAX_MEMORY_TOKENS ] && memory_status="过大"
    [ $current_count -gt $MAX_CURRENT_LOGS ] && logs_status="过多"

    cat > "$HEALTH_FILE" << EOF
# 记忆系统健康状态

**最后检查**: $timestamp
**检查间隔**: 每次心跳

---

## 📊 当前状态

| 指标 | 数值 | 状态 |
|------|------|------|
| MEMORY.md | $memory_tokens tokens | $( [ $memory_tokens -le $MAX_MEMORY_TOKENS ] && echo "✅ 正常" || echo "⚠️ 过大" ) |
| 当前日志 | $current_count 个 | $( [ $current_count -le $MAX_CURRENT_LOGS ] && echo "✅ 正常" || echo "⚠️ 过多" ) |
| 归档日志 | $archive_count 个 | ✅ 正常 |

---

## 📋 检查历史

$( [ -f "$HEALTH_FILE" ] && tail -n +20 "$HEALTH_FILE" 2>/dev/null || echo "首次检查" )

---

**检查工具**: \`scripts/heartbeat-memory-check.sh\`
**维护者**: 大领导 🎯
EOF

    log_success "健康状态已保存: $HEALTH_FILE"
}

# =============================================================================
# 主流程
# =============================================================================

main() {
    echo ""
    log_info "=========================================="
    log_info "记忆系统健康检查"
    log_info "=========================================="
    echo ""

    local issues=0

    # 执行所有检查
    check_memory_md || issues=$((issues + 1))
    echo ""
    check_current_logs || issues=$((issues + 1))
    echo ""
    check_archive || issues=$((issues + 1))
    echo ""
    check_latest_log || issues=$((issues + 1))
    echo ""
    check_retain_format || issues=$((issues + 1))
    echo ""
    check_duplicates || issues=$((issues + 1))
    echo ""

    # 生成摘要
    generate_summary

    # 保存健康状态
    save_health_status

    return $issues
}

# 运行主流程
main "$@"
