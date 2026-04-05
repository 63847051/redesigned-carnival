#!/bin/bash
# =============================================================================
# Rollback - 回滚到快照
# =============================================================================
# 功能: 恢复到指定快照，支持软回滚和强制回滚
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
FILES_DIR="${CHECKPOINTS_DIR}/files"

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

confirm() {
    local prompt="$1"
    local response

    echo -n "$prompt [y/N] "
    read -r response

    [[ "$response" =~ ^[Yy]$ ]]
}

# =============================================================================
# 核心函数
# =============================================================================

show_checkpoint_info() {
    local checkpoint_file="$1"

    local checkpoint_id=$(basename "$checkpoint_file" .json)
    local timestamp=$(jq -r '.timestamp' "$checkpoint_file")
    local message=$(jq -r '.message' "$checkpoint_file")
    local tag=$(jq -r '.tag // ""' "$checkpoint_file")
    local total_files=$(jq -r '.stats.totalFiles' "$checkpoint_file")
    local total_size=$(jq -r '.stats.totalSize' "$checkpoint_file")

    echo ""
    echo "📸 快照信息:"
    echo "  ID: $checkpoint_id"
    echo "  时间: $timestamp"
    echo "  描述: $message"
    if [ -n "$tag" ] && [ "$tag" != "null" ]; then
        echo "  标签: $tag"
    fi
    echo "  文件: $total_files 个"
    echo "  大小: $total_size 字节"
    echo ""
}

show_changes() {
    local checkpoint_file="$1"

    local checkpoint_files=$(jq -r '.files[].path' "$checkpoint_file")
    local current_files=$(find "$WORKSPACE_DIR" -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.json" 2>/dev/null)

    local added=0
    local removed=0
    local modified=0

    # 统计变化
    while IFS= read -r file; do
        if ! echo "$checkpoint_files" | grep -q "^$file$"; then
            ((added++))
        fi
    done <<< "$current_files"

    while IFS= read -r file; do
        if ! echo "$current_files" | grep -q "^$file$"; then
            ((removed++))
        fi
    done <<< "$checkpoint_files"

    while IFS= read -r file; do
        if echo "$checkpoint_files" | grep -q "^$file$" && echo "$current_files" | grep -q "^$file$"; then
            local checkpoint_hash=$(jq -r ".files[] | select(.path == \"$file\") | .hash" "$checkpoint_file")
            local current_hash=$(sha256sum "$file" | awk '{print $1}')

            if [ "$checkpoint_hash" != "$current_hash" ]; then
                ((modified++))
            fi
        fi
    done <<< "$checkpoint_files"

    echo "📊 变化预览:"
    echo "  ➕ 新增: $added 个文件"
    echo "  ➖ 删除: $removed 个文件"
    echo "  ~ 修改: $modified 个文件"
    echo ""
}

rollback_git() {
    local checkpoint_file="$1"

    # 检查是否有 Git
    if [ ! -d "$WORKSPACE_DIR/.git" ]; then
        log_warning "未找到 Git，跳过 Git 回滚"
        return 0
    fi

    local commit=$(jq -r '.git.commit' "$checkpoint_file")

    if [ "$commit" = "unknown" ]; then
        log_warning "快照中没有 Git 提交信息，跳过 Git 回滚"
        return 0
    fi

    log_info "回滚 Git 到: $commit"

    cd "$WORKSPACE_DIR"

    # 重置到指定提交
    git reset --hard "$commit" 2>/dev/null || {
        log_error "Git 回滚失败"
        return 1
    }

    log_success "Git 回滚完成"
}

rollback_files() {
    local checkpoint_id="$1"
    local files_dir="${FILES_DIR}/${checkpoint_id}"

    # 检查是否有文件快照
    if [ ! -d "$files_dir" ]; then
        log_warning "未找到文件快照，跳过文件回滚"
        return 0
    fi

    log_info "回滚文件..."

    # 使用 rsync 恢复文件
    rsync -av --delete "$files_dir/" "$WORKSPACE_DIR/" 2>/dev/null || {
        log_error "文件回滚失败"
        return 1
    }

    log_success "文件回滚完成"
}

perform_rollback() {
    local checkpoint_id="$1"
    local soft_rollback="$2"
    local force_rollback="$3"

    local checkpoint_file="${META_DIR}/${checkpoint_id}.json"

    # 检查快照是否存在
    if [ ! -f "$checkpoint_file" ]; then
        log_error "快照不存在: $checkpoint_id"
        return 1
    fi

    # 显示快照信息
    show_checkpoint_info "$checkpoint_file"

    # 显示变化预览
    show_changes "$checkpoint_file"

    # 确认回滚
    if [ "$force_rollback" != "true" ]; then
        if ! confirm "确认回滚到这个快照？"; then
            log_warning "回滚已取消"
            return 0
        fi
    fi

    echo ""
    log_info "开始回滚..."
    echo ""

    # Git 回滚
    rollback_git "$checkpoint_file"

    # 文件回滚（如果有快照）
    if [ "$soft_rollback" != "true" ]; then
        rollback_files "$checkpoint_id"
    fi

    echo ""
    log_success "回滚完成"
    echo ""
}

list_checkpoints() {
    if [ ! -d "$META_DIR" ]; then
        log_warning "未找到快照"
        return
    fi

    echo ""
    echo "📋 可用快照:"
    echo ""

    local checkpoints=($(ls -t "${META_DIR}"/checkpoint-*.json 2>/dev/null))

    if [ ${#checkpoints[@]} -eq 0 ]; then
        echo "  (无)"
        echo ""
        return
    fi

    local index=1
    for checkpoint in "${checkpoints[@]}"; do
        local id=$(basename "$checkpoint" .json)
        local timestamp=$(jq -r '.timestamp' "$checkpoint")
        local message=$(jq -r '.message' "$checkpoint")

        echo "  [$index] $id"
        echo "      $timestamp"
        echo "      $message"
        echo ""

        ((index++))
    done
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 [选项]

选项:
  --to <id>         回滚到指定快照
  --soft            软回滚（保留当前文件）
  --force           强制回滚（不确认）
  --list            列出所有快照
  --help            显示帮助

示例:
  # 回滚到指定快照
  $0 --to checkpoint-20260402-220000

  # 软回滚（保留当前文件）
  $0 --to checkpoint-20260402-220000 --soft

  # 强制回滚（不确认）
  $0 --to checkpoint-20260402-220000 --force

  # 列出所有快照
  $0 --list

EOF
}

main() {
    local checkpoint_id=""
    local soft_rollback=false
    local force_rollback=false
    local list_only=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --to)
                checkpoint_id="$2"
                shift 2
                ;;
            --soft)
                soft_rollback=true
                shift
                ;;
            --force)
                force_rollback=true
                shift
                ;;
            --list)
                list_only=true
                shift
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
    log_info "Rollback - 回滚到快照"
    log_info "=========================================="
    echo ""

    # 列出模式
    if [ "$list_only" = true ]; then
        list_checkpoints
        exit 0
    fi

    # 检查快照 ID
    if [ -z "$checkpoint_id" ]; then
        log_error "请指定快照 ID (--to)"
        show_usage
        exit 1
    fi

    # 执行回滚
    perform_rollback "$checkpoint_id" "$soft_rollback" "$force_rollback"
}

# =============================================================================
# 运行主流程
# =============================================================================

main "$@"
