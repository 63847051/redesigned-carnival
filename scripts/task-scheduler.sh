#!/bin/bash
# 后台任务调度器 - Bash 包装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本位置
PYTHON_SCRIPT="/root/.openclaw/workspace/scripts/task-scheduler.py"
PID_FILE="/root/.openclaw/workspace/memory/.scheduler.pid"

# 帮助信息
show_help() {
    echo "⏰ 后台任务调度器"
    echo ""
    echo "用法: $0 <action> [options]"
    echo ""
    echo "操作:"
    echo "  start     - 启动调度器（后台运行）"
    echo "  stop      - 停止调度器"
    echo "  restart   - 重启调度器"
    echo "  status    - 查看状态"
    echo "  run       - 立即运行所有任务"
    echo "  test      - 测试单个任务"
    echo ""
    echo "测试选项:"
    echo "  --task    - 任务名称 (compress|layer|cleanup|optimize)"
    echo ""
    echo "示例:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 run"
    echo "  $0 test --task compress"
    echo "  $0 stop"
    echo ""
}

# 检查 Python 脚本
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ Python 脚本不存在: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# 启动调度器
start_scheduler() {
    echo -e "${BLUE}🚀 启动任务调度器...${NC}"

    # 检查是否已经运行
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  调度器已经在运行 (PID: $pid)${NC}"
            exit 0
        else
            echo -e "${YELLOW}⚠️  清理过期的 PID 文件${NC}"
            rm -f "$PID_FILE"
        fi
    fi

    # 后台启动
    nohup python3 "$PYTHON_SCRIPT" start > /dev/null 2>&1 &
    pid=$!

    # 保存 PID
    echo "$pid" > "$PID_FILE"

    echo -e "${GREEN}✓ 调度器已启动 (PID: $pid)${NC}"
    echo -e "${YELLOW}📋 定时任务:${NC}"
    echo -e "  - 记忆压缩: 每天 02:00"
    echo -e "  - 记忆分层: 每天 03:00"
    echo -e "  - 缓存清理: 每周日 04:00"
    echo -e "  - 性能优化: 每周日 05:00"
}

# 停止调度器
stop_scheduler() {
    echo -e "${BLUE}🛑 停止任务调度器...${NC}"

    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}⚠️  调度器未运行${NC}"
        exit 0
    fi

    pid=$(cat "$PID_FILE")

    if ps -p "$pid" > /dev/null 2>&1; then
        kill "$pid"
        rm -f "$PID_FILE"
        echo -e "${GREEN}✓ 调度器已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  调度器未运行（清理 PID 文件）${NC}"
        rm -f "$PID_FILE"
    fi
}

# 重启调度器
restart_scheduler() {
    echo -e "${BLUE}🔄 重启任务调度器...${NC}"
    stop_scheduler
    sleep 1
    start_scheduler
}

# 查看状态
show_status() {
    echo -e "${BLUE}📊 调度器状态:${NC}"

    if [ ! -f "$PID_FILE" ]; then
        echo -e "  状态: ${RED}未运行${NC}"
        exit 0
    fi

    pid=$(cat "$PID_FILE")

    if ps -p "$pid" > /dev/null 2>&1; then
        echo -e "  状态: ${GREEN}运行中${NC}"
        echo -e "  PID: $pid"

        # 显示运行时间
        uptime=$(ps -p "$pid" -o etime= | tr -d ' ')
        echo -e "  运行时间: $uptime"

        # 显示日志
        log_file="/root/.openclaw/workspace/memory/.scheduler.log"
        if [ -f "$log_file" ]; then
            echo -e "  日志文件: $log_file"
            echo -e ""
            echo -e "${YELLOW}最近日志:${NC}"
            tail -5 "$log_file" | sed 's/^/    /'
        fi
    else
        echo -e "  状态: ${RED}未运行（PID 文件过期）${NC}"
        rm -f "$PID_FILE"
    fi
}

# 参数处理
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

action="$1"
shift

case "$action" in
    start)
        start_scheduler
        ;;

    stop)
        stop_scheduler
        ;;

    restart)
        restart_scheduler
        ;;

    status)
        show_status
        ;;

    run)
        echo -e "${BLUE}🚀 立即运行所有任务...${NC}"
        python3 "$PYTHON_SCRIPT" run
        ;;

    test)
        if [ -z "$1" ] || [ "$1" != "--task" ]; then
            echo -e "${RED}❌ 请使用 --task 参数指定任务${NC}"
            show_help
            exit 1
        fi

        shift  # 移除 --task
        if [ -z "$1" ]; then
            echo -e "${RED}❌ 请指定任务名称${NC}"
            show_help
            exit 1
        fi

        echo -e "${BLUE}🧪 测试任务: $1${NC}"
        python3 "$PYTHON_SCRIPT" test --task "$1"
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
