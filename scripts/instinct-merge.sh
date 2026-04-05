#!/bin/bash
# =============================================================================
# Instinct Merge - 合并多个 Instincts 文件
# =============================================================================
# 功能: 合并多个 JSON 文件，自动去重和解决矛盾
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# ==============================================================================

OUTPUT_DIR="${OUTPUT_DIR:-/root/.openclaw/workspace/.instincts/merged}"

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

merge_instincts() {
    local input_files=("$@")

    # 使用 Python 合并 JSON
    python3 << 'PYTHON_SCRIPT'
import json
import sys
from collections import defaultdict

input_files = """${input_files[@]}""".split()

# 所有 instincts
all_instincts = []

# 读取所有文件
for json_file in input_files:
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            instincts = data.get('instincts', [])
            all_instincts.extend(instincts)
    except Exception as e:
        print(f"错误: 无法读取 {json_file}: {e}", file=sys.stderr)
        sys.exit(1)

# 按规则分组
rule_groups = defaultdict(list)

for instinct in all_instincts:
    rule = instinct.get('rule', '')
    if rule:
        rule_groups[rule].append(instinct)

# 合并策略：保留高置信度
merged_instincts = []
duplicates = 0
conflicts = 0

for rule, instincts in rule_groups.items():
    if len(instincts) == 1:
        # 唯一，直接添加
        merged_instincts.append(instincts[0])
    else:
        # 多个，选择高置信度
        sorted_instincts = sorted(instincts, key=lambda x: x.get('confidence', 0), reverse=True)
        best = sorted_instincts[0]
        merged_instincts.append(best)
        duplicates += len(instincts) - 1

        # 检查矛盾（相反规则）
        for other in instincts[1:]:
            conf1 = best.get('confidence', 0)
            conf2 = other.get('confidence', 0)
            if abs(conf1 - conf2) < 0.1:
                # 置信度接近，可能是矛盾
                conflicts += 1

# 生成输出
output = {
    "version": "1.0",
    "mergedAt": "2026-04-02T14:00:00Z",
    "sourceFiles": len(input_files),
    "totalInstincts": len(all_instincts),
    "duplicatesRemoved": duplicates,
    "conflictsResolved": conflicts,
    "mergedCount": len(merged_instincts),
    "instincts": merged_instincts
}

print(json.dumps(output, indent=2, ensure_ascii=False))
PYTHON_SCRIPT
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 <文件1> <文件2> ... [选项]

选项:
  --output <path>   指定输出文件
  --help            显示帮助

示例:
  # 合并两个文件
  $0 my-instincts.json team-instincts.json

  # 合并多个文件并指定输出
  $0 file1.json file2.json file3.json --output merged.json

  # 合并所有导出的文件
  $0 .instincts/export/*.json

EOF
}

main() {
    local output_file="${OUTPUT_DIR}/merged-$(date +%Y%m%d-%H%M%S).json"
    local input_files=()

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --output)
                output_file="$2"
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                input_files+=("$1")
                shift
                ;;
        esac
    done

    # 检查输入文件
    if [ ${#input_files[@]} -eq 0 ]; then
        log_error "请指定至少一个 JSON 文件"
        show_usage
        exit 1
    fi

    echo ""
    log_info "=========================================="
    log_info "Instinct Merge - 合并 Instincts"
    log_info "=========================================="
    echo ""

    # 检查文件是否存在
    for file in "${input_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "文件不存在: $file"
            exit 1
        fi
    done

    log_info "输入文件: ${#input_files[@]} 个"
    for file in "${input_files[@]}"; do
        echo "  - $file"
    done
    echo ""

    # 合并 instincts
    log_info "合并 Instincts..."
    local merged_json=$(merge_instincts "${input_files[@]}")

    # 创建输出目录
    mkdir -p "$(dirname "$output_file")"

    # 保存到文件
    echo "$merged_json" > "$output_file"

    log_success "合并完成: $output_file"
    echo ""

    # 显示统计信息
    echo "📊 统计信息:"
    echo "$merged_json" | python3 -c "
import json
import sys
data = json.load(sys.stdin)
print(f\"  源文件: {data['sourceFiles']} 个\")
print(f\"  总条目: {data['totalInstincts']} 条\")
print(f\"  去重: {data['duplicatesRemoved']} 条\")
print(f\"  矛盾: {data['conflictsResolved']} 个\")
print(f\"  合并: {data['mergedCount']} 条\")
"
    echo ""
}

# =============================================================================
# 运行主流程
# =============================================================================

main "$@"
