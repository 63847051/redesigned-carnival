#!/bin/bash
# 测试 GLM-4.7 API 连接（Anthropic Messages API 格式）

echo "🧪 测试 GLM-4.7 API（Anthropic Messages API）"
echo "========================="
echo ""

API_KEY="c26c6bd6acfc44cda167b15dc338dabc.Hmfe3HhV5TjJiXqp"

# 测试 Anthropic Messages API 端点
curl -s -X POST "https://open.bigmodel.cn/api/anthropic/v1/messages" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "model": "glm-4.7",
    "max_tokens": 100,
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }' 2>&1

echo ""
echo "如果返回回复，说明 API 可用"
