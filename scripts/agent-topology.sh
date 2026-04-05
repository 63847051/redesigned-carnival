#!/bin/bash
# =============================================================================
# Agent 拓扑设计工具 - Agent Topology Designer
# =============================================================================
# 功能: 生成 Agent 拓扑图（Mermaid 格式）
# 作者: 大领导 🎯
# 创建: 2026-04-02
# =============================================================================

set -euo pipefail

# =============================================================================
# 配置
# =============================================================================

OUTPUT_DIR="${OUTPUT_DIR:-/root/.openclaw/workspace/docs/topology}"
TOPOLOGY_TYPE="${TOPOLOGY_TYPE:-star}"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# =============================================================================
# 工具函数
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $@"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $@"
}

# =============================================================================
# 拓扑生成函数
# =============================================================================

generate_star_topology() {
    local main_agent=$1
    shift
    local sub_agents=("$@")

    cat << EOF
graph TD
    User[用户] --> ${main_agent}[主 Agent]
EOF

    for agent in "${sub_agents[@]}"; do
        cat << EOF
    ${main_agent} --> ${agent}[${agent}]
EOF
    done

    cat << EOF

    classDef mainAgent fill:#f9f,stroke:#333,stroke-width:2px
    classDef subAgent fill:#bbf,stroke:#333,stroke-width:1px
    classDef user fill:#ffd,stroke:#333,stroke-width:2px

    class ${main_agent} mainAgent
    class ${sub_agents[*]} subAgent
    class User user
EOF
}

generate_pipeline_topology() {
    local main_agent=$1
    shift
    local pipeline_agents=("$@")

    cat << EOF
graph LR
    User[用户] --> ${main_agent}[${main_agent}]
EOF

    local prev_agent=$main_agent
    for agent in "${pipeline_agents[@]}"; do
        cat << EOF
    ${prev_agent}[${prev_agent}] -->|sessions_send| ${agent}[${agent}]
EOF
        prev_agent=$agent
    done

    cat << EOF
    ${prev_agent} --> Result[结果]

    classDef agent fill:#bbf,stroke:#333,stroke-width:2px
    classDef user fill:#ffd,stroke:#333,stroke-width:2px
    classDef result fill:#bfb,stroke:#333,stroke-width:2px

    class ${main_agent},${pipeline_agents[*]} agent
    class User user
    class Result result
EOF
}

generate_broadcast_topology() {
    local main_agent=$1
    shift
    local targets=("$@")

    cat << EOF
graph TD
    User[用户] --> ${main_agent}[主 Agent]
EOF

    for agent in "${targets[@]}"; do
        cat << EOF
    ${main_agent} -->|broadcast| ${agent}[${agent}]
EOF
    done

    cat << EOF

    classDef mainAgent fill:#f9f,stroke:#333,stroke-width:2px
    classDef targetAgent fill:#bfb,stroke:#333,stroke-width:1px
    classDef user fill:#ffd,stroke:#333,stroke-width:2px

    class ${main_agent} mainAgent
    class ${targets[*]} targetAgent
    class User user
EOF
}

generate_hybrid_topology() {
    local main_agent=$1
    local star_agents=$2
    local pipeline_agent=$3

    cat << EOF
graph TD
    User[用户] --> ${main_agent}[主 Agent]

    %% 星型分支
    ${main_agent} -->|spawn| AgentA[数据采集 A]
    ${main_agent} -->|spawn| AgentB[分析 B]

    %% 流水线分支
    ${main_agent} -->|send| ${pipeline_agent}[后台 Agent]
    ${pipeline_agent} -->|send| AgentC[子 Agent 1]
    ${pipeline_agent} -->|send| AgentD[子 Agent 2]

    classDef mainAgent fill:#f9f,stroke:#333,stroke-width:2px
    classDef starAgent fill:#bbf,stroke:#333,stroke-width:1px
    classDef pipelineAgent fill:#fbf,stroke:#333,stroke-width:2px
    classDef subAgent fill:#bfb,stroke:#333,stroke-width:1px
    classDef user fill:#ffd,stroke:#333,stroke-width:2px

    class ${main_agent} mainAgent
    class AgentA,AgentB starAgent
    class ${pipeline_agent} pipelineAgent
    class AgentC,AgentD subAgent
    class User user
EOF
}

# =============================================================================
# 主流程
# =============================================================================

show_usage() {
    cat << EOF
用法: $0 <拓扑类型> [参数]

拓扑类型:
  star <主Agent> <子Agent1> [子Agent2] ...
      星型拓扑：主 Agent 分发，子 Agent 并行

  pipeline <主Agent> <Agent2> [Agent3] ...
      流水线拓扑：顺序依赖，数据流转

  broadcast <主Agent> <目标1> [目标2] ...
      广播拓扑：同一消息发给多个 Agent

  hybrid <主Agent> <星型Agent列表> <流水线Agent>
      混合拓扑：星型 + 流水线

示例:
  # 星型拓扑
  $0 star MainAgent DataCollector1 DataCollector2 DataCollector3

  # 流水线拓扑
  $0 pipeline ResearchAgent AnalysisAgent WriterAgent

  # 广播拓扑
  $0 broadcast MainAgent AgentA AgentB AgentC

  # 混合拓扑
  $0 hybrid MainAgent "AgentA,AgentB" BackgroundAgent

输出:
  Mermaid 格式的拓扑图，可以粘贴到:
  - https://mermaid.live
  - Notion
  - GitHub README
  - Markdown 文档

EOF
}

main() {
    if [ $# -lt 2 ]; then
        show_usage
        exit 1
    fi

    local topology_type=$1
    shift

    # 创建输出目录
    mkdir -p "$OUTPUT_DIR"

    local output_file=""
    local mermaid_code=""

    case $topology_type in
        star)
            if [ $# -lt 2 ]; then
                log_error "星型拓扑需要至少 1 个主 Agent 和 1 个子 Agent"
                exit 1
            fi
            output_file="${OUTPUT_DIR}/star-topology-$(date +%Y%m%d-%H%M%S).mmd"
            mermaid_code=$(generate_star_topology "$@")
            ;;
        pipeline)
            if [ $# -lt 2 ]; then
                log_error "流水线拓扑需要至少 2 个 Agent"
                exit 1
            fi
            output_file="${OUTPUT_DIR}/pipeline-topology-$(date +%Y%m%d-%H%M%S).mmd"
            mermaid_code=$(generate_pipeline_topology "$@")
            ;;
        broadcast)
            if [ $# -lt 2 ]; then
                log_error "广播拓扑需要至少 1 个主 Agent 和 1 个目标"
                exit 1
            fi
            output_file="${OUTPUT_DIR}/broadcast-topology-$(date +%Y%m%d-%H%M%S).mmd"
            mermaid_code=$(generate_broadcast_topology "$@")
            ;;
        hybrid)
            if [ $# -lt 3 ]; then
                log_error "混合拓扑需要: 主Agent 星型Agent列表(逗号分隔) 流水线Agent"
                exit 1
            fi
            output_file="${OUTPUT_DIR}/hybrid-topology-$(date +%Y%m%d-%H%M%S).mmd"
            mermaid_code=$(generate_hybrid_topology "$@")
            ;;
        *)
            log_error "未知的拓扑类型: $topology_type"
            show_usage
            exit 1
            ;;
    esac

    # 保存到文件
    echo "$mermaid_code" > "$output_file"

    log_success "拓扑图已生成: $output_file"
    echo ""
    echo "Mermaid 代码:"
    echo "-----------"
    echo "$mermaid_code"
    echo ""
    echo "查看方式:"
    echo "1. 在线预览: https://mermaid.live"
    echo "2. 复制到 Notion/GitHub/Markdown 文档"

    # 可选：自动打开浏览器
    # if command -v xdg-open &> /dev/null; then
    #     xdg-open "https://mermaid.live" &
    # fi
}

main "$@"
