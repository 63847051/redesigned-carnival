#!/bin/bash

##############################################################################
# 任务优先级队列脚本
# 基于 ClawCorp DP-CC-001: 任务依赖调度模式
##############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 任务存储目录
TASKS_DIR="${HOME}/.openclaw/workspace/tasks"
QUEUE_FILE="${TASKS_DIR}/priority-queue.json"

# 优先级定义
PRIORITY_CRITICAL=1  # 关键任务
PRIORITY_HIGH=2      # 高优先级
PRIORITY_NORMAL=3    # 普通优先级
PRIORITY_LOW=4       # 低优先级

##############################################################################
# 函数：初始化优先级队列
##############################################################################
init_queue() {
    echo -e "${BLUE}🔧 初始化优先级队列...${NC}"

    mkdir -p "${TASKS_DIR}"

    if [ ! -f "${QUEUE_FILE}" ]; then
        cat > "${QUEUE_FILE}" << EOF
{
  "version": "1.0.0",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "queue": [],
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
        echo -e "${GREEN}✅ 优先级队列初始化完成${NC}"
    else
        echo -e "${YELLOW}⚠️  优先级队列已存在${NC}"
    fi
}

##############################################################################
# 函数：添加任务到队列
##############################################################################
add_to_queue() {
    local task_id="$1"
    local priority="${2:-3}"  # 默认普通优先级

    echo -e "${BLUE}➕ 添加任务到队列${NC}"

    # 验证优先级
    if ! [[ "${priority}" =~ ^[1-4]$ ]]; then
        echo -e "${RED}❌ 无效的优先级: ${priority}${NC}" >&2
        echo "优先级必须是 1(关键) 2(高) 3(普通) 4(低)" >&2
        return 1
    fi

    # 检查任务是否已在队列中
    if jq -e ".queue[] | select(.task_id == \"${task_id}\")" "${QUEUE_FILE}" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  任务已在队列中: ${task_id}${NC}"
        return 0
    fi

    # 添加任务到队列
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    jq --arg tid "${task_id}" \
       --arg p "${priority}" \
       --arg ts "${timestamp}" \
       '.queue += [{"task_id": $tid, "priority": ($p | tonumber), "added_at": $ts}] | .queue |= sort_by(.priority)' \
       "${QUEUE_FILE}" > "${QUEUE_FILE}.tmp"
    mv "${QUEUE_FILE}.tmp" "${QUEUE_FILE}"

    # 更新时间戳
    jq --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '.last_updated = $ts' "${QUEUE_FILE}" > "${QUEUE_FILE}.tmp"
    mv "${QUEUE_FILE}.tmp" "${QUEUE_FILE}"

    echo -e "${GREEN}✅ 任务已添加到队列${NC}"
    echo "任务: ${task_id}"
    echo "优先级: ${priority}"
}

##############################################################################
# 函数：从队列中获取下一个任务
##############################################################################
get_next_task() {
    echo -e "${BLUE}🎯 获取下一个任务${NC}"
    echo ""

    # 检查队列是否为空
    local queue_size=$(jq '.queue | length' "${QUEUE_FILE}")
    if [ "${queue_size}" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  队列为空${NC}"
        return 1
    fi

    # 获取第一个任务（最高优先级）
    local next_task=$(jq '.queue[0]' "${QUEUE_FILE}")
    local task_id=$(echo "${next_task}" | jq -r '.task_id')
    local priority=$(echo "${next_task}" | jq -r '.priority')

    # 打印任务信息
    echo -e "${GREEN}✅ 下一个任务${NC}"
    echo "任务ID: ${task_id}"
    echo "优先级: ${priority}"
    echo ""

    # 从队列中移除该任务
    jq '.queue |= .[1:]' "${QUEUE_FILE}" > "${QUEUE_FILE}.tmp"
    mv "${QUEUE_FILE}.tmp" "${QUEUE_FILE}"

    # 更新时间戳
    jq --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '.last_updated = $ts' "${QUEUE_FILE}" > "${QUEUE_FILE}.tmp"
    mv "${QUEUE_FILE}.tmp" "${QUEUE_FILE}"

    echo "${task_id}"
}

##############################################################################
# 函数：列出队列中的所有任务
##############################################################################
list_queue() {
    echo -e "${BLUE}📋 优先级队列${NC}"
    echo ""

    local queue_size=$(jq '.queue | length' "${QUEUE_FILE}")
    if [ "${queue_size}" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  队列为空${NC}"
        return 0
    fi

    echo "队列大小: ${queue_size}"
    echo ""

    # 按优先级分组显示
    echo "🔴 关键任务 (Priority 1):"
    jq -r '.queue[] | select(.priority == 1) | "  \(.task_id) (添加时间: \(.added_at))"' "${QUEUE_FILE}" || echo "  无"
    echo ""

    echo "🟠 高优先级 (Priority 2):"
    jq -r '.queue[] | select(.priority == 2) | "  \(.task_id) (添加时间: \(.added_at))"' "${QUEUE_FILE}" || echo "  无"
    echo ""

    echo "🟡 普通优先级 (Priority 3):"
    jq -r '.queue[] | select(.priority == 3) | "  \(.task_id) (添加时间: \(.added_at))"' "${QUEUE_FILE}" || echo "  无"
    echo ""

    echo "🟢 低优先级 (Priority 4):"
    jq -r '.queue[] | select(.priority == 4) | "  \(.task_id) (添加时间: \(.added_at))"' "${QUEUE_FILE}" || echo "  无"
    echo ""
}

##############################################################################
# 函数：清空队列
##############################################################################
clear_queue() {
    echo -e "${YELLOW}🗑️  清空优先级队列${NC}"

    jq '.queue = [] | .last_updated = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' "${QUEUE_FILE}" > "${QUEUE_FILE}.tmp"
    mv "${QUEUE_FILE}.tmp" "${QUEUE_FILE}"

    echo -e "${GREEN}✅ 队列已清空${NC}"
}

##############################################################################
# 函数：从队列中移除任务
##############################################################################
remove_from_queue() {
    local task_id="$1"

    echo -e "${BLUE}➖ 从队列中移除任务${NC}"

    # 检查任务是否在队列中
    if ! jq -e ".queue[] | select(.task_id == \"${task_id}\")" "${QUEUE_FILE}" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  任务不在队列中: ${task_id}${NC}"
        return 0
    fi

    # 从队列中移除任务
    jq --arg tid "${task_id}" \
       '.queue |= map(select(.task_id != $tid)) | .last_updated = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' \
       "${QUEUE_FILE}" > "${QUEUE_FILE}.tmp"
    mv "${QUEUE_FILE}.tmp" "${QUEUE_FILE}"

    echo -e "${GREEN}✅ 任务已从队列中移除${NC}"
    echo "任务: ${task_id}"
}

##############################################################################
# 函数：更新任务优先级
##############################################################################
update_priority() {
    local task_id="$1"
    local new_priority="$2"

    echo -e "${BLUE}🔄 更新任务优先级${NC}"

    # 验证优先级
    if ! [[ "${new_priority}" =~ ^[1-4]$ ]]; then
        echo -e "${RED}❌ 无效的优先级: ${new_priority}${NC}" >&2
        echo "优先级必须是 1(关键) 2(高) 3(普通) 4(低)" >&2
        return 1
    fi

    # 检查任务是否在队列中
    if ! jq -e ".queue[] | select(.task_id == \"${task_id}\")" "${QUEUE_FILE}" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  任务不在队列中: ${task_id}${NC}"
        return 0
    fi

    # 更新任务优先级
    jq --arg tid "${task_id}" \
       --arg p "${new_priority}" \
       '.queue |= map((select(.task_id == $tid) | .priority = ($p | tonumber))) | sort_by(.priority) | .last_updated = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' \
       "${QUEUE_FILE}" > "${QUEUE_FILE}.tmp"
    mv "${QUEUE_FILE}.tmp" "${QUEUE_FILE}"

    echo -e "${GREEN}✅ 任务优先级已更新${NC}"
    echo "任务: ${task_id}"
    echo "新优先级: ${new_priority}"
}

##############################################################################
# 函数：打印使用说明
##############################################################################
usage() {
    echo "🎯 任务优先级队列脚本"
    echo ""
    echo "用法:"
    echo "  $0 init                      初始化优先级队列"
    echo "  $0 add <task-id> [priority]  添加任务到队列"
    echo "  $0 next                      获取下一个任务"
    echo "  $0 list                      列出队列中的所有任务"
    echo "  $0 remove <task-id>          从队列中移除任务"
    echo "  $0 update <task-id> <priority> 更新任务优先级"
    echo "  $0 clear                     清空队列"
    echo ""
    echo "优先级说明:"
    echo "  1 - 关键任务 (最高优先级)"
    echo "  2 - 高优先级"
    echo "  3 - 普通优先级 (默认)"
    echo "  4 - 低优先级"
    echo ""
    echo "示例:"
    echo "  $0 init"
    echo "  $0 add TASK-001 1"
    echo "  $0 add TASK-002 2"
    echo "  $0 next"
    echo "  $0 list"
    echo ""
}

##############################################################################
# 主函数
##############################################################################
main() {
    local command="$1"
    shift || true

    # 确保队列已初始化
    if [ "${command}" != "init" ] && [ ! -f "${QUEUE_FILE}" ]; then
        echo -e "${YELLOW}⚠️  优先级队列未初始化${NC}" >&2
        echo "运行 '$0 init' 初始化" >&2
        exit 1
    fi

    case "${command}" in
        init)
            init_queue
            ;;
        add)
            if [ -z "$1" ]; then
                echo -e "${RED}❌ 错误: 请提供任务ID${NC}" >&2
                usage
                exit 1
            fi
            add_to_queue "$1" "$2"
            ;;
        next)
            get_next_task
            ;;
        list)
            list_queue
            ;;
        remove)
            if [ -z "$1" ]; then
                echo -e "${RED}❌ 错误: 请提供任务ID${NC}" >&2
                usage
                exit 1
            fi
            remove_from_queue "$1"
            ;;
        update)
            if [ -z "$1" ] || [ -z "$2" ]; then
                echo -e "${RED}❌ 错误: 请提供任务ID和新优先级${NC}" >&2
                usage
                exit 1
            fi
            update_priority "$1" "$2"
            ;;
        clear)
            clear_queue
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
