#!/bin/bash
# 大模型 API 调用脚本
# 使用方法: ./call-llm.sh <provider> <prompt>

PROVIDER=$1
PROMPT=$2

# API Keys
GROQ_KEY="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"
GOOGLE_KEY="AIzaSyAcMMIXeaM7Or0Z2HA20z00VgWG8RxXHyg"
OPENROUTER_KEY="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"

case $PROVIDER in
  groq)
    echo "🚀 调用 Groq (Llama-3.3-70B)..."
    curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $GROQ_KEY" \
      -d "{
        \"model\": \"llama-3.3-70b-versatile\",
        \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}],
        \"max_tokens\": 500
      }" 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['choices'][0]['message']['content'])"
    ;;

  google)
    echo "🌏 调用 Google (Gemini-2.5-Flash)..."
    curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"contents\": [{\"parts\":[{\"text\": \"$PROMPT\"}]}]
      }" 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['candidates'][0]['content']['parts'][0]['text'])"
    ;;

  openrouter)
    echo "💰 调用 OpenRouter (Gemma-3-4B)..."
    curl -X POST "https://openrouter.ai/api/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $OPENROUTER_KEY" \
      -H "HTTP-Referer: http://43.134.63.176:18789" \
      -d "{
        \"model\": \"google/gemma-3-4b-it:free\",
        \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}],
        \"max_tokens\": 500
      }" 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['choices'][0]['message']['content'])"
    ;;

  *)
    echo "❌ 未知的提供商: $PROVIDER"
    echo ""
    echo "使用方法:"
    echo "  ./call-llm.sh groq \"你的问题\""
    echo "  ./call-llm.sh google \"你的问题\""
    echo "  ./call-llm.sh openrouter \"你的问题\""
    exit 1
    ;;
esac
