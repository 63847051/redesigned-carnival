#!/bin/bash
# =============================================================================
# 记忆归档脚本 - Archive Old Memory Logs
# =============================================================================
# 功能: 将 30 天以上的日志文件自动归档到 memory/archive/
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail  # 严格模式

# =============================================================================
# 配置
# =============================================================================

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
ARCHIVE_DIR="${ARCHIVE_DIR:-${MEMORY_DIR}/archive}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
LOG_FILE="${LOG_FILE:-${MEMORY_DIR}/archive.log}"
DRY_RUN="${DRY_RUN:-false}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# 工具函数
# =============================================================================

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $@" | tee -a "$LOG_FILE"
}

# =============================================================================
# 核心功能
# =============================================================================

check_requirements() {
    log_info "检查环境..."

    # 检查 memory 目录
    if [ ! -d "$MEMORY_DIR" ]; then
        log_error "memory 目录不存在: $MEMORY_DIR"
        exit 1
    fi

    # 创建归档目录
    if [ ! -d "$ARCHIVE_DIR" ]; then
        log_info "创建归档目录: $ARCHIVE_DIR"
        mkdir -p "$ARCHIVE_DIR"
    fi

    log_success "环境检查完成"
}

count_files() {
    local dir=$1
    find "$dir" -maxdepth 1 -name "*.md" -type f | wc -l
}

get_file_age_days() {
    local file=$1
    local file_date=$(basename "$file" .md)

    # 尝试解析文件名中的日期 (YYYY-MM-DD)
    if [[ $file_date =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        local file_sec=$(date -d "$file_date" +%s 2>/dev/null || echo "0")
        local current_sec=$(date +%s)
        local age_days=$(( (current_sec - file_sec) / 86400 ))

        if [ $file_sec -gt 0 ]; then
            echo $age_days
            return
        fi
    fi

    # 回退到文件修改时间
    local file_mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
    local current_sec=$(date +%s)
    local age_days=$(( (current_sec - file_mtime) / 86400 ))

    echo $age_days
}

archive_old_logs() {
    log_info "开始归档 ${RETENTION_DAYS} 天以上的日志..."

    local archived_count=0
    local skipped_count=0
    local total_size_before=0
    local total_size_after=0

    # 查找所有日志文件
    while IFS= read -r -d '' file; do
        # 跳过 archive 目录
        if [[ "$file" == */archive/* ]]; then
            continue
        fi

        # 计算文件年龄
        local age_days=$(get_file_age_days "$file")

        # 检查是否需要归档
        if [ $age_days -ge $RETENTION_DAYS ]; then
            local filename=$(basename "$file")
            local file_date=${filename%.md}

            # 提取年月
            if [[ $file_date =~ ^([0-9]{4})-([0-9]{2})-[0-9]{2}$ ]]; then
                local year="${BASH_REMATCH[1]}"
                local month="${BASH_REMATCH[2]}"
            else
                # 使用文件的修改时间
                local file_mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
                local file_date_str=$(date -d "@$file_mtime" +%Y-%m 2>/dev/null || date -r "$file_mtime" +%Y-%m)
                year=${file_date_str:0:4}
                month=${file_date_str:5:2}
            fi

            # 创建目标目录
            local target_dir="${ARCHIVE_DIR}/${year}-${month}"
            mkdir -p "$target_dir"

            # 获取文件大小
            local file_size=$(stat -c %s "$file" 2>/dev/null || stat -f %z "$file" 2>/dev/null)
            total_size_before=$((total_size_before + file_size))

            # 移动文件
            if [ "$DRY_RUN" = "true" ]; then
                log_info "[DRY RUN] 会归档: $filename (${age_days} 天)"
            else
                mv "$file" "$target_dir/"
                log_success "归档: $filename → ${year}-${month}/ (${age_days} 天)"
            fi

            archived_count=$((archived_count + 1))
            total_size_after=$((total_size_after + file_size))
        else
            skipped_count=$((skipped_count + 1))
        fi
    done < <(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -type f -print0)

    # 生成报告
    echo ""
    log_info "归档完成"
    echo "  归档文件数: $archived_count"
    echo "  跳过文件数: $skipped_count"
    echo "  归档数据量: $(numfmt --to=iec $total_size_after)"

    if [ "$DRY_RUN" = "true" ]; then
        log_warning "DRY RUN 模式：未实际移动文件"
    fi
}

generate_index() {
    log_info "生成归档索引..."

    local index_file="${ARCHIVE_DIR}/index.md"

    cat > "$index_file" << 'EOF'
# 记忆归档索引

**最后更新**: $(date '+%Y-%m-%d %H:%M:%S')

## 归档说明

本目录存放 30 天以上的历史日志，按月份组织。

## 目录结构

EOF

    # 列出所有月份目录
    find "$ARCHIVE_DIR" -maxdepth 1 -type d -name "*-*" | sort | while read dir; do
        local month_dir=$(basename "$dir")
        local count=$(find "$dir" -name "*.md" | wc -l)

        echo "### ${month_dir}" >> "$index_file"
        echo "- 文件数量: ${count}" >> "$index_file"
        echo "" >> "$index_file"
    done

    log_success "索引已生成: $index_file"
}

show_stats() {
    log_info "当前统计:"

    local current_count=$(count_files "$MEMORY_DIR")
    local archived_count=$(find "$ARCHIVE_DIR" -name "*.md" | wc -l)
    local current_size=$(du -sh "$MEMORY_DIR" 2>/dev/null | cut -f1)
    local archive_size=$(du -sh "$ARCHIVE_DIR" 2>/dev/null | cut -f1)

    echo "  当前日志数: $current_count"
    echo "  归档文件数: $archived_count"
    echo "  当前日志大小: $current_size"
    echo "  归档占用空间: $archive_size"
}

# =============================================================================
# 主流程
# =============================================================================

main() {
    log_info "=========================================="
    log_info "记忆归档脚本启动"
    log_info "=========================================="
    echo ""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                log_warning "启用 DRY RUN 模式"
                shift
                ;;
            --days)
                RETENTION_DAYS="$2"
                shift 2
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --dry-run    预演模式，不实际移动文件"
                echo "  --days N     设置保留天数（默认: 30）"
                echo "  --help       显示帮助"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done

    # 执行归档
    check_requirements
    show_stats
    echo ""
    archive_old_logs
    echo ""
    generate_index
    echo ""
    show_stats

    log_success "归档脚本完成"
}

# 运行主流程
main "$@"
