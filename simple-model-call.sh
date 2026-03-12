#!/bin/bash
# 简化的智能模型调用脚本
# 自动选择最佳模型并执行

export OPENROUTER_API_KEY="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"
export NVIDIA_API_KEY="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"

TASK_TYPE="${1:-general}"
CONTENT="${2:-Hello!}"

echo "🧠 智能模型调用"
echo "================"
echo "任务类型: $TASK_TYPE"
echo "内容: $CONTENT"
echo ""

# 根据任务类型选择模型
case "$TASK_TYPE" in
    "code"|"编程"|"开发")
        echo "🔧 代码任务 → 使用 NVIDIA gpt-oss-120b"
        python3 << 'PYTHON'
from openai import OpenAI
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="$NVIDIA_API_KEY"
)
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "$CONTENT"}],
    max_tokens=500
)
print(response.choices[0].message.content)
PYTHON
        ;;
    
    "chinese"|"中文")
        echo "🇨🇳 中文任务 → 使用 OpenRouter GLM-4.5-Air"
        curl -s -X POST https://openrouter.ai/api/v1/chat/completions \
            -H "Authorization: Bearer $OPENROUTER_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{
                \"model\": \"z-ai/glm-4.5-air:free\",
                \"messages\": [{\"role\": \"user\", \"content\": \"$CONTENT\"}],
                \"max_tokens\": 500
            }" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('choices',[{}])[0].get('message',{}').get('content','No response'))"
        ;;
    
    "ultra_fast"|"超快"|"快速")
        echo "⚡ 超快速任务 → 使用 OpenRouter Gemma 3 4B"
        curl -s -X POST https://openrouter.ai/api/v1/chat/completions \
            -H "Authorization: Bearer $OPENROUTER_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{
                \"model\": \"google/gemma-3-4b-it:free\",
                \"messages\": [{\"role\": \"user\", \"content\": \"$CONTENT\"}],
                \"max_tokens\": 200
            }" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('choices',[{}])[0].get('message',{}').get('content','No response'))"
        ;;
    
    *)
        echo "🎯 通用任务 → 使用 NVIDIA gpt-oss-120b"
        python3 << 'PYTHON'
from openai import OpenAI
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="$NVIDIA_API_KEY"
)
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "$CONTENT"}],
    max_tokens=500
)
print(response.choices[0].message.content)
PYTHON
        ;;
esac

echo ""
echo "================"
echo "✅ 完成！"
