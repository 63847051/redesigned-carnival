#!/bin/bash

##############################################################################
# 并行执行调度脚本
# 基于 ClawCorp DP-CC-001: 任务依赖调度模式
##############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
MAX_PARALLEL=5  # 最大并行任务数
TASKS_DIR="${HOME}/.openclaw/workspace/tasks"
QUEUE_FILE="${TASKS_DIR}/priority-queue.json"
STATUS_FILE="${TASKS_DIR}/execution-status.json"

##############################################################################
# 函数：初始化执行状态
##############################################################################
init_status() {
    cat > "${STATUS_FILE}" << EOF
{
  "version": "1.0.0",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "max_parallel": ${MAX_PARALLEL},
  "running": [],
  "completed": [],
  "failed": [],
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
}

##############################################################################
# 函数：获取当前运行中的任务数
##############################################################################
get_running_count() {
    if [ ! -f "${STATUS_FILE}" ]; then
        echo 0
        return
    fi

    jq '.running | length' "${STATUS_FILE}"
}

##############################################################################
# 函数：检查是否可以启动新任务
##############################################################################
can_start_task() {
    local running_count=$(get_running_count)
    [ "${running_count}" -lt "${MAX_PARALLEL}" ]
}

##############################################################################
# 函数：启动任务
##############################################################################
start_task() {
    local task_id="$1"

    echo -e "${BLUE}🚀 启动任务: ${task_id}${NC}"

    # 检查是否可以启动新任务
    if ! can_start_task; then
        echo -e "${YELLOW}⚠️  已达到最大并行数 (${MAX_PARALLEL})${NC}" >&2
        return 1
    fi

    # 检查任务是否存在
    if [ ! -f "${TASKS_DIR}/${task_id}.json" ]; then
        echo -e "${RED}❌ 任务不存在: ${task_id}${NC}" >&2
        return 1
    fi

    # 更新任务状态为运行中
    jq --arg tid "${task_id}" \
       --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.running += [{"task_id": $tid, "started_at": $ts}] | .last_updated = $ts' \
       "${STATUS_FILE}" > "${STATUS_FILE}.tmp"
    mv "${STATUS_FILE}.tmp" "${STATUS_FILE}"

    # 更新任务文件状态
    jq --arg s "running" \
       --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.status = $s | .started_at = $ts' \
       "${TASKS_DIR}/${task_id}.json" > "${TASKS_DIR}/${task_id}.json.tmp"
    mv "${TASKS_DIR}/${task_id}.json.tmp" "${TASKS_DIR}/${task_id}.json"

    echo -e "${GREEN}✅ 任务已启动: ${task_id}${NC}"
    return 0
}

##############################################################################
# 函数：完成任务
##############################################################################
complete_task() {
    local task_id="$1"
    local success="${2:-true}"

    echo -e "${BLUE}🏁 完成任务: ${task_id}${NC}"

    # 从运行中列表移除
    jq --arg tid "${task_id}" \
       --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.running |= map(select(.task_id != $tid)) | .last_updated = $ts' \
       "${STATUS_FILE}" > "${STATUS_FILE}.tmp"
    mv "${STATUS_FILE}.tmp" "${STATUS_FILE}"

    # 添加到已完成或失败列表
    if ${success}; then
        jq --arg tid "${task_id}" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '.completed += [{"task_id": $tid, "completed_at": $ts}] | .last_updated = $ts' \
           "${STATUS_FILE}" > "${STATUS_FILE}.tmp"
        mv "${STATUS_FILE}.tmp" "${STATUS_FILE}"

        # 更新任务文件状态
        jq --arg s "completed" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '.status = $s | .completed_at = $ts' \
           "${TASKS_DIR}/${task_id}.json" > "${TASKS_DIR}/${task_id}.json.tmp"
        mv "${TASKS_DIR}/${task_id}.json.tmp" "${TASKS_DIR}/${task_id}.json"

        echo -e "${GREEN}✅ 任务已完成: ${task_id}${NC}"
    else
        jq --arg tid "${task_id}" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '.failed += [{"task_id": $tid, "failed_at": $ts}] | .last_updated = $ts' \
           "${STATUS_FILE}" > "${STATUS_FILE}.tmp"
        mv "${STATUS_FILE}.tmp" "${STATUS_FILE}"

        # 更新任务文件状态
        jq --arg s "failed" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '.status = $s | .failed_at = $ts' \
           "${TASKS_DIR}/${task_id}.json" > "${TASKS_DIR}/${task_id}.json.tmp"
        mv "${TASKS_DIR}/${task_id}.json.tmp" "${TASKS_DIR}/${task_id}.json"

        echo -e "${RED}❌ 任务已失败: ${task_id}${NC}"
    fi
}

##############################################################################
# 函数：调度并启动可执行任务
##############################################################################
schedule_tasks() {
    echo -e "${BLUE}📋 调度任务${NC}"
    echo ""

    # 初始化状态文件（如果不存在）
    if [ ! -f "${STATUS_FILE}" ]; then
        init_status
    fi

    # 获取当前运行中的任务数
    local running_count=$(get_running_count)
    local slots_available=$((MAX_PARALLEL - running_count))

    echo "最大并行数: ${MAX_PARALLEL}"
    echo "运行中任务: ${running_count}"
    echo "可用槽位: ${slots_available}"
    echo ""

    if [ ${slots_available} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  无可用槽位${NC}"
        return 0
    fi

    # 获取可执行任务
    local runnable_tasks=()
    for task_file in "${TASKS_DIR}"/*.json; do
        if [ -f "${task_file}" ]; then
            local task_id=$(basename "${task_file}" .json)
            local task_data=$(cat "${task_file}")
            local task_status=$(echo "${task_data}" | jq -r '.status // "pending"')

            # 只处理 pending 状态的任务
            if [ "${task_status}" = "pending" ]; then
                # 检查依赖
                local can_run=true
                local depends_on=$(echo "${task_data}" | jq -r '.depends_on // []')

                for dep_id in $(echo "${depends_on}" | jq -r '.[]'); do
                    if [ -f "${TASKS_DIR}/${dep_id}.json" ]; then
                        local dep_status=$(jq -r '.status // "pending"' "${TASKS_DIR}/${dep_id}.json")
                        if [ "${dep_status}" != "completed" ]; then
                            can_run=false
                            break
                        fi
                    else
                        can_run=false
                        break
                    fi
                done

                if ${can_run}; then
                    runnable_tasks+=("${task_id}")
                fi
            fi
        fi
    done

    if [ ${#runnable_tasks[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  无可执行任务${NC}"
        return 0
    fi

    echo "可执行任务: ${#runnable_tasks[@]}"
    echo ""

    # 启动任务（最多 slots_available 个）
    local started=0
    for task_id in "${runnable_tasks[@]}"; do
        if [ ${started} -ge ${slots_available} ]; then
            break
        fi

        if start_task "${task_id}"; then
            started=$((started + 1))
        fi
    done

    echo ""
    echo -e "${GREEN}✅ 已启动 ${started} 个任务${NC}"
}

##############################################################################
# 函数：显示执行状态
##############################################################################
show_status() {
    echo -e "${BLUE}📊 执行状态${NC}"
    echo ""

    if [ ! -f "${STATUS_FILE}" ]; then
        echo -e "${YELLOW}⚠️  无执行状态${NC}"
        return 0
    fi

    local running_count=$(jq '.running | length' "${STATUS_FILE}")
    local completed_count=$(jq '.completed | length' "${STATUS_FILE}")
    local failed_count=$(jq '.failed | length' "${STATUS_FILE}")

    echo "运行中: ${running_count}"
    if [ ${running_count} -gt 0 ]; then
        jq -r '.running[] | "  \(.task_id) (开始时间: \(.started_at))"' "${STATUS_FILE}"
    fi
    echo ""

    echo "已完成: ${completed_count}"
    if [ ${completed_count} -gt 0 ]; then
        jq -r '.completed[] | "  \(.task_id) (完成时间: \(.completed_at))"' "${STATUS_FILE}"
    fi
    echo ""

    echo "已失败: ${failed_count}"
    if [ ${failed_count} -gt 0 ]; then
        jq -r '.failed[] | "  \(.task_id) (失败时间: \(.failed_at))"' "${STATUS_FILE}"
    fi
    echo ""

    local total=$((running_count + completed_count + failed_count))
    echo "总计: ${total}"
}

##############################################################################
# 函数：重置执行状态
##############################################################################
reset_status() {
    echo -e "${YELLOW}🔄 重置执行状态${NC}"

    init_status

    echo -e "${GREEN}✅ 执行状态已重置${NC}"
}

##############################################################################
# 函数：打印使用说明
##############################################################################
usage() {
    echo "🚀 并行执行调度脚本"
    echo ""
    echo "用法:"
    echo "  $0 schedule              调度并启动可执行任务"
    echo "  $0 start <task-id>       启动指定任务"
    echo "  $0 complete <task-id> [success|fail]  完成指定任务"
    echo "  $0 status                显示执行状态"
    echo "  $0 reset                 重置执行状态"
    echo ""
    echo "配置:"
    echo "  MAX_PARALLEL=${MAX_PARALLEL} (最大并行任务数)"
    echo ""
    echo "示例:"
    echo "  $0 schedule"
    echo "  $0 start TASK-001"
    echo "  $0 complete TASK-001 success"
    echo "  $0 status"
    echo ""
}

##############################################################################
# 主函数
##############################################################################
main() {
    local command="$1"
    shift || true

    # 确保任务目录存在
    mkdir -p "${TASKS_DIR}"

    case "${command}" in
        schedule)
            schedule_tasks
            ;;
        start)
            if [ -z "$1" ]; then
                echo -e "${RED}❌ 错误: 请提供任务ID${NC}" >&2
                usage
                exit 1
            fi

            # 初始化状态文件（如果不存在）
            if [ ! -f "${STATUS_FILE}" ]; then
                init_status
            fi

            start_task "$1"
            ;;
        complete)
            if [ -z "$1" ]; then
                echo -e "${RED}❌ 错误: 请提供任务ID${NC}" >&2
                usage
                exit 1
            fi

            local success="${2:-true}"
            if [ "${success}" = "success" ] || [ "${success}" = "true" ]; then
                success=true
            elif [ "${success}" = "fail" ] || [ "${success}" = "false" ]; then
                success=false
            fi

            # 初始化状态文件（如果不存在）
            if [ ! -f "${STATUS_FILE}" ]; then
                init_status
            fi

            complete_task "$1" "${success}"
            ;;
        status)
            show_status
            ;;
        reset)
            reset_status
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
