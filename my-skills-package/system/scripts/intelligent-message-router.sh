#!/bin/bash
# 智能消息路由系统
# 自动识别任务类型，并行分配给对应专家
#
# 版本: v1.0
# 创建时间: 2026-03-12
# 方案: C - 混合方案（单一机器人 + 智能路由）

set -e

WORKSPACE="/root/.openclaw/workspace"
DISPATCHER="$WORKSPACE/scripts/parallel-task-dispatcher.sh"
LOG_DIR="$WORKSPACE/logs/intelligent-router"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/router_${TIMESTAMP}.log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ============================================================================
# 任务类型识别
# ============================================================================

# 分析消息，识别任务类型
analyze_message() {
    local message="$1"
    local -n tasks_ref=$2

    log "🔍 分析消息内容..."
    log "   原始消息: ${message:0:100}..."

    # 定义任务类型和关键词
    local design_keywords="设计|图纸|平面图|立面图|天花|地面|排砖|柜体|会议室|更衣室|茶水区|室内|空间|装修"
    local tech_keywords="代码|脚本|爬虫|API|数据|前端|开发|编程|函数|Python|JavaScript|抓取|统计"
    local log_keywords="日志|记录|任务|进度|更新状态|统计|汇总|工作|跟踪"
    local orchestrator_keywords="分配|安排|协调|汇总|分析|完成|处理|帮我|一起"

    # 检测到的任务类型
    local detected_tasks=()

    # 检查设计任务
    if [[ "$message" =~ $design_keywords ]]; then
        detected_tasks+=("design")
        log "   ✅ 检测到设计任务"
    fi

    # 检查技术任务
    if [[ "$message" =~ $tech_keywords ]]; then
        detected_tasks+=("tech")
        log "   ✅ 检测到技术任务"
    fi

    # 检查日志任务
    if [[ "$message" =~ $log_keywords ]]; then
        detected_tasks+=("log")
        log "   ✅ 检测到日志任务"
    fi

    # 检查是否需要协调
    if [[ "$message" =~ $orchestrator_keywords ]] || [[ ${#detected_tasks[@]} -gt 1 ]]; then
        detected_tasks+=("orchestrator")
        log "   ✅ 检测到协调需求"
    fi

    # 如果没有检测到任何任务，默认为通用任务
    if [[ ${#detected_tasks[@]} -eq 0 ]]; then
        detected_tasks+=("general")
        log "   ℹ️ 未检测到特定任务类型，作为通用任务处理"
    fi

    # 去重
    local unique_tasks=($(printf "%s\n" "${detected_tasks[@]}" | sort -u))

    # 返回结果
    tasks_ref=("${unique_tasks[@]}")

    log "📊 最终识别的任务类型: ${tasks_ref[*]}（共 ${#tasks_ref[@]} 个）"
}

# 将任务类型映射到角色
map_task_to_role() {
    local task_type="$1"

    case "$task_type" in
        "design")
            echo "设计"
            ;;
        "tech")
            echo "技术"
            ;;
        "log")
            echo "小蓝"
            ;;
        "orchestrator")
            echo "大领导"
            ;;
        "general")
            echo "大领导"
            ;;
        *)
            echo "大领导"
            ;;
    esac
}

# 提取任务内容
extract_task_content() {
    local message="$1"
    local task_type="$2"

    # 简化版：直接返回原始消息
    # 在实际使用中，可以更精确地提取特定任务的内容
    echo "$message"
}

# ============================================================================
# 并行任务处理
# ============================================================================

# 并行处理多个任务
process_tasks_parallel() {
    local message="$1"
    local sender="$2"
    local chat_id="$3"
    shift 3
    local task_types=("$@")

    log "🚀 开始并行处理 ${#task_types[@]} 个任务"

    # 为每个任务类型创建任务规范
    local task_specs=()
    local task_counter=0

    for task_type in "${task_types[@]}"; do
        local role=$(map_task_to_role "$task_type")
        local task_content=$(extract_task_content "$message" "$task_type")
        local task_id="$(date +%s)_$((task_counter++))"

        task_specs+=("$role|$task_content|$task_id")
        log "   📦 任务 $task_counter: $role ($task_type)"
    done

    log "📋 准备执行的任务："
    for spec in "${task_specs[@]}"; do
        IFS='|' read -r role content task_id <<< "$spec"
        log "   - $role: ${content:0:50}..."
    done

    # 调用并行任务分发器
    if [[ -x "$DISPATCHER" ]]; then
        log "✅ 调用并行任务分发器..."

        # 创建临时消息，包含所有角色提及
        local constructed_message="@大领导 智能路由识别到以下任务："
        for spec in "${task_specs[@]}"; do
            IFS='|' read -r role content task_id <<< "$spec"
            constructed_message+=" @$role $content"
        done

        log "📨 构造的消息: ${constructed_message:0:200}..."

        # 调用分发器
        "$DISPATCHER" "$constructed_message" "$sender" "$chat_id" >> "$LOG_FILE" 2>&1

        log "✅ 并行任务分发完成"
    else
        log "❌ 错误: 分发器不可执行: $DISPATCHER"
        return 1
    fi
}

# ============================================================================
# 主函数
# ============================================================================

main() {
    local message="$1"
    local sender="$2"
    local chat_id="$3"
    local chat_type="${4:-direct}"

    log "=================================================="
    log "🧠 智能消息路由系统 v1.0"
    log "=================================================="
    log "发送者: $sender"
    log "聊天ID: $chat_id"
    log "聊天类型: $chat_type"
    log "消息内容: ${message:0:200}..."
    log "=================================================="
    log ""

    # Step 1: 分析消息，识别任务类型
    local task_types=()
    analyze_message "$message" task_types

    log ""

    # Step 2: 并行处理所有识别到的任务
    if [[ ${#task_types[@]} -gt 0 ]]; then
        process_tasks_parallel "$message" "$sender" "$chat_id" "${task_types[@]}"
    else
        log "⚠️ 未识别到任何任务类型"
    fi

    log ""
    log "=================================================="
    log "✅ 智能路由完成"
    log "=================================================="
    log ""
    log "📊 处理结果:"
    log "  - 识别任务类型: ${#task_types[@]} 个"
    log "  - 执行方式: 并行处理"
    log "  - 详细日志: $LOG_FILE"
    log ""
}

# ============================================================================
# 脚本入口
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 3 ]]; then
        echo "用法: $0 <message> <sender> <chat_id> [chat_type]"
        echo ""
        echo "示例:"
        echo "  $0 \"帮我设计客厅并写个脚本\" \"user123\" \"chat456\" \"group\""
        echo ""
        echo "任务类型会自动识别："
        echo "  - 设计任务: 设计、图纸、平面图、天花..."
        echo "  - 技术任务: 代码、脚本、爬虫、API..."
        echo "  - 日志任务: 日志、记录、任务、进度..."
        echo "  - 协调任务: 分配、安排、汇总、分析..."
        exit 1
    fi

    main "$@"
fi
