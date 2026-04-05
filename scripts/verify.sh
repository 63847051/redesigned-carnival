#!/bin/bash
# =============================================================================
# Verify - 验证进度
# =============================================================================
# 功能: 对比快照，验证进度，生成报告
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

WORKSPACE_DIR="${WORKSPACE_DIR:-/root/.openclaw/workspace}"
CHECKPOINTS_DIR="${CHECKPOINTS_DIR:-${WORKSPACE_DIR}/.checkpoints}"
META_DIR="${CHECKPOINTS_DIR}/meta"
LATEST_LINK="${CHECKPOINTS_DIR}/latest"

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

collect_current_files() {
    local files=()
    while IFS= read -r file; do
        [ -f "$file" ] && files+=("$file")
    done < <(find "$WORKSPACE_DIR" -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.json" 2>/dev/null)

    printf '%s\n' "${files[@]}"
}

compare_files() {
    local baseline_file="$1"

    # 读取基线快照
    if [ ! -f "$baseline_file" ]; then
        log_error "快照不存在: $baseline_file"
        return 1
    fi

    local baseline_files=$(jq -r '.files[].path' "$baseline_file")
    local current_files=$(collect_current_files)

    # 找出新增文件
    echo ""
    echo "📄 文件变化:"
    echo ""

    # 新增文件
    echo "  ➕ 新增:"
    while IFS= read -r file; do
        if ! echo "$baseline_files" | grep -q "^$file$"; then
            local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
            echo "     + $file ($size 字节)"
        fi
    done <<< "$current_files"

    # 删除文件
    echo ""
    echo "  ➖ 删除:"
    while IFS= read -r file; do
        if ! echo "$current_files" | grep -q "^$file$"; then
            echo "     - $file"
        fi
    done <<< "$baseline_files"

    # 修改文件
    echo ""
    echo "  ~ 修改:"
    while IFS= read -r file; do
        if echo "$baseline_files" | grep -q "^$file$" && echo "$current_files" | grep -q "^$file$"; then
            local baseline_hash=$(jq -r ".files[] | select(.path == \"$file\") | .hash" "$baseline_file")
            local current_hash=$(sha256sum "$file" | awk '{print $1}')

            if [ "$baseline_hash" != "$current_hash" ]; then
                echo "     ~ $file (已修改)"
            fi
        fi
    done <<< "$current_files"

    echo ""
}

check_stats() {
    local baseline_file="$1"

    # 读取基线统计
    local baseline_count=$(jq -r '.stats.totalFiles' "$baseline_file")
    local baseline_size=$(jq -r '.stats.totalSize' "$baseline_file")

    # 当前统计
    local current_count=$(collect_current_files | wc -l)
    local current_size=0
    while IFS= read -r file; do
        [ -f "$file" ] && current_size=$((current_size + $(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")))
    done < <(collect_current_files)

    # 显示统计对比
    echo "📊 统计对比:"
    echo ""
    echo "  文件数:"
    echo "    基线: $baseline_count"
    echo "    当前: $current_count"
    echo "    变化: $((current_count - baseline_count))"
    echo ""
    echo "  文件大小:"
    echo "    基线: $baseline_size 字节"
    echo "    当前: $current_size 字节"
    echo "    变化: $((current_size - baseline_size)) 字节"
    echo ""
}

run_checks() {
    local baseline_file="$1"
    shift
    local check_items=("$@")

    if [ ${#check_items[@]} -eq 0 ]; then
        # 默认检查项
        check_items=("文件数量" "测试通过")
    fi

    echo "🔍 检查项:"
    echo ""

    for item in "${check_items[@]}"; do
        case "$item" in
            "文件数量")
                local baseline_count=$(jq -r '.stats.totalFiles' "$baseline_file")
                local current_count=$(collect_current_files | wc -l)

                if [ $current_count -ge $baseline_count ]; then
                    echo "  ✅ 文件数量: 符合预期 ($current_count >= $baseline_count)"
                else
                    echo "  ⚠️  文件数量: 低于预期 ($current_count < $baseline_count)"
                fi
                ;;
            "测试通过")
                if command -v pytest &>/dev/null; then
                    if pytest "$WORKSPACE_DIR" --quiet 2>/dev/null; then
                        echo "  ✅ 测试通过: 所有测试通过"
                    else
                        echo "  ⚠️  测试通过: 有测试失败"
                    fi
                else
                    echo "  ⏭️  测试通过: 未配置 pytest"
                fi
                ;;
            *)
                echo "  ❓ $item: 未知检查项"
                ;;
        esac
    done

    echo ""
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 [选项]

选项:
  --against <id>    对比指定快照
  --check <item>    检查项（可多次使用）
  --help            显示帮助

示例:
  # 验证当前进度（对比最新快照）
  $0

  # 对比指定快照
  $0 --against checkpoint-20260402-220000

  # 指定检查项
  $0 --check "文件数量" --check "测试通过"

EOF
}

main() {
    local baseline_file=""
    local check_items=()

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --against)
                local checkpoint_id="$2"
                baseline_file="${META_DIR}/${checkpoint_id}.json"
                shift 2
                ;;
            --check)
                check_items+=("$2")
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    echo ""
    log_info "=========================================="
    log_info "Verify - 验证进度"
    log_info "=========================================="
    echo ""

    # 如果未指定快照，使用最新快照
    if [ -z "$baseline_file" ]; then
        if [ -L "$LATEST_LINK" ]; then
            baseline_file=$(readlink -f "$LATEST_LINK")
            log_info "使用最新快照: $(basename "$baseline_file" .json)"
        else
            log_warning "未找到快照，无法对比"
            exit 0
        fi
    fi

    # 检查快照是否存在
    if [ ! -f "$baseline_file" ]; then
        log_error "快照不存在: $baseline_file"
        exit 1
    fi

    local checkpoint_id=$(basename "$baseline_file" .json)
    local timestamp=$(jq -r '.timestamp' "$baseline_file")
    local message=$(jq -r '.message' "$baseline_file")

    echo "📸 基线快照:"
    echo "  ID: $checkpoint_id"
    echo "  时间: $timestamp"
    echo "  描述: $message"
    echo ""

    # 对比文件
    compare_files "$baseline_file"

    # 检查统计
    check_stats "$baseline_file"

    # 运行检查项
    run_checks "$baseline_file" "${check_items[@]}"

    log_success "验证完成"
    echo ""
}

# =============================================================================
# 运行主流程
# =============================================================================

main "$@"
