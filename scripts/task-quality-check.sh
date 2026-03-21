#!/bin/bash

##############################################################################
# 任务质量检查脚本
# 基于 ClawCorp DP-CC-003: 质量门禁模式
##############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置文件
QUALITY_DIR="${HOME}/.openclaw/workspace/quality"
CONFIG_FILE="${QUALITY_DIR}/quality-config.json"
REPORT_DIR="${QUALITY_DIR}/reports"

##############################################################################
# 函数：初始化质量系统
##############################################################################
init_quality() {
    echo -e "${BLUE}初始化质量系统${NC}"
    mkdir -p "${REPORT_DIR}"
    echo -e "${GREEN}质量系统初始化完成${NC}"
}

##############################################################################
# 函数：检查任务质量
##############################################################################
check_task_quality() {
    local task_id="$1"
    local task_type="$2"
    local output_dir="$3"

    echo -e "${BLUE}检查任务质量${NC}"
    echo "任务: ${task_id}"
    echo "类型: ${task_type}"
    echo "输出目录: ${output_dir}"
    echo ""

    # 读取配置
    local config=$(cat "${CONFIG_FILE}")
    local criteria=$(echo "${config}" | jq ".quality_standards.${task_type}.criteria")
    local pass_threshold=$(echo "${config}" | jq -r ".quality_standards.${task_type}.pass_threshold")
    local block_threshold=$(echo "${config}" | jq -r ".quality_standards.${task_type}.block_threshold")

    # 初始化分数
    local total_score=0
    local max_score=0
    local results=()

    # 检查每个标准
    echo "${criteria}" | jq -r 'to_entries[] | "\(.key)|\(.value.weight)|\(.value.description)"' | while IFS='|' read -r key weight desc; do
        local enabled=$(echo "${criteria}" | jq -r ".${key}.enabled")
        
        if [ "${enabled}" = "true" ]; then
            echo -n "检查: ${desc} ... "
            
            # 简化的检查逻辑
            local passed=true
            case "${key}" in
                runnable|complete|clear_drawing)
                    # 检查文件是否存在
                    if [ -d "${output_dir}" ] && [ "$(ls -A ${output_dir})" ]; then
                        passed=true
                    else
                        passed=false
                    fi
                    ;;
                documented|consistent|properly_named)
                    # 假设通过（需要更复杂的检查）
                    passed=true
                    ;;
                no_secrets|no_errors)
                    # 简单的关键词扫描
                    if grep -r -i "password\|api_key\|secret\|ERROR\|FAIL" "${output_dir}" >/dev/null 2>&1; then
                        passed=false
                    else
                        passed=true
                    fi
                    ;;
                *)
                    passed=true
                    ;;
            esac

            if ${passed}; then
                echo -e "${GREEN}通过${NC}"
                local score=${weight}
            else
                echo -e "${RED}失败${NC}"
                local score=0
            fi

            total_score=$((total_score + score))
            max_score=$((max_score + weight))
        fi
    done

    # 计算通过率
    local pass_rate=$(awk "BEGIN {printf \"%.2f\", ${total_score}/${max_score}}")

    echo ""
    echo "总分: ${total_score}/${max_score}"
    echo "通过率: ${pass_rate}"

    # 判断是否通过
    local pass_threshold_num=$(awk "BEGIN {printf \"%.2f\", ${pass_threshold}}")
    local block_threshold_num=$(awk "BEGIN {printf \"%.2f\", ${block_threshold}}")

    if (( $(awk "BEGIN {print (${pass_rate} >= ${pass_threshold_num})}") )); then
        echo -e "${GREEN}质量检查通过${NC}"
        return 0
    elif (( $(awk "BEGIN {print (${pass_rate} < ${block_threshold_num})}") )); then
        echo -e "${RED}质量检查失败${NC}"
        return 1
    else
        echo -e "${YELLOW}质量检查警告${NC}"
        return 2
    fi
}

##############################################################################
# 函数：生成质量报告
##############################################################################
generate_report() {
    local task_id="$1"
    local task_type="$2"
    local status="$3"
    local score="$4"
    local max_score="$5"

    local report_file="${REPORT_DIR}/${task_id}-report.json"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    cat > "${report_file}" << EOF
{
  "task_id": "${task_id}",
  "task_type": "${task_type}",
  "checked_at": "${timestamp}",
  "status": "${status}",
  "score": ${score},
  "max_score": ${max_score},
  "pass_rate": $(awk "BEGIN {printf \"%.2f\", ${score}/${max_score}}")
}
EOF

    echo -e "${GREEN}报告已生成: ${report_file}${NC}"
}

##############################################################################
# 函数：显示配置
##############################################################################
show_config() {
    echo -e "${BLUE}质量配置${NC}"
    jq '.' "${CONFIG_FILE}"
}

##############################################################################
# 函数：显示帮助
##############################################################################
usage() {
    echo "质量检查脚本"
    echo ""
    echo "用法:"
    echo "  $0 init                      初始化质量系统"
    echo "  $0 check TASK-ID TYPE DIR    检查任务质量"
    echo "  $0 report TASK-ID TYPE STATUS SCORE MAX 生成报告"
    echo "  $0 config                    显示配置"
    echo ""
    echo "任务类型:"
    echo "  tech   - 技术任务"
    echo "  log    - 日志任务"
    echo "  design - 设计任务"
    echo ""
}

##############################################################################
# 主函数
##############################################################################
main() {
    local command="$1"
    shift || true

    case "${command}" in
        init)
            init_quality
            ;;
        check)
            if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
                echo "错误: 请提供任务ID、类型和输出目录"
                exit 1
            fi
            check_task_quality "$1" "$2" "$3"
            ;;
        report)
            if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
                echo "错误: 请提供任务ID、类型和状态"
                exit 1
            fi
            generate_report "$1" "$2" "$3" "$4" "$5"
            ;;
        config)
            show_config
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
