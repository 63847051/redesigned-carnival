#!/bin/bash
# =============================================================================
# PAI 操作前检查脚本
# =============================================================================
# 功能：在执行任务前自动检查历史错误和类似任务
# 用途：防止重复犯错，提供历史经验参考
# =============================================================================

PAI_DIR="/root/.openclaw/workspace/.pai-learning"
HOT_MEMORY="$PAI_DIR/hot-memory.jsonl"
WARNINGS_FOUND=0

# 颜色定义
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 PAI 操作前检查${NC}"
echo "======================================"

# 检查参数
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}⚠️  用法: $0 <关键词1> [关键词2] [关键词3]${NC}"
    echo "示例："
    echo "  $0 时间戳 日期"
    echo "  $0 飞书 表格"
    echo "  $0 设计 图纸"
    echo ""
    exit 0
fi

# 构建搜索关键词
KEYWORDS="$*"
echo -e "${BLUE}📋 搜索关键词：${NC}$KEYWORDS"
echo ""

# =============================================================================
# 检查 1: Hot Memory 中的错误记录
# =============================================================================
echo -e "${BLUE}1️⃣  检查 Hot Memory 中的错误...${NC}"

ERRORS_IN_HOT=$(grep -i "\"emotion\":\"negative\"" "$HOT_MEMORY" 2>/dev/null | grep -i "$KEYWORDS" | wc -l)

if [ "$ERRORS_IN_HOT" -gt 0 ]; then
    echo -e "${RED}🚨 发现 $ERRORS_IN_HOT 条相关错误记录！${NC}"
    echo ""
    echo "最近的错误："
    grep -i "\"emotion\":\"negative\"" "$HOT_MEMORY" 2>/dev/null | \
        grep -i "$KEYWORDS" | \
        tail -3 | \
        while IFS= read -r line; do
            DESC=$(echo "$line" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
            DATE=$(echo "$line" | grep -o '"date":"[^"]*"' | cut -d'"' -f4)
            echo -e "  ${RED}❌ [$DATE]${NC} $DESC"
        done
    echo ""
    WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
else
    echo -e "${GREEN}✅ 未发现相关错误记录${NC}"
fi

echo ""

# =============================================================================
# 检查 2: Hot Memory 中的类似任务
# =============================================================================
echo -e "${BLUE}2️⃣  检查 Hot Memory 中的类似任务...${NC}"

SIMILAR_TASKS=$(grep -i "$KEYWORDS" "$HOT_MEMORY" 2>/dev/null | wc -l)

if [ "$SIMILAR_TASKS" -gt 0 ]; then
    echo -e "${YELLOW}📊 发现 $SIMILAR_TASKS 条相关任务记录${NC}"
    echo ""
    echo "最近的任务："
    grep -i "$KEYWORDS" "$HOT_MEMORY" 2>/dev/null | \
        tail -5 | \
        while IFS= read -r line; do
            DESC=$(echo "$line" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
            DATE=$(echo "$line" | grep -o '"date":"[^"]*"' | cut -d'"' -f4)
            SUCCESS=$(echo "$line" | grep -o '"success":[01]' | cut -d':' -f2)
            if [ "$SUCCESS" = "1" ]; then
                echo -e "  ${GREEN}✅ [$DATE]${NC} $DESC"
            else
                echo -e "  ${RED}❌ [$DATE]${NC} $DESC"
            fi
        done
    echo ""
    WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
else
    echo -e "${GREEN}✅ 未发现相关任务记录${NC}"
fi

echo ""

# =============================================================================
# 检查 3: 今天的错误记录
# =============================================================================
echo -e "${BLUE}3️⃣  检查今天的错误记录...${NC}"

TODAY=$(date +%Y-%m-%d)
TODAY_SIGNALS="$PAI_DIR/signals/$TODAY-signals.jsonl"

if [ -f "$TODAY_SIGNALS" ]; then
    TODAY_ERRORS=$(grep -i "\"emotion\":\"negative\"" "$TODAY_SIGNALS" 2>/dev/null | grep -i "$KEYWORDS" | wc -l)

    if [ "$TODAY_ERRORS" -gt 0 ]; then
        echo -e "${RED}🚨 今天已发生 $TODAY_ERRORS 次相关错误！${NC}"
        echo ""
        echo "今天的错误："
        grep -i "\"emotion\":\"negative\"" "$TODAY_SIGNALS" 2>/dev/null | \
            grep -i "$KEYWORDS" | \
            while IFS= read -r line; do
                DESC=$(echo "$line" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
                echo -e "  ${RED}❌${NC} $DESC"
            done
        echo ""
        WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
    else
        echo -e "${GREEN}✅ 今天没有相关错误${NC}"
    fi
else
    echo -e "${GREEN}✅ 今天还没有记录${NC}"
fi

echo ""
echo "======================================"

# =============================================================================
# 总结和建议
# =============================================================================

if [ "$WARNINGS_FOUND" -gt 0 ]; then
    echo -e "${RED}⚠️  检查完成：发现 $WARNINGS_FOUND 个警告${NC}"
    echo ""
    echo -e "${YELLOW}💡 建议：${NC}"
    echo "1. 仔细查看上面的历史错误和任务"
    echo "2. 确认不会重复犯错"
    echo "3. 参考成功任务的经验"
    echo ""
    echo -e "${RED}🚨 是否继续执行？(Ctrl+C 取消，回车继续)${NC}"
    read
else
    echo -e "${GREEN}✅ 检查完成：未发现问题${NC}"
    echo ""
    echo -e "${GREEN}🚀 可以安全执行任务！${NC}"
fi

echo ""
