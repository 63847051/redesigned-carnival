#!/bin/bash
# =============================================================================
# PAI 智能查询助手
# =============================================================================
# 功能：快速查询 PAI 记忆和历史记录
# 用途：在执行任务前快速了解相关经验和教训
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
HOT_MEMORY="$PAI_DIR/hot-memory.jsonl"

# 颜色定义
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 显示使用帮助
show_help() {
    echo -e "${CYAN}🤖 PAI 智能查询助手${NC}"
    echo "======================================"
    echo ""
    echo "用法："
    echo "  $0 <查询内容>"
    echo ""
    echo "示例："
    echo "  $0 时间戳错误          # 查询时间戳相关的错误"
    echo "  $0 飞书表格           # 查询飞书表格相关的任务"
    echo "  $0 设计图纸           # 查询设计相关的任务"
    echo "  $0 今天               # 查询今天的所有记录"
    echo "  $0 错误               # 查询所有错误记录"
    echo ""
    echo "特殊命令："
    echo "  $0 --stats            # 显示统计信息"
    echo "  $0 --recent           # 显示最近 10 条记录"
    echo "  $0 --errors           # 显示所有错误记录"
    echo "  $0 --success          # 显示所有成功记录"
    echo ""
}

# 显示统计信息
show_stats() {
    echo -e "${CYAN}📊 PAI 系统统计${NC}"
    echo "======================================"
    echo ""

    # 总记录数
    TOTAL=$(wc -l < "$HOT_MEMORY" 2>/dev/null || echo "0")
    echo -e "${BLUE}总记录数：${NC}$TOTAL"

    # 成功记录
    SUCCESS=$(grep -c '"success":1' "$HOT_MEMORY" 2>/dev/null || echo "0")
    echo -e "${GREEN}成功记录：${NC}$SUCCESS"

    # 失败记录
    FAILED=$(grep -c '"success":0' "$HOT_MEMORY" 2>/dev/null || echo "0")
    echo -e "${RED}失败记录：${NC}$FAILED"

    # 成功率
    if [ "$TOTAL" -gt 0 ]; then
        SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($SUCCESS/$TOTAL)*100}")
        echo -e "${BLUE}成功率：${NC}${SUCCESS_RATE}%"
    fi

    # 平均复杂度
    AVG_COMPLEXITY=$(awk -F'"complexity":' '{print $2}' "$HOT_MEMORY" 2>/dev/null | \
                      awk -F',' '{print $1}' | \
                      awk '{sum+=$1; count++} END {if(count>0) printf "%.1f", sum/count; else print "0"}')
    echo -e "${BLUE}平均复杂度：${NC}${AVG_COMPLEXITY}/5"

    echo ""
    echo "======================================"
}

# 显示最近记录
show_recent() {
    echo -e "${CYAN}🕐 最近 10 条记录${NC}"
    echo "======================================"
    echo ""

    tail -10 "$HOT_MEMORY" 2>/dev/null | \
        while IFS= read -r line; do
            DESC=$(echo "$line" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
            DATE=$(echo "$line" | grep -o '"date":"[^"]*"' | cut -d'"' -f4)
            SUCCESS=$(echo "$line" | grep -o '"success":[01]' | cut -d':' -f2)
            if [ "$SUCCESS" = "1" ]; then
                echo -e "${GREEN}✅ [$DATE]${NC} $DESC"
            else
                echo -e "${RED}❌ [$DATE]${NC} $DESC"
            fi
        done

    echo ""
    echo "======================================"
}

# 显示所有错误
show_errors() {
    echo -e "${RED}❌ 所有错误记录${NC}"
    echo "======================================"
    echo ""

    grep '"success":0' "$HOT_MEMORY" 2>/dev/null | \
        while IFS= read -r line; do
            DESC=$(echo "$line" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
            DATE=$(echo "$line" | grep -o '"date":"[^"]*"' | cut -d'"' -f4)
            echo -e "${RED}❌ [$DATE]${NC} $DESC"
        done

    echo ""
    echo "======================================"
}

# 显示所有成功记录
show_success() {
    echo -e "${GREEN}✅ 所有成功记录${NC}"
    echo "======================================"
    echo ""

    grep '"success":1' "$HOT_MEMORY" 2>/dev/null | \
        while IFS= read -r line; do
            DESC=$(echo "$line" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
            DATE=$(echo "$line" | grep -o '"date":"[^"]*"' | cut -d'"' -f4)
            echo -e "${GREEN}✅ [$DATE]${NC} $DESC"
        done

    echo ""
    echo "======================================"
}

# 查询特定内容
query_content() {
    local QUERY="$*"
    local RESULTS=$(grep -i "$QUERY" "$HOT_MEMORY" 2>/dev/null | wc -l)

    echo -e "${CYAN}🔍 查询结果：$QUERY${NC}"
    echo "======================================"
    echo ""

    if [ "$RESULTS" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  未找到相关记录${NC}"
    else
        echo -e "${BLUE}找到 $RESULTS 条相关记录：${NC}"
        echo ""

        grep -i "$QUERY" "$HOT_MEMORY" 2>/dev/null | \
            while IFS= read -r line; do
                DESC=$(echo "$line" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
                DATE=$(echo "$line" | grep -o '"date":"[^"]*"' | cut -d'"' -f4)
                SUCCESS=$(echo "$line" | grep -o '"success":[01]' | cut -d':' -f2)
                if [ "$SUCCESS" = "1" ]; then
                    echo -e "${GREEN}✅ [$DATE]${NC} $DESC"
                else
                    echo -e "${RED}❌ [$DATE]${NC} $DESC"
                fi
            done
    fi

    echo ""
    echo "======================================"
}

# 主程序
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    case "$1" in
        -h|--help)
            show_help
            ;;
        --stats)
            show_stats
            ;;
        --recent)
            show_recent
            ;;
        --errors)
            show_errors
            ;;
        --success)
            show_success
            ;;
        *)
            query_content "$*"
            ;;
    esac
}

main "$@"
