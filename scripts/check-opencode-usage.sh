#!/bin/bash
# OpenCode CLI 使用检查脚本
# 防止错误地使用 sessions_spawn 调用 opencode 模型

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查命令是否错误使用了 sessions_spawn 调用 opencode
check_opencode_usage() {
    local command="$1"
    
    # 检查是否错误地使用了 sessions_spawn 调用 opencode
    if echo "$command" | grep -q "sessions_spawn.*opencode"; then
        echo -e "${RED}❌ 错误：不要用 sessions_spawn 调用 opencode 模型！${NC}"
        echo ""
        echo -e "${YELLOW}问题${NC}: sessions_spawn 无法访问 OpenCode CLI 的配置"
        echo -e "${YELLOW}原因${NC}: OpenCode CLI 使用自己的配置文件"
        echo ""
        echo -e "${GREEN}✅ 正确方式 1: 直接使用 OpenCode CLI${NC}"
        echo "opencode -m opencode/minimax-m2.5-free run \"任务\""
        echo ""
        echo -e "${GREEN}✅ 正确方式 2: 使用智能分配脚本${NC}"
        echo "bash /root/.openclaw/workspace/scripts/assign-task.sh \"任务\" \"tech\""
        echo ""
        return 1
    fi
    
    return 0
}

# 检查最近的命令历史
check_recent_commands() {
    echo -e "${BLUE}🔍 检查最近的命令...${NC}"
    echo ""
    
    # 查找最近 10 分钟内错误使用 sessions_spawn 调用 opencode 的命令
    local wrong_commands=$(grep -r "sessions_spawn.*opencode" ~/.bash_history 2>/dev/null | tail -5)
    
    if [ -n "$wrong_commands" ]; then
        echo -e "${RED}⚠️  发现错误的命令使用：${NC}"
        echo "$wrong_commands"
        echo ""
        echo -e "${YELLOW}请使用正确的方式：${NC}"
        echo "opencode -m opencode/minimax-m2.5-free run \"任务\""
        echo ""
        return 1
    else
        echo -e "${GREEN}✅ 最近没有错误的命令使用${NC}"
        echo ""
        return 0
    fi
}

# 主函数
main() {
    case "${1:-check}" in
        check)
            if [ -n "$2" ]; then
                check_opencode_usage "$2"
            else
                echo -e "${YELLOW}用法: $0 check \"命令\"${NC}"
                exit 1
            fi
            ;;
        history)
            check_recent_commands
            ;;
        *)
            echo "OpenCode CLI 使用检查脚本"
            echo ""
            echo "用法:"
            echo "  $0 check \"命令\"     - 检查命令是否正确"
            echo "  $0 history           - 检查命令历史"
            echo ""
            exit 0
            ;;
    esac
}

main "$@"
