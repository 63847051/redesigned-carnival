#!/bin/bash
# 群聊 @ 提及处理器
# 自动识别 @ 触发，路由到对应的 Agent
#
# 版本: v1.0
# 创建时间: 2026-03-12

set -e

WORKSPACE="/root/.openclaw/workspace"
DISPATCHER="$WORKSPACE/scripts/parallel-task-dispatcher.sh"

# ============================================================================
# @ 触发规则配置
# ============================================================================

# 飞书群聊 @ 触发映射
declare -A MENTION_RULES=(
    ["@大领导"]="orchestrator"
    ["@设计"]="design-expert"
    ["@技术"]="tech-expert"
    ["@小蓝"]="xiaolan"
)

# ============================================================================
# 消息处理
# ============================================================================

process_message() {
    local message="$1"
    local sender="$2"
    local chat_id="$3"
    local chat_type="$4" # group, direct
    
    log "📨 收到消息 (类型: $chat_type)"
    log "   发送者: $sender"
    log "   内容: ${message:0:100}..."
    
    # 只处理群聊消息
    if [[ "$chat_type" != "group" ]]; then
        log "ℹ️ 非群聊消息，跳过 @ 处理"
        return 0
    fi
    
    # 检查是否包含 @ 提及
    if [[ ! "$message" =~ @[^\s[:punct:]]+ ]]; then
        log "ℹ️ 无 @ 提及，跳过"
        return 0
    fi
    
    log "✅ 检测到 @ 提及，调用并行任务分发器"
    
    # 调用并行任务分发器
    if [[ -x "$DISPATCHER" ]]; then
        "$DISPATCHER" "$message" "$sender" "$chat_id"
    else
        log "❌ 错误: 分发器不存在或不可执行: $DISPATCHER"
        return 1
    fi
}

# ============================================================================
# 日志函数
# ============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# ============================================================================
# 脚本入口
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 4 ]]; then
        echo "用法: $0 <message> <sender> <chat_id> <chat_type>"
        echo "示例: $0 \"@设计 修改图纸\" \"user123\" \"chat456\" \"group\""
        exit 1
    fi
    
    process_message "$@"
fi
