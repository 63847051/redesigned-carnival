#!/bin/bash
# =============================================================================
# Checkpoint - 创建快照
# =============================================================================
# 功能: 保存当前状态（文件、Git 状态、元数据）
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
LOG_FILE="${CHECKPOINTS_DIR}/logs/checkpoint.log"
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

log_message() {
    local message="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE"
}

# =============================================================================
# 核心函数
# =============================================================================

collect_files() {
    local include_patterns=("${FILE_PATTERNS[@]:-*.py *.sh *.md *.json}")

    # 使用 find 收集文件
    local files=()
    for pattern in "${include_patterns[@]}"; do
        while IFS= read -r file; do
            [ -f "$file" ] && files+=("$file")
        done < <(find "$WORKSPACE_DIR" -name "$pattern" -type f 2>/dev/null)
    done

    printf '%s\n' "${files[@]}"
}

calculate_hash() {
    local file="$1"
    sha256sum "$file" | awk '{print $1}'
}

get_file_info() {
    local file="$1"

    if [ ! -f "$file" ]; then
        return 1
    fi

    local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
    local hash=$(calculate_hash "$file")
    local modified=$(stat -c%Y "$file" 2>/dev/null || stat -f%m "$file")
    local modified_iso=$(date -d "@$modified" -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -r "$modified" -u +"%Y-%m-%dT%H:%M:%SZ")

    echo "$file|$size|$hash|$modified_iso"
}

get_git_info() {
    local git_dir="$1"

    if [ ! -d "$git_dir/.git" ]; then
        echo "{}"
        return
    fi

    cd "$git_dir"

    local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    local commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    local status=$(git status --porcelain 2>/dev/null | wc -l)

    local is_clean="false"
    if [ "$status" -eq 0 ]; then
        is_clean="true"
    fi

    cat << EOF
{
  "branch": "$branch",
  "commit": "$commit",
  "status": "$([ "$is_clean" = "true" ] && echo "clean" || echo "dirty")",
  "modifiedFiles": $status
}
EOF
}

create_metadata() {
    local checkpoint_id="$1"
    local message="$2"
    local tag="$3"
    shift 3
    local files=("$@")

    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local workspace="$WORKSPACE_DIR"
    local creator="大领导 🎯"

    # 收集文件信息
    local file_infos=()
    local total_size=0
    local languages=$(echo "{}" | jq '.')

    for file in "${files[@]}"; do
        local info=$(get_file_info "$file")
        IFS='|' read -r path size hash modified <<< "$info"

        file_infos+=("$info")

        ((total_size += size))

        # 统计语言
        local ext="${file##*.}"
        if [ -n "$ext" ] && [ "$ext" != "$file" ]; then
            languages=$(echo "$languages" | jq --arg ext "$ext" '. + {($ext): (.[$ext] // 0) + 1}')
        fi
    done

    # 获取 Git 信息
    local git_info=$(get_git_info "$workspace")

    # 生成 JSON
    cat << EOF
{
  "id": "$checkpoint_id",
  "timestamp": "$timestamp",
  "message": "$message",
  "tag": "$tag",
  "creator": "$creator",
  "workspace": "$workspace",
  "files": [
EOF

    local first=true
    for info in "${file_infos[@]}"; do
        IFS='|' read -r path size hash modified <<< "$info"

        # 转义路径
        path=$(echo "$path" | sed 's/"/\\"/g')

        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi

        printf '    {
      "path": "%s",
      "size": %s,
      "hash": "%s",
      "modified": "%s"
    }' "$path" "$size" "$hash" "$modified"
    done

    echo ""
    echo "  ],"
    echo "  \"git\": $git_info,"
    echo "  \"stats\": {"
    echo "    \"totalFiles\": ${#files[@]},"
    echo "    \"totalSize\": $total_size,"
    echo "    \"languages\": $languages"
    echo "  }"
    echo "}"
}

save_checkpoint() {
    local checkpoint_id="$1"
    local metadata="$2"
    local save_files="${3:-false}"

    # 保存元数据
    local meta_file="${META_DIR}/${checkpoint_id}.json"
    echo "$metadata" > "$meta_file"

    log_success "元数据已保存: $meta_file"

    # 可选：保存文件快照
    if [ "$save_files" = "true" ]; then
        local files_dir="${FILES_DIR}/${checkpoint_id}"
        mkdir -p "$files_dir"

        # 使用 rsync 保存文件
        while IFS= read -r file; do
            if [ -f "$file" ]; then
                local rel_path="${file#$WORKSPACE_DIR/}"
                local dest="${files_dir}/${rel_path}"
                mkdir -p "$(dirname "$dest")"
                cp "$file" "$dest"
            fi
        done < <(echo "$metadata" | jq -r '.files[].path')

        log_success "文件快照已保存: $files_dir"
    fi

    # 更新 latest 链接
    ln -sf "$meta_file" "$LATEST_LINK"

    # 记录日志
    log_message "CREATE $checkpoint_id: $message"
}

list_checkpoints() {
    if [ ! -d "$META_DIR" ]; then
        log_warning "未找到快照"
        return
    fi

    echo ""
    echo "📋 快照列表:"
    echo ""

    local checkpoints=($(ls -t "${META_DIR}"/checkpoint-*.json 2>/dev/null))

    if [ ${#checkpoints[@]} -eq 0 ]; then
        echo "  (无)"
        echo ""
        return
    fi

    for checkpoint in "${checkpoints[@]}"; do
        local id=$(basename "$checkpoint" .json)
        local timestamp=$(jq -r '.timestamp' "$checkpoint")
        local message=$(jq -r '.message' "$checkpoint")
        local tag=$(jq -r '.tag // ""' "$checkpoint")

        echo "  📸 $id"
        echo "     时间: $timestamp"
        echo "     描述: $message"
        if [ -n "$tag" ] && [ "$tag" != "null" ]; then
            echo "     标签: $tag"
        fi
        echo ""
    done
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 [选项]

选项:
  --message <msg>    快照描述
  --tag <tag>        添加标签
  --files <pattern>  文件模式（默认: *.py *.sh *.md *.json）
  --save-files       保存文件快照（占用更多空间）
  --list             列出所有快照
  --help             显示帮助

示例:
  # 创建快照
  $0 --message "完成基础架构"

  # 创建带标签的快照
  $0 --message "完成 API 设计" --tag "milestone"

  # 保存文件快照
  $0 --message "重要节点" --save-files

  # 列出所有快照
  $0 --list

EOF
}

main() {
    local message=""
    local tag=""
    local save_files=false
    local list_only=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --message)
                message="$2"
                shift 2
                ;;
            --tag)
                tag="$2"
                shift 2
                ;;
            --files)
                FILE_PATTERNS+=("$2")
                shift 2
                ;;
            --save-files)
                save_files=true
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
    log_info "Checkpoint - 创建快照"
    log_info "=========================================="
    echo ""

    # 创建目录
    mkdir -p "$META_DIR" "$FILES_DIR" "$(dirname "$LOG_FILE")"

    # 列出模式
    if [ "$list_only" = true ]; then
        list_checkpoints
        exit 0
    fi

    # 检查消息
    if [ -z "$message" ]; then
        log_error "请提供快照描述 (--message)"
        show_usage
        exit 1
    fi

    # 生成快照 ID
    local checkpoint_id="checkpoint-$(date +%Y%m%d-%H%M%S)"

    log_info "快照 ID: $checkpoint_id"
    log_info "描述: $message"
    if [ -n "$tag" ]; then
        log_info "标签: $tag"
    fi
    echo ""

    # 收集文件
    log_info "收集文件..."
    local files=()
    while IFS= read -r file; do
        [ -n "$file" ] && files+=("$file")
    done < <(collect_files)

    local count=${#files[@]}
    log_success "找到 $count 个文件"
    echo ""

    # 生成元数据
    log_info "生成元数据..."
    local metadata=$(create_metadata "$checkpoint_id" "$message" "$tag" "${files[@]}")

    # 保存快照
    log_info "保存快照..."
    save_checkpoint "$checkpoint_id" "$metadata" "$save_files"

    echo ""
    log_success "快照已创建: $checkpoint_id"
    echo ""

    # 显示统计
    echo "📊 统计信息:"
    echo "$metadata" | jq -r '.stats | "  文件数: \(.totalFiles)\n  大小: \(.totalSize) 字节\n  语言: \([.languages | to_entries[] | "\(.key): \(.value)"] | join(", "))"'
    echo ""
}

# =============================================================================
# 运行主流程
# =============================================================================

main "$@"
