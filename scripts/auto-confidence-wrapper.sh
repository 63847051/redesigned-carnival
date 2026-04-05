#!/bin/bash
# =============================================================================
# 自动置信度计算包装脚本 - Auto Confidence Wrapper
# =============================================================================
# 功能: 从今日日志中提取 O 类型条目，自动计算置信度
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
TODAY_LOG="${MEMORY_DIR}/$(date +%Y-%m-%d).md"
AUTO_CONFIDENCE_SCRIPT="${MEMORY_DIR}/../scripts/auto-confidence.py"

# =============================================================================
# 工具函数
# =============================================================================

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $@"
}

log_success() {
    echo -e "\033[0;32m[✓]\033[0m $@"
}

log_error() {
    echo -e "\033[0;31m[✗]\033[0m $@"
}

# =============================================================================
# 提取 Retain 条目
# =============================================================================

extract_retain_entries() {
    local log_file=$1

    if [ ! -f "$log_file" ]; then
        log_error "日志文件不存在: $log_file"
        return 1
    fi

    # 提取 O 类型的 Retain 条目
    grep "^- O" "$log_file" || echo ""
}

# =============================================================================
# 转换为 JSON 格式
# =============================================================================

convert_to_json() {
    local retain_text=$1

    echo "$retain_text" | while IFS= read -r line; do
        # 解析: - O(c=0.9) @领域: 内容
        if [[ $line =~ ^-O\(c=([0-9.]+)\)?@([[:alnum:]]+):\ (.+)$ ]]; then
            local confidence="${BASH_REMATCH[1]}"
            local domain="${BASH_REMATCH[2]}"
            local content="${BASH_REMATCH[3]}"

            # 如果没有置信度，设为 null
            if [ -z "$confidence" ]; then
                confidence="null"
            fi

            # 输出 JSON
            cat << EOF
{
  "type": "O",
  "domain": "$domain",
  "content": "$content",
  "confidence": $confidence
},
EOF
        fi
    done | sed '$ s/,$//' # 移除最后一个逗号
}

# =============================================================================
# 主流程
# =============================================================================

main() {
    log_info "自动置信度计算"
    echo ""

    # 提取 Retain 条目
    local retain_text
    retain_text=$(extract_retain_entries "$TODAY_LOG")

    if [ -z "$retain_text" ]; then
        log_error "今日日志中没有找到 O 类型条目"
        return 1
    fi

    log_info "找到 O 类型条目，正在分析..."

    # 转换为 JSON
    local retain_json
    retain_json=$(convert_to_json "$retain_text")

    # 添加数组包装
    retain_json="[$retain_json]"

    # 调用 Python 脚本计算置信度
    local results
    results=$(python3 "$AUTO_CONFIDENCE_SCRIPT" "$retain_json")

    # 输出结果
    echo ""
    log_success "分析完成："
    echo ""
    echo "$results" | python3 -m json.tool
}

main "$@"
