#!/bin/bash
# =============================================================================
# 记忆清理报告脚本 - Memory Cleanup Report
# =============================================================================
# 功能: 生成记忆清理统计报告
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
ARCHIVE_DIR="${ARCHIVE_DIR:-${MEMORY_DIR}/archive}"
REPORT_FILE="${REPORT_FILE:-${MEMORY_DIR}/cleanup-report.md}"
STATS_FILE="${STATS_FILE:-${MEMORY_DIR}/cleanup-stats.json}"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# =============================================================================
# 工具函数
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@"
}

# =============================================================================
# 统计函数
# =============================================================================

count_files_by_age() {
    local dir=$1
    local days=$2

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        find "$dir" -maxdepth 1 -name "*.md" -type f -mtime -$days | wc -l
    else
        # macOS fallback
        find "$dir" -maxdepth 1 -name "*.md" -type f | while read file; do
            local file_age=$(( ($(date +%s) - $(stat -f %m "$file")) / 86400 ))
            if [ $file_age -lt $days ]; then
                echo 1
            fi
        done | wc -l
    fi
}

get_directory_size() {
    local dir=$1
    du -sh "$dir" 2>/dev/null | cut -f1
}

get_file_count() {
    local dir=$1
    find "$dir" -name "*.md" -type f | wc -l
}

get_archive_stats() {
    local stats=""

    # 遍历所有月份目录
    find "$ARCHIVE_DIR" -maxdepth 1 -type d -name "*-*" | sort | while read month_dir; do
        local month=$(basename "$month_dir")
        local count=$(find "$month_dir" -name "*.md" | wc -l)
        local size=$(get_directory_size "$month_dir")

        echo "$month|$count|$size"
    done
}

get_memory_file_size() {
    local file=$1
    local chars=$(wc -c < "$file" 2>/dev/null || echo "0")
    local lines=$(wc -l < "$file" 2>/dev/null || echo "0")
    local tokens=$((chars / 2))

    echo "$chars|$lines|$tokens"
}

# =============================================================================
# 报告生成
# =============================================================================

generate_report() {
    log_info "生成清理报告..."

    # 收集统计数据
    local current_count=$(get_file_count "$MEMORY_DIR")
    local current_size=$(get_directory_size "$MEMORY_DIR")
    local archived_count=$(get_file_count "$ARCHIVE_DIR")
    local archive_size=$(get_directory_size "$ARCHIVE_DIR")

    # 统计当前日志年龄分布
    local current_7d=$(count_files_by_age "$MEMORY_DIR" 7)
    local current_30d=$(count_files_by_age "$MEMORY_DIR" 30)
    local current_90d=$(count_files_by_age "$MEMORY_DIR" 90)

    # MEMORY.md 统计
    local memory_md="${MEMORY_DIR}/../MEMORY.md"
    local memory_md_stats="N/A|N/A|N/A"
    if [ -f "$memory_md" ]; then
        memory_md_stats=$(get_memory_file_size "$memory_md")
    fi

    # 生成报告
    cat > "$REPORT_FILE" << EOF
# 记忆清理报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**生成者**: 大领导 🎯

---

## 📊 总体统计

### 当前日志（${MEMORY_DIR}）

| 指标 | 数值 |
|------|------|
| 总文件数 | ${current_count} |
| 占用空间 | ${current_size} |
| 7 天内 | ${current_7d} |
| 30 天内 | ${current_30d} |
| 90 天内 | ${current_90d} |

### 归档日志（${ARCHIVE_DIR}）

| 指标 | 数值 |
|------|------|
| 总文件数 | ${archived_count} |
| 占用空间 | ${archive_size} |

---

## 📁 归档详情

### 按月份统计

| 月份 | 文件数 | 大小 |
|------|--------|------|
$(get_archive_stats | awk -F'|' '{printf "| %s | %s | %s |\n", $1, $2, $3}')

---

## 📈 MEMORY.md 状态

| 指标 | 数值 |
|------|------|
| 字符数 | $(echo $memory_md_stats | cut -d'|' -f1) |
| 行数 | $(echo $memory_md_stats | cut -d'|' -f2) |
| 估算 tokens | $(echo $memory_md_stats | cut -d'|' -f3) |

---

## 🎯 清理建议

### 立即执行

1. **归档旧日志**
   - 当前有 ${current_count} 个日志文件
   - 建议归档 30 天以上的文件

2. **审计 MEMORY.md**
   - 检查矛盾规则
   - 删除过时信息
   - 移除可推导内容

### 定期维护

- **每日**: 自动归档检查（archive-old-logs.sh）
- **每周**: MEMORY.md 审计（audit-memory.sh）
- **每月**: 生成清理报告（cleanup-report.sh）

### 优化建议

- 保持 MEMORY.md 精炼（< 8000 tokens）
- 定期删除临时性信息
- 使用引用而非复制内容
- 归档旧日志，保持检索速度

---

## 📊 历史趋势

$(if [ -f "$STATS_FILE" ]; then
    echo "历史统计数据保存在: \`$STATS_FILE\`"
else
    echo "暂无历史数据。首次运行本脚本。"
fi)

---

## 🔧 相关工具

- \`archive-old-logs.sh\` - 归档旧日志
- \`audit-memory.sh\` - 审计 MEMORY.md
- \`cleanup-report.sh\` - 生成清理报告（本脚本）

---

**报告位置**: \`$REPORT_FILE\`
**下次更新**: 建议每月运行一次
EOF

    log_success "报告已生成: $REPORT_FILE"
}

save_stats() {
    log_info "保存统计数据..."

    local current_count=$(get_file_count "$MEMORY_DIR")
    local archived_count=$(get_file_count "$ARCHIVE_DIR")
    local timestamp=$(date +%s)

    # 保存 JSON 格式统计
    cat > "$STATS_FILE" << EOF
{
  "timestamp": $timestamp,
  "date": "$(date -d @$timestamp '+%Y-%m-%d %H:%M:%S')",
  "current_logs": {
    "count": $current_count,
    "size": "$(get_directory_size "$MEMORY_DIR")"
  },
  "archived_logs": {
    "count": $archived_count,
    "size": "$(get_directory_size "$ARCHIVE_DIR")"
  }
}
EOF

    log_success "统计数据已保存: $STATS_FILE"
}

show_summary() {
    log_info "清理统计摘要:"
    echo ""
    echo "  📁 当前日志: $(get_file_count "$MEMORY_DIR") 个 ($(get_directory_size "$MEMORY_DIR"))"
    echo "  📦 归档日志: $(get_file_count "$ARCHIVE_DIR") 个 ($(get_directory_size "$ARCHIVE_DIR"))"
    echo "  📄 MEMORY.md: $(wc -c < "${MEMORY_DIR}/../MEMORY.md" 2>/dev/null | awk '{print $1}') 字符"
    echo ""
}

# =============================================================================
# 主流程
# =============================================================================

main() {
    echo ""
    log_info "=========================================="
    log_info "记忆清理报告"
    log_info "=========================================="
    echo ""

    # 生成报告
    generate_report
    echo ""

    # 保存统计
    save_stats
    echo ""

    # 显示摘要
    show_summary

    log_success "报告生成完成"
}

main "$@"
