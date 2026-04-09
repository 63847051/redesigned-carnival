#!/bin/bash
# API 健康监控脚本 v1.0
# 监控 GLM API 可用性，自动记录失败模式

set -e

LOG_FILE="/root/.openclaw/workspace/logs/api-health.log"
STATE_FILE="/root/.openclaw/workspace/.api-health-state.json"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 初始化状态
if [ ! -f "$STATE_FILE" ]; then
    echo '{"consecutive_failures": 0, "last_success": null}' > "$STATE_FILE"
fi

# 读取状态
CONSECUTIVE_FAILURES=$(grep -o '"consecutive_failures": [0-9]*' "$STATE_FILE" | grep -o '[0-9]*' || echo "0")

# 测试 API（模拟 Gateway 的请求）
test_api() {
    local response=$(curl -s -w "\n%{http_code}" -X POST \
        https://open.bigmodel.cn/api/anthropic/v1/messages \
        -H "Content-Type: application/json" \
        -H "x-api-key: c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp" \
        -H "anthropic-version: 2023-06-01" \
        -d '{
            "model": "glm-4.7",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hi"}]
        }' 2>/dev/null)

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "200" ]; then
        echo "success"
    else
        echo "failed_$http_code"
    fi
}

# 执行测试
echo "🔍 API 健康检查 - $(date)"
RESULT=$(test_api)

if [ "$RESULT" = "success" ]; then
    echo "✅ API 正常"
    echo "0" > "$STATE_FILE.tmp"
    echo '{"consecutive_failures": 0, "last_success": "'$(date -Iseconds)'"}' > "$STATE_FILE"
    CONSECUTIVE_FAILURES=0
else
    CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
    echo "❌ API 失败: $RESULT"
    echo "{\"consecutive_failures\": $CONSECUTIVE_FAILURES, \"last_success\": null}" > "$STATE_FILE"

    # 记录到日志
    echo "[$(date -Iseconds)] API 失败: $RESULT (连续失败: $CONSECUTIVE_FAILURES)" >> "$LOG_FILE"

    # 如果连续失败 3 次，告警
    if [ $CONSECUTIVE_FAILURES -ge 3 ]; then
        echo "🚨 警告: API 连续失败 $CONSECUTIVE_FAILURES 次"
        # 这里可以添加告警通知逻辑
    fi
fi

echo "📊 当前状态: 连续失败 $CONSECUTIVE_FAILURES 次"
