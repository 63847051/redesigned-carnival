#!/bin/bash
# 记忆迁移脚本
# 将现有的每日记忆迁移到新的分层结构

set -e

# 配置
MEMORY_DIR="/root/.openclaw/workspace/memory"
KEY_POINTS_DIR="$MEMORY_DIR/key-points"
STRUCTURED_DIR="$MEMORY_DIR/structured"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo "🔄 记忆迁移脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --dry-run    - 模拟运行，不实际修改文件"
    echo "  --force      - 强制覆盖已存在的文件"
    echo "  --help       - 显示帮助信息"
    echo ""
    echo "说明:"
    echo "  此脚本将现有的 memory/YYYY-MM-DD.md 文件迁移到新的分层结构："
    echo "  - L1: key-points/YYYY-MM.md（关键点）"
    echo "  - L2: structured/{people,projects,knowledge,preferences}/YYYY-MM-DD.md（分类知识）"
    echo ""
}

# 统计函数
count_files() {
    find "$MEMORY_DIR" -name "*.md" -type f | wc -l
}

# 迁移函数
migrate_memory() {
    local daily_file="$1"
    local date=$(basename "$daily_file" .md)
    local month="${date:0:7}"

    # 检查日期格式
    if [[ ! "$date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        return
    fi

    echo -e "${BLUE}处理: $date${NC}"

    # L1: 提取关键点到月度文件
    local month_file="$KEY_POINTS_DIR/${month}.md"
    if [ ! -f "$month_file" ] || [ "$FORCE" = "true" ]; then
        if [ "$DRY_RUN" = "true" ]; then
            echo -e "  ${YELLOW}[模拟] 创建 L1: $month_file${NC}"
        else
            # 提取关键信息
            echo "# ${month} 关键点" > "$month_file"
            echo "" >> "$month_file"
            grep -E "^## |^### " "$daily_file" >> "$month_file" 2>/dev/null || true
            echo -e "  ${GREEN}✓ 创建 L1${NC}"
        fi
    else
        echo -e "  ${YELLOW}⊘ L1 已存在${NC}"
    fi

    # L2: 分类结构化知识
    local categories=("people" "projects" "knowledge" "preferences")

    for category in "${categories[@]}"; do
        local category_file="$STRUCTURED_DIR/${category}/${date}.md"

        if [ ! -f "$category_file" ] || [ "$FORCE" = "true" ]; then
            if [ "$DRY_RUN" = "true" ]; then
                echo -e "  ${YELLOW}[模拟] 创建 L2: $category_file${NC}"
            else
                # 根据分类提取相关内容
                case "$category" in
                    people)
                        grep -A 5 -E "幸运小行星|用户|客户|人" "$daily_file" > "$category_file" 2>/dev/null || touch "$category_file"
                        ;;
                    projects)
                        grep -A 5 -E "项目|任务|工作|开发" "$daily_file" > "$category_file" 2>/dev/null || touch "$category_file"
                        ;;
                    knowledge)
                        grep -A 5 -E "学习|研究|分析|发现|技术" "$daily_file" > "$category_file" 2>/dev/null || touch "$category_file"
                        ;;
                    preferences)
                        grep -A 5 -E "喜欢|偏好|习惯|风格" "$daily_file" > "$category_file" 2>/dev/null || touch "$category_file"
                        ;;
                esac
                echo -e "  ${GREEN}✓ 创建 L2: $category${NC}"
            fi
        else
            echo -e "  ${YELLOW}⊘ L2 已存在: $category${NC}"
        fi
    done
}

# 主流程
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}🔄 记忆迁移${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # 统计现有文件
    local total_files=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -type f | wc -l)
    echo -e "${YELLOW}发现 $total_files 个记忆文件${NC}"
    echo ""

    if [ "$DRY_RUN" = "true" ]; then
        echo -e "${YELLOW}⚠️  模拟运行模式${NC}"
        echo ""
    fi

    # 创建目录
    if [ "$DRY_RUN" != "true" ]; then
        mkdir -p "$KEY_POINTS_DIR"
        mkdir -p "$STRUCTURED_DIR"/{people,projects,knowledge,preferences}
    fi

    # 迁移每个文件
    find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -type f | sort | while read -r file; do
        migrate_memory "$file"
        echo ""
    done

    # 统计结果
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ 迁移完成${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    if [ "$DRY_RUN" != "true" ]; then
        local l1_count=$(find "$KEY_POINTS_DIR" -name "*.md" -type f | wc -l)
        local l2_count=$(find "$STRUCTURED_DIR" -name "*.md" -type f | wc -l)

        echo -e "${YELLOW}📊 迁移统计:${NC}"
        echo -e "  L1 文件: $l1_count"
        echo -e "  L2 文件: $l2_count"
        echo ""
        echo -e "${YELLOW}💡 下一步:${NC}"
        echo -e "  1. 检查生成的文件"
        echo -e "  2. 手动审查并优化分类"
        echo -e "  3. 运行 memory-compressor.sh 压缩新的记忆"
    fi
}

# 参数处理
DRY_RUN="false"
FORCE="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --force)
            FORCE="true"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 未知参数: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

main "$@"
