#!/bin/bash
# 记忆压缩脚本
# 将每日记忆压缩成分层结构
#
# L0: 原始数据（memory/YYYY-MM-DD.md）
# L1: 关键点（memory/key-points/YYYY-MM.md）
# L2: 结构化知识（memory/structured/{people,projects,knowledge,preferences}）
# L3: 长期洞察（MEMORY.md）

set -e

# 配置
MEMORY_DIR="/root/.openclaw/workspace/memory"
KEY_POINTS_DIR="$MEMORY_DIR/key-points"
STRUCTURED_DIR="$MEMORY_DIR/structured"
MEMORY_FILE="$MEMORY_DIR/../MEMORY.md"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo "🧠 记忆压缩脚本"
    echo ""
    echo "用法: $0 [日期]"
    echo ""
    echo "参数:"
    echo "  日期        - YYYY-MM-DD 格式（默认：昨天）"
    echo ""
    echo "示例:"
    echo "  $0                    # 压缩昨天的记忆"
    echo "  $0 2026-03-28        # 压缩指定日期的记忆"
    echo ""
}

# 提取关键点（L1）
extract_key_points() {
    local daily_file="$1"
    local month_file="$2"

    echo -e "${BLUE}📝 提取关键点（L1）...${NC}"

    # 提取关键信息（日期、主题、决策、行动项）
    cat >> "$month_file" << EOF

## $(basename $daily_file .md)

### 核心事件
$(grep -E "^## |^### " "$daily_file" | head -5)

### 重要决策
$(grep -E "^✅|^❌|决策" "$daily_file" | head -3)

### 行动项
$(grep -E "^→|TODO|待办" "$daily_file" | head -3)

EOF
}

# 分类结构化知识（L2）
categorize_knowledge() {
    local daily_file="$1"
    local date="$2"

    echo -e "${BLUE}🗂️  分类结构化知识（L2）...${NC}"

    # 提取人物相关
    if grep -qiE "幸运小行星|用户|客户" "$daily_file"; then
        cat >> "$STRUCTURED_DIR/people/${date}.md" << EOF
# ${date}

$(grep -A 5 -E "幸运小行星|用户|客户" "$daily_file" | head -20)

EOF
    fi

    # 提取项目相关
    if grep -qiE "项目|任务|工作" "$daily_file"; then
        cat >> "$STRUCTURED_DIR/projects/${date}.md" << EOF
# ${date}

$(grep -A 5 -E "项目|任务|工作" "$daily_file" | head -20)

EOF
    fi

    # 提取知识相关
    if grep -qiE "学习|研究|分析|发现" "$daily_file"; then
        cat >> "$STRUCTURED_DIR/knowledge/${date}.md" << EOF
# ${date}

$(grep -A 5 -E "学习|研究|分析|发现" "$daily_file" | head -20)

EOF
    fi

    # 提取偏好相关
    if grep -qiE "喜欢|偏好|习惯|风格" "$daily_file"; then
        cat >> "$STRUCTURED_DIR/preferences/${date}.md" << EOF
# ${date}

$(grep -A 5 -E "喜欢|偏好|习惯|风格" "$daily_file" | head -20)

EOF
    fi
}

# 提炼长期洞察（L3）
extract_insights() {
    local daily_file="$1"

    echo -e "${BLUE}💎 提炼长期洞察（L3）...${NC}"

    # 检查是否有新的重要洞察需要添加到 MEMORY.md
    local insights=$(grep -E "洞察|发现|教训|经验" "$daily_file" | head -3)

    if [ -n "$insights" ]; then
        echo -e "${YELLOW}发现新洞察，请手动审查后添加到 MEMORY.md${NC}"
        echo "$insights"
    fi
}

# 主流程
main() {
    local date="${1:-$(date -d 'yesterday' +%Y-%m-%d)}"
    local daily_file="$MEMORY_DIR/${date}.md"
    local month="${date:0:7}"
    local month_file="$KEY_POINTS_DIR/${month}.md"

    # 检查日期格式
    if [[ ! "$date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo -e "${RED}❌ 日期格式错误，应为 YYYY-MM-DD${NC}"
        exit 1
    fi

    # 检查文件是否存在
    if [ ! -f "$daily_file" ]; then
        echo -e "${RED}❌ 文件不存在: $daily_file${NC}"
        exit 1
    fi

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}🧠 记忆压缩${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}日期: $date${NC}"
    echo -e "${YELLOW}文件: $daily_file${NC}"
    echo ""

    # 创建目录
    mkdir -p "$KEY_POINTS_DIR"
    mkdir -p "$STRUCTURED_DIR"/{people,projects,knowledge,preferences}

    # L1: 提取关键点
    extract_key_points "$daily_file" "$month_file"

    # L2: 分类结构化知识
    categorize_knowledge "$daily_file" "$date"

    # L3: 提炼长期洞察
    extract_insights "$daily_file"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ 压缩完成${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}📁 输出文件:${NC}"
    echo -e "  L1: $month_file"
    echo -e "  L2: $STRUCTURED_DIR/{people,projects,knowledge,preferences}/${date}.md"
    echo ""
    echo -e "${YELLOW}💡 下一步:${NC}"
    echo -e "  1. 检查生成的文件"
    echo -e "  2. 手动审查并添加重要洞察到 MEMORY.md"
    echo ""
}

# 参数处理
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

main "$@"
