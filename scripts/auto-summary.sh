#!/bin/bash
# 自动摘要生成系统 - Bash 包装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本位置
PYTHON_SCRIPT="/root/.openclaw/workspace/scripts/auto-summary.py"

# 帮助信息
show_help() {
    echo "🧠 自动摘要生成系统"
    echo ""
    echo "用法: $0 [options]"
    echo ""
    echo "选项:"
    echo "  --date DATE    - 指定日期 (YYYY-MM-DD)"
    echo "  --month MONTH  - 指定月份 (YYYY-MM)"
    echo "  --layer LAYER  - 处理的层级 (l1|l2|l3|all)"
    echo ""
    echo "层级说明:"
    echo "  l1  - L0 → L1: 每日对话 → 关键点"
    echo "  l2  - L1 → L2: 月度关键点 → 结构化知识"
    echo "  l3  - L2 → L3: 分类知识 → 长期洞察"
    echo "  all - 全部层级（默认）"
    echo ""
    echo "示例:"
    echo "  $0                           # 处理所有层级（昨天的数据）"
    echo "  $0 --date 2026-03-28        # 处理指定日期"
    echo "  $0 --month 2026-03          # 处理指定月份"
    echo "  $0 --layer l1               # 只处理 L0 → L1"
    echo "  $0 --layer l2 --month 2026-03  # 处理指定月份的 L1 → L2"
    echo ""
}

# 检查 Python 脚本
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ Python 脚本不存在: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# 解析参数
ARGS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --date)
            ARGS="$ARGS --date $2"
            shift 2
            ;;
        --month)
            ARGS="$ARGS --month $2"
            shift 2
            ;;
        --layer)
            ARGS="$ARGS --layer $2"
            shift 2
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

# 执行 Python 脚本
echo -e "${BLUE}🧠 自动摘要生成系统${NC}"
echo ""
python3 "$PYTHON_SCRIPT" $ARGS

# 检查执行结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ 摘要生成完成${NC}"
else
    echo ""
    echo -e "${RED}✗ 摘要生成失败${NC}"
    exit 1
fi
