#!/bin/bash

##############################################################################
# 专家资源监控脚本
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
STATS_FILE="${EXPERTS_DIR}/usage-stats.json"

##############################################################################
# 函数：初始化统计文件
##############################################################################
init_stats() {
    if [ ! -f "${STATS_FILE}" ]; then
        cat > "${STATS_FILE}" << EOF
{
  "version": "1.0.0",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "stats": {
    "tech": {
      "total_allocations": 0,
      "total_releases": 0,
      "peak_usage": 0,
      "last_reset": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    "log": {
      "total_allocations": 0,
      "total_releases": 0,
      "peak_usage": 0,
      "last_reset": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    "design": {
      "total_allocations": 0,
      "total_releases": 0,
      "peak_usage": 0,
      "last_reset": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  },
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    fi
}

##############################################################################
# 函数：记录分配事件
##############################################################################
record_allocation() {
    local expert_type="$1"

    init_stats

    # 更新分配统计
    local current_allocations=$(jq -r ".stats.${expert_type}.total_allocations" "${STATS_FILE}")
    local new_allocations=$((current_allocations + 1))

    # 更新峰值使用
    local current_running=$(jq -r ".pools.${expert_type}.running | length" "${POOL_FILE}")
    local peak_usage=$(jq -r ".stats.${expert_type}.peak_usage" "${STATS_FILE}")

    if [ ${current_running} -gt ${peak_usage} ]; then
        peak_usage=${current_running}
    fi

    jq --arg et "${expert_type}" \
       --arg alloc "${new_allocations}" \
       --arg peak "${peak_usage}" \
       --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.stats[$et].total_allocations = ($alloc | tonumber) | .stats[$et].peak_usage = ($peak | tonumber) | .last_updated = $ts' \
       "${STATS_FILE}" > "${STATS_FILE}.tmp"
    mv "${STATS_FILE}.tmp" "${STATS_FILE}"
}

##############################################################################
# 函数：记录释放事件
##############################################################################
record_release() {
    local expert_type="$1"

    init_stats

    # 更新释放统计
    local current_releases=$(jq -r ".stats.${expert_type}.total_releases" "${STATS_FILE}")
    local new_releases=$((current_releases + 1))

    jq --arg et "${expert_type}" \
       --arg rel "${new_releases}" \
       --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.stats[$et].total_releases = ($rel | tonumber) | .last_updated = $ts' \
       "${STATS_FILE}" > "${STATS_FILE}.tmp"
    mv "${STATS_FILE}.tmp" "${STATS_FILE}"
}

##############################################################################
# 函数：显示资源使用情况
##############################################################################
show_resource_usage() {
    echo -e "${BLUE}📊 专家资源使用情况${NC}"
    echo ""

    if [ ! -f "${POOL_FILE}" ]; then
        echo -e "${YELLOW}⚠️  专家池未初始化${NC}"
        return 1
    fi

    # 读取配置
    local config=$(cat "${CONFIG_FILE}")

    # 遍历每个专家类型
    jq -r '.pools | keys[]' "${POOL_FILE}" | while read -r expert_type; do
        local expert_name=$(jq -r ".experts.${expert_type}.name" "${CONFIG_FILE}")
        local total=$(jq -r ".pools.${expert_type}.total" "${POOL_FILE}")
        local available=$(jq -r ".pools.${expert_type}.available" "${POOL_FILE}")
        local running=$(jq -r ".pools.${expert_type}.running | length" "${POOL_FILE}")
        local usage_percent=$(( (total - available) * 100 / total ))

        # 颜色编码
        local color="${GREEN}"
        if [ ${usage_percent} -ge 80 ]; then
            color="${RED}"
        elif [ ${usage_percent} -ge 50 ]; then
            color="${YELLOW}"
        fi

        echo -e "${expert_type} ${expert_name}"
        echo "  总数: ${total} | 可用: ${available} | 运行中: ${running}"
        
        # 进度条
        local used=$((total - available))
        printf "  使用率: ["
        for i in $(seq 1 ${total}); do
            if [ ${i} -le ${used} ]; then
                echo -ne "${color}█${NC}"
            else
                echo -ne "░"
            fi
        done
        printf "] ${usage_percent}%"
        echo ""
        echo ""
    done
}

##############################################################################
# 函数：显示使用统计
##############################################################################
show_usage_stats() {
    echo -e "${BLUE}📈 专家使用统计${NC}"
    echo ""

    init_stats

    local current_time=$(date +%s)

    # 读取配置
    jq -r '.stats | keys[]' "${STATS_FILE}" | while read -r expert_type; do
        local expert_name=$(jq -r ".experts.${expert_type}.name" "${CONFIG_FILE}")
        local total_allocations=$(jq -r ".stats.${expert_type}.total_allocations" "${STATS_FILE}")
        local total_releases=$(jq -r ".stats.${expert_type}.total_releases" "${STATS_FILE}")
        local peak_usage=$(jq -r ".stats.${expert_type}.peak_usage" "${STATS_FILE}")
        local last_reset=$(jq -r ".stats.${expert_type}.last_reset" "${STATS_FILE}")

        # 计算运行时间
        local last_reset_sec=$(date -d "${last_reset}" +%s 2>/dev/null || echo 0)
        local uptime_sec=$((current_time - last_reset_sec))
        local uptime_hours=$((uptime_sec / 3600))

        echo -e "${expert_type} ${expert_name}"
        echo "  总分配次数: ${total_allocations}"
        echo "  总释放次数: ${total_releases}"
        echo "  峰值使用: ${peak_usage}"
        echo "  运行时间: ${uptime_hours} 小时"
        echo ""
    done
}

##############################################################################
# 函数：重置统计
##############################################################################
reset_stats() {
    echo -e "${YELLOW}🔄 重置统计${NC}"

    init_stats

    jq -r '.stats | keys[]' "${STATS_FILE}" | while read -r expert_type; do
        jq --arg et "${expert_type}" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '.stats[$et].total_allocations = 0 | .stats[$et].total_releases = 0 | .stats[$et].peak_usage = 0 | .stats[$et].last_reset = $ts | .last_updated = $ts' \
           "${STATS_FILE}" > "${STATS_FILE}.tmp"
        mv "${STATS_FILE}.tmp" "${STATS_FILE}"
    done

    echo -e "${GREEN}✅ 统计已重置${NC}"
}

##############################################################################
# 函数：导出报告
##############################################################################
export_report() {
    local output_file="${1:-${EXPERTS_DIR}/report-$(date +%Y%m%d-%H%M%S).json}"

    echo -e "${BLUE}📄 导出报告${NC}"

    # 生成完整报告
    cat > "${output_file}" << EOF
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "config": $(cat "${CONFIG_FILE}"),
  "pool_status": $(cat "${POOL_FILE}"),
  "usage_stats": $(cat "${STATS_FILE}")
}
EOF

    echo -e "${GREEN}✅ 报告已导出${NC}"
    echo "文件: ${output_file}"
}

##############################################################################
# 函数：实时监控
##############################################################################
monitor_realtime() {
    local interval="${1:-5}"

    echo -e "${BLUE}🔍 实时监控${NC}"
    echo "刷新间隔: ${interval} 秒"
    echo "按 Ctrl+C 停止"
    echo ""

    while true; do
        clear
        echo -e "${BLUE}📊 专家资源实时监控${NC}"
        echo -e "时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""

        show_resource_usage

        sleep ${interval}
    done
}

##############################################################################
# 函数：打印使用说明
##############################################################################
usage() {
    echo "📊 专家资源监控脚本"
    echo ""
    echo "用法:"
    echo "  $0 usage           显示资源使用情况"
    echo "  $0 stats           显示使用统计"
    echo "  $0 reset           重置统计"
    echo "  $0 export [file]   导出报告"
    echo "  $0 monitor [sec]   实时监控（默认 5 秒）"
    echo ""
    echo "示例:"
    echo "  $0 usage"
    echo "  $0 stats"
    echo "  $0 monitor"
    echo "  $0 export /tmp/report.json"
    echo ""
}

##############################################################################
# 主函数
##############################################################################
main() {
    local command="$1"
    shift || true

    # 确保专家系统已初始化
    if [ ! -f "${CONFIG_FILE}" ]; then
        echo -e "${YELLOW}⚠️  专家系统未初始化${NC}" >&2
        echo "运行 'allocate-experts.sh init' 初始化" >&2
        exit 1
    fi

    case "${command}" in
        usage)
            show_resource_usage
            ;;
        stats)
            show_usage_stats
            ;;
        reset)
            reset_stats
            ;;
        export)
            export_report "$1"
            ;;
        monitor)
            monitor_realtime "$1"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
