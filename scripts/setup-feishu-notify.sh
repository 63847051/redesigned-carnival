#!/bin/bash
# 飞书通知快速配置脚本

echo "🔔 飞书通知配置"
echo "════════════════════════════════════"
echo ""

# 检查是否已配置
if [ -n "$FEISHU_WEBHOOK_URL" ]; then
  echo "✅ 已配置飞书 Webhook"
  echo "   Webhook URL: ${FEISHU_WEBHOOK_URL:0:50}..."
  echo ""
  read -p "是否重新配置？(y/N): " reconfig
  if [[ ! "$reconfig" =~ ^[Yy]$ ]]; then
    echo "保持现有配置"
    exit 0
  fi
fi

echo "请输入飞书机器人 Webhook URL"
echo "提示: 在飞书群聊中添加自定义机器人即可获得"
echo ""
read -p "Webhook URL: " webhook_url

if [ -z "$webhook_url" ]; then
  echo "❌ 未输入 Webhook URL"
  exit 1
fi

# 验证 URL 格式
if [[ ! "$webhook_url" =~ ^https://open\.feishu\.cn/open-apis/bot/v2/hook/ ]]; then
  echo "⚠️  警告: URL 格式可能不正确"
  echo "   正确格式: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  read -p "是否继续？(y/N): " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# 写入到系统配置
echo "配置到系统环境变量..."

# 创建配置文件
sudo tee /etc/profile.d/feishu-notify.sh > /dev/null << EOF
# 飞书通知配置
# 生成时间: $(date)
export FEISHU_WEBHOOK_URL="$webhook_url"
EOF

sudo chmod +x /etc/profile.d/feishu-notify.sh

echo ""
echo "✅ 配置完成！"
echo ""
echo "配置文件: /etc/profile.d/feishu-notify.sh"
echo ""
echo "⚠️  重要提示:"
echo "   1. 请运行以下命令使配置生效："
echo "      source /etc/profile.d/feishu-notify.sh"
echo ""
echo "   2. 或者重新登录系统"
echo ""
echo "   3. 配置将在新会话中自动加载"
echo ""

# 询问是否测试
read -p "是否现在测试通知？(Y/n): " test_now
if [[ "$test_now" =~ ^[Nn]$ ]]; then
  echo "跳过测试"
  echo "稍后可以运行: bash /root/.openclaw/workspace/scripts/feishu-notify.sh '测试' '测试内容'"
  exit 0
fi

# 测试通知
echo "发送测试通知..."
export FEISHU_WEBHOOK_URL="$webhook_url"
bash /root/.openclaw/workspace/scripts/feishu-notify.sh "✅ 配置成功" "**飞书通知已配置**

系统告警将实时发送到此群聊

测试时间: $(date '+%Y-%m-%d %H:%M:%S')"

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ 测试成功！请检查飞书群聊是否收到消息"
else
  echo ""
  echo "❌ 测试失败，请检查 Webhook URL 是否正确"
fi
