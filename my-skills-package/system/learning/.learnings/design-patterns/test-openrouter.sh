#!/bin/bash
# 测试 OpenRouter API Key

OPENROUTER_KEY="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"

echo "🧪 测试 OpenRouter API Key..."
echo ""

# 测试 1: 简单问答
echo "📝 测试 1: 简单问答"
curl -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_KEY" \
  -H "HTTP-Referer: https://openclaw.ai" \
  -H "X-Title: OpenClaw" \
  -d '{
    "model": "openai/gpt-oss-120b:free",
    "messages": [{"role": "user", "content": "Hello, respond with OK"}],
    "max_tokens": 10
  }' 2>/dev/null | head -20

echo ""
echo ""

# 测试 2: 查看可用模型
echo "📋 测试 2: 查看免费模型列表"
curl -X GET "https://openrouter.ai/api/v1/models" \
  -H "Authorization: Bearer $OPENROUTER_KEY" \
  2>/dev/null | grep -o '"id":[^,]*' | head -10

echo ""
echo "✅ 测试完成"
