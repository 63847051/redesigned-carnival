#!/bin/bash

##############################################################################
# 专家分配脚本
# 基于 ClawCorp DP-CC-002: 角色池化管理模式
##############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 专家配置目录
EXPERTS_DIR="${HOME}/.openclaw/workspace/experts"
CONFIG_FILE="${EXPERTS_DIR}/config.json"
POOL_FILE="${EXPERTS_DIR}/pool-status.json"

##############################################################################
# 函数：初始化专家系统
##############################################################################
init_experts() {
    echo -e "${BLUE}🔧 初始化专家系统...${NC}"

    mkdir -p "${EXPERTS_DIR}"

    # 创建专家配置文件
    if [ ! -f "${CONFIG_FILE}" ]; then
        cat > "${CONFIG_FILE}" << EOF
{
  "version": "1.0.0",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "experts": {
    "tech": {
      "name": "小新",
      "role": "技术支持专家",
      "max_parallel": 2,
      "model": "opencode/minimax-m2.5-free",
      "trigger_keywords": ["代码", "爬虫", "数据", "API", "前端", "脚本", "开发", "编程"]
    },
    "log": {
      "name": "小蓝",
      "role": "工作日志管理专家",
      "max_parallel": 1,
      "model": "glmcode/glm-4.5-air",
      "trigger_keywords": ["日志", "记录", "工作", "任务", "进度", "统计", "汇总"]
    },
    "design": {
      "name": "室内设计专家",
      "role": "室内设计专家",
      "max_parallel": 1,
      "model": "glmcode/glm-4.7",
      "trigger_keywords": ["设计", "图纸", "平面图", "立面图", "天花", "地面", "排砖", "柜体", "会议室"]
    }
  },
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
        echo -e "${GREEN}✅ 专家系统初始化完成${NC}"
    else
        echo -e "${YELLOW}⚠️  专家系统已存在${NC}"
    fi

    # 创建池状态文件
    if [ ! -f "${POOL_FILE}" ]; then
        cat > "${POOL_FILE}" << EOF
{
  "version": "1.0.0",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "pools": {
    "tech": {
      "total": 2,
      "available": 2,
      "running": []
    },
    "log": {
      "total": 1,
      "available": 1,
      "running": []
    },
    "design": {
      "total": 1,
      "available": 1,
      "running": []
    }
  },
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    fi
}

##############################################################################
# 函数：显示专家配置
##############################################################################
show_config() {
    echo -e "${BLUE}📋 专家配置${NC}"
    echo ""

    if [ ! -f "${CONFIG_FILE}" ]; then
        echo -e "${YELLOW}⚠️  专家系统未初始化${NC}"
        echo "运行 '$0 init' 初始化"
        return 1
    fi

    jq -r '.experts | to_entries[] | "
\(.value.name) (\(.key))
  角色: \(.value.role)
  最大并行数: \(.value.max_parallel)
  模型: \(.value.model)
  触发词: \(.value.trigger_keywords | join(", "))
"' "${CONFIG_FILE}"
}

##############################################################################
# 函数：显示池状态
##############################################################################
show_pool_status() {
    echo -e "${BLUE}📊 专家池状态${NC}"
    echo ""

    if [ ! -f "${POOL_FILE}" ]; then
        echo -e "${YELLOW}⚠️  专家池未初始化${NC}"
        echo "运行 '$0 init' 初始化"
        return 1
    fi

    jq -r '.pools | to_entries[] | "
\(.key | ascii_upcase) 池
  总数: \(.value.total)
  可用: \(.value.available)
  运行中: \(.value.running | length)
"' "${POOL_FILE}"

    echo ""

    # 显示运行中的任务
    local has_running=false
    jq -r '.pools | to_entries[] | select(.value.running | length > 0) | 
      "\(.key | ascii_upcase) 池运行中的任务:\n  \(.value.running[])"' "${POOL_FILE}" && has_running=true

    if ! ${has_running}; then
        echo -e "${GREEN}✅ 所有专家池空闲${NC}"
    fi
}

##############################################################################
# 函数：获取专家类型
##############################################################################
get_expert_type() {
    local task_description="$1"

    # 读取专家配置
    local config=$(cat "${CONFIG_FILE}")

    # 遍历每个专家类型
    while IFS= read -r expert_line; do
        local expert_key=$(echo "${expert_line}" | jq -r '.key')
        local expert_name=$(echo "${expert_line}" | jq -r '.value.name')
        local trigger_keywords=$(echo "${expert_line}" | jq -r '.value.trigger_keywords[]')

        # 检查是否包含触发词
        for keyword in ${trigger_keywords}; do
            if echo "${task_description}" | grep -qi "${keyword}"; then
                echo "${expert_key}"
                return 0
            fi
        done
    done < <(jq '.experts | to_entries[]' "${CONFIG_FILE}")

    # 如果没有匹配的专家，返回 tech（默认）
    echo "tech"
}

##############################################################################
# 函数：分配专家
##############################################################################
allocate_expert() {
    local task_id="$1"
    local task_description="$2"

    echo -e "${BLUE}👥 分配专家${NC}"
    echo ""

    # 获取专家类型
    local expert_type=$(get_expert_type "${task_description}")
    local expert_name=$(jq -r ".experts.${expert_type}.name" "${CONFIG_FILE}")
    local expert_model=$(jq -r ".experts.${expert_type}.model" "${CONFIG_FILE}")

    echo "任务: ${task_id}"
    echo "描述: ${task_description}"
    echo "专家类型: ${expert_type}"
    echo "专家: ${expert_name}"
    echo "模型: ${expert_model}"
    echo ""

    # 检查池状态
    local pool_data=$(jq ".pools.${expert_type}" "${POOL_FILE}")
    local available=$(echo "${pool_data}" | jq -r '.available')

    if [ "${available}" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  ${expert_name} 池已满，等待释放${NC}" >&2
        echo ""
        show_pool_status
        return 1
    fi

    # 分配专家
    jq --arg et "${expert_type}" \
       --arg tid "${task_id}" \
       --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.pools[$et].available -= 1 | .pools[$et].running += [$tid] | .last_updated = $ts' \
       "${POOL_FILE}" > "${POOL_FILE}.tmp"
    mv "${POOL_FILE}.tmp" "${POOL_FILE}"

    echo -e "${GREEN}✅ 专家已分配${NC}"
    echo ""
    echo "专家: ${expert_name}"
    echo "模型: ${expert_model}"

    # 返回专家信息（JSON 格式）
    echo ""
    echo "{"
    echo "  \"expert_type\": \"${expert_type}\","
    echo "  \"expert_name\": \"${expert_name}\","
    echo "  \"model\": \"${expert_model}\""
    echo "}"
}

##############################################################################
# 函数：释放专家
##############################################################################
release_expert() {
    local task_id="$1"
    local expert_type="$2"

    echo -e "${BLUE}➕ 释放专家${NC}"

    # 如果没有指定专家类型，自动查找
    if [ -z "${expert_type}" ]; then
        expert_type=$(jq -r '.pools | to_entries[] | select(.value.running[] == $tid) | .key' --arg tid "${task_id}" "${POOL_FILE}" | head -1)
    fi

    if [ -z "${expert_type}" ]; then
        echo -e "${YELLOW}⚠️  任务不在运行中: ${task_id}${NC}" >&2
        return 1
    fi

    local expert_name=$(jq -r ".experts.${expert_type}.name" "${CONFIG_FILE}")

    # 释放专家
    jq --arg et "${expert_type}" \
       --arg tid "${task_id}" \
       --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.pools[$et].available += 1 | .pools[$et].running |= map(select(. != $tid)) | .last_updated = $ts' \
       "${POOL_FILE}" > "${POOL_FILE}.tmp"
    mv "${POOL_FILE}.tmp" "${POOL_FILE}"

    echo -e "${GREEN}✅ 专家已释放${NC}"
    echo "专家: ${expert_name}"
    echo "任务: ${task_id}"
}

##############################################################################
# 函数：更新专家配置
##############################################################################
update_config() {
    local expert_type="$1"
    local setting="$2"
    local value="$3"

    echo -e "${BLUE}🔄 更新专家配置${NC}"

    # 验证专家类型
    if ! jq -e ".experts.${expert_type}" "${CONFIG_FILE}" >/dev/null 2>&1; then
        echo -e "${RED}❌ 无效的专家类型: ${expert_type}${NC}" >&2
        return 1
    fi

    # 更新配置
    case "${setting}" in
        max_parallel)
            if ! [[ "${value}" =~ ^[0-9]+$ ]] || [ "${value}" -lt 1 ]; then
                echo -e "${RED}❌ 无效的并行数: ${value}${NC}" >&2
                return 1
            fi

            # 更新配置
            jq --arg et "${expert_type} \
               --arg v "${value}" \
               '.experts[$et].max_parallel = ($v | tonumber) | .last_updated = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' \
               "${CONFIG_FILE}" > "${CONFIG_FILE}.tmp"
            mv "${CONFIG_FILE}.tmp" "${CONFIG_FILE}"

            # 更新池状态
            local current_running=$(jq -r ".pools.${expert_type}.running | length" "${POOL_FILE}")
            local new_total=${value}
            local new_available=$((new_total - current_running))

            jq --arg et "${expert_type} \
               --arg total "${new_total}" \
               --arg avail "${new_available}" \
               '.pools[$et].total = ($total | tonumber) | .pools[$et].available = ($avail | tonumber) | .last_updated = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' \
               "${POOL_FILE}" > "${POOL_FILE}.tmp"
            mv "${POOL_FILE}.tmp" "${POOL_FILE}"

            echo -e "${GREEN}✅ 配置已更新${NC}"
            echo "专家类型: ${expert_type}"
            echo "最大并行数: ${value}"
            ;;
        model)
            jq --arg et "${expert_type} \
               --arg v "${value}" \
               '.experts[$et].model = $v | .last_updated = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' \
               "${CONFIG_FILE}" > "${CONFIG_FILE}.tmp"
            mv "${CONFIG_FILE}.tmp" "${CONFIG_FILE}"

            echo -e "${GREEN}✅ 配置已更新${NC}"
            echo "专家类型: ${expert_type}"
            echo "模型: ${value}"
            ;;
        *)
            echo -e "${RED}❌ 无效的设置: ${setting}${NC}" >&2
            echo "支持的设置: max_parallel, model" >&2
            return 1
            ;;
    esac
}

##############################################################################
# 函数：打印使用说明
##############################################################################
usage() {
    echo "👥 专家分配脚本"
    echo ""
    echo "用法:"
    echo "  $0 init                      初始化专家系统"
    echo "  $0 config                    显示专家配置"
    echo "  $0 status                    显示池状态"
    echo "  $0 allocate TASK-ID DESC 分配专家"
    echo "  $0 release TASK-ID TYPE 释放专家"
    echo "  $0 update TYPE KEY VAL 更新配置"
    echo ""
    echo "专家类型:"
    echo "  tech   - 小新（技术支持专家）"
    echo "  log    - 小蓝（工作日志管理专家）"
    echo "  design - 室内设计专家"
    echo ""
    echo "示例:"
    echo "  $0 init"
    echo "  $0 config"
    echo "  $0 status"
    echo "  $0 allocate TASK-001 \"写一个Python脚本\""
    echo "  $0 release TASK-001"
    echo "  $0 update tech max_parallel 3"
    echo ""
}

##############################################################################
# 主函数
##############################################################################
main() {
    local command="$1"
    shift || true

    # 确保专家系统已初始化
    if [ "${command}" != "init" ] && [ ! -f "${CONFIG_FILE}" ]; then
        echo -e "${YELLOW}⚠️  专家系统未初始化${NC}" >&2
        echo "运行 '$0 init' 初始化" >&2
        exit 1
    fi

    case "${command}" in
        init)
            init_experts
            ;;
        config)
            show_config
            ;;
        status)
            show_pool_status
            ;;
        allocate)
            if [ -z "$1" ] || [ -z "$2" ]; then
                echo -e "${RED}❌ 错误: 请提供任务ID和描述${NC}" >&2
                usage
                exit 1
            fi

            # 确保池状态文件存在
            if [ ! -f "${POOL_FILE}" ]; then
                init_experts
            fi

            allocate_expert "$1" "$2"
            ;;
        release)
            if [ -z "$1" ]; then
                echo -e "${RED}❌ 错误: 请提供任务ID${NC}" >&2
                usage
                exit 1
            fi

            release_expert "$1" "$2"
            ;;
        update)
            if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
                echo -e "${RED}❌ 错误: 请提供专家类型、设置和值${NC}" >&2
                usage
                exit 1
            fi

            update_config "$1" "$2" "$3"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
