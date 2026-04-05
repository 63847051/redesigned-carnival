#!/bin/bash
# =============================================================================
# Instinct Export - 导出个人经验
# =============================================================================
# 功能: 从 Retain 条目中提取规则和置信度，导出为 JSON 文件
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
OUTPUT_DIR="${OUTPUT_DIR:-${MEMORY_DIR}/../.instincts/export}"
TODAY=$(date +%Y-%m-%d)
OUTPUT_FILE="${OUTPUT_FILE:-${OUTPUT_DIR}/instincts-${TODAY}.json}"

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

extract_instincts() {
    local memory_file="$1"
    local instincts=()

    # 从 Retain 条目中提取 O 类型（观点偏好）
    while IFS= read -r line; do
        # 跳过空行和标题
        [[ -z "$line" ]] && continue
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ "$line" =~ ^-.*$ ]] || continue

        # 提取置信度
        local confidence=""
        if [[ "$line" =~ c=([0-9.]+) ]]; then
            confidence="${BASH_REMATCH[1]}"
        else
            confidence="0.5"  # 默认置信度
        fi

        # 提取规则内容
        local rule=$(echo "$line" | sed -E 's/^- O\(c=[0-9.]+\)? @[^:]+: (.*)/\1/p')

        # 提取分类
        local category=""
        if [[ "$line" =~ @([a-zA-Z_-]+): ]]; then
            category="${BASH_REMATCH[1]}"
        fi

        # 生成 ID
        local id="instinct-$(date +%s%N | head -c 6)"

        # 如果提取到了规则，添加到列表
        if [ -n "$rule" ]; then
            instincts+=("$id|$rule|$confidence|$category")
        fi
    done < "$memory_file"

    # 输出结果
    printf '%s\n' "${instincts[@]}"
}

generate_json() {
    local instincts_array=("$@")
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # 开始 JSON
    cat << EOF
{
  "version": "1.0",
  "exportedAt": "$timestamp",
  "exportedBy": "大领导 🎯",
  "source": "memory/${TODAY}.md",
  "instincts": [
EOF

    # 添加每个 instinct
    local first=true
    for instinct in "${instincts_array[@]}"; do
        IFS='|' read -r id rule confidence category <<< "$instinct"

        # 转义 JSON 字符
        rule=$(echo "$rule" | sed 's/"/\\"/g')

        # 添加逗号（除了第一个）
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi

        # 输出 instinct
        printf '    {
      "id": "%s",
      "rule": "%s",
      "confidence": %s,
      "source": "retain",
      "learnedAt": "%s",
      "category": "%s",
      "tags": [%s]
    }' \
            "$id" \
            "$rule" \
            "$confidence" \
            "$timestamp" \
            "$category" \
            "\"$category\""
    done

    # 结束 JSON
    echo ""
    echo "  ]"
    echo "}"
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 [选项]

选项:
  --file <path>     指定记忆文件（默认: 今天）
  --output <path>   指定输出文件
  --help            显示帮助

示例:
  # 导出今天的 Retain 条目
  $0

  # 导出指定文件
  $0 --file /root/.openclaw/workspace/memory/2026-04-01.md

  # 指定输出文件
  $0 --output my-instincts.json

EOF
}

main() {
    local memory_file="${MEMORY_DIR}/${TODAY}.md"

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --file)
                memory_file="$2"
                shift 2
                ;;
            --output)
                OUTPUT_FILE="$2"
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
    log_info "Instinct Export - 导出个人经验"
    log_info "=========================================="
    echo ""

    # 检查记忆文件
    if [ ! -f "$memory_file" ]; then
        log_error "记忆文件不存在: $memory_file"
        exit 1
    fi

    log_info "读取记忆: $memory_file"

    # 创建输出目录
    mkdir -p "$OUTPUT_DIR"

    # 提取 instincts
    log_info "提取 Retain 条目..."
    local instincts=()
    while IFS= read -r line; do
        [ -n "$line" ] && instincts+=("$line")
    done < <(extract_instincts "$memory_file")

    local count=${#instincts[@]}

    if [ $count -eq 0 ]; then
        log_warning "未找到 Retain 条目"
        exit 0
    fi

    log_success "找到 $count 条规则"

    # 生成 JSON
    log_info "生成 JSON..."
    local json_output=$(generate_json "${instincts[@]}")

    # 保存到文件
    echo "$json_output" > "$OUTPUT_FILE"

    log_success "导出完成: $OUTPUT_FILE"
    echo ""

    # 统计信息
    local high_conf=0
    local med_conf=0
    local low_conf=0

    for instinct in "${instincts[@]}"; do
        IFS='|' read -r id rule confidence category <<< "$instinct"
        conf=$(echo "$confidence" | awk '{printf "%.0f", $1}')

        if [ "$conf" -ge 7 ]; then
            ((high_conf++))
        elif [ "$conf" -ge 5 ]; then
            ((med_conf++))
        else
            ((low_conf++))
        fi
    done

    echo "📊 统计信息:"
    echo "  总数: $count"
    echo "  高置信度 (0.7-1.0): $high_conf"
    echo "  中置信度 (0.5-0.7): $med_conf"
    echo "  低置信度 (0.0-0.5): $low_conf"
    echo ""
}

# =============================================================================
# 运行主流程
# =============================================================================

main "$@"
