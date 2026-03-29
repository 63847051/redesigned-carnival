#!/bin/bash
# 智能任务分配脚本
# 自动将任务分配给合适的 Agent

set -e

TASK="$1"
TYPE="${2:-auto}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo "🤖 智能任务分配脚本"
    echo ""
    echo "用法: $0 \"任务描述\" [类型]"
    echo ""
    echo "类型:"
    echo "  tech    - 技术任务（代码、爬虫、API）→ 小新"
    echo "  log     - 日志任务（记录、统计）→ 小蓝"
    echo "  design  - 设计任务（图纸、平面图）→ 设计专家"
    echo "  auto    - 自动检测类型（默认）"
    echo ""
    echo "示例:"
    echo "  $0 \"写个 Python 脚本\" tech"
    echo "  $0 \"更新工作日志\" log"
    echo "  $0 \"分析这个设计图\" design"
    echo "  $0 \"帮我处理这个\" auto"
    echo ""
}

# 自动检测任务类型
auto_detect() {
    local task="$1"
    
    # 技术任务关键词
    if echo "$task" | grep -qiE "代码|爬虫|API|脚本|开发|编程|python|javascript|前端|后端|数据库"; then
        echo "tech"
    # 日志任务关键词
    elif echo "$task" | grep -qiE "日志|记录|工作|任务|进度|统计|汇总|整理"; then
        echo "log"
    # 设计任务关键词
    elif echo "$task" | grep -qiE "设计|图纸|平面图|立面图|天花|地面|排砖|柜体|会议室"; then
        echo "design"
    else
        echo "unknown"
    fi
}

# 执行任务
execute_task() {
    local task="$1"
    local type="$2"
    
    case "$type" in
        tech)
            echo -e "${BLUE}📱 分配给小新（技术专家）${NC}"
            echo -e "${GREEN}任务: $task${NC}"
            echo ""
            opencode -m opencode/minimax-m2.5-free run "$task"
            ;;
        log)
            echo -e "${YELLOW}📋 分配给小蓝（日志专家）${NC}"
            echo -e "${GREEN}任务: $task${NC}"
            echo ""
            sessions_spawn -runtime subagent -model glmcode/glm-4.5-air "$task"
            ;;
        design)
            echo -e "${PURPLE}🏠 分配给设计专家${NC}"
            echo -e "${GREEN}任务: $task${NC}"
            echo ""
            sessions_spawn -runtime subagent -model glmcode/glm-4.6 "$task"
            ;;
        *)
            echo -e "${RED}❌ 无法识别的任务类型${NC}"
            echo ""
            echo "请手动指定类型:"
            echo "  $0 \"$task\" tech|log|design"
            exit 1
            ;;
    esac
}

# 主流程
main() {
    # 检查帮助参数
    if [ "$TASK" = "--help" ] || [ "$TASK" = "-h" ]; then
        show_help
        exit 0
    fi
    
    # 检查参数
    if [ -z "$TASK" ]; then
        show_help
        exit 1
    fi
    
    # 自动检测类型
    if [ "$TYPE" = "auto" ]; then
        TYPE=$(auto_detect "$TASK")
        echo -e "${BLUE}🔍 自动检测任务类型: $TYPE${NC}"
        echo ""
    fi
    
    # 执行任务
    execute_task "$TASK" "$TYPE"
}

main "$@"
