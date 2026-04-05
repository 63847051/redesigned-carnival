#!/bin/bash
# =============================================================================
# Instinct Evolve - 升华为 Skill
# =============================================================================
# 功能: 从 Instincts 中提取共同模式，生成 Skill 模板
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

INSTINCTS_DIR="${INSTINCTS_DIR:-/root/.openclaw/workspace/.instincts/export}"
SKILLS_DIR="${SKILLS_DIR:-/root/.openclaw/workspace/.instincts/skills}"

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

find_related_instincts() {
    local keyword="$1"
    local json_file=""

    # 查找最新的 JSON 文件
    json_file=$(find "$INSTINCTS_DIR" -name "*.json" -type f | sort -r | head -1)

    if [ -z "$json_file" ]; then
        log_error "未找到 Instincts 文件"
        return 1
    fi

    # 使用 Python 查找相关条目
    python3 << PYTHON_SCRIPT
import json
import sys

with open('$json_file', 'r') as f:
    data = json.load(f)
    instincts = data.get('instincts', [])

keyword = '$keyword'.lower()
related = []

for instinct in instincts:
    rule = instinct.get('rule', '').lower()
    category = instinct.get('category', '').lower()

    if keyword in rule or keyword in category:
        related.append(instinct)

# 输出相关条目
for instinct in related:
    print(f"{instinct.get('rule', '')}|{instinct.get('confidence', 0.5)}|{instinct.get('category', '')}")
PYTHON_SCRIPT
}

generate_skill_template() {
    local topic="$1"
    local instincts=("$@")

    # 转换主题为安全文件名
    local skill_name=$(echo "$topic" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g')
    local skill_dir="${SKILLS_DIR}/${skill_name}"
    local skill_file="${skill_dir}/SKILL.md"

    # 创建目录
    mkdir -p "$skill_dir"

    # 生成 SKILL.md
    cat > "$skill_file" << EOF
# ${topic}

**创建时间**: $(date '+%Y-%m-%d %H:%M:%S')
**来源**: 从 Instincts 升华
**作者**: 大领导 🎯

---

## 🎯 技能描述

这个 Skill 是从团队的实战经验中提炼出来的最佳实践。

**核心理念**:
EOF

    # 添加核心理念
    local first=true
    for instinct in "${instincts[@]}"; do
        IFS='|' read -r rule confidence category <<< "$instinct"
        if [ "$first" = true ]; then
            echo "- $rule" >> "$skill_file"
            first=false
        else
            echo "- $rule" >> "$skill_file"
        fi
    done

    cat >> "$skill_file" << EOF

---

## 📋 使用场景

当你需要以下操作时，使用此 Skill：

EOF

    # 添加使用场景（基于 category）
    local categories=()
    for instinct in "${instincts[@]}"; do
        IFS='|' read -r rule confidence category <<< "$instinct"
        if [ -n "$category" ] && [[ ! " ${categories[@]} " =~ " ${category} " ]]; then
            categories+=("$category")
        fi
    done

    for category in "${categories[@]}"; do
        echo "- $category 相关操作" >> "$skill_file"
    done

    cat >> "$skill_file" << EOF

---

## 🚀 实施步骤

### 步骤 1: 准备
- 检查前置条件
- 准备所需工具
- 规划实施计划

### 步骤 2: 执行
- 按照最佳实践操作
- 遵循核心理念
- 注意常见陷阱

### 步骤 3: 验证
- 检查结果
- 确认质量
- 记录经验

---

## 💡 最佳实践

EOF

    # 添加最佳实践（基于高置信度规则）
    for instinct in "${instincts[@]}"; do
        IFS='|' read -r rule confidence category <<< "$instinct"
        conf=$(echo "$confidence" | awk '{printf "%.0f", $1}')

        if [ "$conf" -ge 7 ]; then
            echo "#### ✅ $rule" >> "$skill_file"
            echo "" >> "$skill_file"
            echo "**置信度**: ${confidence}" >> "$skill_file"
            echo "" >> "$skill_file"
        fi
    done

    cat >> "$skill_file" << EOF

---

## ⚠️ 常见陷阱

EOF

    # 添加常见陷阱（基于低置信度规则）
    for instinct in "${instincts[@]}"; do
        IFS='|' read -r rule confidence category <<< "$instinct"
        conf=$(echo "$confidence" | awk '{printf "%.0f", $1}')

        if [ "$conf" -lt 7 ] && [ "$conf" -ge 5 ]; then
            echo "#### ⚠️ $rule" >> "$skill_file"
            echo "" >> "$skill_file"
            echo "**置信度**: ${confidence}（仍在验证）" >> "$skill_file"
            echo "" >> "$skill_file"
        fi
    done

    cat >> "$skill_file" << EOF

---

## 📚 参考资料

- 来源 Instincts: \`$INSTINCTS_DIR\`
- 创建时间: $(date '+%Y-%m-%d %H:%M:%S')
- 升华自: ${#instincts[@]} 条规则

---

**下一步**:
1. 编辑此 SKILL.md，补充细节
2. 添加示例代码
3. 测试验证
4. 分享给团队

EOF

    echo "$skill_file"
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 <主题关键词> [选项]

选项:
  --file <path>     指定 Instincts 文件
  --output <path>   指定输出目录
  --help            显示帮助

示例:
  # 从 Bash 相关的 Instincts 生成 Skill
  $0 "Bash 脚本最佳实践"

  # 从 Git 相关的 Instincts 生成 Skill
  $0 "Git 工作流"

  # 指定输入文件
  $0 "Python 开发" --file my-instincts.json

EOF
}

main() {
    local topic=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --file)
                INSTINCTS_DIR="$(dirname "$2")"
                shift 2
                ;;
            --output)
                SKILLS_DIR="$2"
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                topic="$1"
                shift
                ;;
        esac
    done

    # 检查主题
    if [ -z "$topic" ]; then
        log_error "请指定主题关键词"
        show_usage
        exit 1
    fi

    echo ""
    log_info "=========================================="
    log_info "Instinct Evolve - 升华为 Skill"
    log_info "=========================================="
    echo ""

    log_info "主题: $topic"
    echo ""

    # 查找相关 Instincts
    log_info "查找相关 Instincts..."
    local related_instincts=()
    while IFS= read -r line; do
        [ -n "$line" ] && related_instincts+=("$line")
    done < <(find_related_instincts "$topic")

    local count=${#related_instincts[@]}

    if [ $count -eq 0 ]; then
        log_warning "未找到相关 Instincts"
        exit 0
    fi

    log_success "找到 $count 条相关规则"
    echo ""

    # 显示预览
    echo "📄 相关规则（前 5 条）:"
    for instinct in "${related_instincts[@]:0:5}"; do
        IFS='|' read -r rule confidence category <<< "$instinct"
        echo "  - [$confidence] $rule"
    done
    echo ""

    # 生成 Skill 模板
    log_info "生成 Skill 模板..."
    local skill_file=$(generate_skill_template "$topic" "${related_instincts[@]}")

    log_success "Skill 已创建: $skill_file"
    echo ""

    echo "📊 统计信息:"
    echo "  主题: $topic"
    echo "  相关规则: $count 条"
    echo "  Skill 文件: $skill_file"
    echo ""
    echo "🎯 下一步:"
    echo "  1. 编辑 SKILL.md，补充细节"
    echo "  2. 添加示例代码"
    echo "  3. 测试验证"
    echo "  4. 分享给团队"
    echo ""
}

# =============================================================================
# 运行主流程
# =============================================================================

main "$@"
