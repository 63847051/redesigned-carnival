#!/bin/bash
# 健康检查脚本 - 使用验证有效的 API 调用格式

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 子 Agent 健康检查..."
echo ""

# API Keys
GROQ_KEY="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"
GOOGLE_KEY="AIzaSyAcMMIXeaM7Or0Z2HA20z00VgWG8RxXHyg"
OPENROUTER_KEY="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"

# 1. 测试 Groq（技术专家）
echo "💻 测试 Groq（技术专家）..."
groq_response=$(curl -s -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GROQ_KEY" \
  -d '{"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "测试"}], "max_tokens": 10}' 2>/dev/null)

if echo "$groq_response" | grep -q '"error"'; then
    echo -e "${RED}❌ 技术专家（Groq）: 不可用${NC}"
    groq_status=1
else
    echo -e "${GREEN}✅ 技术专家（Groq）: 正常${NC}"
    groq_status=0
fi

# 2. 测试 OpenRouter（日志专家）
echo ""
echo "📋 测试 OpenRouter（日志专家）..."
or_response=$(curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_KEY" \
  -H "HTTP-Referer: http://43.134.63.176:18789" \
  -H "X-Title: OpenClaw" \
  -d '{"model": "google/gemma-3-4b-it:free", "messages": [{"role": "user", "content": "测试"}], "max_tokens": 10}' 2>/dev/null)

if echo "$or_response" | grep -q '"error"'; then
    echo -e "${RED}❌ 日志专家（OpenRouter）: 不可用${NC}"
    or_status=1
else
    echo -e "${GREEN}✅ 日志专家（OpenRouter）: 正常${NC}"
    or_status=0
fi

# 3. 测试 Google（设计专家）- 使用 call-llm.sh 验证有效的格式
echo ""
echo "🏠 测试 Google（设计专家）..."
google_response=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents": [{"parts":[{"text": "测试"}]}]}' 2>/dev/null)

if echo "$google_response" | grep -q '"error"' || [ -z "$google_response" ]; then
    echo -e "${RED}❌ 设计专家（Google）: 不可用${NC}"
    google_status=1
else
    echo -e "${GREEN}✅ 设计专家（Google）: 正常${NC}"
    google_status=0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 总结
echo "📊 状态总结:"
echo "   Groq（技术）: $([ $groq_status -eq 0 ] && echo "✅ 正常" || echo "❌ 不可用")"
echo "   OpenRouter（日志）: $([ $or_status -eq 0 ] && echo "✅ 正常" || echo "❌ 不可用")"
echo "   Google（设计）: $([ $google_status -eq 0 ] && echo "✅ 正常" || echo "❌ 不可用")"

echo ""

# 返回退出码
if [ $groq_status -ne 0 ] || [ $or_status -ne 0 ] || [ $google_status -ne 0 ]; then
    echo "⚠️ 有专家不可用，建议："
    echo "   1. 检查 API Key 是否正确"
    echo "   2. 检查网络连接"
    echo "   3. 使用可用的专家继续工作"
    exit 1
fi

echo "✅ 所有专家正常 - 系统完全可用！"
exit 0
