#!/bin/bash
# 智能模型切换脚本
# 根据任务复杂度自动选择最佳模型（优先使用o3/o1，免费模型备用）

TASK_TYPE="$1"
TASK_COMPLEXITY="${2:-3}"  # 默认中等复杂度（1-5）
CONTENT="$3"

# 环境变量
OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}"
NVIDIA_API_KEY="${NVIDIA_API_KEY:-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}"
GROQ_API_KEY="${GROQ_API_KEY:-}"
GOOGLE_API_KEY="${GOOGLE_API_KEY:-}"

# 日志
LOG_FILE="$HOME/.openclaw/workspace/.model-switching.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# 检查API Key
check_api_key() {
    local key_name="$1"
    local api_key="$2"
    
    if [ -z "$api_key" ]; then
        return 1
    fi
    
    # 简单验证
    if [[ ! "$api_key" =~ ^(sk-|gsk_|nvapi-|AIza|ghp_) ]]; then
        return 1
    fi
    
    return 0
}

# 选择模型
select_model() {
    local task_type="$1"
    local complexity="$2"
    
    log "🎯 任务类型: $task_type"
    log "复杂度: $complexity/5"
    
    # 优先级1: 尝试使用 o3/o1（如果有GitHub Copilot）
    if check_api_key "GITHUB_TOKEN" "$GITHUB_TOKEN"; then
        log "🏆 尝试使用 o3（GitHub Models）"
        
        response=$(curl -s -X POST https://models.inference.github.azure.com/openai/deployments \
            -H "Authorization: Bearer $GITHUB_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{
                "model": "openai/o3",
                "messages": [{"role": "user", "content": "$CONTENT"}],
                "max_tokens": 1000,
                "stream": false
            }' 2>&1)
        
        if echo "$response" | grep -q "content"; then
            log "✅ 使用 o3"
            echo "github:openai/o3"
            return 0
        else
            log "⚠️ o3 不可用"
        fi
    fi
    
    # 优先级2: 根据复杂度和类型选择免费模型
    case "$task_type" in
        "code"|"编程"|"开发")
            if [ "$complexity" -ge 4 ]; then
                # 高复杂度：代码专家
                if check_api_key "NVIDIA" "$NVIDIA_API_KEY"; then
                    log "✅ 使用 NVIDIA gpt-oss-120b"
                    echo "nvidia:openai/gpt-oss-120b"
                elif check_api_key "OpenRouter" "$OPENROUTER_API_KEY"; then
                    log "✅ 使用 OpenRouter gpt-oss-120b"
                    echo "openrouter:openai/gpt-oss-120b:free"
                else
                    log "⚠️ 回退到基础模型"
                    echo "openrouter:meta-llama/llama-3.3-70b-instruct:free"
                fi
            else
                # 低复杂度：快速模型
                if check_api_key "OpenRouter" "$OPENROUTER_API_KEY"; then
                    log "✅ 使用 OpenRouter Gemma 3 4B"
                    echo "openrouter:google/gemma-3-4b-it:free"
                elif check_api_key "Groq" "$GROQ_API_KEY"; then
                    log "✅ 使用 Groq Gemma 3 2B"
                    echo "groq:gemma-3-2b-it"
                else
                    log "⚠️ 回退到默认"
                    echo "openrouter:google/gemma-3-4b-it:free"
                fi
            fi
            ;;
        
        "chinese"|"中文"|"翻译")
            # 中文优先
            if check_api_key "Google AI Studio" "$GOOGLE_API_KEY"; then
                log "✅ 使用 Google Gemini 3 Flash"
                echo "googleai:gemini-2.5-flash"
            elif check_api_key "OpenRouter" "$OPENROUTER_API_KEY"; then
                log "✅ 使用 OpenRouter GLM-4.5-Air"
                echo "openrouter:z-ai/glm-4.5-air:free"
            else
                log "⚠️ 回退到通用模型"
                echo "openrouter:meta-llama/llama-3.3-70b-instruct:free"
            fi
            ;;
        
        "ultra_fast"|"超快"|"快速")
            # 超快速响应
            if check_api_key "Groq" "$GROQ_API_KEY"; then
                log "✅ 使用 Groq Gemma 3 2B"
                echo "groq:gemma-3-2b-it"
            elif check_api_key "OpenRouter" "$OPENROUTER_API_KEY"; then
                log "✅ 使用 OpenRouter Gemma 3 4B"
                echo "openrouter:google/gemma-3-4b-it:free"
            else
                log "⚠️ 使用默认模型"
                echo "openrouter:google/gmeqa-3-4b-it:free"
            fi
            ;;
        
        "flagship"|"旗舰"|"最强")
            # 尝试旗舰模型
            if check_api_key "GitHub Models" "$GITHUB_TOKEN"; then
                log "✅ 尝试 GitHub gpt-5"
                echo "github:openai/gpt-5"
            elif check_api_key "OpenRouter" "$OPENROUTER_API_KEY"; then
                log "✅ 使用 OpenRouter Llama 3.3 70B"
                echo "openrouter:meta-llama/llama-3.3-70b-instruct:free"
            else
                log "⚠️ 回退到基础模型"
                echo "openrouter:google/gemma-3-4b-it:free"
            fi
            ;;
        
        *)
            # 默认：通用模型
            if check_api_key "NVIDIA" "$NVIDIA_API_KEY"; then
                log "✅ 使用 NVIDIA gpt-oss-120b"
                echo "nvidia:openai/gpt-oss-120b"
            elif check_api_key "OpenRouter" "$OPENROUTER_API_KEY"; then
                log "✅ 使用 OpenRouter Llama 3.3 70B"
                echo "openrouter:meta-llama/llama-3.3-70b-instruct:free"
            else
                log "⚠️ 使用基础模型"
                echo "openrouter:google/gemma-3-4b-it:free"
            fi
            ;;
    esac
    
    return 0
}

# 调用模型
call_model() {
    local model_choice="$1"
    IFS=':' read -r provider model <<< "$model_choice"
    
    log "📞 调用模型: $provider/$model"
    
    case "$provider" in
        "openrouter")
            curl -s -X POST https://openrouter.ai/api/v1/chat/completions \
                -H "Authorization: Bearer $OPENROUTER_API_KEY" \
                -H "Content-Type: application/json" \
                -H "HTTP-Referer: $OPENCLAW_APP_NAME" \
                -d "{
                    \"model\": \"$model\",
                    \"messages\": [{\"role\": \"user\", \"content\": \"$CONTENT\"}],
                    \"max_tokens\": 1000
                }" 2>&1
            ;;
        
        "nvidia")
            python3 << 'PYTHON'
from openai import OpenAI
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="$NVIDIA_API_KEY"
)
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "$CONTENT"}],
    max_tokens=1000
)
print(response.choices[0].message.content)
PYTHON
            ;;
        
        "groq")
            curl -s -X POST https://api.groq.com/openai/v1/chat/completions \
                -H "Authorization: Bearer $GROQ_API_KEY" \
                -H "Content-Type: application/json" \
                -d "{
                    \"model\": \"$model\",
                    \"messages\": [{\"role\": \"user\", \"content\": \"$CONTENT\"}],
                    \"max_tokens\": 1000
                }" 2>&1
            ;;
        
        "googleai")
            curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY" \
                -H "Content-Type: application/json" \
                -d "{
                    \"contents\": [{
                        \"parts\": [{\"text\": \"$CONTENT\"}]
                    }]
                }" 2>&1
            ;;
        
        "github")
            # GitHub Models需要特殊处理
            log "⚠️ GitHub Models需要通过 GitHub Copilot"
            echo "请使用GitHub Copilot访问gpt-5"
            ;;
        
        *)
            log "❌ 未知的提供商: $provider"
            echo "错误：不支持的模型提供商"
            return 1
            ;;
    esac
    
    return 0
}

# 快速调用函数
model() {
    local task_type="$1"
    local complexity="${2:-3}"
    local content="$3"
    
    if [ -z "$content" ]; then
        echo "用法: model <task_type> [complexity] <content>"
        echo ""
        echo "任务类型:"
        echo "  code, 编程, 开发"
        echo "  chinese, 中文, 翻译"
        "   ultra_fast, 超快, 快速"
        "   flagship, 旗舰, 最强"
        ""
        echo "复杂度: 1-5 (默认3)"
        echo ""
        echo "示例:"
        echo "  model code 5 '写一个Python排序算法'"
        echo "  model chinese 3 '你好'"
        echo "  model ultra_fast 1 '在吗'"
        echo "  model flagship 5 '量子计算是什么'"
        exit 0
    fi
    
    # 选择模型
    model_choice=$(select_model "$task_type" "$complexity")
    
    # 调用模型
    call_model "$model_choice" "$content"
}

# 如果直接运行脚本，显示帮助
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    model "$@"
fi
