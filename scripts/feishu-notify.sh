#!/bin/bash
# 飞书通知脚本
# 用于发送系统告警到飞书

# 配置飞书 Webhook URL（请替换为你的 Webhook）
FEISHU_WEBHOOK_URL="${FEISHU_WEBHOOK_URL:-}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 发送飞书通知
send_feishu_notification() {
  local title="$1"
  local content="$2"
  local status="$3"  # success, warning, error, info

  # 如果没有配置 Webhook，直接返回
  if [ -z "$FEISHU_WEBHOOK_URL" ]; then
    echo "⚠️  未配置飞书 Webhook URL"
    echo "   请设置环境变量: export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/xxx'"
    return 1
  fi

  # 根据状态选择颜色
  local color=""
  case "$status" in
    success)
      color="green"
      ;;
    warning)
      color="yellow"
      ;;
    error)
      color="red"
      ;;
    info|*)
      color="blue"
      ;;
  esac

  # 构建消息
  local message=$(cat <<EOF
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "$title"
      },
      "template": "$color"
    },
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "$content"
        }
      },
      {
        "tag": "hr"
      },
      {
        "tag": "div",
        "text": {
          "tag": "plain_text",
          "content": "服务器: $(hostname) | 时间: $(date '+%Y-%m-%d %H:%M:%S')"
        }
      }
    ]
  }
}
EOF
)

  # 发送请求
  local response=$(curl -s -X POST "$FEISHU_WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$message" \
    --max-time 10)

  # 检查响应
  if echo "$response" | grep -q '"StatusCode":0'; then
    echo "✅ 飞书通知发送成功"
    return 0
  else
    echo "❌ 飞书通知发送失败: $response"
    return 1
  fi
}

# 告警类型
case "$1" in
  memory)
    # 内存告警
    MEMORY_USAGE="$2"
    THRESHOLD="$3"
    send_feishu_notification \
      "⚠️ 内存使用告警" \
      "**内存使用过高**

当前使用: **${MEMORY_USAGE}%**
告警阈值: ${THRESHOLD}%

请及时检查系统状态！" \
      "warning"
    ;;

  service)
    # 服务告警
    SERVICE_NAME="$2"
    STATUS="$3"
    send_feishu_notification \
      "🚨 服务状态告警" \
      "**${SERVICE_NAME} 状态异常**

当前状态: **${STATUS}**

请及时检查服务状态！" \
      "error"
    ;;

  evolution)
    # 进化完成通知
    EVOLUTION_REPORT="$2"
    send_feishu_notification \
      "🧬 进化学习完成" \
      "**系统进化完成**

${EVOLUTION_REPORT}

系统已变得更强大！✨" \
      "success"
    ;;

  health)
    # 健康检查报告
    HEALTH_REPORT="$2"
    send_feishu_notification \
      "📊 系统健康检查" \
      "**系统健康状态**

${HEALTH_REPORT}

一切正常！✅" \
      "info"
    ;;

  *)
    # 自定义消息
    TITLE="$1"
    CONTENT="$2"
    send_feishu_notification "$TITLE" "$CONTENT" "info"
    ;;
esac
