#!/bin/bash

##############################################################################
# 专家分配脚本（修复版）
# 基于 ClawCorp DP-CC-002: 角色池化管理模式
##############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 专家配置目录
EXPERTS_DIR="${HOME}/.openclaw/workspace/experts"
CONFIG_FILE="${EXPERTS_DIR}/config.json"
POOL_FILE="${EXPERTS_DIR}/pool-status.json"

##############################################################################
# 函数：初始化专家系统
##############################################################################
init_experts() {
    echo -e "${BLUE}初始化专家系统...${NC}"
    mkdir -p "${EXPERTS_DIR}"

    if [ ! -f "${CONFIG_FILE}" ]; then
        cat > "${CONFIG_FILE}" << 'EOF'
{
  "version": "1.0.0",
  "experts": {
    "tech": {
      "name": "小新",
      "max_parallel": 2,
      "model": "opencode/minimax-m2.5-free"
    },
    "log": {
      "name": "小蓝",
      "max_parallel": 1,
      "model": "glmcode/glm-4.5-air"
    },
    "design": {
      "name": "室内设计专家",
      "max_parallel": 1,
      "model": "glmcode/glm-4.7"
    }
  }
}
EOF
        echo -e "${GREEN}专家系统初始化完成${NC}"
    fi

    if [ ! -f "${POOL_FILE}" ]; then
        cat > "${POOL_FILE}" << 'EOF'
{
  "pools": {
    "tech": {"total": 2, "available": 2, "running": []},
    "log": {"total": 1, "available": 1, "running": []},
    "design": {"total": 1, "available": 1, "running": []}
  }
}
EOF
    fi
}

##############################################################################
# 函数：显示配置
##############################################################################
show_config() {
    echo -e "${BLUE}专家配置${NC}"
    jq '.' "${CONFIG_FILE}"
}

##############################################################################
# 函数：显示池状态
##############################################################################
show_pool_status() {
    echo -e "${BLUE}专家池状态${NC}"
    jq '.' "${POOL_FILE}"
}

##############################################################################
# 函数：分配专家
##############################################################################
allocate_expert() {
    local task_id="$1"
    local expert_type="$2"

    echo -e "${BLUE}分配专家${NC}"
    echo "任务: ${task_id}"
    echo "专家: ${expert_type}"

    local available=$(jq -r ".pools.${expert_type}.available" "${POOL_FILE}")
    
    if [ "${available}" -eq 0 ]; then
        echo -e "${RED}专家池已满${NC}"
        return 1
    fi

    jq --arg et "${expert_type}" \
       --arg tid "${task_id}" \
       '.pools[$et].available -= 1 | .pools[$et].running += [$tid]' \
       "${POOL_FILE}" > "${POOL_FILE}.tmp"
    mv "${POOL_FILE}.tmp" "${POOL_FILE}"

    echo -e "${GREEN}专家已分配${NC}"
}

##############################################################################
# 函数：释放专家
##############################################################################
release_expert() {
    local task_id="$1"
    local expert_type="$2"

    echo -e "${BLUE}释放专家${NC}"

    jq --arg et "${expert_type}" \
       --arg tid "${task_id}" \
       '.pools[$et].available += 1 | .pools[$et].running |= map(select(. != $tid))' \
       "${POOL_FILE}" > "${POOL_FILE}.tmp"
    mv "${POOL_FILE}.tmp" "${POOL_FILE}"

    echo -e "${GREEN}专家已释放${NC}"
}

##############################################################################
# 主函数
##############################################################################
main() {
    local command="$1"
    shift || true

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
            allocate_expert "$1" "$2"
            ;;
        release)
            release_expert "$1" "$2"
            ;;
        *)
            echo "用法: $0 init|config|status|allocate|release"
            exit 1
            ;;
    esac
}

main "$@"
