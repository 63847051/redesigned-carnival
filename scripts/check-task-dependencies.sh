#!/bin/bash

##############################################################################
# 任务依赖检查脚本
# 基于 ClawCorp DP-CC-001: 任务依赖调度模式
##############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 任务状态定义
STATUS_PENDING="pending"
STATUS_RUNNING="running"
STATUS_COMPLETED="completed"
STATUS_FAILED="failed"

# 任务存储目录
TASKS_DIR="${HOME}/.openclaw/workspace/tasks"
mkdir -p "${TASKS_DIR}"

##############################################################################
# 函数：打印使用说明
##############################################################################
usage() {
    echo "🔍 任务依赖检查脚本"
    echo ""
    echo "用法:"
    echo "  $0 check <task-id>           检查单个任务的依赖"
    echo "  $0 list                      列出所有任务"
    echo "  $0 runnable                  列出所有可执行的任务"
    echo "  $0 graph                     生成任务依赖图"
    echo "  $0 add <task-id> <deps>      添加任务依赖"
    echo "  $0 init                      初始化任务系统"
    echo ""
    echo "示例:"
    echo "  $0 check TASK-001"
    echo "  $0 runnable"
    echo "  $0 add TASK-002 TASK-001,TASK-003"
    echo ""
}

##############################################################################
# 函数：初始化任务系统
##############################################################################
init_tasks() {
    echo -e "${BLUE}🔧 初始化任务系统...${NC}"

    # 创建任务存储目录
    mkdir -p "${TASKS_DIR}"

    # 创建任务索引文件
    if [ ! -f "${TASKS_DIR}/index.json" ]; then
        cat > "${TASKS_DIR}/index.json" << EOF
{
  "version": "1.0.0",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "tasks": [],
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
        echo -e "${GREEN}✅ 任务系统初始化完成${NC}"
    else
        echo -e "${YELLOW}⚠️  任务系统已存在${NC}"
    fi
}

##############################################################################
# 函数：获取任务文件路径
##############################################################################
get_task_file() {
    local task_id="$1"
    echo "${TASKS_DIR}/${task_id}.json"
}

##############################################################################
# 函数：检查任务是否存在
##############################################################################
task_exists() {
    local task_id="$1"
    local task_file=$(get_task_file "${task_id}")
    [ -f "${task_file}" ]
}

##############################################################################
# 函数：加载任务数据
##############################################################################
load_task() {
    local task_id="$1"
    local task_file=$(get_task_file "${task_id}")

    if [ ! -f "${task_file}" ]; then
        echo -e "${RED}❌ 任务不存在: ${task_id}${NC}" >&2
        return 1
    fi

    cat "${task_file}"
}

##############################################################################
# 函数：检查任务依赖
##############################################################################
check_task_dependencies() {
    local task_id="$1"

    echo -e "${BLUE}🔍 检查任务依赖: ${task_id}${NC}"
    echo ""

    # 检查任务是否存在
    if ! task_exists "${task_id}"; then
        echo -e "${RED}❌ 任务不存在: ${task_id}${NC}"
        return 1
    fi

    # 加载任务数据
    local task_data=$(load_task "${task_id}")
    local task_status=$(echo "${task_data}" | jq -r '.status // "pending"')
    local depends_on=$(echo "${task_data}" | jq -r '.depends_on // []')

    # 打印任务状态
    echo -e "📋 任务状态: ${task_status}"
    echo ""

    # 如果没有依赖，直接可执行
    if [ "${depends_on}" = "[]" ]; then
        echo -e "${GREEN}✅ 无依赖任务，可以执行${NC}"
        return 0
    fi

    # 检查依赖任务
    echo -e "📊 依赖任务检查:"
    echo ""

    local all_completed=true
    local has_failed=false

    # 遍历依赖任务
    for dep_id in $(echo "${depends_on}" | jq -r '.[]'); do
        if task_exists "${dep_id}"; then
            local dep_data=$(load_task "${dep_id}")
            local dep_status=$(echo "${dep_data}" | jq -r '.status // "pending"')

            case "${dep_status}" in
                ${STATUS_COMPLETED})
                    echo -e "  ${GREEN}✅${NC} ${dep_id} - 已完成"
                    ;;
                ${STATUS_RUNNING})
                    echo -e "  ${YELLOW}🔄${NC} ${dep_id} - 运行中"
                    all_completed=false
                    ;;
                ${STATUS_PENDING})
                    echo -e "  ${BLUE}⏳${NC} ${dep_id} - 待执行"
                    all_completed=false
                    ;;
                ${STATUS_FAILED})
                    echo -e "  ${RED}❌${NC} ${dep_id} - 失败"
                    all_completed=false
                    has_failed=true
                    ;;
                *)
                    echo -e "  ${YELLOW}⚠️${NC}  ${dep_id} - 未知状态 (${dep_status})"
                    all_completed=false
                    ;;
            esac
        else
            echo -e "  ${RED}❌${NC} ${dep_id} - 不存在"
            all_completed=false
            has_failed=true
        fi
    done

    echo ""

    # 判断是否可执行
    if ${has_failed}; then
        echo -e "${RED}❌ 存在失败的依赖任务，无法执行${NC}"
        return 1
    elif ${all_completed}; then
        echo -e "${GREEN}✅ 所有依赖已完成，可以执行${NC}"
        return 0
    else
        echo -e "${YELLOW}⏳ 存在未完成的依赖任务，等待执行${NC}"
        return 2
    fi
}

##############################################################################
# 函数：列出所有任务
##############################################################################
list_tasks() {
    echo -e "${BLUE}📋 所有任务列表${NC}"
    echo ""

    if [ ! -d "${TASKS_DIR}" ]; then
        echo -e "${YELLOW}⚠️  任务系统未初始化${NC}"
        echo "运行 '$0 init' 初始化"
        return 1
    fi

    local task_count=0

    for task_file in "${TASKS_DIR}"/*.json; do
        if [ -f "${task_file}" ]; then
            local task_id=$(basename "${task_file}" .json)
            local task_data=$(cat "${task_file}")
            local task_name=$(echo "${task_data}" | jq -r '.name // "未命名"')
            local task_status=$(echo "${task_data}" | jq -r '.status // "pending"')
            local depends_on=$(echo "${task_data}" | jq -r '.depends_on // []' | jq -r 'length')

            # 状态图标
            local status_icon=""
            case "${task_status}" in
                ${STATUS_COMPLETED}) status_icon="${GREEN}✅${NC}" ;;
                ${STATUS_RUNNING}) status_icon="${YELLOW}🔄${NC}" ;;
                ${STATUS_PENDING}) status_icon="${BLUE}⏳${NC}" ;;
                ${STATUS_FAILED}) status_icon="${RED}❌${NC}" ;;
                *) status_icon="${YELLOW}⚠️${NC}" ;;
            esac

            echo -e "${status_icon} ${task_id} - ${task_name}"
            echo "   状态: ${task_status} | 依赖: ${depends_on} 个"
            echo ""
            task_count=$((task_count + 1))
        fi
    done

    if [ ${task_count} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  暂无任务${NC}"
    else
        echo -e "总计: ${task_count} 个任务"
    fi
}

##############################################################################
# 函数：列出所有可执行的任务
##############################################################################
list_runnable_tasks() {
    echo -e "${BLUE}🚀 可执行任务列表${NC}"
    echo ""

    if [ ! -d "${TASKS_DIR}" ]; then
        echo -e "${YELLOW}⚠️  任务系统未初始化${NC}"
        return 1
    fi

    local runnable_count=0

    for task_file in "${TASKS_DIR}"/*.json; do
        if [ -f "${task_file}" ]; then
            local task_id=$(basename "${task_file}" .json)
            local task_data=$(cat "${task_file}")
            local task_status=$(echo "${task_data}" | jq -r '.status // "pending"')

            # 只检查 pending 状态的任务
            if [ "${task_status}" = "${STATUS_PENDING}" ]; then
                # 检查依赖
                local can_run=true
                local depends_on=$(echo "${task_data}" | jq -r '.depends_on // []')

                for dep_id in $(echo "${depends_on}" | jq -r '.[]'); do
                    if task_exists "${dep_id}"; then
                        local dep_data=$(load_task "${dep_id}")
                        local dep_status=$(echo "${dep_data}" | jq -r '.status // "pending"')

                        if [ "${dep_status}" != "${STATUS_COMPLETED}" ]; then
                            can_run=false
                            break
                        fi
                    else
                        can_run=false
                        break
                    fi
                done

                if ${can_run}; then
                    local task_name=$(echo "${task_data}" | jq -r '.name // "未命名"')
                    echo -e "${GREEN}✅${NC} ${task_id} - ${task_name}"
                    runnable_count=$((runnable_count + 1))
                fi
            fi
        fi
    done

    echo ""
    if [ ${runnable_count} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  暂无可执行任务${NC}"
    else
        echo -e "可执行: ${runnable_count} 个任务"
    fi
}

##############################################################################
# 函数：生成任务依赖图
##############################################################################
generate_dependency_graph() {
    echo -e "${BLUE}📊 任务依赖图${NC}"
    echo ""

    if [ ! -d "${TASKS_DIR}" ]; then
        echo -e "${YELLOW}⚠️  任务系统未初始化${NC}"
        return 1
    fi

    # 使用 Graphviz 格式生成依赖图
    echo "digraph TaskDependencies {"
    echo "  rankdir=LR;"
    echo "  node [shape=box];"
    echo ""

    for task_file in "${TASKS_DIR}"/*.json; do
        if [ -f "${task_file}" ]; then
            local task_id=$(basename "${task_file}" .json)
            local task_data=$(cat "${task_file}")
            local task_status=$(echo "${task_data}" | jq -r '.status // "pending"')
            local depends_on=$(echo "${task_data}" | jq -r '.depends_on // []')

            # 根据状态设置颜色
            local color="lightgray"
            case "${task_status}" in
                ${STATUS_COMPLETED}) color="lightgreen" ;;
                ${STATUS_RUNNING}) color="lightyellow" ;;
                ${STATUS_PENDING}) color="lightgray" ;;
                ${STATUS_FAILED}) color="lightcoral" ;;
            esac

            echo "  \"${task_id}\" [fillcolor=${color}, style=filled];"

            # 绘制依赖关系
            for dep_id in $(echo "${depends_on}" | jq -r '.[]'); do
                echo "  \"${dep_id}\" -> \"${task_id}\";"
            done
        fi
    done

    echo "}"
    echo ""
    echo "提示: 将上述内容保存为 .dot 文件，使用 Graphviz 可视化"
}

##############################################################################
# 函数：添加任务依赖
##############################################################################
add_task_dependency() {
    local task_id="$1"
    local dependencies="$2"

    echo -e "${BLUE}🔗 添加任务依赖${NC}"
    echo ""

    # 检查任务是否存在
    if ! task_exists "${task_id}"; then
        echo -e "${RED}❌ 任务不存在: ${task_id}${NC}"
        return 1
    fi

    # 解析依赖列表
    IFS=',' read -ra DEPS <<< "${dependencies}"
    local dep_array=()

    for dep_id in "${DEPS[@]}"; do
        dep_id=$(echo "${dep_id}" | xargs) # 去除空格
        if task_exists "${dep_id}"; then
            dep_array+=("\"${dep_id}\"")
        else
            echo -e "${YELLOW}⚠️  依赖任务不存在: ${dep_id}${NC}"
        fi
    done

    # 更新任务依赖
    local task_file=$(get_task_file "${task_id}")
    local deps_json=$(printf '%s\n' "${dep_array[@]}" | jq -R . | jq -s .)

    jq --argjson deps "${deps_json}" \
       '.depends_on = $deps' "${task_file}" > "${task_file}.tmp"
    mv "${task_file}.tmp" "${task_file}"

    echo -e "${GREEN}✅ 任务依赖已更新${NC}"
    echo ""
    echo "任务: ${task_id}"
    echo "依赖: $(echo "${deps_json}" | jq -r 'join(", ")')"
}

##############################################################################
# 主函数
##############################################################################
main() {
    local command="$1"
    shift || true

    case "${command}" in
        init)
            init_tasks
            ;;
        check)
            if [ -z "$1" ]; then
                echo -e "${RED}❌ 错误: 请提供任务ID${NC}" >&2
                usage
                exit 1
            fi
            check_task_dependencies "$1"
            ;;
        list)
            list_tasks
            ;;
        runnable)
            list_runnable_tasks
            ;;
        graph)
            generate_dependency_graph
            ;;
        add)
            if [ -z "$1" ] || [ -z "$2" ]; then
                echo -e "${RED}❌ 错误: 请提供任务ID和依赖列表${NC}" >&2
                usage
                exit 1
            fi
            add_task_dependency "$1" "$2"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
