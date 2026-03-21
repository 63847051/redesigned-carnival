#!/bin/bash

##############################################################################
# 集成工作流脚本
# 基于 ClawCorp DP-CC-001 到 DP-CC-004 的完整集成
##############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 脚本目录
SCRIPTS_DIR="${HOME}/.openclaw/workspace/scripts"
TASKS_DIR="${HOME}/.openclaw/workspace/tasks"
PROMPTS_DIR="${HOME}/.openclaw/workspace/prompts"

##############################################################################
# 函数：显示帮助
##############################################################################
usage() {
    echo "集成工作流脚本"
    echo ""
    echo "用法:"
    echo "  $0 execute TASK-ID TYPE REQUIREMENT OUTPUT"
    echo ""
    echo "示例:"
    echo "  $0 execute TASK-001 tech \"写一个Python脚本\" /root/output"
    echo "  $0 execute TASK-002 log \"更新工作日志\" /root/output"
    echo ""
}

##############################################################################
# 函数：执行完整工作流
##############################################################################
execute_workflow() {
    local task_id="$1"
    local task_type="$2"
    local requirement="$3"
    local output_dir="$4"

    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}   集成工作流执行${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
    echo "任务: ${task_id}"
    echo "类型: ${task_type}"
    echo "需求: ${requirement}"
    echo "输出: ${output_dir}"
    echo ""

    # Step 1: 检查任务依赖
    echo -e "${YELLOW}Step 1: 检查任务依赖${NC}"
    "${SCRIPTS_DIR}/check-task-dependencies.sh" check "${task_id}" || {
        echo -e "${RED}任务依赖检查失败${NC}"
        return 1
    }
    echo ""

    # Step 2: 分配专家
    echo -e "${YELLOW}Step 2: 分配专家${NC}"
    "${SCRIPTS_DIR}/allocate-experts-fixed.sh" allocate "${task_id}" "${task_type}" || {
        echo -e "${RED}专家分配失败${NC}"
        return 1
    }
    echo ""

    # Step 3: 应用 Prompt 模板
    echo -e "${YELLOW}Step 3: 应用 Prompt 模板${NC}"
    local template_file="${PROMPTS_DIR}/${task_type}-task-template.md"
    if [ -f "${template_file}" ]; then
        echo "使用模板: ${template_file}"
    else
        echo -e "${YELLOW}未找到模板，使用默认流程${NC}"
    fi
    echo ""

    # Step 4: 执行任务
    echo -e "${YELLOW}Step 4: 执行任务${NC}"
    echo "任务类型: ${task_type}"
    echo "需求: ${requirement}"
    echo "输出目录: ${output_dir}"
    echo ""
    
    # 创建输出目录
    mkdir -p "${output_dir}"
    
    # 记录任务信息
    cat > "${output_dir}/task-info.json" << EOF
{
  "task_id": "${task_id}",
  "task_type": "${task_type}",
  "requirement": "${requirement}",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

    echo -e "${GREEN}任务已记录${NC}"
    echo ""

    # Step 5: 质量检查
    echo -e "${YELLOW}Step 5: 质量检查${NC}"
    "${SCRIPTS_DIR}/task-quality-check.sh" check "${task_id}" "${task_type}" "${output_dir}" || {
        echo -e "${YELLOW}质量检查警告${NC}"
    }
    echo ""

    # Step 6: 释放专家
    echo -e "${YELLOW}Step 6: 释放专家${NC}"
    "${SCRIPTS_DIR}/allocate-experts-fixed.sh" release "${task_id}" "${task_type}"
    echo ""

    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}   工作流执行完成${NC}"
    echo -e "${GREEN}======================================${NC}"
}

##############################################################################
# 函数：显示状态
##############################################################################
show_status() {
    echo -e "${BLUE}系统状态${NC}"
    echo ""

    # 专家池状态
    echo "专家池状态:"
    "${SCRIPTS_DIR}/allocate-experts-fixed.sh" status
    echo ""

    # 资源使用情况
    echo "资源使用情况:"
    "${SCRIPTS_DIR}/monitor-expert-resources.sh" usage
    echo ""
}

##############################################################################
# 主函数
##############################################################################
main() {
    local command="$1"
    shift || true

    case "${command}" in
        execute)
            if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
                echo "错误: 请提供任务ID、类型、需求和输出目录"
                usage
                exit 1
            fi
            execute_workflow "$1" "$2" "$3" "$4"
            ;;
        status)
            show_status
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
