#!/bin/bash
# v5.2轻量级模型调用接口
# 通过CLIProxyAPI调用免费AI模型

CLI_PROXY_API="http://localhost:8317"
LOG_FILE="/root/.openclaw/workspace/.evolution/model-calls.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ============================================================================
# 功能: 调用免费AI模型
# =============================================================================

call_free_model() {
    local model="$1"
    local prompt="$2"
    local system_prompt="${3:-你是一个AI助手}"

    log "🤖 调用模型: $model"

    # 根据模型类型选择端点
    local endpoint=""
    case "$model" in
        gemini*|gemini-*)
            endpoint="$CLI_PROXY_API/v1/chat/completions"
            ;;
        gpt-*|gpt*)
            endpoint="$CLI_PROXY_API/v1/chat/completions"
            ;;
        claude-*|claude*)
            endpoint="$CLI_PROXY_API/v1/messages"
            ;;
        *)
            endpoint="$CLI_PROXY_API/v1/chat/completions"
            ;;
    esac

    # 调用API
    local response=$(curl -s "$endpoint" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"$model\",
            \"messages\": [
                {\"role\": \"system\", \"content\": \"$system_prompt\"},
                {\"role\": \"user\", \"content\": \"$prompt\"}
            ],
            \"stream\": false
        }" 2>&1)

    # 检查响应
    if echo "$response" | grep -q "error"; then
        log "⚠️ API调用失败: $response"
        return 1
    fi

    # 提取内容
    local content=$(echo "$response" | grep -o '"content":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -z "$content" ]; then
        log "⚠️ 无法提取响应内容"
        return 1
    fi

    log "✅ API调用成功"
    echo "$content"
    return 0
}

# ============================================================================
# 功能: 智能模型选择
# =============================================================================

smart_model_select() {
    local task_type="$1"
    local complexity="${2:-medium}"

    log "🎯 智能模型选择: 任务=$task_type, 复杂度=$complexity"

    case "$task_type" in
        "代码"|"编程"|"技术")
            if [ "$complexity" = "high" ]; then
                echo "gemini-2.5-pro"
            else
                echo "gemini-2.0-flash"
            fi
            ;;
        "写作"|"翻译"|"总结")
            echo "gemini-2.5-pro"
            ;;
        "分析"|"推理"|"决策")
            echo "gemini-2.5-pro"
            ;;
        *)
            echo "gemini-2.0-flash"
            ;;
    esac
}

# ============================================================================
# 功能: 自动任务处理
# =============================================================================

auto_task() {
    local task_type="$1"
    local prompt="$2"
    local complexity="${3:-medium}"

    # 自动选择模型
    local model=$(smart_model_select "$task_type" "$complexity")

    log "🚀 自动任务处理"
    log "任务类型: $task_type"
    log "使用模型: $model"

    # 调用模型
    local result=$(call_free_model "$model" "$prompt")

    if [ $? -eq 0 ]; then
        log "✅ 任务完成"
        echo "$result"
    else
        log "❌ 任务失败"
        return 1
    fi
}

# ============================================================================
# 主程序入口
# =============================================================================

case "${1:-help}" in
    call)
        call_free_model "$2" "$3" "$4"
        ;;

    smart)
        smart_model_select "$2" "$3"
        ;;

    auto)
        auto_task "$2" "$3" "$4"
        ;;

    status)
        log "📊 CLIProxyAPI状态检查"
        if netstat -tuln 2>/dev/null | grep -q ":8317 "; then
            echo "✅ CLIProxyAPI运行中 (端口8317)"
            log "✅ 服务正常"
        else
            echo "❌ CLIProxyAPI未运行"
            log "❌ 服务离线"
        fi
        ;;

    *)
        echo "v5.2轻量级模型调用接口"
        echo "======================"
        echo ""
        echo "用法:"
        echo "  $0 call <模型> <提示> [系统提示]"
        echo "  $0 smart <任务类型> [复杂度]"
        echo "  $0 auto <任务类型> <提示> [复杂度]"
        echo "  $0 status"
        echo ""
        echo "支持的模型:"
        echo "  - gemini-2.5-pro (免费，高质量)"
        echo "  - gemini-2.0-flash (免费，快速)"
        echo "  - gpt-4o (通过Codex)"
        echo "  - claude-3.5-sonnet (通过Claude Code)"
        echo ""
        echo "任务类型:"
        echo "  - 代码/编程/技术"
        echo "  - 写作/翻译/总结"
        echo "  - 分析/推理/决策"
        echo ""
        echo "复杂度:"
        echo "  - low (简单)"
        echo "  - medium (中等)"
        echo "  - high (复杂)"
        echo ""
        echo "示例:"
        echo "  $0 status"
        echo "  $0 call gemini-2.5-pro '写一个Python函数'"
        echo "  $0 smart '代码' 'high'"
        echo "  $0 auto '代码' '写一个快速排序算法' 'medium'"
        echo ""
        echo "注意: 需要先在CLIProxyAPI中配置OAuth账户"
        exit 0
        ;;
esac

exit 0
