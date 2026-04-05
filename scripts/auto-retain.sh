#!/bin/bash
# =============================================================================
# Retain 自动提取包装脚本 - Auto Retain Wrapper
# =============================================================================
# 功能: 便捷调用 Python 提取脚本，支持多种输入方式
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRACT_SCRIPT="${SCRIPT_DIR}/extract-retain.py"
MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
TODAY_LOG="${MEMORY_DIR}/$(date +%Y-%m-%d).md"
APPEND_TO_LOG="${APPEND_TO_LOG:-true}"

# 颜色输出
GREEN='\033[0;32m'
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

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 [选项] <输入>

输入方式:
  <文本>              直接提供文本内容
  -                   从标准输入读取
  <文件路径>           从文件读取内容

选项:
  -a, --append        追加到今日日志（默认）
  -n, --no-append     不追加到日志，仅输出
  -h, --help          显示帮助

示例:
  # 直接提供文本
  $0 "飞书不支持 img 标签"

  # 从标准输入
  echo "完成了脚本创建" | $0 -

  # 从文件读取
  $0 conversation.txt

  # 仅输出，不追加
  $0 -n "完成了任务"

EOF
}

main() {
    local append_mode=true

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--append)
                append_mode=true
                shift
                ;;
            -n|--no-append)
                append_mode=false
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done

    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi

    # 调用 Python 脚本提取
    local retain_content
    retain_content=$(python3 "$EXTRACT_SCRIPT" "$@")

    # 输出到标准输出
    echo "$retain_content"

    # 追加到今日日志
    if [ "$append_mode" = "true" ]; then
        log_info "追加到今日日志: $TODAY_LOG"

        # 确保日志文件存在
        if [ ! -f "$TODAY_LOG" ]; then
            log_info "创建今日日志"
            touch "$TODAY_LOG"
        fi

        # 追加内容
        echo "" >> "$TODAY_LOG"
        echo "$retain_content" >> "$TODAY_LOG"

        # 验证
        if [ -x "${SCRIPT_DIR}/wal-verify.sh" ]; then
            if "${SCRIPT_DIR}/wal-verify.sh" -q retain "$TODAY_LOG" 2>/dev/null; then
                log_success "Retain 条目已追加并验证通过"
            else
                log_info "Retain 条目已追加（格式验证失败，但可能正常）"
            fi
        else
            log_success "Retain 条目已追加"
        fi
    fi
}

main "$@"
