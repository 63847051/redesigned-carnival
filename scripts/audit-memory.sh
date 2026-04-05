#!/bin/bash
# =============================================================================
# MEMORY.md 审计脚本 - Audit MEMORY.md
# =============================================================================
# 功能: 检查 MEMORY.md 的健康状态，发现矛盾规则和过时信息
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

WORKSPACE="${WORKSPACE:-/root/.openclaw/workspace}"
MEMORY_FILE="${MEMORY_FILE:-${WORKSPACE}/MEMORY.md}"
REPORT_FILE="${REPORT_FILE:-${WORKSPACE}/memory/audit-report.md}"
MAX_TOKENS="${MAX_TOKENS:-8000}"  # 约 6000 汉字

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
# 审计检查
# =============================================================================

check_file_exists() {
    log_info "检查文件存在性..."

    if [ ! -f "$MEMORY_FILE" ]; then
        log_error "MEMORY.md 不存在: $MEMORY_FILE"
        return 1
    fi

    log_success "文件存在"
}

check_file_size() {
    log_info "检查文件大小..."

    local chars=$(wc -c < "$MEMORY_FILE")
    local lines=$(wc -l < "$MEMORY_FILE")
    local tokens=$((chars / 2))  # 粗略估算

    echo "  字符数: $chars"
    echo "  行数: $lines"
    echo "  估算 tokens: $tokens"
    echo "  限制: $MAX_TOKENS"

    if [ $tokens -gt $MAX_TOKENS ]; then
        log_warning "文件过大！超过限制 $((tokens - MAX_TOKENS)) tokens"
        return 1
    fi

    log_success "文件大小正常"
}

check_duplicate_sections() {
    log_info "检查重复章节..."

    local duplicates=$(grep -E "^#+ " "$MEMORY_FILE" | sort | uniq -d)

    if [ -n "$duplicates" ]; then
        log_warning "发现重复章节:"
        echo "$duplicates" | sed 's/^/    /'
        return 1
    fi

    log_success "无重复章节"
}

check_conflicting_rules() {
    log_info "检查矛盾规则..."

    local conflicts=0

    # 检查模型配置冲突
    local model_count=$(grep -c "模型:" "$MEMORY_FILE" 2>/dev/null || echo "0")
    if [ $model_count -gt 3 ]; then
        log_warning "发现多个模型配置（$model_count 处），可能有冲突"
        conflicts=$((conflicts + 1))
    fi

    # 检查相互排斥的规则
    if grep -qi "记录.*日志" "$MEMORY_FILE" && grep -qi "不.*记录.*日志" "$MEMORY_FILE"; then
        log_warning "发现矛盾规则：关于日志记录"
        conflicts=$((conflicts + 1))
    fi

    # 检查版本号冲突
    local versions=$(grep -oE "v[0-9]+\.[0-9]+" "$MEMORY_FILE" | sort -u | wc -l)
    if [ $versions -gt 5 ]; then
        log_warning "发现多个版本号（$versions 个），需要统一"
        conflicts=$((conflicts + 1))
    fi

    if [ $conflicts -eq 0 ]; then
        log_success "无明显矛盾规则"
    else
        log_warning "发现 $conflicts 处潜在冲突"
    fi

    return $conflicts
}

check_outdated_info() {
    log_info "检查过时信息..."

    local outdated=0

    # 检查日期
    local old_dates=$(grep -oE "202[0-9]-[0-9]{2}-[0-9]{2}" "$MEMORY_FILE" | \
                     while read date; do
                         age_days=$(( ($(date +%s) - $(date -d "$date" +%s 2>/dev/null || echo "0")) / 86400 ))
                         if [ $age_days -gt 90 ]; then
                             echo "$date ($age_days 天)"
                         fi
                     done | head -3)

    if [ -n "$old_dates" ]; then
        log_warning "发现旧日期信息:"
        echo "$old_dates" | sed 's/^/    /'
        outdated=$((outdated + 1))
    fi

    # 检查临时性信息
    if grep -qi "临时\|待定\|TODO\|FIXME" "$MEMORY_FILE"; then
        log_warning "发现临时性信息标记"
        echo "  这些信息应该已处理或移除"
        outdated=$((outdated + 1))
    fi

    # 检查过时技术信息
    if grep -qi "v[0-4]\." "$MEMORY_FILE"; then
        log_warning "发现可能的过时版本号（v0.x - v4.x）"
        outdated=$((outdated + 1))
    fi

    if [ $outdated -eq 0 ]; then
        log_success "无明显过时信息"
    else
        log_warning "发现 $outdated 类潜在过时信息"
    fi

    return $outdated
}

check_derivability() {
    log_info "检查可推导信息..."

    local derivable=0

    # 检查可从代码推导的信息
    if grep -qi "配置文件位于" "$MEMORY_FILE"; then
        log_warning "记录了配置文件路径（可从代码推导）"
        derivable=$((derivable + 1))
    fi

    # 检查可从系统推导的信息
    if grep -qi "服务器 IP\|内网地址" "$MEMORY_FILE"; then
        log_warning "记录了网络地址（可从系统推导）"
        derivable=$((derivable + 1))
    fi

    # 检查可从其他文件推导的信息
    if grep -qi "详见.*\.md" "$MEMORY_FILE"; then
        log_warning "包含参考链接（可从文件系统推导）"
        derivable=$((derivable + 1))
    fi

    if [ $derivable -eq 0 ]; then
        log_success "无明显冗余信息"
    else
        log_warning "发现 $derivable 类可推导信息"
        log_info "  考虑删除这些信息，保持 MEMORY.md 精炼"
    fi

    return $derivable
}

check_structure() {
    log_info "检查文件结构..."

    local issues=0

    # 检查是否有标题
    if ! grep -q "^# " "$MEMORY_FILE"; then
        log_error "缺少主标题"
        issues=$((issues + 1))
    fi

    # 检查是否有关键章节
    local required_sections=("关于" "规则" "项目" "工具")
    for section in "${required_sections[@]}"; do
        if ! grep -qi "$section" "$MEMORY_FILE"; then
            log_warning "缺少章节: $section"
            issues=$((issues + 1))
        fi
    done

    # 检查空行过多
    local consecutive_empty=$(grep -P "^\n$" "$MEMORY_FILE" | wc -l)
    if [ $consecutive_empty -gt 50 ]; then
        log_warning "空行过多（$consecutive_empty 行）"
        issues=$((issues + 1))
    fi

    if [ $issues -eq 0 ]; then
        log_success "文件结构良好"
    else
        log_warning "发现 $issues 处结构问题"
    fi

    return $issues
}

generate_report() {
    log_info "生成审计报告..."

    cat > "$REPORT_FILE" << EOF
# MEMORY.md 审计报告

**审计时间**: $(date '+%Y-%m-%d %H:%M:%S')
**文件**: $MEMORY_FILE

---

## 审计结果摘要

$(check_file_size 2>&1 | sed 's/^[^ ]* /- /')

---

## 详细检查

### 1. 文件大小
$(check_file_size 2>&1 | grep -E "字符数|行数|tokens" | sed 's/^/  /')

### 2. 重复章节
$(check_duplicate_sections 2>&1 | sed 's/^/  /')

### 3. 矛盾规则
$(check_conflicting_rules 2>&1 | sed 's/^/  /')

### 4. 过时信息
$(check_outdated_info 2>&1 | sed 's/^/  /')

### 5. 可推导信息
$(check_derivability 2>&1 | sed 's/^/  /')

### 6. 文件结构
$(check_structure 2>&1 | sed 's/^/  /')

---

## 清理建议

### 立即处理
- 删除过时的临时信息
- 解决矛盾规则
- 删除可推导的信息

### 定期维护
- 每周审计一次
- 更新版本号
- 压缩过长的章节

### 优化建议
- 保持文件大小在合理范围
- 使用引用而非复制
- 定期归档旧日志

---

**生成者**: 大领导 🎯
**审计工具**: /root/.openclaw/workspace/scripts/audit-memory.sh
EOF

    log_success "报告已生成: $REPORT_FILE"
}

# =============================================================================
# 主流程
# =============================================================================

main() {
    echo ""
    log_info "=========================================="
    log_info "MEMORY.md 审计"
    log_info "=========================================="
    echo ""

    local total_issues=0

    # 执行所有检查
    check_file_exists || total_issues=$((total_issues + 1))
    echo ""
    check_file_size || total_issues=$((total_issues + $?))
    echo ""
    check_duplicate_sections || total_issues=$((total_issues + $?))
    echo ""
    check_conflicting_rules || total_issues=$((total_issues + $?))
    echo ""
    check_outdated_info || total_issues=$((total_issues + $?))
    echo ""
    check_derivability || total_issues=$((total_issues + $?))
    echo ""
    check_structure || total_issues=$((total_issues + $?))
    echo ""

    # 生成报告
    generate_report
    echo ""

    # 总结
    log_info "=========================================="
    if [ $total_issues -eq 0 ]; then
        log_success "MEMORY.md 状态良好！"
    else
        log_warning "发现 $total_issues 类问题，请查看报告"
    fi
    log_info "=========================================="
}

main "$@"
