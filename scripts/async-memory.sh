#!/bin/bash
# 异步批量写入记忆系统 - Bash 包装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本位置
PYTHON_SCRIPT="/root/.openclaw/workspace/scripts/async-memory-writer-v2.py"

# 帮助信息
show_help() {
    echo "📝 异步批量写入记忆系统"
    echo ""
    echo "用法: $0 <action> [options]"
    echo ""
    echo "操作:"
    echo "  start     - 启动异步写入器"
    echo "  stop      - 停止异步写入器"
    echo "  flush     - 立即刷新缓冲区"
    echo "  status    - 查看状态"
    echo "  test      - 测试写入"
    echo ""
    echo "测试选项:"
    echo "  --type    - 消息类型 (conversation|system|event)"
    echo "  --content - 消息内容"
    echo ""
    echo "示例:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 test --type conversation --content '测试消息'"
    echo "  $0 flush"
    echo "  $0 stop"
    echo ""
}

# 检查 Python 脚本
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ Python 脚本不存在: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# 参数处理
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

action="$1"
shift

# 执行操作
case "$action" in
    start)
        echo -e "${BLUE}🚀 启动异步写入器...${NC}"
        python3 "$PYTHON_SCRIPT" start
        echo -e "${GREEN}✓ 已启动${NC}"
        ;;

    stop)
        echo -e "${BLUE}🛑 停止异步写入器...${NC}"
        python3 "$PYTHON_SCRIPT" stop
        echo -e "${GREEN}✓ 已停止${NC}"
        ;;

    flush)
        echo -e "${BLUE}💾 刷新缓冲区...${NC}"
        python3 "$PYTHON_SCRIPT" flush
        echo -e "${GREEN}✓ 已刷新${NC}"
        ;;

    status)
        echo -e "${BLUE}📊 状态:${NC}"
        python3 "$PYTHON_SCRIPT" status
        ;;

    test)
        echo -e "${BLUE}🧪 测试写入...${NC}"
        python3 "$PYTHON_SCRIPT" test "$@"
        ;;

    --help|-h)
        show_help
        exit 0
        ;;

    *)
        echo -e "${RED}❌ 未知操作: $action${NC}"
        show_help
        exit 1
        ;;
esac
