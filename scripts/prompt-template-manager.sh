#!/bin/bash

##############################################################################
# Prompt 模板管理脚本
# 基于 ClawCorp DP-CC-004: Prompt 模板模式
##############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Prompt 模板目录
PROMPTS_DIR="${HOME}/.openclaw/workspace/prompts"

##############################################################################
# 函数：列出所有模板
##############################################################################
list_templates() {
    echo -e "${BLUE}Prompt 模板列表${NC}"
    echo ""

    if [ ! -d "${PROMPTS_DIR}" ]; then
        echo -e "${YELLOW}Prompts 目录不存在${NC}"
        return 1
    fi

    for template in "${PROMPTS_DIR}"/*.md; do
        if [ -f "${template}" ]; then
            local name=$(basename "${template}" .md)
            local size=$(wc -c < "${template}")
            echo -e "${GREEN}✓${NC} ${name} (${size} 字节)"
        fi
    done
}

##############################################################################
# 函数：显示模板内容
##############################################################################
show_template() {
    local template_name="$1"

    if [ -z "${template_name}" ]; then
        echo -e "${RED}错误: 请提供模板名称${NC}"
        return 1
    fi

    local template_file="${PROMPTS_DIR}/${template_name}.md"

    if [ ! -f "${template_file}" ]; then
        echo -e "${RED}错误: 模板不存在: ${template_name}${NC}"
        return 1
    fi

    echo -e "${BLUE}模板内容: ${template_name}${NC}"
    echo ""
    cat "${template_file}"
}

##############################################################################
# 函数：应用模板
##############################################################################
apply_template() {
    local template_name="$1"
    local output_file="$2"
    shift 2 || true

    if [ -z "${template_name}" ] || [ -z "${output_file}" ]; then
        echo -e "${RED}错误: 请提供模板名称和输出文件${NC}"
        return 1
    fi

    local template_file="${PROMPTS_DIR}/${template_name}.md"

    if [ ! -f "${template_file}" ]; then
        echo -e "${RED}错误: 模板不存在: ${template_name}${NC}"
        return 1
    fi

    # 复制模板到输出文件
    cp "${template_file}" "${output_file}"

    echo -e "${GREEN}模板已应用${NC}"
    echo "模板: ${template_name}"
    echo "输出: ${output_file}"
}

##############################################################################
# 函数：验证模板
##############################################################################
validate_template() {
    local template_name="$1"

    if [ -z "${template_name}" ]; then
        echo -e "${RED}错误: 请提供模板名称${NC}"
        return 1
    fi

    local template_file="${PROMPTS_DIR}/${template_name}.md"

    if [ ! -f "${template_file}" ]; then
        echo -e "${RED}错误: 模板不存在: ${template_name}${NC}"
        return 1
    fi

    echo -e "${BLUE}验证模板: ${template_name}${NC}"
    echo ""

    # 检查必需部分
    local required_sections=("角色定位" "输入要求" "输出要求" "质量标准")

    for section in "${required_sections[@]}"; do
        if grep -q "${section}" "${template_file}"; then
            echo -e "${GREEN}✓${NC} ${section}"
        else
            echo -e "${RED}✗${NC} ${section} 缺失"
        fi
    done
}

##############################################################################
# 函数：显示帮助
##############################################################################
usage() {
    echo "Prompt 模板管理脚本"
    echo ""
    echo "用法:"
    echo "  $0 list                      列出所有模板"
    echo "  $0 show TEMPLATE             显示模板内容"
    echo "  $0 apply TEMPLATE OUTPUT      应用模板到文件"
    echo "  $0 validate TEMPLATE          验证模板"
    echo ""
    echo "模板:"
    echo "  tech-task-template          技术任务模板"
    echo "  log-task-template           日志任务模板"
    echo "  design-task-template        设计任务模板"
    echo ""
}

##############################################################################
# 主函数
##############################################################################
main() {
    local command="$1"
    shift || true

    case "${command}" in
        list)
            list_templates
            ;;
        show)
            if [ -z "$1" ]; then
                echo "错误: 请提供模板名称"
                usage
                exit 1
            fi
            show_template "$1"
            ;;
        apply)
            if [ -z "$1" ] || [ -z "$2" ]; then
                echo "错误: 请提供模板名称和输出文件"
                usage
                exit 1
            fi
            apply_template "$1" "$2"
            ;;
        validate)
            if [ -z "$1" ]; then
                echo "错误: 请提供模板名称"
                usage
                exit 1
            fi
            validate_template "$1"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
