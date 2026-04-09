#!/bin/bash
# API 不变量保护系统 v1.0
# 基于 Claude Code Compaction 设计：前置强约束 + 熔断器 + 重试机制

set -e

# =============================================================================
# ⚙️ 配置
# =============================================================================

STATE_DIR="/root/.openclaw/workspace/.api-guard-state"
LOG_FILE="/root/.openclaw/workspace/logs/api-guard.log"
API_KEY="c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp"
BASE_URL="https://open.bigmodel.cn/api/anthropic"

# 熔断器配置
MAX_CONSECUTIVE_FAILURES=3
COOLDOWN_SECONDS=60

# 重试配置
MAX_RETRIES=3
BASE_BACKOFF_MS=1000

# =============================================================================
# 📊 状态管理
# =============================================================================

init_state() {
    mkdir -p "$STATE_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"

    if [ ! -f "$STATE_DIR/failure-count" ]; then
        echo "0" > "$STATE_DIR/failure-count"
    fi

    if [ ! -f "$STATE_DIR/last-failure-time" ]; then
        echo "0" > "$STATE_DIR/last-failure-time"
    fi

    if [ ! -f "$STATE_DIR/circuit-state" ]; then
        echo "closed" > "$STATE_DIR/circuit-state"
    fi
}

get_failure_count() {
    cat "$STATE_DIR/failure-count"
}

increment_failure_count() {
    local current=$(get_failure_count)
    echo $((current + 1)) > "$STATE_DIR/failure-count"
    echo $(date +%s) > "$STATE_DIR/last-failure-time"
}

reset_failure_count() {
    echo "0" > "$STATE_DIR/failure-count"
    echo "0" > "$STATE_DIR/last-failure-time"
}

get_circuit_state() {
    cat "$STATE_DIR/circuit-state"
}

set_circuit_state() {
    echo "$1" > "$STATE_DIR/circuit-state"
}

is_cooldown_over() {
    local last_failure=$(cat "$STATE_DIR/last-failure-time")
    local current_time=$(date +%s)
    local elapsed=$((current_time - last_failure))
    [ $elapsed -ge $COOLDOWN_SECONDS ]
}

# =============================================================================
# 🔐 熔断器机制（Claude Code Compaction）
# =============================================================================

check_circuit_breaker() {
    local circuit_state=$(get_circuit_state)

    if [ "$circuit_state" = "open" ]; then
        if is_cooldown_over; then
            echo "🔄 半开状态：尝试恢复..."
            set_circuit_state "half-open"
            return 0
        else
            echo "🚨 熔断器打开：跳过 API 调用"
            return 1
        fi
    fi

    return 0
}

record_success() {
    local circuit_state=$(get_circuit_state)

    if [ "$circuit_state" = "half-open" ]; then
        echo "✅ 恢复成功：关闭熔断器"
        set_circuit_state "closed"
    fi

    reset_failure_count
}

record_failure() {
    local failure_count=$(get_failure_count)
    increment_failure_count
    failure_count=$(get_failure_count)

    echo "⚠️ API 失败: $failure_count/$MAX_CONSECUTIVE_FAILURES"

    if [ $failure_count -ge $MAX_CONSECUTIVE_FAILURES ]; then
        echo "🚨 触发熔断器：连续失败 $failure_count 次"
        set_circuit_state "open"
    fi
}

# =============================================================================
# 🔄 重试机制（指数退避）
# =============================================================================

api_call_with_retry() {
    local model=$1
    local prompt=$2
    local max_tokens=$3

    local attempt=1
    local backoff_ms=$BASE_BACKOFF_MS

    while [ $attempt -le $MAX_RETRIES ]; do
        echo "🔄 尝试 $attempt/$MAX_RETRIES..."

        local response=$(curl -s -w "\n%{http_code}" -X POST \
            "$BASE_URL/v1/messages" \
            -H "Content-Type: application/json" \
            -H "x-api-key: $API_KEY" \
            -H "anthropic-version: 2023-06-01" \
            -d "{
                \"model\": \"$model\",
                \"max_tokens\": $max_tokens,
                \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}]
            }" 2>/dev/null)

        local http_code=$(echo "$response" | tail -n1)
        local body=$(echo "$response" | head -n-1)

        if [ "$http_code" = "200" ]; then
            echo "✅ API 调用成功"
            record_success
            echo "$body"
            return 0
        else
            echo "❌ API 调用失败: HTTP $http_code"
            record_failure

            if [ $attempt -lt $MAX_RETRIES ]; then
                echo "⏳ 等待 ${backoff_ms}ms 后重试..."
                sleep $((backoff_ms / 1000))
                backoff_ms=$((backoff_ms * 2))  # 指数退避
            fi
        fi

        attempt=$((attempt + 1))
    done

    echo "❌ 所有重试失败"
    return 1
}

# =============================================================================
# 🧪 测试函数
# =============================================================================

test_invariant_guard() {
    echo ""
    echo "🧪 测试 API 不变量保护..."
    echo ""

    # 初始化状态
    init_state

    # 检查熔断器
    echo "🔍 检查熔断器状态..."
    if check_circuit_breaker; then
        echo "✅ 熔断器允许通过"
    else
        echo "⏸️ 熔断器阻止调用"
        return 1
    fi

    # 执行 API 调用
    echo ""
    echo "📞 执行 API 调用..."
    local result=$(api_call_with_retry "glm-4.7" "Hi" 10)

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ API 调用成功"
        echo "📊 响应: $(echo "$result" | head -c 100)..."
    else
        echo ""
        echo "❌ API 调用失败"
    fi

    # 显示状态
    echo ""
    echo "📊 当前状态:"
    echo "  - 失败计数: $(get_failure_count)/$MAX_CONSECUTIVE_FAILURES"
    echo "  - 熔断器状态: $(get_circuit_state)"
    echo "  - 上次失败: $(cat "$STATE_DIR/last-failure-time")"
}

# =============================================================================
# 🚀 主流程
# =============================================================================

main() {
    echo "🛡️ API 不变量保护系统 v1.0"
    echo "⏰ 时间: $(date)"
    echo ""

    case "${1:-test}" in
        test)
            test_invariant_guard
            ;;
        reset)
            echo "🔄 重置熔断器状态..."
            init_state
            reset_failure_count
            set_circuit_state "closed"
            echo "✅ 已重置"
            ;;
        status)
            echo "📊 熔断器状态:"
            echo "  - 失败计数: $(get_failure_count)/$MAX_CONSECUTIVE_FAILURES"
            echo "  - 熔断器状态: $(get_circuit_state)"
            echo "  - 上次失败: $(cat "$STATE_DIR/last-failure-time")"
            ;;
        *)
            echo "用法: $0 {test|reset|status}"
            exit 1
            ;;
    esac
}

# 执行主流程
main "$@"
