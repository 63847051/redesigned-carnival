#!/bin/bash
# =============================================================================
# 简化版记忆搜索 - Simple Memory Search
# =============================================================================
# 功能: 使用 grep 进行本地全文搜索，不依赖外部 API
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
MEMORY_FILE="${MEMORY_DIR}/MEMORY.md"
MAX_RESULTS="${MAX_RESULTS:-20}"

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

log_error() {
    echo -e "${RED}[✗]${NC} $@"
}

# =============================================================================
# 搜索函数
# =============================================================================

search_memory() {
    local query="$1"
    local case_sensitive="${2:-insensitive}"

    log_info "🔍 搜索记忆: $query"
    echo ""

    local grep_opts="-r"
    if [ "$case_sensitive" = "insensitive" ]; then
        grep_opts="-ri"
    else
        grep_opts="-r"
    fi

    # 搜索 MEMORY.md
    if [ -f "$MEMORY_FILE" ]; then
        echo "📄 MEMORY.md:"
        grep $grep_opts "$query" "$MEMORY_FILE" | head -5 || echo "  (未找到)"
        echo ""
    fi

    # 搜索最近的日志（前 10 个）
    local recent_logs=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -type f ! -name "health-status.md" ! -name "cleanup-report.md" ! -name "audit-report.md" | sort -r | head -10)

    if [ -n "$recent_logs" ]; then
        echo "📝 最近日志:"
        for log_file in $recent_logs; do
            local filename=$(basename "$log_file")
            local matches=$(grep $grep_opts "$query" "$log_file" | head -3)
            if [ -n "$matches" ]; then
                echo "  $filename:"
                echo "$matches" | sed 's/^/    /'
            fi
        done
    fi

    echo ""
    log_success "搜索完成"
    echo ""
    echo "💡 提示："
    echo "  - 搜索区分大小写: $0 <query>"
    echo "  - 搜索特定文件: grep <query> <文件路径>"
    echo "  - 正则表达式: grep -E <pattern> <路径>"
}

# =============================================================================
# 主流程
# =============================================================================

main() {
    local query="${1:-}"
    local case_sensitive="insensitive"

    if [ -z "$query" ]; then
        echo "使用方法: $0 <搜索关键词> [case-sensitive]"
        echo ""
        echo "示例:"
        echo "  $0 Retain"
        echo "  $0 Retain case-sensitive"
        echo "  $0 \"先画拓扑图\""
        exit 0
    fi

    if [ "${2:-}" = "case-sensitive" ]; then
        case_sensitive="sensitive"
    fi

    search_memory "$query" "$case_sensitive"
}

main "$@"
