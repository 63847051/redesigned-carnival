#!/bin/bash
# =============================================================================
# WAL 验证工具 - WAL Verification Tool
# =============================================================================
# 功能: 验证文件写入是否成功，确保 WAL 协议正确执行
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
SESSION_STATE="${SESSION_STATE:-${MEMORY_DIR}/../SESSION-STATE.md}"
VERBOSE="${VERBOSE:-false}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 验证结果
VERIFY_SUCCESS=0
VERIFY_FAILED=1

# =============================================================================
# 工具函数
# =============================================================================

log_debug() {
    if [ "$VERBOSE" = "true" ]; then
        echo -e "${BLUE}[DEBUG]${NC} $@" >&2
    fi
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@" >&2
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $@" >&2
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $@" >&2
}

log_error() {
    echo -e "${RED}[✗]${NC} $@" >&2
}

# =============================================================================
# 验证函数
# =============================================================================

verify_file_exists() {
    local file=$1

    log_debug "检查文件存在: $file"

    if [ ! -f "$file" ]; then
        log_error "文件不存在: $file"
        return $VERIFY_FAILED
    fi

    log_debug "文件存在"
    return $VERIFY_SUCCESS
}

verify_file_not_empty() {
    local file=$1

    log_debug "检查文件非空: $file"

    if [ ! -s "$file" ]; then
        log_error "文件为空: $file"
        return $VERIFY_FAILED
    fi

    local size=$(wc -c < "$file")
    log_debug "文件大小: $size 字节"
    return $VERIFY_SUCCESS
}

verify_content_written() {
    local file=$1
    local content=$2

    log_debug "检查内容写入: $file"

    if [ -z "$content" ]; then
        log_debug "无内容需要验证"
        return $VERIFY_SUCCESS
    fi

    # 检查内容是否在文件中
    if ! grep -q "$content" "$file" 2>/dev/null; then
        log_error "内容未写入文件: $content"
        return $VERIFY_FAILED
    fi

    log_debug "内容已写入"
    return $VERIFY_SUCCESS
}

verify_retain_format() {
    local file=$1

    log_debug "检查 Retain 格式: $file"

    # 检查是否有 Retain 段落
    if ! grep -q "^## 🧠 Retain" "$file" 2>/dev/null; then
        log_warning "未找到 Retain 段落"
        return $VERIFY_FAILED
    fi

    # 检查是否有 Retain 条目
    if ! grep -q "^- [WBO]" "$file" 2>/dev/null; then
        log_warning "未找到 Retain 条目"
        return $VERIFY_FAILED
    fi

    # 统计条目数量
    local retain_count=$(grep -c "^- [WBO]" "$file" 2>/dev/null || echo "0")
    log_debug "Retain 条目数: $retain_count"

    if [ $retain_count -eq 0 ]; then
        log_warning "Retain 条目为空"
        return $VERIFY_FAILED
    fi

    log_debug "Retain 格式正常"
    return $VERIFY_SUCCESS
}

verify_timestamp() {
    local file=$1
    local max_age_minutes=${2:-60}

    log_debug "检查时间戳: $file"

    if [ ! -f "$file" ]; then
        log_error "文件不存在"
        return $VERIFY_FAILED
    fi

    local file_mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
    local current_time=$(date +%s)
    local age_minutes=$(( (current_time - file_mtime) / 60 ))

    log_debug "文件年龄: ${age_minutes} 分钟"

    if [ $age_minutes -gt $max_age_minutes ]; then
        log_error "文件超过 ${max_age_minutes} 分钟未更新"
        return $VERIFY_FAILED
    fi

    log_debug "时间戳正常"
    return $VERIFY_SUCCESS
}

verify_session_state() {
    log_debug "检查 SESSION-STATE.md"

    if [ ! -f "$SESSION_STATE" ]; then
        log_warning "SESSION-STATE.md 不存在"
        return $VERIFY_FAILED
    fi

    # 检查是否有当前任务
    if ! grep -q "^## 当前任务" "$SESSION_STATE" 2>/dev/null; then
        log_warning "SESSION-STATE.md 缺少当前任务"
        return $VERIFY_FAILED
    fi

    log_debug "SESSION-STATE.md 正常"
    return $VERIFY_SUCCESS
}

# =============================================================================
# 综合验证
# =============================================================================

verify_memory_update() {
    local file=$1
    local content=${2:-}
    local check_retain=${3:-true}

    log_info "验证记忆更新: $file"

    local failed=0

    # 基础检查
    verify_file_exists "$file" || failed=1
    verify_file_not_empty "$file" || failed=1

    # 内容检查
    if [ -n "$content" ]; then
        verify_content_written "$file" "$content" || failed=1
    fi

    # Retain 格式检查
    if [ "$check_retain" = "true" ]; then
        # 检查是否是今日日志
        if [[ "$file" =~ memory/[0-9]{4}-[0-9]{2}-[0-9]{2}\.md ]]; then
            verify_retain_format "$file" || failed=1
        fi
    fi

    if [ $failed -eq 0 ]; then
        log_success "记忆更新验证通过"
        return $VERIFY_SUCCESS
    else
        log_error "记忆更新验证失败"
        return $VERIFY_FAILED
    fi
}

verify_all() {
    log_info "全面验证 WAL 协议"

    local failed=0

    # 验证 SESSION-STATE.md
    verify_session_state || failed=1

    # 验证今日日志
    local today_log="${MEMORY_DIR}/$(date +%Y-%m-%d).md"
    if [ -f "$today_log" ]; then
        verify_memory_update "$today_log" "" true || failed=1
    fi

    # 验证 MEMORY.md
    local memory_md="${MEMORY_DIR}/../MEMORY.md"
    if [ -f "$memory_md" ]; then
        verify_file_exists "$memory_md" || failed=1
        verify_file_not_empty "$memory_md" || failed=1
    fi

    if [ $failed -eq 0 ]; then
        log_success "WAL 协议验证全部通过"
        return $VERIFY_SUCCESS
    else
        log_error "WAL 协议验证失败"
        return $VERIFY_FAILED
    fi
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 [选项] <命令> [参数]

命令:
  file <文件> [内容]     验证文件写入
  retain <文件>          验证 Retain 格式
  timestamp <文件> [分钟] 验证时间戳（默认 60 分钟）
  session               验证 SESSION-STATE.md
  all                   全面验证 WAL 协议
  help                  显示帮助

选项:
  -v, --verbose         详细输出
  -q, --quiet           静默模式（仅返回退出码）

示例:
  $0 file memory/2026-04-02.md "关键内容"
  $0 retain memory/2026-04-02.md
  $0 timestamp memory/2026-04-02.md 120
  $0 session
  $0 all

退出码:
  0 - 验证通过
  1 - 验证失败

EOF
}

main() {
    local command=""
    local quiet_mode=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -q|--quiet)
                quiet_mode=true
                shift
                ;;
            file|retain|timestamp|session|all|help)
                command=$1
                shift
                break
                ;;
            *)
                log_error "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # 执行命令
    local result=$VERIFY_SUCCESS

    case $command in
        file)
            if [ $# -lt 1 ]; then
                log_error "缺少文件参数"
                show_usage
                exit 1
            fi
            verify_memory_update "$1" "${2:-}" false
            result=$?
            ;;
        retain)
            if [ $# -lt 1 ]; then
                log_error "缺少文件参数"
                show_usage
                exit 1
            fi
            verify_retain_format "$1"
            result=$?
            ;;
        timestamp)
            if [ $# -lt 1 ]; then
                log_error "缺少文件参数"
                show_usage
                exit 1
            fi
            verify_timestamp "$1" "${2:-60}"
            result=$?
            ;;
        session)
            verify_session_state
            result=$?
            ;;
        all)
            verify_all
            result=$?
            ;;
        help|"")
            show_usage
            exit 0
            ;;
        *)
            log_error "未知命令: $command"
            show_usage
            exit 1
            ;;
    esac

    # 输出结果
    if [ "$quiet_mode" = "false" ]; then
        if [ $result -eq $VERIFY_SUCCESS ]; then
            echo "✅ PASS"
        else
            echo "❌ FAIL"
        fi
    fi

    exit $result
}

main "$@"
