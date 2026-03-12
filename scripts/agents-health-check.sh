#!/bin/bash
# 子 Agent 健康检查脚本
# 检查所有专家的 API 连接状态

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 子 Agent 健康检查..."
echo ""

check_api() {
    local name=$1
    local url=$2
    local key=$3
    local model=$4
    local test_prompt="测试"

    echo "检查: $name"

    # 根据不同的 API 格式调整
    if [[ $url == *"generativelanguage"* ]]; then
        # Google API 格式
        response=$(curl -s -X POST "${url}?key=${key}" \
            -H "Content-Type: application/json" \
            -d "{\"contents\": [{\"parts\":[{\"text\": \"${test_prompt}\"}]}]}]" 2>&1)
        
        if echo "$response" | grep -q '"error"'; then
            echo -e "${RED}❌ ${name}: API 错误${NC}"
            return 1
        else
            echo -e "${GREEN}✅ ${name}: 正常${NC}"
            return 0
        fi
    else
        # OpenAI 兼容格式（Groq, OpenRouter）
        response=$(curl -s -X POST "$url" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${key}" \
            -d "{\"model\": \"${model}\", \"messages\": [{\"role\": \"user\", \"content\": \"${test_prompt}\"}], \"max_tokens\": 10}" 2>&1)
        
        if echo "$response" | grep -q '"error"'; then
            echo -e "${RED}❌ ${name}: API 错误${NC}"
            return 1
        else
            echo -e "${GREEN}✅ ${name}: 正常${NC}"
            return 0
        fi
    fi
}

# 检查所有专家
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 设计专家（Google）
check_api \
    "🏠 设计专家(Google)" \
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyAcMMIXeaM7Or0Z2HA20z00VgWG8RxXHyg" \
    "AIzaSyAcMMIXeaM7Or0Z2HA20z00VgWG8RxXHyg" \
    "gemini-2.5-flash"

echo ""

# 技术专家（Groq）
check_api \
    "💻 技术专家(Groq)" \
    "https://api.groq.com/openai/v1/chat/completions" \
    "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" \
    "llama-3.3-70b-versatile"

echo ""

# 日志专家（OpenRouter）
check_api \
    "📋 日志专家(OpenRouter)" \
    "https://openrouter.ai/api/v1/chat/completions" \
    "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" \
    "google/gemma-3-4b-it:free"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 健康检查完成"
echo ""
