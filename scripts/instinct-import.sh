#!/bin/bash
# =============================================================================
# Instinct Import - 导入团队经验
# =============================================================================
# 功能: 从 JSON 文件导入 Instincts，合并到记忆文件
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
TODAY=$(date +%Y-%m-%d)
MEMORY_FILE="${MEMORY_FILE:-${MEMORY_DIR}/${TODAY}.md}"

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

# =============================================================================
# 核心函数
# =============================================================================

read_json() {
    local json_file="$1"

    # 使用 Python 读取 JSON（更可靠）
    python3 -c "
import json
import sys

with open('$json_file', 'r') as f:
    data = json.load(f)
    instincts = data.get('instincts', [])

for instinct in instincts:
    rule = instinct.get('rule', '')
    confidence = instinct.get('confidence', 0.5)
    category = instinct.get('category', '')

    # 格式化为 Retain 条目
    if confidence >= 0.7:
        print(f'- O(c={confidence}) @{category}: {rule}')
    elif confidence >= 0.5:
        print(f'- O(c={confidence}) @{category}: {rule}')
    else:
        print(f'- O(c={confidence}) @{category}: {rule}')
"
}

append_to_memory() {
    local retain_entries="$1"
    local memory_file="$2"

    # 检查文件是否存在
    if [ ! -f "$memory_file" ]; then
        log_error "记忆文件不存在: $memory_file"
        return 1
    fi

    # 创建临时文件
    local tmp_file=$(mktemp)

    # 读取原文件内容
    cat "$memory_file" > "$tmp_file"

    # 追加新的 Retain 条目
    echo "" >> "$tmp_file"
    echo "## 📥 导入的团队经验" >> "$tmp_file"
    echo "" >> "$tmp_file"
    echo "**导入时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$tmp_file"
    echo "" >> "$tmp_file"
    echo "$retain_entries" >> "$tmp_file"

    # 替换原文件
    mv "$tmp_file" "$memory_file"

    log_success "已追加到: $memory_file"
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 <JSON文件> [选项]

选项:
  --file <path>     指定记忆文件（默认: 今天）
  --dry-run         只显示不写入
  --help            显示帮助

示例:
  # 导入团队经验
  $0 team-instincts.json

  # 导入到指定文件
  $0 team-instincts.json --file /root/.openclaw/workspace/memory/2026-04-01.md

  # 预览（不写入）
  $0 team-instincts.json --dry-run

EOF
}

main() {
    local json_file=""
    local dry_run=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --file)
                MEMORY_FILE="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            -*)
                log_error "未知参数: $1"
                show_usage
                exit 1
                ;;
            *)
                json_file="$1"
                shift
                ;;
        esac
    done

    # 检查 JSON 文件
    if [ -z "$json_file" ]; then
        log_error "请指定 JSON 文件"
        show_usage
        exit 1
    fi

    if [ ! -f "$json_file" ]; then
        log_error "JSON 文件不存在: $json_file"
        exit 1
    fi

    echo ""
    log_info "=========================================="
    log_info "Instinct Import - 导入团队经验"
    log_info "=========================================="
    echo ""

    log_info "读取 JSON: $json_file"

    # 读取并转换 JSON
    log_info "转换 JSON 为 Retain 格式..."
    local retain_entries=$(read_json "$json_file")

    # 统计条目数
    local count=$(echo "$retain_entries" | grep -c "^- O" || true)

    if [ $count -eq 0 ]; then
        log_warning "未找到 Instincts"
        exit 0
    fi

    log_success "找到 $count 条规则"
    echo ""

    # 显示预览
    echo "📄 预览（前 5 条）:"
    echo "$retain_entries" | head -5
    echo ""

    # Dry run 模式
    if [ "$dry_run" = true ]; then
        log_warning "Dry run 模式，未写入文件"
        exit 0
    fi

    # 追加到记忆文件
    log_info "追加到记忆文件..."
    append_to_memory "$retain_entries" "$MEMORY_FILE"

    echo ""
    log_success "导入完成！"
    echo ""
    echo "📊 统计信息:"
    echo "  导入: $count 条"
    echo "  文件: $MEMORY_FILE"
    echo ""
}

# =============================================================================
# 运行主流程
# =============================================================================

main "$@"
