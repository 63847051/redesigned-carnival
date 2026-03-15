#!/bin/bash

# 限流监控脚本
# 检测 GLM-4.7 限流错误，自动切换到备用模型，并重启 Gateway
# 作者: 小新
# 创建时间: 2026-03-15

set -e

# 配置
LOG_LINES=1000
RATE_LIMIT_KEYWORDS=("rate limit" "429" "quota exceeded" "too many requests")
ALERT_WEBHOOK=""  # 可选：配置告警 Webhook

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARN:${NC} $1"
}

# 检测限流错误
detect_rate_limit() {
    log "🔍 正在检测限流错误..."

    # 从 journalctl 获取最近的日志
    local logs=$(journalctl --user -u openclaw-gateway -n "$LOG_LINES" --no-pager 2>/dev/null || echo "")

    if [ -z "$logs" ]; then
        warn "无法获取 Gateway 日志"
        return 1
    fi

    # 检查是否包含限流关键词
    for keyword in "${RATE_LIMIT_KEYWORDS[@]}"; do
        if echo "$logs" | grep -i "$keyword" > /dev/null; then
            error "检测到限流错误: $keyword"
            echo "$logs" | grep -i "$keyword" | tail -5
            return 0
        fi
    done

    log "✅ 未检测到限流错误"
    return 1
}

# 切换到备用模型
switch_to_fallback_model() {
    log "🔄 正在切换到备用模型..."

    local config_file="$HOME/.openclaw/openclaw.json"

    if [ ! -f "$config_file" ]; then
        error "配置文件不存在: $config_file"
        return 1
    fi

    # 备份当前配置
    cp "$config_file" "$config_file.backup.$(date +%Y%m%d_%H%M%S)"

    # 使用 jq 切换主模型到 GLM-4.6
    if command -v jq &> /dev/null; then
        jq '.agents.defaults.model.primary = "glmcode/glm-4.6"' "$config_file" > "$config_file.tmp"
        mv "$config_file.tmp" "$config_file"
        log "✅ 主模型已切换到: glmcode/glm-4.6"
    else
        warn "jq 未安装，尝试使用 sed..."
        # 如果没有 jq，使用 sed（不太可靠，但可以作为 fallback）
        sed -i 's/"primary": "glmcode\/glm-4.7"/"primary": "glmcode\/glm-4.6"/g' "$config_file"
        log "✅ 主模型已切换到: glmcode/glm-4.6"
    fi
}

# 重启 Gateway
restart_gateway() {
    log "🔄 正在重启 OpenClaw Gateway..."

    # 尝试使用 openclaw CLI
    if command -v openclaw &> /dev/null; then
        openclaw gateway restart
        log "✅ Gateway 已重启"
    else
        # 直接使用 systemctl
        systemctl --user restart openclaw-gateway
        log "✅ Gateway 已重启（systemctl）"
    fi

    # 等待几秒确保服务启动
    sleep 3

    # 检查服务状态
    if systemctl --user is-active --quiet openclaw-gateway; then
        log "✅ Gateway 运行正常"
    else
        error "❌ Gateway 启动失败"
        return 1
    fi
}

# 发送告警
send_alert() {
    local message="⚠️ GLM-4.7 限流告警

检测到 GLM-4.7 触发限流，系统已自动切换到备用模型 GLM-4.6。

时间: $(date '+%Y-%m-%d %H:%M:%S')
主机: $(hostname)
操作: 自动切换模型 + 重启 Gateway

请检查日志: journalctl --user -u openclaw-gateway -n 100"

    if [ -n "$ALERT_WEBHOOK" ]; then
        # 如果配置了 Webhook，发送告警
        curl -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"$message\"}" \
            2>/dev/null || true
    fi

    # 输出到日志
    echo "$message"
}

# 主函数
main() {
    log "🚀 限流监控脚本启动"

    # 检测限流
    if detect_rate_limit; then
        log "⚠️ 检测到限流，开始处理..."

        # 切换模型
        switch_to_fallback_model

        # 重启 Gateway
        restart_gateway

        # 发送告警
        send_alert

        log "✅ 限流处理完成"
    else
        log "✅ 未检测到限流，无需处理"
    fi

    log "✅ 监控脚本执行完毕"
}

# 执行主函数
main "$@"
