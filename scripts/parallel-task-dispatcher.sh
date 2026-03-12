#!/bin/bash
# Multi-Agent Parallel Task Dispatcher
# 并行任务分发器 - 让多个 Agent 同时处理不同任务
#
# 版本: v1.0
# 创建时间: 2026-03-12
# 用途: 群聊 @ 触发，自动并行分配任务给不同专家

set -e

# ============================================================================
# 配置区域
# ============================================================================

WORKSPACE="/root/.openclaw/workspace"
LOG_DIR="$WORKSPACE/logs/parallel-tasks"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/dispatch_${TIMESTAMP}.log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ============================================================================
# 角色配置
# ============================================================================

declare -A AGENT_ROLES=(
    ["大领导"]="orchestrator|glmcode/glm-4.7|任务分配和监督"
    ["设计"]="design-expert|glmcode/glm-4.7|室内设计专家"
    ["技术"]="tech-expert|openrouter/gpt-oss-120b|技术支持专家"
    ["小蓝"]="xiaolan|glmcode/glm-4.5-air|工作日志管理"
)

# 触发词映射
declare -A TRIGGER_MAP=(
    ["设计专家"]="设计"
    ["技术专家"]="技术"
    ["工作日志"]="小蓝"
)

# ============================================================================
# 任务解析
# ============================================================================

# 解析消息中的 @ 提及
parse_mentions() {
    local message="$1"
    local mentions=()

    # 提取所有 @xxx 格式的提及
    while [[ "$message" =~ @([^\s[:punct:]]+) ]]; do
        local mention="${BASH_REMATCH[1]}"
        mentions+=("$mention")
        # 从消息中移除已处理的部分，以便继续匹配
        message="${message#*$mention}"
    done

    printf '%s\n' "${mentions[@]}"
}

# 检测任务类型（基于关键词）
detect_task_type() {
    local content="$1"
    
    # 设计相关关键词
    local design_keywords="设计|图纸|平面图|立面图|天花|地面|排砖|柜体|会议室|更衣室|茶水区"
    # 技术相关关键词
    local tech_keywords="代码|脚本|爬虫|API|数据|前端|开发|编程|函数"
    # 日志相关关键词
    local log_keywords="日志|记录|任务|进度|更新状态|统计|汇总"

    if [[ "$content" =~ $design_keywords ]]; then
        echo "design"
    elif [[ "$content" =~ $tech_keywords ]]; then
        echo "tech"
    elif [[ "$content" =~ $log_keywords ]]; then
        echo "log"
    else
        echo "general"
    fi
}

# ============================================================================
# Agent 生成
# ============================================================================

# 为指定 Agent 生成任务
spawn_agent_task() {
    local role="$1"
    local task_content="$2"
    local task_id="$3"
    
    log "📋 分配任务给: $role"
    log "   任务ID: $task_id"
    log "   内容: ${task_content:0:100}..."
    
    # 获取角色配置
    local role_config="${AGENT_ROLES[$role]}"
    IFS='|' read -r role_id model role_desc <<< "$role_config"
    
    log "   模型: $model"
    log "   角色: $role_desc"
    
    # 生成任务文件
    local task_file="$LOG_DIR/task_${task_id}_${role}.md"
    cat > "$task_file" <<EOF
# 任务分配 - $role

**任务ID**: $task_id
**角色**: $role_desc
**模型**: $model
**时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 任务内容

\`\`\`
$task_content
\`\`\`

## 执行要求

1. 在你的专业领域内完成此任务
2. 如果任务超出你的职责范围，立即报告
3. 完成后汇报结果，包括：
   - ✅ 已完成的工作
   - 📁 相关文件路径
   - ⚠️ 发现的问题
   - 💡 建议

EOF

    log "   任务文件: $task_file"
    
    # 这里可以调用 sessions_spawn 来实际启动 Agent
    # 暂时只记录，等待完整实现
    echo "$task_file"
}

# ============================================================================
# 并行执行
# ============================================================================

# 并行执行多个任务
execute_parallel_tasks() {
    local -n task_array=$1
    local pids=()
    local results=()
    
    log "🚀 开始并行执行 ${#task_array[@]} 个任务"
    
    for task_spec in "${task_array[@]}"; do
        IFS='|' read -r role task task_id <<< "$task_spec"
        
        log "📦 启动任务: $role (ID: $task_id)"
        
        # 在后台执行任务（这里简化为记录日志）
        (
            spawn_agent_task "$role" "$task" "$task_id"
            echo "✅ 完成: $role" >> "$LOG_DIR/result_${task_id}.txt"
        ) &
        
        pids+=($!)
    done
    
    # 等待所有后台任务完成
    log "⏳ 等待所有任务完成..."
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    log "✅ 所有任务已完成"
    
    # 收集结果
    for task_spec in "${task_array[@]}"; do
        IFS='|' read -r role task task_id <<< "$task_spec"
        if [[ -f "$LOG_DIR/result_${task_id}.txt" ]]; then
            results+=("$(cat "$LOG_DIR/result_${task_id}.txt")")
        fi
    done
    
    printf '%s\n' "${results[@]}"
}

# ============================================================================
# 主函数
# ============================================================================

main() {
    local message="$1"
    local sender="$2"
    local chat_id="$3"
    
    log "================================================"
    log "🎯 Multi-Agent 并行任务分发器"
    log "================================================"
    log "发送者: $sender"
    log "聊天ID: $chat_id"
    log "消息内容: ${message:0:200}..."
    log "================================================"
    
    # 解析 @ 提及
    local mentions
    mapfile -t mentions < <(parse_mentions "$message")
    
    if [[ ${#mentions[@]} -eq 0 ]]; then
        log "⚠️ 未检测到 @ 提及，使用主控 Agent 处理"
        # 这里可以调用主控 Agent
        return 0
    fi
    
    log "📋 检测到 ${#mentions[@]} 个 @ 提及: ${mentions[*]}"
    
    # 为每个提及分配任务
    local tasks=()
    local task_counter=0
    
    for mention in "${mentions[@]}"; do
        # 查找对应的角色
        local role=""
        for key in "${!AGENT_ROLES[@]}"; do
            if [[ "$mention" == *"$key"* ]]; then
                role="$key"
                break
            fi
        done
        
        if [[ -z "$role" ]]; then
            log "⚠️ 未识别的角色: $mention"
            continue
        fi
        
        # 提取该角色的任务内容（简化版，实际需要更复杂的解析）
        local task_content="$message"
        local task_id="$(date +%s)_$((task_counter++))"
        
        tasks+=("$role|$task_content|$task_id")
    done
    
    # 并行执行所有任务
    if [[ ${#tasks[@]} -gt 0 ]]; then
        log "📋 准备并行执行 ${#tasks[@]} 个任务"
        
        local results
        mapfile -t results < <(execute_parallel_tasks tasks)
        
        log "================================================"
        log "📊 任务执行结果汇总"
        log "================================================"
        
        for result in "${results[@]}"; do
            log "$result"
        done
        
        log "================================================"
        log "✅ 所有任务已完成，等待大领导汇总..."
        log "================================================"
        
        # 生成汇总报告
        local summary_file="$LOG_DIR/summary_${TIMESTAMP}.md"
        cat > "$summary_file" <<EOF
# 并行任务执行报告

**执行时间**: $(date '+%Y-%m-%d %H:%M:%S')
**任务数量**: ${#tasks[@]}
**执行日志**: $LOG_FILE

## 任务列表

$(for task_spec in "${tasks[@]}"; do
    IFS='|' read -r role task task_id <<< "$task_spec"
    echo "- **$role**: ${task:0:50}..."
done)

## 执行结果

$(for result in "${results[@]}"; do
    echo "- $result"
done)

EOF

        log "📄 汇总报告: $summary_file"
    fi
}

# ============================================================================
# 脚本入口
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 3 ]]; then
        echo "用法: $0 <message> <sender> <chat_id>"
        echo "示例: $0 \"@设计 修改图纸\" \"user123\" \"chat456\""
        exit 1
    fi
    
    main "$@"
fi
